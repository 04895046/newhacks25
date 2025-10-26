from rest_framework import generics, viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.conf import settings # To get the API key
from django.contrib.auth.models import User
from .models import (
    Itinerary, ItineraryItem, BillGroup, Expense, ExpenseSplit # Add new models
)
from .serializers import (
    UserSerializer, UserSimpleSerializer, ItineraryDetailSerializer, ItineraryListSerializer,
    ItineraryItemSerializer, BillGroupSerializer, BillGroupDetailSerializer,
    ExpenseSerializer, ExpenseReadSerializer # Add new serializers
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


class CustomAuthTokenLoginView(ObtainAuthToken):
    """
    Custom login view that returns the auth token AND user info.
    POST /api/login/
    Body: {"username": "user", "password": "pass"}
    Returns: {"token": "...", "user": {"id": 1, "username": "user"}}
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Serialize the user info using UserSimpleSerializer
        user_serializer = UserSimpleSerializer(user)

        return Response({
            'token': token.key,
            'user': user_serializer.data # Include user info here
        })


class UserSearchView(generics.ListAPIView):
    """
    API endpoint to search for users by username.
    Requires authentication.
    Usage: GET /api/users/search/?q=some_username
    """
    serializer_class = UserSimpleSerializer
    permission_classes = [IsAuthenticated] # Only logged-in users can search

    def get_queryset(self):
        """
        Filter users based on the 'q' query parameter (case-insensitive contains).
        Excludes the requesting user.
        """
        queryset = User.objects.all()
        username_query = self.request.query_params.get('q', None)
        if username_query is not None and username_query.strip():
            # Case-insensitive search for usernames containing the query
            queryset = queryset.filter(username__icontains=username_query.strip())

        # Exclude the user making the request from the search results
        queryset = queryset.exclude(id=self.request.user.id)

        # Limit results for performance (optional but recommended)
        return queryset.order_by('username')[:20] # Return max 20 results


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
        Create the group, add the creator, and add any other specified members by ID.
        """
        # Get member IDs from the request data *before* saving the serializer
        member_ids_str = self.request.data.get('members', []) # Expecting a list of IDs as strings or integers
        member_ids = []
        if isinstance(member_ids_str, list):
             try:
                 # Ensure IDs are integers
                 member_ids = [int(id_val) for id_val in member_ids_str]
             except (ValueError, TypeError):
                 # Handle potential errors if input is not list of numbers
                 # Optionally raise a ValidationError here
                 pass

        # Save the group (without members initially via serializer)
        group = serializer.save() # Serializer is read-only for members now

        # Add the creator
        group.members.add(self.request.user)

        # Add other members specified in the request
        if member_ids:
            # Fetch valid users matching the provided IDs
            users_to_add = User.objects.filter(id__in=member_ids).exclude(id=self.request.user.id) # Exclude self if passed
            group.members.add(*users_to_add) # Add the valid users
    
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
    
    @action(detail=True, methods=['get'])
    def settlements(self, request, pk=None):
        """
        CUSTOM ACTION: /api/groups/<id>/settlements/
        Calculates the optimal settlement plan - who owes whom.
        Uses a greedy algorithm to minimize the number of transactions.
        
        Returns:
        [
            {"from": "bob", "to": "alice", "amount": "30.00"},
            {"from": "charlie", "to": "alice", "amount": "20.00"}
        ]
        """
        group = self.get_object()
        
        # Step 1: Calculate net balances for each member (same as balances endpoint)
        total_paid = group.expenses.filter(group=group).values(
            'payer__username'
        ).annotate(
            paid=Sum('total_amount')
        ).order_by()

        total_owed = ExpenseSplit.objects.filter(expense__group=group).values(
            'user_owed__username'
        ).annotate(
            owed=Sum('amount_owed')
        ).order_by()

        balances = {}
        for member in group.members.all():
            balances[member.username] = decimal.Decimal('0.00')

        for paid_data in total_paid:
            balances[paid_data['payer__username']] += paid_data['paid']
            
        for owed_data in total_owed:
            balances[owed_data['user_owed__username']] -= owed_data['owed']
        
        # Step 2: Separate creditors (positive balance) and debtors (negative balance)
        creditors = []  # People who are owed money
        debtors = []    # People who owe money
        
        for username, balance in balances.items():
            if balance > decimal.Decimal('0.01'):  # Use small epsilon for floating point comparison
                creditors.append({"username": username, "amount": balance})
            elif balance < decimal.Decimal('-0.01'):
                debtors.append({"username": username, "amount": abs(balance)})
        
        # Step 3: Match debtors to creditors using greedy algorithm
        settlements = []
        
        # Sort by amount (largest first) for better distribution
        creditors.sort(key=lambda x: x['amount'], reverse=True)
        debtors.sort(key=lambda x: x['amount'], reverse=True)
        
        i = 0  # creditor index
        j = 0  # debtor index
        
        while i < len(creditors) and j < len(debtors):
            creditor = creditors[i]
            debtor = debtors[j]
            
            # Calculate the settlement amount (minimum of what's owed and what's due)
            settlement_amount = min(creditor['amount'], debtor['amount'])
            
            # Only record transactions that are meaningful (> $0.01)
            if settlement_amount > decimal.Decimal('0.01'):
                settlements.append({
                    "from": debtor['username'],
                    "to": creditor['username'],
                    "amount": f"{settlement_amount:.2f}"
                })
            
            # Update remaining amounts
            creditor['amount'] -= settlement_amount
            debtor['amount'] -= settlement_amount
            
            # Move to next creditor/debtor if current one is settled
            if creditor['amount'] < decimal.Decimal('0.01'):
                i += 1
            if debtor['amount'] < decimal.Decimal('0.01'):
                j += 1
        
        return Response(settlements)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating and viewing Expenses.
    Uses different serializers for read vs write operations.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only list expenses for groups the user is in
        return Expense.objects.filter(group__members=self.request.user).order_by('-date')
    
    def get_serializer_class(self):
        """
        Use ExpenseReadSerializer for GET requests (list, retrieve)
        Use ExpenseSerializer for POST/PUT/PATCH requests (create, update)
        """
        if self.action in ['list', 'retrieve']:
            return ExpenseReadSerializer
        return ExpenseSerializer
    
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
