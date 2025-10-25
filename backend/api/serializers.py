from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Itinerary, ItineraryItem


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Used in the 'Create' (register) endpoint.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # This properly hashes the password
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class ItineraryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual itinerary items.
    Used for creating, updating, and deleting items.
    """
    class Meta:
        model = ItineraryItem
        fields = ['id', 'description', 'location_name', 'start_time', 'end_time', 'order']
        

class ItineraryItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating itinerary items.
    Includes the itinerary foreign key.
    """
    class Meta:
        model = ItineraryItem
        fields = ['id', 'itinerary', 'description', 'location_name', 'start_time', 'end_time', 'order']


class ItineraryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a single itinerary.
    This "nests" the items inside the itinerary.
    This is how you send the whole list at once to the frontend.
    """
    items = ItineraryItemSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Itinerary
        fields = ['id', 'owner', 'owner_username', 'title', 'region', 'created_at', 'updated_at', 'items']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class ItineraryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing all itineraries.
    Used in the list view (without nested items for performance).
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = ['id', 'title', 'region', 'owner_username', 'created_at', 'item_count']

    def get_item_count(self, obj):
        return obj.items.count()
