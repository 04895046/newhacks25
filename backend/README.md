# 🚀 Hackathon Backend - AI Itinerary Generator API

Django REST Framework backend for an AI-powered itinerary generation app.

## 📋 Features

- ✅ Token-based authentication (no cookies, works with separate frontend)
- ✅ User registration and login
- ✅ CRUD operations for itineraries
- ✅ CRUD operations for itinerary items
- ✅ **Smart append & insert methods** (automatic order management)
- ✅ **Move & delete with auto-reordering** (no gaps in order)
- ✅ ML-powered itinerary generation endpoint (ready for your model)
- ✅ CORS configured for cross-origin requests
- ✅ Order-based itinerary items (replaces linked list with efficient querying)

> 💡 **NEW!** Easy-to-use methods for appending and inserting items. See `APPEND_INSERT_SUMMARY.md` for details!

## 🛠️ Quick Setup

### 1. Install Dependencies

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

---

## 🔐 Authentication Endpoints

### 1. Register a New User

**Endpoint:** `POST /api/register/`

**Body:**
```json
{
    "username": "john_doe",
    "password": "secure_password123"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "username": "john_doe"
}
```

---

### 2. Login (Get Auth Token)

**Endpoint:** `POST /api/login/`

**Body:**
```json
{
    "username": "john_doe",
    "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
    "token": "a73hdbf92b718392bde981abc123..."
}
```

⚠️ **IMPORTANT:** Save this token! You'll need it for all other requests.

---

## 🔑 How to Authenticate Requests

For all endpoints below (except register/login), include the token in your request headers:

```
Authorization: Token a73hdbf92b718392bde981abc123...
```

**Example (using fetch):**
```javascript
fetch('http://localhost:8000/api/itineraries/', {
    headers: {
        'Authorization': 'Token a73hdbf92b718392bde981abc123...',
        'Content-Type': 'application/json'
    }
})
```

---

## 🗺️ Itinerary Endpoints

### 3. Generate New Itinerary (AI-Powered)

**Endpoint:** `POST /api/itineraries/generate/`

**Headers:** `Authorization: Token <your_token>`

**Body:**
```json
{
    "region": "Toronto",
    "needs": "3 day trip, love museums and good food"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "owner": 1,
    "owner_username": "john_doe",
    "title": "AI Trip to Toronto",
    "region": "Toronto",
    "created_at": "2025-10-25T12:00:00Z",
    "updated_at": "2025-10-25T12:00:00Z",
    "items": [
        {
            "id": 1,
            "description": "AI Generated: Explore Toronto downtown",
            "location_name": "Toronto City Center",
            "start_time": null,
            "end_time": null,
            "order": 0
        },
        {
            "id": 2,
            "description": "AI Generated: Visit a famous landmark in Toronto",
            "location_name": "Famous Landmark",
            "start_time": null,
            "end_time": null,
            "order": 1
        }
    ]
}
```

🤖 **Note:** The dummy data above will be replaced when you integrate your ML model in `api/views.py` → `ItineraryViewSet.generate()` method.

---

### 4. List All User's Itineraries

**Endpoint:** `GET /api/itineraries/`

