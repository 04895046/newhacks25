from rest_framework import generics, viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings # To get the API key
from django.contrib.auth.models import User
from .models import (
    Itinerary, ItineraryItem, BillGroup, Expense, ExpenseSplit # Add new models
)
from .serializers import (
    UserSerializer, ItineraryDetailSerializer, ItineraryListSerializer,
    ItineraryItemSerializer, BillGroupSerializer, BillGroupDetailSerializer,
    ExpenseSerializer # Add new serializers
)
from django.db.models import Sum, Q, F, DecimalField
import decimal, requests, json

import google.generativeai as genai
import PIL.Image
from .schema import Receipt # Import our Pydantic schema


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
    
    serializer_class = ItineraryItemSerializer

# --- LEDGER APP VIEWS ---

class BillGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating, listing, and retrieving BillGroups.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only list groups that the current user is a member of
        return self.request.user.bill_groups.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BillGroupDetailSerializer
        return BillGroupSerializer
    
    def perform_create(self, serializer):
        """
        This is the updated, simpler create method.
        """
        # The serializer.save() will handle saving the 'members' field
        # that was passed in the request (e.g., [1, 2, 3])
        # because 'members' is a writeable field on the serializer.
        group = serializer.save()
        
        # We just need to ensure the creator is also added,
        # in case they forgot to add themselves to the list.
        # .add() is safe and won't create duplicates.
        group.members.add(self.request.user)
    
    @action(detail=True, methods=['get'])
    def balances(self, request, pk=None):
        """
        CUSTOM ACTION: /api/groups/<id>/balances/
        Calculates the final net balance for every member in the group.
        This is the "Settle Up" logic.
        """
        group = self.get_object()
        
        # 1. Get total amount *paid* by each user
        total_paid = group.expenses.filter(group=group).values(
            'payer__username'
        ).annotate(
            paid=Sum('total_amount')
        ).order_by() # payer__username, paid

        # 2. Get total amount *owed* by each user
        total_owed = ExpenseSplit.objects.filter(expense__group=group).values(
            'user_owed__username'
        ).annotate(
            owed=Sum('amount_owed')
        ).order_by() # user_owed__username, owed

        # 3. Combine them in a dictionary, initializing all members
        balances = {}
        for member in group.members.all():
            balances[member.username] = decimal.Decimal('0.00')

        # Add payments
        for paid_data in total_paid:
            balances[paid_data['payer__username']] += paid_data['paid']
            
        # Subtract debts
        for owed_data in total_owed:
            balances[owed_data['user_owed__username']] -= owed_data['owed']

        # Format: [ {"username": "alice", "balance": "15.50"}, ... ]
        final_balances = [
            {"username": username, "balance": f"{balance:.2f}"}
            for username, balance in balances.items()
        ]

        return Response(final_balances)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating Expenses.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only list expenses for groups the user is in
        return Expense.objects.filter(group__members=self.request.user).order_by('-date')
    
    def get_serializer_context(self):
        """
        This is important! It passes the `request` object 
        to the serializer so its 'validate' method can
        check the user.
        """
        return {'request': self.request}
    
    # All the validation and creation logic is now
    # correctly handled by ExpenseSerializer.
    # We don't need a perform_create() method here at all.


class ParseReceiptView(APIView):
    """
    An endpoint that accepts an uploaded image, sends it to Gemini
    for OCR and structured JSON extraction, and returns the JSON.
    
    The image is *not* saved on the server.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Must-have for file uploads

    def post(self, request, *args, **kwargs):
        # 1. Get the uploaded image from the request
        image_file = request.data.get('image')
        
        if not image_file:
            return Response(
                {"error": "No image file provided in 'image' field."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 2. Configure Gemini with the API key from settings.py
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return Response(
                    {"error": "GEMINI_API_KEY not configured on server."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            genai.configure(api_key=api_key)
            
            # 3. Open the uploaded image in memory
            # The uploaded file is a Django UploadedFile, open it with PIL
            img = PIL.Image.open(image_file)

            # 4. Set up the model and prompt
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = "Extract all line items from this receipt. Follow the schema."

            # 5. Call Gemini and enforce the JSON schema
            response = model.generate_content(
                [prompt, img],
                generation_config=genai.GenerationConfig(
                    response_schema=Receipt,  # <-- Enforce your Pydantic schema
                    response_mime_type="application/json"
                )
            )

            # 6. Validate the AI's JSON output (extra safety)
            # This parses the JSON text and validates it with your Pydantic model
            processed_receipt = Receipt.model_validate_json(response.text)
            dict = processed_receipt.model_dump()
            url = "https://api.fxratesapi.com/latest"
            resp = requests.get(url=url).json()

            for item in dict["items"]:
                item["price_in_cad"] = item["price"] / (resp["rates"][item["currency"]] / resp["rates"]["CAD"])


            # 7. Send the clean, validated JSON back to the Android app
            # .model_dump() converts the Pydantic object to a dict
            return Response(dict, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle API errors or validation errors
            return Response(
                {"error": f"Failed to parse receipt: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except KeyboardInterrupt:
            pass
