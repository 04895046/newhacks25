# Complete API Documentation

**Backend Base URL:** `http://your-server:8000/api/`

**Last Updated:** October 25, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Itinerary Management](#itinerary-management)
4. [Bill Group & Expense Management (Ledger)](#bill-group--expense-management-ledger)
5. [Receipt Parsing (OCR)](#receipt-parsing-ocr)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)

---

## Authentication

All endpoints except `/register/` and `/login/` require authentication via token.

**Header Format:**
```
Authorization: Token <your_token_here>
```

### 1.1 Register

**Endpoint:** `POST /api/register/`

**Description:** Create a new user account

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Success Response (201):**
```json
{
  "id": 1,
  "username": "john_doe"
}
```

**Error Response (400):**
```json
{
  "username": ["A user with that username already exists."]
}
```

---

### 1.2 Login (Enhanced for Mobile)

**Endpoint:** `POST /api/login/`

**Description:** Authenticate user and receive auth token + user info

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Success Response (200):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john_doe"
  }
}
```

**Mobile Integration Note:** This endpoint now returns user information alongside the token, eliminating the need for a separate API call to fetch user details after login.

**Error Response (400):**
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

## User Management

### 2.1 Search Users

**Endpoint:** `GET /api/users/search/`

**Description:** Search for users by username (case-insensitive). Returns max 20 results, excludes requesting user.

**Authentication:** Required

**Query Parameters:**
- `q` (required): Username search query

**Example Request:**
```
GET /api/users/search/?q=alice
```

**Success Response (200):**
```json
[
  {
    "id": 2,
    "username": "alice"
  },
  {
    "id": 6,
    "username": "alice_smith"
  }
]
```

**Mobile Integration Note:** Use this endpoint to find user IDs when adding members to bill groups. Search is case-insensitive and supports partial matches.

---

## Itinerary Management

### 3.1 List All Itineraries

**Endpoint:** `GET /api/itineraries/`

**Description:** Retrieve all itineraries belonging to the authenticated user

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "Weekend in Toronto",
    "region": "Toronto",
    "created_at": "2025-10-20T14:30:00Z",
    "updated_at": "2025-10-21T10:15:00Z",
    "owner": 1
  },
  {
    "id": 2,
    "title": "AI Trip to Paris",
    "region": "Paris",
    "created_at": "2025-10-15T09:00:00Z",
    "updated_at": "2025-10-15T09:00:00Z",
    "owner": 1
  }
]
```

---

### 3.2 Get Single Itinerary (with Items)

**Endpoint:** `GET /api/itineraries/{id}/`

**Description:** Retrieve a specific itinerary with all its items

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Weekend in Toronto",
  "region": "Toronto",
  "created_at": "2025-10-20T14:30:00Z",
  "updated_at": "2025-10-21T10:15:00Z",
  "owner": 1,
  "items": [
    {
      "id": 1,
      "description": "Visit CN Tower",
      "location_name": "CN Tower",
      "start_time": "2025-10-25T10:00:00Z",
      "end_time": "2025-10-25T12:00:00Z",
      "order": 0
    },
    {
      "id": 2,
      "description": "Lunch at St. Lawrence Market",
      "location_name": "St. Lawrence Market",
      "start_time": "2025-10-25T12:30:00Z",
      "end_time": "2025-10-25T14:00:00Z",
      "order": 1
    }
  ]
}
```

---

### 3.3 Create Itinerary

**Endpoint:** `POST /api/itineraries/`

**Description:** Create a new itinerary

**Authentication:** Required

**Request Body:**
```json
{
  "title": "Summer Vacation",
  "region": "Montreal"
}
```

**Success Response (201):**
```json
{
  "id": 3,
  "title": "Summer Vacation",
  "region": "Montreal",
  "created_at": "2025-10-25T15:00:00Z",
  "updated_at": "2025-10-25T15:00:00Z",
  "owner": 1,
  "items": []
}
```

---

### 3.4 Update Itinerary

**Endpoint:** `PUT /api/itineraries/{id}/` or `PATCH /api/itineraries/{id}/`

**Description:** Update an existing itinerary

**Authentication:** Required

**Request Body (PATCH - partial update):**
```json
{
  "title": "Updated Summer Vacation"
}
```

**Success Response (200):**
```json
{
  "id": 3,
  "title": "Updated Summer Vacation",
  "region": "Montreal",
  "created_at": "2025-10-25T15:00:00Z",
  "updated_at": "2025-10-25T15:30:00Z",
  "owner": 1,
  "items": []
}
```

---

### 3.5 Delete Itinerary

**Endpoint:** `DELETE /api/itineraries/{id}/`

**Description:** Delete an itinerary and all its items

**Authentication:** Required

**Success Response (204):** No content

---

### 3.6 Generate AI Itinerary

**Endpoint:** `POST /api/itineraries/generate/`

**Description:** Generate an AI-powered itinerary based on region and needs

**Authentication:** Required

**Request Body:**
```json
{
  "region": "Toronto",
  "needs": "3 day trip, love museums and food"
}
```

**Success Response (201):**
```json
{
  "id": 4,
  "title": "AI Trip to Toronto",
  "region": "Toronto",
  "created_at": "2025-10-25T16:00:00Z",
  "updated_at": "2025-10-25T16:00:00Z",
  "owner": 1,
  "items": [
    {
      "id": 10,
      "description": "AI Generated: Explore Toronto downtown",
      "location_name": "Toronto City Center",
      "start_time": null,
      "end_time": null,
      "order": 0
    },
    {
      "id": 11,
      "description": "AI Generated: Visit a famous landmark in Toronto",
      "location_name": "Famous Landmark",
      "start_time": null,
      "end_time": null,
      "order": 1
    },
    {
      "id": 12,
      "description": "AI Generated: Enjoy local cuisine",
      "location_name": "Local Restaurant",
      "start_time": null,
      "end_time": null,
      "order": 2
    }
  ]
}
```

**Note:** Currently returns placeholder data. Integrate your ML model in `api/views.py` at the marked location.

---

### 3.7 List Itinerary Items

**Endpoint:** `GET /api/itinerary-items/`

**Description:** List all itinerary items belonging to user's itineraries

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 1,
    "itinerary": 1,
    "description": "Visit CN Tower",
    "location_name": "CN Tower",
    "start_time": "2025-10-25T10:00:00Z",
    "end_time": "2025-10-25T12:00:00Z",
    "order": 0
  },
  {
    "id": 2,
    "itinerary": 1,
    "description": "Lunch at St. Lawrence Market",
    "location_name": "St. Lawrence Market",
    "start_time": "2025-10-25T12:30:00Z",
    "end_time": "2025-10-25T14:00:00Z",
    "order": 1
  }
]
```