**Headers:** `Authorization: Token <your_token>`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "AI Trip to Toronto",
        "region": "Toronto",
        "owner_username": "john_doe",
        "created_at": "2025-10-25T12:00:00Z",
        "item_count": 3
    },
    {
        "id": 2,
        "title": "My Custom Trip",
        "region": "Paris",
        "owner_username": "john_doe",
        "created_at": "2025-10-24T10:00:00Z",
        "item_count": 5
    }
]
```

---

### 5. Get Single Itinerary (with all items)

**Endpoint:** `GET /api/itineraries/<id>/`

**Headers:** `Authorization: Token <your_token>`

**Example:** `GET /api/itineraries/1/`

**Response (200 OK):**
```json
{
    "id": 1,
    "owner": 1,
    "owner_username": "john_doe",
    "title": "AI Trip to Toronto",
    "region": "Toronto",
    "created_at": "2025-10-25T12:00:00Z",
    "updated_at": "2025-10-25T12:00:00Z",
    "items": [
        {
            "id": 1,
            "description": "Visit CN Tower",
            "location_name": "CN Tower",
            "start_time": null,
            "end_time": null,
            "order": 0
        },
        {
            "id": 2,
            "description": "Explore ROM",
            "location_name": "Royal Ontario Museum",
            "start_time": null,
            "end_time": null,
            "order": 1
        }
    ]
}
```

---

### 6. Create Itinerary Manually

**Endpoint:** `POST /api/itineraries/`

**Headers:** `Authorization: Token <your_token>`

**Body:**
```json
{
    "title": "My Custom Trip",
    "region": "Paris"
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "owner": 1,
    "owner_username": "john_doe",
    "title": "My Custom Trip",
    "region": "Paris",
    "created_at": "2025-10-25T12:00:00Z",
    "updated_at": "2025-10-25T12:00:00Z",
    "items": []
}
```

---

### 7. Update Itinerary

**Endpoint:** `PATCH /api/itineraries/<id>/`

**Headers:** `Authorization: Token <your_token>`

**Example:** `PATCH /api/itineraries/1/`

**Body:** (only send fields you want to change)
```json
{
    "title": "Updated Trip Name"
}
```

**Response (200 OK):** Returns the updated itinerary

---

### 8. Delete Itinerary

**Endpoint:** `DELETE /api/itineraries/<id>/`

**Headers:** `Authorization: Token <your_token>`

**Example:** `DELETE /api/itineraries/1/`

**Response (204 No Content)**

---

## 📍 Itinerary Item Endpoints

### 9. Add New Item to Itinerary

**Endpoint:** `POST /api/itinerary-items/`

**Headers:** `Authorization: Token <your_token>`

**Body:**
```json
{
    "itinerary": 1,
    "description": "Have dinner at a local restaurant",
    "location_name": "Le Bistro",
    "start_time": "2025-10-26T19:00:00Z",
    "end_time": "2025-10-26T21:00:00Z",
    "order": 3
}
```

**Response (201 Created):**
```json
{
    "id": 5,
    "itinerary": 1,
    "description": "Have dinner at a local restaurant",
    "location_name": "Le Bistro",
    "start_time": "2025-10-26T19:00:00Z",
    "end_time": "2025-10-26T21:00:00Z",
    "order": 3
}
```

💡 **Tip:** To add an item to the end of an itinerary, use the next order number (e.g., if there are 3 items with order 0, 1, 2, use order 3).

---

### 10. Update Item (Edit or Reorder)

**Endpoint:** `PATCH /api/itinerary-items/<id>/`

**Headers:** `Authorization: Token <your_token>`

**Example:** `PATCH /api/itinerary-items/5/`

**Body:** (only send fields you want to change)
```json
{
    "description": "Updated description",
    "order": 0
}
```

**Response (200 OK):** Returns the updated item

🔄 **Reordering:** To move an item to a different position, just change its `order` value. You may need to update other items' order values to avoid conflicts (due to unique constraint).

---

### 11. Delete Item

**Endpoint:** `DELETE /api/itinerary-items/<id>/`

**Headers:** `Authorization: Token <your_token>`

**Example:** `DELETE /api/itinerary-items/5/`

**Response (204 No Content)**

---

### 12. List All Items (User Owns)

**Endpoint:** `GET /api/itinerary-items/`

**Headers:** `Authorization: Token <your_token>`

**Response (200 OK):** Returns all items from all the user's itineraries

---

## 🧠 Integrating Your ML Model

To connect your ML/AI model to the generate endpoint:

1. Open `backend/api/views.py`
2. Find the `ItineraryViewSet.generate()` method
3. Replace the dummy data section with your ML call:

```python
# Inside api/views.py, ItineraryViewSet.generate() method

# TODO: INTEGRATE YOUR ML MODEL HERE
from your_ml_script import call_ml_agent

generated_data = call_ml_agent(region, needs)

# Expected format:
# generated_data = [
#     {"desc": "Visit CN Tower", "loc": "CN Tower", "order": 0},
#     {"desc": "Visit ROM", "loc": "Royal Ontario Museum", "order": 1},
# ]
```

---

## 🗄️ Database Model Explanation

### Why We Don't Use a Linked List

Your original idea was to use a linked list structure:
```
Item(id: 1, data: "Go to CN Tower", next_item_id: 3)
Item(id: 2, data: "Get breakfast", next_item_id: 1)
```

**Problem:** This requires **N separate database queries** to get the full itinerary (N+1 query problem). Very slow!

**Solution:** We use an `order` field instead:
```
Item(id: 1, data: "Go to CN Tower", itinerary_id: 1, order: 1)
Item(id: 2, data: "Get breakfast", itinerary_id: 1, order: 0)
```

**Benefits:**
- ✅ Get entire itinerary in 1 query: `SELECT * FROM ItineraryItem WHERE itinerary_id = 1 ORDER BY order;`
- ✅ Reordering is trivial (just update the `order` field)
- ✅ Database automatically sorts items

---

## 🧪 Testing the API

### Option 1: Django Admin Panel

1. Visit `http://localhost:8000/admin/`
2. Login with your superuser credentials
3. View/edit users, itineraries, and items

