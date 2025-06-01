from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MobileUserViewSet, UserLoginView, UserRegisterView,
    DeviceTokenViewSet, GestureDataViewSet, ProductViewSet,
    CartViewSet, OrderViewSet, upload_product_image
)
from django.conf import settings
from django.conf.urls.static import static

# Create a router for viewsets
router = DefaultRouter()
router.register(r'users', MobileUserViewSet, basename='user')
router.register(r'devices', DeviceTokenViewSet, basename='device')
router.register(r'gestures', GestureDataViewSet, basename='gesture')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

# Define custom URL patterns
custom_urlpatterns = [
    path('v1/products/upload_image/', upload_product_image, name='product-image-upload'),
    path('v1/users/login/', UserLoginView.as_view(), name='user-login'),
    path('v1/users/register/', UserRegisterView.as_view(), name='user-register'),
]

# Combine URL patterns, ensuring custom patterns take precedence
urlpatterns = custom_urlpatterns + [
    path('v1/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)