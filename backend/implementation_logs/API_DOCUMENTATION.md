# API Documentation - Mobile Integration Updates

## 🚀 **Quick Reference**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/register/` | Register new user |
| POST | `/api/login/` | Get auth token **+ user info** 🆕 |
| GET | `/api/users/search/?q=<query>` | **Search users by username** 🆕 |
| POST | `/api/itineraries/generate/` | AI-generate itinerary 🤖 |
| GET | `/api/itineraries/` | List all itineraries |
| GET | `/api/itineraries/<id>/` | Get single itinerary |
| POST | `/api/itineraries/` | Create itinerary |
| PATCH | `/api/itineraries/<id>/` | Update itinerary |
| DELETE | `/api/itineraries/<id>/` | Delete itinerary |
| GET | `/api/groups/` | List all groups |
| GET | `/api/groups/<id>/` | Get single group **with member IDs** 🆕 |
| POST | `/api/groups/` | Create group **with member IDs** 🆕 |
| PATCH | `/api/groups/<id>/` | Update group |
| DELETE | `/api/groups/<id>/` | Delete group |
| GET | `/api/groups/<id>/balances/` | Get balances for group |
| GET | `/api/expenses/` | List all expenses |
| POST | `/api/expenses/` | Create expense |
| PATCH | `/api/expenses/<id>/` | Update expense |
| DELETE | `/api/expenses/<id>/` | Delete expense |

---

## 🔐 **Authentication**

### **1. Register User**

`POST /api/register/`

```json
{
    "username": "testuser",
    "password": "password123"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "username": "testuser"
}
```

### **2. Login (Get Token + User Info)** 🆕

`POST /api/login/`

```json
{
    "username": "testuser",
    "password": "password123"
}
```

**Response (200 OK):**
```json
{
    "token": "a73hdbf92b718392bde981...",
    "user": {
        "id": 1,
        "username": "testuser"
    }
}
```

> **Note:** Include this token in all future requests: `Authorization: Token <your_token>`

> **🆕 Mobile Integration Change:** Login now returns user info (id + username) in addition to the token. This allows the mobile app to immediately know the logged-in user's ID without an additional API call.

---

## 👥 **User Management** 🆕

### **Search Users**

`GET /api/users/search/?q=<search_query>`

Search for users by username (case-insensitive, partial match).

**Example:** `GET /api/users/search/?q=alice`

**Response (200 OK):**
```json
[
    {
        "id": 2,
        "username": "alice"
    },
    {
        "id": 5,
        "username": "alice_smith"
    }
]
```

**Notes:**
- Requires authentication
- Returns max 20 results
- Excludes the requesting user from results
- Use this to find user IDs when creating groups

---

## 💰 **Bill Splitting / Groups**

### **List Groups**

`GET /api/groups/`

Returns all groups where the current user is a member.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Trip to NYC",
        "members": [
            {
                "id": 1,
                "username": "alice"
            },
            {
                "id": 2,
                "username": "bob"
            }
        ],
        "created_at": "2025-10-25T12:00:00Z"
    }
]
```

> **🆕 Mobile Integration Change:** The `members` field now returns an array of objects with `id` and `username` instead of just usernames. This allows the mobile app to use member IDs when creating expenses.

### **Get Single Group**

`GET /api/groups/<id>/`

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Trip to NYC",
    "members": [
        {
            "id": 1,
            "username": "alice"
        },
        {
            "id": 2,
            "username": "bob"
        },
        {
            "id": 3,
            "username": "charlie"
        }
    ],
    "created_at": "2025-10-25T12:00:00Z",
    "expenses": [
        {
            "id": 1,
            "group": 1,
            "description": "Dinner",
            "total_amount": "90.00",
            "split_type": "E",
            "receipt_image": null,
            "item_data_json": null
        }
    ]
}
```

> **🆕 Mobile Integration Change:** Members are now returned with both `id` and `username`.

### **Create Group**

`POST /api/groups/`

```json
{
    "name": "Weekend Trip",
    "members": [2, 3]
}
```

**Request Body:**
- `name` (required): Group name
- `members` (optional): Array of user IDs to add as members

**Response (201 Created):**
```json
{
    "id": 2,
    "name": "Weekend Trip",
    "members": [
        {
            "id": 1,
            "username": "alice"
        },
        {
            "id": 2,
            "username": "bob"
        },
        {
            "id": 3,
            "username": "charlie"
        }
    ],
    "created_at": "2025-10-25T14:30:00Z"
}
```

