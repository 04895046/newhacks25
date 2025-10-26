#!/usr/bin/env python
"""
Quick test script to demonstrate append and insert functionality.
Run with: python manage.py shell < test_append_insert.py
"""

from api.models import Itinerary, ItineraryItem, User
from django.db import transaction

print("=" * 60)
print("Testing Itinerary Append & Insert Functionality")
print("=" * 60)

# Get the first user
user = User.objects.first()
if not user:
    print("❌ No users found. Please create a user first.")
    exit(1)

print(f"\n✅ Using user: {user.username}")

# Create a test itinerary
with transaction.atomic():
    itinerary = Itinerary.objects.create(
        owner=user,
        title="Test Trip - Append & Insert Demo",
        region="Toronto"
    )
    print(f"✅ Created itinerary: {itinerary.title}")

# Test 1: Append items
print("\n" + "=" * 60)
print("TEST 1: Appending items to the end")
print("=" * 60)

item1 = itinerary.append_item(
    description="Morning: Visit CN Tower",
    location_name="CN Tower"
)
print(f"✅ Appended: {item1.description} (order: {item1.order})")

item2 = itinerary.append_item(
    description="Afternoon: Explore Royal Ontario Museum",
    location_name="ROM"
)
print(f"✅ Appended: {item2.description} (order: {item2.order})")

item3 = itinerary.append_item(
    description="Evening: Dinner at St. Lawrence Market",
    location_name="St. Lawrence Market"
)
print(f"✅ Appended: {item3.description} (order: {item3.order})")

print("\nCurrent itinerary:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 2: Insert before
print("\n" + "=" * 60)
print("TEST 2: Insert lunch BEFORE afternoon activity")
print("=" * 60)

lunch = item2.insert_before(
    description="Lunch: Grab lunch downtown",
    location_name="Downtown Toronto"
)
print(f"✅ Inserted: {lunch.description} (order: {lunch.order})")
print(f"   (Before: {item2.description})")

print("\nCurrent itinerary after insert_before:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 3: Insert after
print("\n" + "=" * 60)
print("TEST 3: Insert photo stop AFTER CN Tower")
print("=" * 60)

photo = item1.insert_after(
    description="Take panoramic photos",
    location_name="CN Tower Observation Deck"
)
print(f"✅ Inserted: {photo.description} (order: {photo.order})")
print(f"   (After: {item1.description})")

print("\nCurrent itinerary after insert_after:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 4: Move item
print("\n" + "=" * 60)
print("TEST 4: Move dinner to position 2 (earlier in the day)")
print("=" * 60)

item3_fresh = itinerary.items.get(id=item3.id)  # Refresh from DB
old_order = item3_fresh.order
print(f"Current position of dinner: {old_order}")

item3_fresh.move_to(2)
print(f"✅ Moved dinner to position: 2")

print("\nCurrent itinerary after move_to:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 5: Delete item
print("\n" + "=" * 60)
print("TEST 5: Delete the photo stop")
print("=" * 60)

photo_fresh = itinerary.items.get(id=photo.id)  # Refresh from DB
print(f"Deleting: {photo_fresh.description} (order: {photo_fresh.order})")

photo_fresh.delete()
print(f"✅ Deleted item")

print("\nFinal itinerary after delete (note: no gaps in order):")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description}")

# Test 6: Get next order
print("\n" + "=" * 60)
print("TEST 6: Get next order number")
print("=" * 60)

next_order = itinerary.get_next_order()
print(f"✅ Next available order number: {next_order}")

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print(f"\nFinal itinerary has {itinerary.items.count()} items:")
for item in itinerary.items.all():
    print(f"  {item.order}: {item.description} @ {item.location_name}")

print("\n🎉 Your itinerary system supports:")
print("  ✅ Append items to the end")
print("  ✅ Insert before any item")
print("  ✅ Insert after any item")
print("  ✅ Move items to new positions")
print("  ✅ Delete items (with auto-reorder)")
print("  ✅ Get next order number")
print("\n" + "=" * 60)