---

### 3.8 Create Itinerary Item

**Endpoint:** `POST /api/itinerary-items/`

**Description:** Add a new item to an itinerary

**Authentication:** Required

**Request Body:**
```json
{
  "itinerary": 1,
  "description": "Visit Royal Ontario Museum",
  "location_name": "ROM",
  "start_time": "2025-10-25T14:30:00Z",
  "end_time": "2025-10-25T17:00:00Z",
  "order": 2
}
```

**Success Response (201):**
```json
{
  "id": 3,
  "itinerary": 1,
  "description": "Visit Royal Ontario Museum",
  "location_name": "ROM",
  "start_time": "2025-10-25T14:30:00Z",
  "end_time": "2025-10-25T17:00:00Z",
  "order": 2
}
```

---

### 3.9 Update Itinerary Item

**Endpoint:** `PUT /api/itinerary-items/{id}/` or `PATCH /api/itinerary-items/{id}/`

**Description:** Update an existing itinerary item

**Authentication:** Required

**Request Body (PATCH):**
```json
{
  "description": "Extended visit to Royal Ontario Museum"
}
```

**Success Response (200):**
```json
{
  "id": 3,
  "itinerary": 1,
  "description": "Extended visit to Royal Ontario Museum",
  "location_name": "ROM",
  "start_time": "2025-10-25T14:30:00Z",
  "end_time": "2025-10-25T17:00:00Z",
  "order": 2
}
```

---

### 3.10 Delete Itinerary Item

