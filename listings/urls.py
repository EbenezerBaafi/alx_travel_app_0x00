from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'listings'

router = DefaultRouter()
# ViewSets will be registered here later
# Example: router.register(r'properties', PropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Additional URL patterns can be added here
]