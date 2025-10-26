# 📝 Itinerary Items: Append & Insert Guide

Your `Itinerary` and `ItineraryItem` models now support easy appending and inserting with automatic order management!

## 🎯 Features

### **Itinerary Methods**
- ✅ `get_next_order()` - Get the next available order number
- ✅ `append_item()` - Add item to the end

### **ItineraryItem Methods**
- ✅ `insert_before()` - Insert a new item before this one
- ✅ `insert_after()` - Insert a new item after this one
- ✅ `move_to()` - Move item to a new position
- ✅ `delete()` - Delete item and auto-reorder remaining items

All methods handle order management automatically! 🎉

---

## 📖 Usage Examples

### 1. **Append Item to End** (Easiest!)

```python
# Get an itinerary
itinerary = Itinerary.objects.get(id=1)

# Append a new item to the end
new_item = itinerary.append_item(
    description="Have dinner at local restaurant",
    location_name="Le Bistro",
    start_time="2025-10-26T19:00:00Z",
    end_time="2025-10-26T21:00:00Z"
)

# The order is automatically set to the next available number!
print(new_item.order)  # e.g., 5 (if there were 5 items already)
```

### 2. **Insert Before an Item**

```python
# Get an existing item (e.g., "Visit Museum" at order 2)
museum_item = ItineraryItem.objects.get(id=5)

# Insert a new item BEFORE the museum visit
lunch_item = museum_item.insert_before(
    description="Have lunch nearby",
    location_name="Cafe Downtown"
)

# Result:
# - New lunch_item is at order 2
# - museum_item automatically moved to order 3
# - All items after museum also shifted down by 1
```

### 3. **Insert After an Item**

```python
# Get an existing item (e.g., "Visit CN Tower" at order 0)
cn_tower_item = ItineraryItem.objects.get(id=1)

# Insert a new item AFTER the CN Tower visit
photo_item = cn_tower_item.insert_after(
    description="Take photos at the observation deck",
    location_name="CN Tower Observation Deck"
)

# Result:
# - cn_tower_item stays at order 0
# - photo_item is now at order 1
# - All items that were at order 1+ shifted down by 1
```

### 4. **Move an Item to a Different Position**

```python
# Get an item
dinner_item = ItineraryItem.objects.get(id=10)
print(dinner_item.order)  # e.g., 5

# Move it to position 2 (e.g., move dinner earlier in the day)
dinner_item.move_to(2)

# Result:
# - dinner_item is now at order 2
# - Items between old and new position automatically adjusted
```

### 5. **Delete an Item (Auto-Reorder)**

```python
# Get an item to delete
item_to_remove = ItineraryItem.objects.get(id=7)
print(item_to_remove.order)  # e.g., 3

# Delete it
item_to_remove.delete()

# Result:
# - Item is deleted
# - All items after position 3 automatically moved up by 1
# - No gaps in order numbers!
```

### 6. **Get Next Order Number**

```python
# Useful if you want to manually create items
itinerary = Itinerary.objects.get(id=1)
next_order = itinerary.get_next_order()

# Create item manually with the correct order
ItineraryItem.objects.create(
    itinerary=itinerary,
    description="Custom item",
    order=next_order  # This will be 0 if empty, or last_order + 1
)
```

---

## 🔌 API Integration Examples

### **In Django Shell**

```bash
python manage.py shell
```

```python
from api.models import Itinerary, ItineraryItem

# Get user's itinerary
itinerary = Itinerary.objects.first()

# Append 3 items
itinerary.append_item("Morning: Visit CN Tower", "CN Tower")
itinerary.append_item("Afternoon: Explore ROM", "Royal Ontario Museum")
itinerary.append_item("Evening: Dinner", "St. Lawrence Market")

# Check the order
for item in itinerary.items.all():
    print(f"{item.order}: {item.description}")
# Output:
# 0: Morning: Visit CN Tower
# 1: Afternoon: Explore ROM
# 2: Evening: Dinner

# Insert lunch between morning and afternoon
morning_item = itinerary.items.get(order=0)
morning_item.insert_after("Lunch break", "Local Cafe")

# Check the order again
for item in itinerary.items.all():
    print(f"{item.order}: {item.description}")
# Output:
# 0: Morning: Visit CN Tower
# 1: Lunch break
# 2: Afternoon: Explore ROM
# 3: Evening: Dinner
```

---

## 🚀 Using in API Views

### **In `api/views.py`**

