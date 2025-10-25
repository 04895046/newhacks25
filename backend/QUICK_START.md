# 🚀 QUICK REFERENCE CARD

## Start the Server
```bash
./start.sh
# OR
python manage.py runserver
```

## Test the API
```bash
./test_api.sh
```

## Create Admin User
```bash
python manage.py createsuperuser
```

## API Endpoints Cheatsheet

### Auth (No token required)
```bash
POST /api/register/     # Create account
POST /api/login/        # Get token
```

### Itineraries (Token required)
```bash
GET    /api/itineraries/              # List all
GET    /api/itineraries/<id>/         # Get one
POST   /api/itineraries/              # Create
PATCH  /api/itineraries/<id>/         # Update
DELETE /api/itineraries/<id>/         # Delete
POST   /api/itineraries/generate/     # AI Generate 🤖
```

### Items (Token required)
```bash
GET    /api/itinerary-items/          # List all
POST   /api/itinerary-items/          # Create
PATCH  /api/itinerary-items/<id>/     # Update/Reorder
DELETE /api/itinerary-items/<id>/     # Delete
```

## Example Frontend Code

### JavaScript (Fetch API)
```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        username: 'user', 
        password: 'pass' 
    })
});
const { token } = await loginResponse.json();

// 2. Save token
localStorage.setItem('token', token);

// 3. Use token for authenticated requests
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
};

// 4. Generate itinerary
const response = await fetch('http://localhost:8000/api/itineraries/generate/', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
        region: 'Toronto',
        needs: '3 days, museums'
    })
});
const itinerary = await response.json();
```

## ML Integration

Edit `api/views.py` → `ItineraryViewSet.generate()`:

```python
# Replace dummy data with:
from .ml_integration import generate_itinerary_with_ml
generated_data = generate_itinerary_with_ml(region, needs)
```

Then implement your ML logic in `api/ml_integration.py`.

## Troubleshooting

### CORS errors?
✅ Already fixed! `CORS_ORIGIN_ALLOW_ALL = True`

### "Invalid token"?
Use: `Authorization: Token abc123...` (not Bearer)

### Database errors?
```bash
python manage.py makemigrations
python manage.py migrate
```

## File Structure
```
backend/
├── api/
│   ├── models.py          # Database models
│   ├── serializers.py     # JSON converters
│   ├── views.py           # API endpoints ⭐
│   ├── urls.py            # URL routing
│   └── ml_integration.py  # Your ML code goes here 🤖
├── my_backend/
│   ├── settings.py        # Configuration
│   └── urls.py            # Main routing
├── manage.py
├── db.sqlite3
├── README.md              # Full documentation
└── start.sh               # Quick start
```

## Next Steps
1. ✅ Backend is ready!
2. 🎨 Build your frontend
3. 🤖 Add ML model to `api/ml_integration.py`
4. 🚀 Demo time!
