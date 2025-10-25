from django.contrib import admin
from .models import Itinerary, ItineraryItem


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'region', 'created_at']
    list_filter = ['created_at', 'region']
    search_fields = ['title', 'owner__username', 'region']


@admin.register(ItineraryItem)
class ItineraryItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'itinerary', 'description_short', 'location_name', 'order']
    list_filter = ['itinerary']
    search_fields = ['description', 'location_name']
    ordering = ['itinerary', 'order']
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'