**Notes:**
- The creator is automatically added as a member
- Use the `/api/users/search/` endpoint to find user IDs
- Invalid user IDs are silently ignored

> **🆕 Mobile Integration Change:** You can now pass an array of user IDs in the `members` field. The response includes full member objects with IDs and usernames.

### **Get Group Balances**

`GET /api/groups/<id>/balances/`

**Response (200 OK):**
```json
[
    {
        "username": "alice",
        "balance": "60.00"
    },
    {
        "username": "bob",
        "balance": "-10.00"
    },
    {
        "username": "charlie",
        "balance": "-50.00"
    }
]
```

**Notes:**
- Positive balance: person is owed money
- Negative balance: person owes money
- Balances always sum to zero

---

## 💸 **Expenses**

### **Create Expense**

`POST /api/expenses/`

```json
{
    "group": 1,
    "payer_id": 1,
    "description": "Dinner at restaurant",
    "total_amount": "90.00",
    "split_type": "E",
    "splits": [
        {
            "user_owed_id": 1,
            "amount_owed": "30.00"
        },
        {
            "user_owed_id": 2,
            "amount_owed": "30.00"
        },
        {
            "user_owed_id": 3,
            "amount_owed": "30.00"
        }
    ]
}
```

**Request Body:**
- `group` (required): Group ID
- `payer_id` (required): User ID of the person who paid
- `description` (required): Description of the expense
- `total_amount` (required): Total amount paid
- `split_type` (required): "E" (Even) or "M" (Manual)
- `splits` (required): Array of split objects
  - `user_owed_id`: User ID who owes this amount
  - `amount_owed`: Amount this user owes

**Validation:**
- ✅ Payer must exist and be a group member
- ✅ All users in splits must exist and be group members
- ✅ Sum of splits must equal total_amount

**Response (201 Created):**
```json
{
    "id": 1,
    "group": 1,
    "description": "Dinner at restaurant",
    "total_amount": "90.00",
    "split_type": "E",
    "receipt_image": null,
    "item_data_json": null
}
```

---

## 🗺️ **Itinerary Endpoints**

### **Generate Itinerary (AI)**

`POST /api/itineraries/generate/`

```json
{
    "region": "Toronto",
    "needs": "3 day trip, love museums"
}
```

### **List Itineraries**

`GET /api/itineraries/`

### **Get Single Itinerary**

`GET /api/itineraries/<id>/`

### **Create Itinerary**

`POST /api/itineraries/`

```json
{
    "title": "My Trip to Paris",
    "region": "Paris"
}
```

### **Update Itinerary**

`PATCH /api/itineraries/<id>/`

```json
{
    "title": "My Awesome Trip to Paris"
}
```

### **Delete Itinerary**

`DELETE /api/itineraries/<id>/`

---

## 📝 **Summary of Mobile Integration Changes**

### 1. Login Response Enhanced
**Before:**
```json
{
    "token": "..."
}
```

**After:** 🆕
```json
{
    "token": "...",
    "user": {
        "id": 1,
        "username": "alice"
    }
}
```

### 2. Group Members Include IDs
**Before:**
```json
{
    "members": ["alice", "bob", "charlie"]
}
```

**After:** 🆕
```json
{
    "members": [
        {"id": 1, "username": "alice"},
        {"id": 2, "username": "bob"},
        {"id": 3, "username": "charlie"}
    ]
}
```

### 3. User Search Endpoint Added
**New Endpoint:** 🆕
```
GET /api/users/search/?q=alice
```

Returns users matching the search query, allowing the mobile app to find user IDs for adding members to groups.

---

## 🔧 **Error Responses**

### 400 Bad Request
```json
{
    "non_field_errors": [
        "The sum of splits ($90.00) does not match the total_amount ($100.00)."
    ]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

---

## 📱 **Mobile App Integration Guide**

### Initial Setup
1. Register user: `POST /api/register/`
2. Login: `POST /api/login/` → Save token AND user info
3. Include token in all requests: `Authorization: Token <token>`

### Creating a Group
1. Search for users: `GET /api/users/search/?q=<username>`
2. Get user IDs from search results
3. Create group: `POST /api/groups/` with `members: [id1, id2, ...]`

### Adding an Expense
1. Get group details: `GET /api/groups/<id>/` to see all members
2. Use member IDs for `payer_id` and `user_owed_id` fields
3. Create expense: `POST /api/expenses/`

### Checking Balances
1. Get balances: `GET /api/groups/<id>/balances/`
2. Display who owes whom

---

**Last Updated:** October 25, 2025  
**API Version:** 1.1 (Mobile Integration Update)
