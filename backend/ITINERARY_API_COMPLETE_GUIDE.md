# Complete Itinerary API Guide

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Data Structure](#data-structure)
4. [Authentication](#authentication)
5. [Usage Examples](#usage-examples)
6. [Frontend Integration](#frontend-integration)
7. [Grounding Sources](#grounding-sources)
8. [Error Handling](#error-handling)

---

## Overview

The Itinerary API provides AI-powered travel planning using Google Gemini with Google Search and Maps integration. It generates complete day-by-day itineraries with activities, transportation, and pricing information.

### Key Features
- ✅ AI-generated itineraries using Gemini 2.5 Flash
- ✅ Google Maps integration for locations and places
- ✅ Google Search for up-to-date information
- ✅ Complete transportation planning between activities
- ✅ Source citations (grounding chunks) for credibility
- ✅ Price estimation in local currency
- ✅ Automatic flight detection (regional vs long-distance)

---

## API Endpoints

### 1. Generate Itinerary
**Create a new AI-generated itinerary**

```http
POST /api/itineraries/generate/
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "destination": "Downtown Toronto",
  "currentLocation": {
    "latitude": 43.6532,
    "longitude": -79.3832
  },
  "tripLength": "1 day",
  "budget": "200"
}
```

**Required Fields:**
- `destination` (string) - Where you want to go
- `currentLocation` (object) - Your starting location with lat/lng
- `tripLength` (string) - Duration (e.g., "1 day", "3 days")
- `budget` (string) - Budget in Canadian dollars

**Response:** (Status 201 Created)
```json
{
  "id": 1,
  "owner": 1,
  "owner_username": "john",
  "title": "Perfect Day in Downtown Toronto",
  "region": "Downtown Toronto",
  "created_at": "2025-10-26T10:30:00Z",
  "updated_at": "2025-10-26T10:30:00Z",
  "items": [],
  "ai_generated_data": {
    "itinerary": { /* See Data Structure section */ },
    "groundingChunks": [ /* See Grounding Sources section */ ]
  }
}
```

**Performance Note:** This endpoint takes 10-30 seconds due to AI generation. Show a loading indicator!

---

### 2. Get Single Itinerary
**Retrieve a specific itinerary by ID**

```http
GET /api/itineraries/{id}/
Authorization: Token YOUR_TOKEN
```

**Response:** (Status 200 OK)
```json
{
  "id": 1,
  "owner": 1,
  "owner_username": "john",
  "title": "Perfect Day in Downtown Toronto",
  "region": "Downtown Toronto",
  "created_at": "2025-10-26T10:30:00Z",
  "updated_at": "2025-10-26T10:30:00Z",
  "items": [],
  "ai_generated_data": { /* Complete AI data */ }
}
```

---

### 3. List All Itineraries
**Get all itineraries for the authenticated user**

```http
GET /api/itineraries/
Authorization: Token YOUR_TOKEN
```

**Response:** (Status 200 OK)
```json
[
  {
    "id": 1,
    "title": "Perfect Day in Downtown Toronto",
    "region": "Downtown Toronto",
    "created_at": "2025-10-26T10:30:00Z",
    "ai_generated_data": { /* Full data */ }
  },
  {
    "id": 2,
    "title": "Weekend in Vancouver",
    "region": "Vancouver",
    "created_at": "2025-10-25T15:00:00Z",
    "ai_generated_data": { /* Full data */ }
  }
]
```

---

### 4. Update Itinerary
**Update an existing itinerary**

```http
PUT /api/itineraries/{id}/
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Trip Title",
  "region": "Toronto"
}
```

---

### 5. Delete Itinerary
**Delete an itinerary**

```http
DELETE /api/itineraries/{id}/
Authorization: Token YOUR_TOKEN
```

**Response:** (Status 204 No Content)

---

## Data Structure

### Complete Itinerary Object

```json
{
  "id": 1,
  "owner": 1,
  "owner_username": "john",
  "title": "Perfect Day in Downtown Toronto",
  "region": "Downtown Toronto",
  "created_at": "2025-10-26T10:30:00Z",
  "updated_at": "2025-10-26T10:30:00Z",
  "items": [],
  "ai_generated_data": {
    "itinerary": {
      "tripTitle": "Perfect Day in Downtown Toronto",
      "summary": "Experience the best of Toronto in one action-packed day...",
      "flightInfo": null,
      "dailyPlan": [
        {
          "day": 1,
          "activities": [
            {
              "duration": 2.0,
              "description": "Visit the iconic CN Tower with breathtaking views...",
              "name": "CN Tower, 301 Front St W, Toronto",
              "coordinates": {
                "latitude": 43.6426,
                "longitude": -79.3871
              },
              "price": 40,
              "bookingLink": "https://www.cntower.ca/tickets"
            },
            {
              "type": "transport",
              "transportationType": "walk",
              "startPoint": "CN Tower, 301 Front St W",
              "endPoint": "Ripley's Aquarium, 288 Bremner Blvd",
              "startCoordinates": {
                "latitude": 43.6426,
                "longitude": -79.3871
              },
              "endCoordinates": {
                "latitude": 43.6424,
                "longitude": -79.3860
              },
              "duration": 0.08,
              "price": 0,
              "description": "5-minute walk along Bremner Boulevard"
            },
            {
              "duration": 2.5,
              "description": "Explore marine life at one of North America's best aquariums...",
              "name": "Ripley's Aquarium of Canada",
              "coordinates": {
                "latitude": 43.6424,
                "longitude": -79.3860
              },
              "price": 44,
              "bookingLink": "https://www.ripleyaquariums.com/canada"
            }
          ]
        }
      ]
    },
    "groundingChunks": [
      {
        "type": "maps",
        "place_id": "places/ChIJ...",
        "title": "CN Tower",
        "uri": "https://maps.google.com/?cid=..."
      },
      {
        "type": "search",
        "title": "Current time information in Toronto",
        "text": "The time in Toronto is 4:44 AM...",
        "uri": "https://www.google.com/search?q=..."
      }
    ]
  }
}
```

### Activity Types

**Regular Activity:**
```json
{
  "duration": 2.0,
  "description": "Activity description",
  "name": "Location name and address",
  "coordinates": {
    "latitude": 43.6426,
    "longitude": -79.3871
  },
  "price": 40,
  "bookingLink": "https://example.com"
}
```

**Transport Activity:**
```json
{
  "type": "transport",
  "transportationType": "walk",
  "startPoint": "Starting location",
  "endPoint": "Ending location",
  "startCoordinates": {
    "latitude": 43.6426,
    "longitude": -79.3871
  },
  "endCoordinates": {
    "latitude": 43.6424,
    "longitude": -79.3860
  },
  "duration": 0.25,
  "price": 0,
  "description": "Brief description"
}
```

**Transportation Types:**
- `walk` - Walking (free)
- `metro` - Subway/Metro
- `train` - Train
- `bus` - Bus
- `taxi` - Taxi/Rideshare
- `ferry` - Ferry boat
- `tram` - Streetcar/Tram
- `bicycle` - Bike/Bike share
- `car` - Private car/Rental

### Flight Information

For long-distance trips, `flightInfo` will contain:

```json
{
  "flightInfo": {
    "departure": {
      "airline": "Air Canada",
      "flightNumber": "AC123",
      "departureAirport": "YYZ",
      "arrivalAirport": "YVR",
      "departureTime": "2025-10-26T08:00:00Z",
      "arrivalTime": "2025-10-26T10:30:00Z",
      "duration": "5h 30m",
      "departureCoordinates": {
        "latitude": 43.6777,
        "longitude": -79.6248
      },
      "arrivalCoordinates": {
        "latitude": 49.1947,
        "longitude": -123.1815
      }
    },
    "return": { /* Same structure */ },
    "price": "~$500 CAD",
    "bookingLink": "https://www.google.com/flights/..."
  }
}
```

For regional trips (same city or nearby), `flightInfo` will be `null`.

---

## Grounding Sources

Grounding chunks provide sources and citations for the AI-generated content. There are three types:

### 1. Web Sources
```json
{
  "type": "web",
  "uri": "https://www.cntower.ca",
  "title": "CN Tower Official Website"
}
```

### 2. Google Maps Places
```json
{
  "type": "maps",
  "place_id": "places/ChIJBxZ2UMw0K4gR1LmKMBvveP0",
  "title": "Nathan Phillips Square",
  "uri": "https://maps.google.com/?cid=18264611188858599892"
}
```

### 3. Google Search Snippets
```json
{
  "type": "search",
  "text": "The time in Toronto is 4:44 AM. Timezone: America/Toronto.",
  "title": "Current time information in Toronto",
  "uri": "https://www.google.com/search?q=time+in+Toronto"
}
```

**Usage:** Display these as "Sources" or "References" at the bottom of your itinerary to show users where the information came from.

---

## Authentication

All endpoints require token authentication.

### Get Token
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user": {
    "id": 1,
    "username": "your_username"
  }
}
```

### Using the Token
Include in header for all requests:
```
Authorization: Token abc123def456...
```

---

## Usage Examples

### cURL Examples

**Generate Itinerary:**
```bash
curl -X POST http://localhost:8000/api/itineraries/generate/ \
  -H 'Authorization: Token YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "destination": "Downtown Toronto",
    "currentLocation": {"latitude": 43.6532, "longitude": -79.3832},
    "tripLength": "1 day",
    "budget": "200"
  }'
```

**Get Itinerary:**
```bash
curl -X GET http://localhost:8000/api/itineraries/1/ \
  -H 'Authorization: Token YOUR_TOKEN'
```

**List All Itineraries:**
```bash
curl -X GET http://localhost:8000/api/itineraries/ \
  -H 'Authorization: Token YOUR_TOKEN'
```

---

## Frontend Integration

### JavaScript/Fetch

```javascript
const API_BASE = 'http://localhost:8000';
const token = localStorage.getItem('authToken');

// Generate new itinerary
async function generateItinerary(destination, location, tripLength, budget) {
  const response = await fetch(`${API_BASE}/api/itineraries/generate/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      destination,
      currentLocation: location,
      tripLength,
      budget
    })
  });
  
  return await response.json();
}

// Get specific itinerary
async function getItinerary(id) {
  const response = await fetch(`${API_BASE}/api/itineraries/${id}/`, {
    headers: {
      'Authorization': `Token ${token}`
    }
  });
  
  return await response.json();
}

// Get all itineraries
async function getAllItineraries() {
  const response = await fetch(`${API_BASE}/api/itineraries/`, {
    headers: {
      'Authorization': `Token ${token}`
    }
  });
  
  return await response.json();
}

// Usage
const itinerary = await generateItinerary(
  "Downtown Toronto",
  { latitude: 43.6532, longitude: -79.3832 },
  "1 day",
  "200"
);

console.log(itinerary.ai_generated_data.itinerary.tripTitle);
```

### React Example

```jsx
import { useState, useEffect } from 'react';

function ItineraryDisplay({ itineraryId }) {
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchItinerary() {
      const token = localStorage.getItem('authToken');
      const response = await fetch(
        `http://localhost:8000/api/itineraries/${itineraryId}/`,
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      
      const data = await response.json();
      setItinerary(data);
      setLoading(false);
    }
    
    fetchItinerary();
  }, [itineraryId]);
  
  if (loading) return <div>Loading itinerary...</div>;
  if (!itinerary) return <div>Itinerary not found</div>;
  
  const ai = itinerary.ai_generated_data?.itinerary;
  
  return (
    <div className="itinerary">
      <h1>{ai.tripTitle}</h1>
      <p>{ai.summary}</p>
      
      {/* Daily Plan */}
      {ai.dailyPlan.map(day => (
        <div key={day.day} className="day">
          <h2>Day {day.day}</h2>
          
          {day.activities.map((activity, idx) => (
            <div key={idx} className="activity">
              {activity.type === 'transport' ? (
                <div className="transport">
                  <span className="icon">🚶</span>
                  <span>{activity.transportationType}</span>
                  <span>{activity.startPoint} → {activity.endPoint}</span>
                  <span>{activity.duration}h</span>
                  <span>${activity.price}</span>
                </div>
              ) : (
                <div className="location">
                  <h3>{activity.name}</h3>
                  <p>{activity.description}</p>
                  <div className="details">
                    <span>⏱️ {activity.duration}h</span>
                    <span>💰 ${activity.price}</span>
                    {activity.bookingLink && (
                      <a href={activity.bookingLink}>Book Now</a>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ))}
      
      {/* Sources */}
      <div className="sources">
        <h3>Sources</h3>
        {itinerary.ai_generated_data.groundingChunks.map((chunk, idx) => (
          <div key={idx} className="source">
            <span className="type">{chunk.type}</span>
            <a href={chunk.uri} target="_blank" rel="noopener noreferrer">
              {chunk.title}
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ItineraryDisplay;
```

### React Native Example

```jsx
import { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

function ItineraryScreen({ route }) {
  const { itineraryId } = route.params;
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchItinerary() {
      const token = await AsyncStorage.getItem('authToken');
      const response = await fetch(
        `http://localhost:8000/api/itineraries/${itineraryId}/`,
        {
          headers: { 'Authorization': `Token ${token}` }
        }
      );
      
      const data = await response.json();
      setItinerary(data);
      setLoading(false);
    }
    
    fetchItinerary();
  }, [itineraryId]);
  
  if (loading) {
    return <ActivityIndicator size="large" />;
  }
  
  const ai = itinerary.ai_generated_data?.itinerary;
  
  return (
    <ScrollView>
      <Text style={styles.title}>{ai.tripTitle}</Text>
      <Text style={styles.summary}>{ai.summary}</Text>
      
      {ai.dailyPlan.map(day => (
        <View key={day.day}>
          <Text style={styles.dayTitle}>Day {day.day}</Text>
          
          {day.activities.map((activity, idx) => (
            <View key={idx}>
              {activity.type === 'transport' ? (
                <View style={styles.transport}>
                  <Text>🚶 {activity.transportationType}</Text>
                  <Text>{activity.startPoint} → {activity.endPoint}</Text>
                </View>
              ) : (
                <View style={styles.activity}>
                  <Text style={styles.activityName}>{activity.name}</Text>
                  <Text>{activity.description}</Text>
                  <Text>⏱️ {activity.duration}h | 💰 ${activity.price}</Text>
                </View>
              )}
            </View>
          ))}
        </View>
      ))}
    </ScrollView>
  );
}
```

---

## Error Handling

### Common Errors

**400 Bad Request - Missing Destination**
```json
{
  "error": "Missing required field: 'destination'"
}
```

**401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**404 Not Found**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error - AI Generation Failed**
```json
{
  "error": "Failed to generate itinerary: <error details>"
}
```

### Handling Errors in Frontend

```javascript
async function generateItinerary(data) {
  try {
    const response = await fetch('/api/itineraries/generate/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.detail || 'Failed to generate itinerary');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error generating itinerary:', error);
    // Show error to user
    alert(`Error: ${error.message}`);
    return null;
  }
}
```

---

## Best Practices

### 1. Show Loading States
AI generation takes 10-30 seconds. Always show a loading indicator:
```jsx
{loading && (
  <div className="loading">
    <Spinner />
    <p>Generating your perfect itinerary...</p>
    <p>This may take up to 30 seconds</p>
  </div>
)}
```

### 2. Cache Itineraries
Store fetched itineraries in state/context to avoid repeated API calls:
```javascript
const [itineraries, setItineraries] = useState({});

async function getItinerary(id) {
  // Check cache first
  if (itineraries[id]) {
    return itineraries[id];
  }
  
  // Fetch from API
  const data = await fetch(`/api/itineraries/${id}/`);
  const itinerary = await data.json();
  
  // Cache it
  setItineraries(prev => ({ ...prev, [id]: itinerary }));
  
  return itinerary;
}
```

### 3. Handle Null Flight Info
Not all trips have flights (regional trips):
```javascript
{ai.flightInfo ? (
  <FlightDetails flight={ai.flightInfo} />
) : (
  <p>This is a regional trip - no flights needed!</p>
)}
```

### 4. Display Grounding Sources
Show credibility by displaying sources:
```jsx
<section className="sources">
  <h3>📚 Information Sources</h3>
  {groundingChunks.map(chunk => (
    <a key={chunk.uri} href={chunk.uri} target="_blank">
      {chunk.type === 'maps' && '📍'}
      {chunk.type === 'web' && '🌐'}
      {chunk.type === 'search' && '🔍'}
      {chunk.title}
    </a>
  ))}
</section>
```

### 5. Validate User Input
Before sending to API:
```javascript
function validateItineraryRequest(data) {
  if (!data.destination) {
    throw new Error('Destination is required');
  }
  
  if (!data.currentLocation?.latitude || !data.currentLocation?.longitude) {
    throw new Error('Current location is required');
  }
  
  if (!data.tripLength) {
    throw new Error('Trip length is required');
  }
  
  if (!data.budget) {
    throw new Error('Budget is required');
  }
  
  return true;
}
```

---

## Performance Notes

- **Generation Time:** 10-30 seconds (Gemini API call)
- **Retrieval Time:** <100ms (database query)
- **Storage:** Complete JSON stored in database
- **Caching:** Consider implementing Redis cache for frequently accessed itineraries

---

## Support

For issues or questions:
- Check error messages in API responses
- Verify authentication token is valid
- Ensure all required fields are provided
- Check Django server logs for detailed error traces

---

**Last Updated:** October 26, 2025  
**API Version:** 1.0  
**Gemini Model:** gemini-2.5-flash