**Endpoint:** `DELETE /api/itinerary-items/{id}/`

**Description:** Delete an itinerary item

**Authentication:** Required

**Success Response (204):** No content

---

## Bill Group & Expense Management (Ledger)

### 4.1 List Bill Groups

**Endpoint:** `GET /api/groups/`

**Description:** List all bill groups the authenticated user is a member of

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 1,
    "name": "Tokyo Trip 2025",
    "description": "Group expenses for Tokyo",
    "created_at": "2025-10-20T10:00:00Z",
    "members": [
      {
        "id": 1,
        "username": "john_doe"
      },
      {
        "id": 2,
        "username": "alice"
      },
      {
        "id": 3,
        "username": "bob"
      }
    ]
  }
]
```

**Mobile Integration Note:** The `members` field now includes user IDs alongside usernames, enabling direct expense creation without additional API calls.

---

### 4.2 Get Single Bill Group (with Expenses)

**Endpoint:** `GET /api/groups/{id}/`

**Description:** Retrieve a specific bill group with all its expenses

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Tokyo Trip 2025",
  "description": "Group expenses for Tokyo",
  "created_at": "2025-10-20T10:00:00Z",
  "members": [
    {
      "id": 1,
      "username": "john_doe"
    },
    {
      "id": 2,
      "username": "alice"
    },
    {
      "id": 3,
      "username": "bob"
    }
  ],
  "expenses": [
    {
      "id": 1,
      "group": 1,
      "description": "Hotel booking",
      "total_amount": "450.00",
      "date": "2025-10-22T10:30:00.000000Z",
      "payer": 1,
      "payer_username": "john_doe",
      "split_type": "E",
      "receipt_image": null,
      "item_data_json": null,
      "splits_read": [
        {
          "user_owed": 1,
          "user_owed_username": "john_doe",
          "amount_owed": "150.00"
        },
        {
          "user_owed": 2,
          "user_owed_username": "alice",
          "amount_owed": "150.00"
        },
        {
          "user_owed": 3,
          "user_owed_username": "bob",
          "amount_owed": "150.00"
        }
      ]
    }
  ]
}
```

**Response Field Details:**
- `payer`: User ID of the person who paid (integer)
- `payer_username`: Username of the payer for display (string)
- `date`: Timestamp when expense was created (datetime)
- `splits_read`: Array of split details with user IDs and usernames

---

### 4.3 Create Bill Group

**Endpoint:** `POST /api/groups/`

**Description:** Create a new bill group with members

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Weekend Getaway",
  "description": "Expenses for cottage trip",
  "members": [2, 3, 5]
}
```

**Field Details:**
- `name`: Group name (required)
- `description`: Group description (optional)
- `members`: Array of user IDs to add as members (optional). The creator is automatically added.

**Success Response (201):**
```json
{
  "id": 2,
  "name": "Weekend Getaway",
  "description": "Expenses for cottage trip",
  "created_at": "2025-10-25T16:30:00Z",
  "members": [
    {
      "id": 1,
      "username": "john_doe"
    },
    {
      "id": 2,
      "username": "alice"
    },
    {
      "id": 3,
      "username": "bob"
    },
    {
      "id": 5,
      "username": "charlie"
    }
  ]
}
```

**Mobile Integration Note:** Use the `/api/users/search/` endpoint to find user IDs before creating a group.

---

### 4.4 Update Bill Group

**Endpoint:** `PUT /api/groups/{id}/` or `PATCH /api/groups/{id}/`

**Description:** Update bill group details

**Authentication:** Required

**Request Body (PATCH):**
```json
{
  "description": "Updated description for cottage trip"
}
```

**Success Response (200):** Returns updated group with same structure as 4.2

**Note:** Member management via this endpoint is not currently supported. Members are set during creation.

---

### 4.5 Delete Bill Group

**Endpoint:** `DELETE /api/groups/{id}/`

**Description:** Delete a bill group and all associated expenses

**Authentication:** Required

**Success Response (204):** No content

---

### 4.6 Get Group Balances (Settle Up)

**Endpoint:** `GET /api/groups/{id}/balances/`

**Description:** Calculate net balances for all group members

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "username": "john_doe",
    "balance": "150.00"
  },
  {
    "username": "alice",
    "balance": "-50.00"
  },
  {
    "username": "bob",
    "balance": "-100.00"
  }
]
```

