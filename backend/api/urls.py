from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserCreateView, CustomAuthTokenLoginView, UserSearchView,
    ItineraryViewSet, ItineraryItemViewSet,
    BillGroupViewSet, ExpenseViewSet, ParseReceiptView
)

# ... (urlpatterns = [...] is already here) ...

# The DefaultRouter automatically creates all the REST API endpoints
# (GET, POST, PUT, PATCH, DELETE) for the registered ViewSets
router = DefaultRouter()
router.register(r'itineraries', ItineraryViewSet, basename='itinerary')
router.register(r'itinerary-items', ItineraryItemViewSet, basename='itineraryitem')


# --- ADD THESE NEW ROUTES ---
router.register(r'groups', BillGroupViewSet, basename='billgroup')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    # API endpoints from the router
    # This will create:
    # - /api/itineraries/ (list, create)
    # - /api/itineraries/<id>/ (retrieve, update, delete)
    # - /api/itineraries/generate/ (custom action)
    # - /api/itinerary-items/ (list, create)
    # - /api/itinerary-items/<id>/ (retrieve, update, delete)
    # - /api/groups/ (list, create)
    # - /api/groups/<id>/ (retrieve, update, delete)
    # - /api/groups/<id>/balances/ (custom action)
    # - /api/expenses/ (list, create)
    # - /api/expenses/<id>/ (retrieve, update, delete)
    path('', include(router.urls)),

    # Auth endpoints
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomAuthTokenLoginView.as_view(), name='login'),  # Custom login view
    
    # User search endpoint
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    
    # OCR endpoint
    path('ocr/parse-receipt/', ParseReceiptView.as_view(), name='parse-receipt'),
]