### Option 2: cURL (Command Line)

```bash
# Register
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# Generate Itinerary (replace TOKEN with your actual token)
curl -X POST http://localhost:8000/api/itineraries/generate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token <YOUR_TOKEN>" \
  -d '{"region": "Toronto", "needs": "3 days, museums"}'
```

### Option 3: Django REST Framework Web Interface

Visit any endpoint in your browser while logged in:
- `http://localhost:8000/api/itineraries/`
- `http://localhost:8000/api/itinerary-items/`

DRF provides a beautiful browsable API!

---

## 🚀 Deployment Tips

### For Hackathon Demo (Quick & Dirty)

Keep using SQLite and `python manage.py runserver`. Just make sure CORS is enabled (it already is).

### For Production (Post-Hackathon)

1. **Change `SECRET_KEY`** in `settings.py`
2. **Set `DEBUG = False`**
3. **Update `ALLOWED_HOSTS`** with your domain
4. **Use PostgreSQL** instead of SQLite
5. **Restrict CORS** to your frontend domain:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "https://your-frontend.com",
   ]
   ```
6. **Use Gunicorn + Nginx** instead of `runserver`
7. **Deploy to Heroku/DigitalOcean/AWS**

---

## 📁 Project Structure

```
backend/
├── .venv/                  # Virtual environment
├── manage.py               # Django management script
├── my_backend/             # Main project folder
│   ├── __init__.py
│   ├── settings.py         # ✅ Configured with DRF, CORS, Token Auth
│   ├── urls.py             # ✅ Routes /api/ to api.urls
│   └── wsgi.py
├── api/                    # Your API app
│   ├── __init__.py
│   ├── models.py           # ✅ Itinerary & ItineraryItem models
│   ├── serializers.py      # ✅ JSON serializers
│   ├── views.py            # ✅ API endpoints (ViewSets)
│   ├── urls.py             # ✅ API URL routing
│   ├── admin.py
│   ├── apps.py
│   └── tests.py
├── db.sqlite3              # Database (created after migrations)
├── requirements.txt        # ✅ Dependencies
└── README.md               # ✅ This file
```

---

## 🐛 Troubleshooting

### CORS Error: "No 'Access-Control-Allow-Origin' header"

✅ Already fixed! `CORS_ORIGIN_ALLOW_ALL = True` is set in `settings.py`.

### "Invalid token" error

Make sure you're sending the token in the correct format:
```
Authorization: Token abc123...
```
(Not `Bearer abc123...`)

### Can't login with admin panel

Run `python manage.py createsuperuser` first.

### Database errors

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🎯 Next Steps for Your Hackathon

1. ✅ **Backend is done!** (You're here)
2. 🔨 Build your frontend (React/Vue/etc.)
3. 🤖 Integrate your ML model in `api/views.py`
4. 🎨 Design the UI/UX
5. 🚀 Deploy and demo!

---

## 📞 API Quick Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Register new user | ❌ |
| POST | `/api/login/` | Get auth token | ❌ |
| POST | `/api/itineraries/generate/` | AI-generate itinerary | ✅ |
| GET | `/api/itineraries/` | List all itineraries | ✅ |
| GET | `/api/itineraries/<id>/` | Get single itinerary | ✅ |
| POST | `/api/itineraries/` | Create itinerary | ✅ |
| PATCH | `/api/itineraries/<id>/` | Update itinerary | ✅ |
| DELETE | `/api/itineraries/<id>/` | Delete itinerary | ✅ |
| GET | `/api/itinerary-items/` | List all items | ✅ |
| POST | `/api/itinerary-items/` | Add item | ✅ |
| PATCH | `/api/itinerary-items/<id>/` | Update/reorder item | ✅ |
| DELETE | `/api/itinerary-items/<id>/` | Delete item | ✅ |

---

## 🏆 Good Luck with Your Hackathon!

You now have a production-ready REST API backend. Focus your remaining time on the frontend and ML integration!

Questions? Check Django REST Framework docs: https://www.django-rest-framework.org/