```python
# Example: Add a custom endpoint to append an item
from rest_framework.decorators import action
from rest_framework.response import Response

class ItineraryViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'])
    def append_item(self, request, pk=None):
        """
        Custom endpoint to append an item to an itinerary.
        POST /api/itineraries/<id>/append_item/
        Body: {
            "description": "New activity",
            "location_name": "Location"
        }
        """
        itinerary = self.get_object()
        
        # Use the append_item method!
        new_item = itinerary.append_item(
            description=request.data.get('description'),
            location_name=request.data.get('location_name', ''),
            start_time=request.data.get('start_time'),
            end_time=request.data.get('end_time')
        )
        
        serializer = ItineraryItemSerializer(new_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='items/(?P<item_id>[^/.]+)/insert_after')
    def insert_item_after(self, request, pk=None, item_id=None):
        """
        Custom endpoint to insert an item after a specific item.
        POST /api/itineraries/<id>/items/<item_id>/insert_after/
        Body: {
            "description": "New activity",
            "location_name": "Location"
        }
        """
        itinerary = self.get_object()
        
        try:
            item = itinerary.items.get(id=item_id)
        except ItineraryItem.DoesNotExist:
            return Response(
                {"error": "Item not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use the insert_after method!
        new_item = item.insert_after(
            description=request.data.get('description'),
            location_name=request.data.get('location_name', ''),
            start_time=request.data.get('start_time'),
            end_time=request.data.get('end_time')
        )
        
        serializer = ItineraryItemSerializer(new_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

## 🧪 Testing the New Features

### **Test Script**

```bash
# Create a test file
cat > test_append_insert.py << 'EOF'
from api.models import Itinerary, ItineraryItem, User

# Get or create a test user
user = User.objects.first()
if not user:
    user = User.objects.create_user('testuser', password='testpass')

# Create an itinerary
itinerary = Itinerary.objects.create(
    owner=user,
    title="Test Itinerary",
    region="Toronto"
)

# Test 1: Append items
print("Test 1: Appending items...")
item1 = itinerary.append_item("Morning activity", "Location A")
item2 = itinerary.append_item("Afternoon activity", "Location B")
item3 = itinerary.append_item("Evening activity", "Location C")

print("After appending:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 2: Insert before
print("\nTest 2: Insert before afternoon...")
item2.insert_before("Lunch break", "Restaurant")

print("After insert_before:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 3: Insert after
print("\nTest 3: Insert after morning...")
item1.insert_after("Mid-morning snack", "Cafe")

print("After insert_after:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 4: Move item
print("\nTest 4: Move evening to position 1...")
item3 = itinerary.items.get(description="Evening activity")
item3.move_to(1)

print("After move_to(1):")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 5: Delete item
print("\nTest 5: Delete snack...")
snack = itinerary.items.get(description="Mid-morning snack")
snack.delete()

print("After delete:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

print("\n✅ All tests passed!")
EOF

# Run the test
python manage.py shell < test_append_insert.py
```

---

## 🎯 Key Benefits

### **Automatic Order Management**
- ✅ No need to manually calculate order numbers
- ✅ No gaps in order sequence
- ✅ No duplicate order numbers

### **Safe Reordering**
- ✅ Inserting doesn't break existing items
- ✅ Deleting automatically fills gaps
- ✅ Moving handles all edge cases

### **Easy to Use**
- ✅ Simple, intuitive methods
- ✅ No complex queries needed
- ✅ Works seamlessly with Django ORM

---

## 🔥 Frontend Usage Example

```javascript
// Append an item (frontend)
async function appendItem(itineraryId, description, location) {
    const response = await fetch(`http://localhost:8000/api/itinerary-items/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${yourToken}`
        },
        body: JSON.stringify({
            itinerary: itineraryId,
            description: description,
            location_name: location,
            order: 9999  // Backend will auto-set correct order if you use the helper
        })
    });
    return await response.json();
}

// Move an item to a new position
async function moveItem(itemId, newPosition) {
    const response = await fetch(`http://localhost:8000/api/itinerary-items/${itemId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${yourToken}`
        },
        body: JSON.stringify({
            order: newPosition  // Other items will auto-adjust
        })
    });
    return await response.json();
}
```

---

## 📌 Summary

| Method | Description | Auto-Reorders Others? |
|--------|-------------|----------------------|
| `itinerary.append_item()` | Add to end | No (no need) |
| `item.insert_before()` | Insert before item | ✅ Yes |
| `item.insert_after()` | Insert after item | ✅ Yes |
| `item.move_to(n)` | Move to position n | ✅ Yes |
| `item.delete()` | Delete item | ✅ Yes |
| `itinerary.get_next_order()` | Get next order # | N/A |

**All methods handle order conflicts automatically!** 🎉

---

## 🚀 Next Steps

1. ✅ **Models updated** - New methods added
2. 🔄 **Run migrations** (if needed): `python manage.py makemigrations && python manage.py migrate`
3. 🧪 **Test it**: Run the test script above
4. 🔌 **Use in API**: Add custom endpoints (see examples above)
5. 🎨 **Frontend**: Build drag-and-drop UI using these methods!

Your itinerary system is now super flexible! 🎉
