from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserCreateView, ItineraryViewSet, ItineraryItemViewSet

# The DefaultRouter automatically creates all the REST API endpoints
# (GET, POST, PUT, PATCH, DELETE) for the registered ViewSets
router = DefaultRouter()
router.register(r'itineraries', ItineraryViewSet, basename='itinerary')
router.register(r'itinerary-items', ItineraryItemViewSet, basename='itineraryitem')

urlpatterns = [
    # API endpoints from the router
    # This will create:
    # - /api/itineraries/ (list, create)
    # - /api/itineraries/<id>/ (retrieve, update, delete)
    # - /api/itineraries/generate/ (custom action)
    # - /api/itinerary-items/ (list, create)
    # - /api/itinerary-items/<id>/ (retrieve, update, delete)
    path('', include(router.urls)),

    # Auth endpoints
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),  # This is the 'Log in' endpoint
]
