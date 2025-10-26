from django.db import models
from django.contrib.auth.models import User


class Itinerary(models.Model):
    """
    Represents an entire trip or plan, linked to a user.
    This is the "head" of your itinerary structure.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="itineraries")
    title = models.CharField(max_length=255, default="My New Itinerary")
    region = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'Toronto', 'Paris'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # NEW: Store the entire AI-generated JSON blob
    ai_generated_data = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Complete AI-generated itinerary JSON from Gemini API"
    )

    class Meta:
        verbose_name_plural = "Itineraries"
        ordering = ['-created_at']

    def __str__(self):
        return f"'{self.title}' by {self.owner.username}"
    
    def get_next_order(self):
        """Get the next order number for appending a new item."""
        last_item = self.items.order_by('-order').first()
        return (last_item.order + 1) if last_item else 0
    
    def append_item(self, description, location_name='', start_time=None, end_time=None):
        """
        Append a new item to the end of the itinerary.
        Returns the created ItineraryItem.
        """
        next_order = self.get_next_order()
        return ItineraryItem.objects.create(
            itinerary=self,
            description=description,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            order=next_order
        )


class ItineraryItem(models.Model):
    """
    Represents one "node" or "state" in your itinerary.
    Instead of a linked list, we use an 'order' field.
    This makes querying and reordering trivial.
    """
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="items")
    description = models.TextField(help_text="e.g., 'Visit the CN Tower'")
    location_name = models.CharField(max_length=255, blank=True, help_text="e.g., 'CN Tower'")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    # This integer field is the key! It defines the sequence.
    order = models.PositiveIntegerField()

    class Meta:
        # This ensures all items in an itinerary are ordered correctly by default
        ordering = ['order']
        # Ensure order is unique per itinerary
        unique_together = ['itinerary', 'order']

    def __str__(self):
        return f"{self.order}: {self.description[:50]}"
    
    def insert_before(self, description, location_name='', start_time=None, end_time=None):
        """
        Insert a new item BEFORE this item.
        Automatically shifts this item and all items after it down by 1.
        Returns the newly created ItineraryItem.
        """
        # Shift all items at or after this position down by 1
        items_to_shift = ItineraryItem.objects.filter(
            itinerary=self.itinerary,
            order__gte=self.order
        ).order_by('-order')
        
        for item in items_to_shift:
            item.order += 1
            item.save()
        
        # Create the new item at the current position
        return ItineraryItem.objects.create(
            itinerary=self.itinerary,
            description=description,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            order=self.order
        )
    
    def insert_after(self, description, location_name='', start_time=None, end_time=None):
        """
        Insert a new item AFTER this item.
        Automatically shifts all items after this item down by 1.
        Returns the newly created ItineraryItem.
        """
        new_order = self.order + 1
        
        # Shift all items after this position down by 1
        items_to_shift = ItineraryItem.objects.filter(
            itinerary=self.itinerary,
            order__gte=new_order
        ).order_by('-order')
        
        for item in items_to_shift:
            item.order += 1
            item.save()
        
        # Create the new item at the new position
        return ItineraryItem.objects.create(
            itinerary=self.itinerary,
            description=description,
            location_name=location_name,
            start_time=start_time,
            end_time=end_time,
            order=new_order
        )
    
    def move_to(self, new_order):
        """
        Move this item to a new position in the itinerary.
        Automatically handles reordering of other items.
        """
        if new_order < 0:
            raise ValueError("Order must be non-negative")
        
        old_order = self.order
        
        if old_order == new_order:
            return  # No change needed
        
        # Temporarily set this item to a very high order to avoid conflicts
        temp_order = 999999
        self.order = temp_order
        self.save()
        
        if new_order > old_order:
            # Moving down: shift items between old and new position up
            ItineraryItem.objects.filter(
                itinerary=self.itinerary,
                order__gt=old_order,
                order__lte=new_order
            ).update(order=models.F('order') - 1)
        else:
            # Moving up: shift items between new and old position down
            ItineraryItem.objects.filter(
                itinerary=self.itinerary,
                order__gte=new_order,
                order__lt=old_order
            ).update(order=models.F('order') + 1)
        
        # Now set this item to its final position
        self.order = new_order
        self.save()
    
    def delete(self, *args, **kwargs):
        """
        Override delete to automatically reorder remaining items.
        When an item is deleted, all items after it shift up by 1.
        """
        deleted_order = self.order
        itinerary = self.itinerary
        
        # First, move items after the deleted position to temporary high orders
        items_to_shift = list(ItineraryItem.objects.filter(
            itinerary=itinerary,
            order__gt=deleted_order
        ).order_by('order'))
        
        # Delete the item first
        super().delete(*args, **kwargs)
        
        # Now shift all items after the deleted position up by 1
        for item in items_to_shift:
            item.order = item.order - 1
            item.save()

class BillGroup(models.Model):
    """
    Represents a group of users sharing bills.
    e.g., "NYC Trip Crew", "Apartment Roommates"
    """
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="bill_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    """
    Represents a single bill or transaction.
    e.g., "Dinner at Joe's Pizza"
    """
    SPLIT_TYPES = [
        ('E', 'Evenly'),
        ('M', 'Manually'),
        ('I', 'Itemized'), # Stored as 'Manually' but flagged for client
    ]

    group = models.ForeignKey(BillGroup, on_delete=models.CASCADE, related_name="expenses")
    description = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # The user who paid the bill
    payer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="paid_expenses")
    
    date = models.DateTimeField(auto_now_add=True)
    split_type = models.CharField(max_length=1, choices=SPLIT_TYPES, default='E')

    # --- For the OCR / Itemized Flow ---
    # The backend just *stores* this data for proof. 
    # The Android app will do the OCR and calculation.
    receipt_image = models.URLField(blank=True, null=True) # Optional: URL to receipt image
    item_data_json = models.TextField(blank=True, null=True) # Optional: JSON string of items

    def __str__(self):
        return f"{self.description} (${self.total_amount})"

class ExpenseSplit(models.Model):
    """
    The core of the ledger. This links an Expense to a User and
    records how much that user *owes* for that expense.
    """
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    user_owed = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owed_splits")
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # A user can only have one split entry per expense
        unique_together = ('expense', 'user_owed')

    def __str__(self):
        return f"{self.user_owed.username} owes ${self.amount_owed} for {self.expense.description}"