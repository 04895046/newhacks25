from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import Itinerary, ItineraryItem
from .serializers import (
    UserSerializer, 
    ItineraryDetailSerializer, 
    ItineraryListSerializer, 
    ItineraryItemSerializer,
    ItineraryItemCreateSerializer
)


# ============================================
# AUTH VIEWS
# Corresponds to "[Create log/in, auth]" box
# ============================================

class UserCreateView(generics.CreateAPIView):
    """
    API endpoint for user registration ('Create' in your diagram).
    POST /api/register/
    Body: {"username": "user", "password": "pass"}
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Allow anyone to register


# ============================================
# ITINERARY VIEWS
# Corresponds to "select region", "input detailed needs", "edit itinerary"
# ============================================

class ItineraryViewSet(viewsets.ModelViewSet):
    """
    Handles all CRUD operations for Itineraries.
    - List all user's itineraries: GET /api/itineraries/
    - Retrieve one itinerary: GET /api/itineraries/<id>/
    - Create itinerary: POST /api/itineraries/
    - Update itinerary: PUT/PATCH /api/itineraries/<id>/
    - Delete itinerary: DELETE /api/itineraries/<id>/
    - Generate itinerary (custom): POST /api/itineraries/generate/
    """
    permission_classes = [IsAuthenticated]  # User must be logged in

    def get_queryset(self):
        # Only return itineraries belonging to the current user
        return Itinerary.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        # Use different serializers for list vs detail views
        if self.action == 'list':
            return ItineraryListSerializer
        return ItineraryDetailSerializer

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the owner
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        CUSTOM API ENDPOINT for ML-powered itinerary generation.
        This corresponds to: "select region" + "input detailed needs" + "generate itinerary..."
        
        Frontend sends:
        POST /api/itineraries/generate/
        Body: {
            "region": "Toronto",
            "needs": "3 day trip, love museums and food"
        }
        
        Backend returns: The newly created itinerary with all items
        """
        region = request.data.get('region')
        needs = request.data.get('needs')

        if not region or not needs:
            return Response(
                {"error": "Both 'region' and 'needs' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ============================================
        # TODO: INTEGRATE YOUR ML MODEL HERE
        # ============================================
        # Replace the dummy data below with your actual ML call:
        # from your_ml_script import call_ml_agent
        # generated_data = call_ml_agent(region, needs)
        #
        # Expected format:
        # generated_data = [
        #     {"desc": "Visit CN Tower", "loc": "CN Tower", "order": 0},
        #     {"desc": "Visit ROM", "loc": "Royal Ontario Museum", "order": 1},
        # ]
        # ============================================
        
        # Dummy data for hackathon testing
        generated_data = [
            {
                "desc": f"AI Generated: Explore {region} downtown", 
                "loc": f"{region} City Center", 
                "order": 0
            },
            {
                "desc": f"AI Generated: Visit a famous landmark in {region}", 
                "loc": "Famous Landmark", 
                "order": 1
            },
            {
                "desc": f"AI Generated: Enjoy local cuisine", 
                "loc": "Local Restaurant", 
                "order": 2
            },
        ]

        # Create the Itinerary and its items in the database
        new_itinerary = Itinerary.objects.create(
            owner=request.user, 
            title=f"AI Trip to {region}",
            region=region
        )

        for item_data in generated_data:
            ItineraryItem.objects.create(
                itinerary=new_itinerary,
                description=item_data['desc'],
                location_name=item_data['loc'],
                order=item_data['order']
            )
        
        # Send the newly created itinerary back to the frontend
        serializer = ItineraryDetailSerializer(new_itinerary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ItineraryItemViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for individual Itinerary Items.
    This is the core of the "edit itinerary" feature.
    
    - List all items: GET /api/itinerary-items/ (all items user owns)
    - Get one item: GET /api/itinerary-items/<id>/
    - Create item: POST /api/itinerary-items/
    - Update item: PUT/PATCH /api/itinerary-items/<id>/
    - Delete item: DELETE /api/itinerary-items/<id>/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only let users access items that belong to their itineraries
        return ItineraryItem.objects.filter(itinerary__owner=self.request.user)
    
    def get_serializer_class(self):
        # Use different serializer for creation (includes itinerary FK)
        if self.action == 'create':
            return ItineraryItemCreateSerializer
        return ItineraryItemSerializer