**Balance Interpretation:**
- **Positive balance:** User is owed money (paid more than their share)
- **Negative balance:** User owes money (paid less than their share)
- **Zero balance:** User is settled up

---

### 4.7 Get Group Settlements (Who Owes Whom)

**Endpoint:** `GET /api/groups/{id}/settlements/`

**Description:** Calculate the optimal settlement plan showing exactly who should pay whom to settle the group. Uses a greedy algorithm to minimize the number of transactions.

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "from": "bob",
    "to": "alice",
    "amount": "30.00"
  },
  {
    "from": "charlie",
    "to": "alice",
    "amount": "70.00"
  },
  {
    "from": "david",
    "to": "alice",
    "amount": "150.00"
  }
]
```

**Response Format:**
- `from`: Username of the person who needs to pay
- `to`: Username of the person who should receive payment
- `amount`: Amount to be transferred (string format with 2 decimal places)

**Use Case:**
This endpoint answers the question "Who owes whom?" by providing a concrete settlement plan. Instead of just knowing net balances, users get actionable payment instructions.

**Example Scenario:**
- Alice paid $400 for hotel
- Bob paid $120 for dinner  
- Charlie paid $80 for gas
- Each person owes $150 total

**Result:**
- Bob pays Alice $30
- Charlie pays Alice $70
- David pays Alice $150

**Mobile Integration:**
```kotlin
// Fetch settlement plan
val settlements = api.getGroupSettlements(groupId)

