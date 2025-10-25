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

    class Meta:
        verbose_name_plural = "Itineraries"
        ordering = ['-created_at']

    def __str__(self):
        return f"'{self.title}' by {self.owner.username}"


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