// Display payment buttons
settlements.forEach { settlement ->
    showPaymentButton(
        message = "${settlement.from} pays ${settlement.to}",
        amount = settlement.amount,
        onPaid = { markAsSettled(settlement) }
    )
}
```

---

### 4.8 List Expenses

**Endpoint:** `GET /api/expenses/`

**Description:** List all expenses from groups the user is a member of

**Authentication:** Required

**Success Response (200):**
```json
[
  {
    "id": 1,
    "group": 1,
    "description": "Hotel booking",
    "total_amount": "450.00",
    "date": "2025-10-22T10:30:00.000000Z",
    "payer": 1,
    "payer_username": "john_doe",
    "split_type": "E",
    "receipt_image": null,
    "item_data_json": null,
    "splits_read": [
      {
        "user_owed": 1,
        "user_owed_username": "john_doe",
        "amount_owed": "150.00"
      },
      {
        "user_owed": 2,
        "user_owed_username": "alice",
        "amount_owed": "150.00"
      },
      {
        "user_owed": 3,
        "user_owed_username": "bob",
        "amount_owed": "150.00"
      }
    ]
  }
]
```

**Response Field Details:**
- `payer`: User ID of the person who paid
- `payer_username`: Username of the payer for display
- `date`: Timestamp when expense was created
- `splits_read`: Array of split details with user IDs and usernames

---

### 4.8 Create Expense

**Endpoint:** `POST /api/expenses/`

**Description:** Create a new expense with automatic split calculation

**Authentication:** Required

**Request Body:**
```json
{
  "group": 1,
  "description": "Dinner at restaurant",
  "total_amount": "120.00",
  "date": "2025-10-25",
  "payer": 1,
  "splits": [
    {
      "user_owed": 1,
      "amount_owed": "40.00"
    },
    {
      "user_owed": 2,
      "amount_owed": "40.00"
    },
    {
      "user_owed": 3,
      "amount_owed": "40.00"
    }
  ]
}
```

**Field Details:**
- `group`: Bill group ID (required)
- `description`: Expense description (required)
- `total_amount`: Total expense amount (required, decimal)
- `date`: Date of expense (required, format: YYYY-MM-DD)
- `payer`: User ID who paid (required)
- `splits`: Array of split objects (required)
  - `user_owed`: User ID who owes this portion
  - `amount_owed`: Amount this user owes (decimal)

**Validation Rules:**
1. Payer must exist and be a member of the group
2. All users in splits must exist and be members of the group
3. Sum of all `amount_owed` must equal `total_amount`

**Success Response (201):**
```json
{
  "id": 2,
  "group": 1,
  "description": "Dinner at restaurant",
  "total_amount": "120.00",
  "date": "2025-10-25T19:30:00.000000Z",
  "payer": 1,
  "payer_username": "john_doe",
  "split_type": "E",
  "receipt_image": null,
  "item_data_json": null,
  "splits_read": [
    {
      "user_owed": 1,
      "user_owed_username": "john_doe",
      "amount_owed": "40.00"
    },
    {
      "user_owed": 2,
      "user_owed_username": "alice",
      "amount_owed": "40.00"
    },
    {
      "user_owed": 3,
      "user_owed_username": "bob",
      "amount_owed": "40.00"
    }
  ]
}
```

**Note:** The response includes complete expense details with payer information and readable splits, unlike the create request which uses `payer_id` and `splits` array.

**Error Response (400) - Invalid Payer:**
```json
{
  "non_field_errors": ["Payer with id 999 does not exist."]
}
```

**Error Response (400) - Payer Not in Group:**
```json
{
  "non_field_errors": ["Payer john_doe is not a member of this group."]
}
```

**Error Response (400) - Split Total Mismatch:**
```json
{
  "non_field_errors": ["Sum of splits (100.00) does not match total_amount (120.00)."]
}
```

**Error Response (400) - Invalid Split User:**
```json
{
  "non_field_errors": ["User with id 999 in splits does not exist or is not a member of this group."]
}
```

---

### 4.9 Get Single Expense

**Endpoint:** `GET /api/expenses/{id}/`

**Description:** Retrieve details of a specific expense

**Authentication:** Required

**Success Response (200):** Same structure as create response

---

### 4.10 Update Expense

**Endpoint:** `PUT /api/expenses/{id}/` or `PATCH /api/expenses/{id}/`

**Description:** Update an existing expense

**Authentication:** Required

**Request Body:** Same validation rules as create

**Success Response (200):** Returns updated expense

---

### 4.11 Delete Expense

**Endpoint:** `DELETE /api/expenses/{id}/`

**Description:** Delete an expense and all its splits

**Authentication:** Required

**Success Response (204):** No content

---

## Receipt Parsing (OCR)

### 5.1 Parse Receipt Image

**Endpoint:** `POST /api/ocr/parse-receipt/`

**Description:** Upload a receipt image for AI-powered OCR and structured data extraction using Google Gemini

**Authentication:** Required

**Content-Type:** `multipart/form-data`

**Request Body:**
- `image`: Image file (jpg, png, etc.)

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/ocr/parse-receipt/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -F "image=@/path/to/receipt.jpg"
```

**Success Response (200):**
```json
{
  "merchant_name": "Coffee Shop",
  "date": "2025-10-25",
  "total": 45.50,
  "items": [
    {
      "name": "Cappuccino",
      "quantity": 2,
      "price": 8.50,
      "currency": "USD",
      "price_in_cad": 11.56
    },
    {
      "name": "Croissant",
      "quantity": 3,
      "price": 4.50,
      "currency": "USD",
      "price_in_cad": 6.12
    },
    {
      "name": "Orange Juice",
      "quantity": 1,
      "price": 5.50,
      "currency": "USD",
      "price_in_cad": 7.48
    }
  ]
}
```

**Field Details:**
- `merchant_name`: Store/restaurant name
- `date`: Receipt date (YYYY-MM-DD)
- `total`: Total amount on receipt
- `items`: Array of line items
  - `name`: Item name
  - `quantity`: Quantity purchased
  - `price`: Price per item in original currency
  - `currency`: Original currency code (USD, EUR, etc.)
  - `price_in_cad`: Converted price in CAD using live exchange rates

**Error Response (400):**
```json
{
  "error": "No image file provided in 'image' field."
}
```

**Error Response (500):**
```json
{
  "error": "Failed to parse receipt: [error details]"
}
```

**Notes:**
- Image is processed in memory and not saved on the server
- Requires `GEMINI_API_KEY` to be configured in backend settings
- Uses live FX rates from fxratesapi.com for currency conversion
- Schema is defined in `api/schema.py` using Pydantic

---

## Data Models

### User
```python
{
  "id": Integer,
  "username": String
}
```

### Itinerary
```python
{
  "id": Integer,
  "title": String,
  "region": String (optional),
  "created_at": DateTime,
  "updated_at": DateTime,
  "owner": Integer (User ID),
  "items": Array<ItineraryItem> (only in detail view)
}
```

### ItineraryItem
```python
{
  "id": Integer,
  "itinerary": Integer (Itinerary ID),
  "description": String,
  "location_name": String (optional),
  "start_time": DateTime (optional),
  "end_time": DateTime (optional),
  "order": Integer (defines sequence)
}
```

### BillGroup
```python
{
  "id": Integer,
  "name": String,
  "description": String (optional),
  "created_at": DateTime,
  "members": Array<{id: Integer, username: String}>,
  "expenses": Array<Expense> (only in detail view)
}
```

### Expense
```python
{
  "id": Integer,
  "group": Integer (BillGroup ID),
  "description": String,
  "total_amount": Decimal (string format),
  "date": Date,
  "payer": Integer (User ID),
  "payer_username": String (read-only),
  "splits": Array<ExpenseSplit>
}
```

### ExpenseSplit
```python
{
  "user_owed": Integer (User ID),
  "user_owed_username": String (read-only),
  "amount_owed": Decimal (string format)
}
```

---

## Error Handling

### Standard HTTP Status Codes

- **200 OK:** Request succeeded
- **201 Created:** Resource created successfully
- **204 No Content:** Resource deleted successfully
- **400 Bad Request:** Invalid request data or validation error
- **401 Unauthorized:** Authentication required or invalid token
- **403 Forbidden:** User doesn't have permission to access resource
- **404 Not Found:** Resource doesn't exist
- **500 Internal Server Error:** Server error

### Error Response Format

```json
{
  "field_name": ["Error message"],
  "another_field": ["Another error message"]
}
```

Or for non-field errors:

```json
{
  "non_field_errors": ["Error message"],
  "detail": "Additional error details"
}
```

---

## Mobile Integration Features

### Summary of Mobile-Friendly Enhancements

1. **Enhanced Login Response:** The `/api/login/` endpoint now returns user info alongside the token, reducing the need for an additional API call after authentication.

2. **Member IDs in Group Responses:** All bill group endpoints now include member IDs in the response, enabling direct expense creation without looking up user IDs separately.

3. **User Search Endpoint:** The new `/api/users/search/` endpoint allows mobile apps to discover users by username when adding members to groups.

4. **Comprehensive Validation:** All expense creation requests are validated at the serializer level, providing clear error messages before database operations.

### Recommended Mobile Flow

**Creating an Expense:**
1. User logs in → Receives token + user ID
2. Fetch group details → Get member IDs from response
3. Create expense → Use member IDs directly in splits array

**Adding Members to Group:**
1. Use `/api/users/search/?q=username` to find users
2. Collect user IDs from search results
3. Include IDs in `members` array when creating group

---

## Testing

Test scripts are available in the backend directory:
- `test_ledger.py` - Tests ledger functionality
- `test_mobile_integration.py` - Tests mobile integration features

Run tests:
```bash
cd /home/jthu/Documents/newhacks25/backend
python3 test_ledger.py
python3 test_mobile_integration.py
```

---

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False in production
GEMINI_API_KEY=your-gemini-api-key
```

### Running the Server

**Development:**
```bash
python manage.py runserver
```

**Production (with Gunicorn):**
```bash
./deploy.sh
```

---

## Additional Resources

- **Implementation Summary:** See `MOBILE_INTEGRATION_SUMMARY.md` for details on recent mobile integration changes
- **Deployment Script:** `deploy.sh` for production deployment with Gunicorn
- **Pydantic Schema:** `api/schema.py` defines the receipt parsing schema

---

**Questions or Issues?**

Contact the backend team or refer to the source code in `/home/jthu/Documents/newhacks25/backend/`.

**Last Updated:** October 25, 2025
