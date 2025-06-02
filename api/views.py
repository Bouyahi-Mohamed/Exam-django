from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import MobileUser, DeviceToken, GestureData, Product, Order, Cart, CartItem, ProductReview
from .serializers import (
    MobileUserSerializer, DeviceTokenSerializer, GestureDataSerializer,
    ProductSerializer, OrderSerializer, CartSerializer, CartItemSerializer,
    ProductReviewSerializer
)
from .tasks import process_gesture_data, send_push_notification, generate_product_with_ai
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import openai
from django.conf import settings
import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import magic  # Pour la détection MIME
import logging
import os
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

logger = logging.getLogger(__name__)

# Create your views here.

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class MobileUserViewSet(viewsets.ModelViewSet):
    queryset = MobileUser.objects.all()
    serializer_class = MobileUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MobileUser.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            
            # Créer un panier pour l'utilisateur s'il n'en a pas
            Cart.objects.get_or_create(user=user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': MobileUserSerializer(user).data,
                'is_admin': user.is_staff
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class DeviceTokenViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def test_notification(self, request, pk=None):
        device_token = self.get_object()
        send_push_notification.delay(
            device_token.id,
            "Test Notification",
            "This is a test notification"
        )
        return Response({'status': 'notification sent'})

class GestureDataViewSet(viewsets.ModelViewSet):
    serializer_class = GestureDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GestureData.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        today = timezone.now().date()
        stats = GestureData.objects.filter(
            user=request.user,
            timestamp__date=today
        ).values('gesture_type').agg(
            total_count=models.Count('id'),
            avg_confidence=models.Avg('confidence_score')
        )
        return Response(stats)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            # First try to find existing products
            queryset = queryset.filter(name__icontains=search)
            
            # If no products found, generate one with AI
            if not queryset.exists():
                result = generate_product_with_ai.delay(search)
                product_data = result.get(timeout=30)  # Wait for AI generation
                
                if product_data:
                    # Return the newly created product
                    return Product.objects.filter(id=product_data['id'])
        
        return queryset

    def update(self, request, *args, **kwargs):
        """Handle both product data and image updates"""
        instance = self.get_object()
        data = request.data.copy()

        # Handle image upload if present
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            
            # Validate file type
            mime_type = get_mime_type(image_file)
            if not mime_type:
                return Response(
                    {'error': 'Image corrompue ou invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if mime_type not in allowed_types:
                return Response(
                    {'error': 'Type de fichier non autorisé'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Delete old image if exists
            if instance.image:
                try:
                    instance.image.delete(save=False)
                except Exception as e:
                    logger.warning(f"Erreur lors de la suppression de l'ancienne image: {str(e)}")

            # Set new image
            instance.image = image_file

        # Update other fields
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Build absolute URL for image if present
        response_data = serializer.data
        if 'image_url' in response_data and response_data['image_url']:
            if request.is_secure():
                protocol = 'https'
            else:
                protocol = 'http'
            host = request.get_host()
            response_data['url'] = f"{protocol}://{host}{response_data['image_url']}"

        return Response(response_data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # <-- CORRECT
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(f"Attempting to delete product {instance.id}: {instance.name}")
            
            # Get all orders for this product
            orders = instance.orders.all()
            if orders.exists():
                order_details = [
                    f"Order #{order.id} (Status: {order.status})"
                    for order in orders
                ]
                print(f"Found orders for product: {', '.join(order_details)}")
                
                # Check for active orders
                active_orders = orders.filter(status__in=['pending', 'paid', 'shipped'])
                if active_orders.exists():
                    active_order_details = [
                        f"Order #{order.id} (Status: {order.status})"
                        for order in active_orders
                    ]
                    error_message = {
                        'error': 'Cannot delete product with active orders.',
                        'detail': f"This product has {active_orders.count()} active orders: {', '.join(active_order_details)}. Cancel or complete these orders before deleting the product."
                    }
                    print(f"Deletion blocked: {error_message}")
                    return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for cart items
            cart_items = CartItem.objects.filter(product=instance)
            if cart_items.exists():
                print(f"Deleting {cart_items.count()} cart items for this product")
                cart_items.delete()
            
            # If we get here, we can safely delete the product
            print(f"No active orders found, proceeding with deletion")
            self.perform_destroy(instance)
            return Response(
                {'message': 'Product successfully deleted'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except models.ProtectedError as e:
            print(f"ProtectedError while deleting product: {str(e)}")
            protected_objects = [str(obj) for obj in e.protected_objects]
            error_message = {
                'error': 'Cannot delete product.',
                'detail': f"This product is referenced by protected objects: {', '.join(protected_objects)}. Cancel or complete these orders first."
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error while deleting product: {str(e)}")
            return Response(
                {
                    'error': 'An unexpected error occurred.',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Add a review to a product"""
        product = self.get_object()
        
        # Check if user already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response(
                {'error': 'You have already reviewed this product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a product"""
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ai_generated(self, request):
        """Get all AI-generated products"""
        products = Product.objects.filter(is_ai_generated=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an AI-generated product for permanent listing"""
        product = self.get_object()
        if not product.is_ai_generated:
            return Response(
                {'error': 'This is not an AI-generated product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.is_ai_generated = False  # Convert to regular product
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('query', '')
        if not query:
            products = Product.objects.all()
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)

        # First, search existing products
        products = Product.objects.filter(name__icontains=query)
        
        # If no products found and we have an API key, generate one with AI
        if not products.exists():
            if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('sk-xxxxxxx'):
                # If no API key, just return empty results
                return Response(
                    [],
                    status=status.HTTP_200_OK
                )

            try:
                # Initialize OpenAI client
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                
                # Generate product details using GPT
                prompt = f"""Generate a product based on this search: {query}
                Format the response as JSON with these fields:
                {{
                    "name": "product name",
                    "description": "detailed description",
                    "price": decimal number between 10 and 1000,
                    "stock": integer between 1 and 100
                }}"""
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI that generates product listings. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Parse the AI response
                try:
                    product_data = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError as e:
                    print(f"JSON Parse Error: {str(e)}")
                    print(f"Raw response: {response.choices[0].message.content}")
                    return Response([], status=status.HTTP_200_OK)
                
                # Validate the required fields
                required_fields = ['name', 'description', 'price', 'stock']
                if not all(field in product_data for field in required_fields):
                    print(f"Missing fields in response: {product_data}")
                    return Response([], status=status.HTTP_200_OK)
                
                # Create the new product
                product_data['is_ai_generated'] = True
                product_data['ai_source'] = 'GPT-3.5'
                
                serializer = self.get_serializer(data=product_data)
                if serializer.is_valid():
                    product = serializer.save()
                    return Response(serializer.data)
                else:
                    print(f"Serializer errors: {serializer.errors}")
                    return Response([], status=status.HTTP_200_OK)
                    
            except Exception as e:
                print(f"AI Generation Error: {str(e)}")
                return Response([], status=status.HTTP_200_OK)
        
        # Return the found products
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

def get_mime_type(file_obj):
    """
    Détecte de manière fiable le type MIME d'un fichier uploadé.
    Fonctionne avec InMemoryUploadedFile et TemporaryUploadedFile.
    """
    try:
        # Si le fichier est en mémoire
        if isinstance(file_obj, InMemoryUploadedFile):
            mime = magic.from_buffer(file_obj.read(), mime=True)
            file_obj.seek(0)  # Remettre le curseur au début
            return mime
        
        # Si le fichier est temporaire sur le disque
        elif isinstance(file_obj, TemporaryUploadedFile):
            return magic.from_file(file_obj.temporary_file_path(), mime=True)
        
        # Fallback : essayer de lire le début du fichier
        else:
            content = file_obj.read(2048)
            file_obj.seek(0)
            return magic.from_buffer(content, mime=True)
            
    except Exception as e:
        logger.error(f"Erreur lors de la détection MIME: {str(e)}")
        return None

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_product_image(request):
    """
    Upload une image pour un produit avec détection MIME robuste.
    Requiert:
        - request.FILES['image']: fichier image
        - request.data['product_id']: ID du produit (optionnel)
    """
    logger.info("Début de l'upload d'image")
    logger.debug(f"Request Data: {request.data}")
    logger.debug(f"Request Files: {request.FILES}")

    # 1. Vérification de la présence de l'image
    if 'image' not in request.FILES:
        logger.warning("Aucune image fournie dans la requête")
        return Response(
            {'error': 'Aucune image fournie'},
            status=status.HTTP_400_BAD_REQUEST
        )

    image_file = request.FILES['image']
    
    # 2. Détection du type MIME
    mime_type = get_mime_type(image_file)
    if not mime_type:
        logger.warning("Image corrompue détectée")
        return Response(
            {'error': 'Image corrompue ou invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logger.info(f"Type MIME détecté: {mime_type}")
    
    # 3. Validation du type MIME
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if mime_type not in allowed_types:
        logger.warning(f"Type de fichier non autorisé: {mime_type}")
        return Response(
            {'error': 'Type de fichier non autorisé'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 4. Gestion du produit (existant ou nouveau)
        product_id = request.data.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                logger.info(f"Mise à jour du produit existant {product_id}")

                # Mise à jour des données du produit si fournies
                if 'name' in request.data:
                    product.name = request.data['name']
                if 'description' in request.data:
                    product.description = request.data['description']
                if 'price' in request.data:
                    try:
                        product.price = float(request.data['price'])
                    except (ValueError, TypeError):
                        pass
                if 'stock' in request.data:
                    try:
                        product.stock = int(request.data['stock'])
                    except (ValueError, TypeError):
                        pass

                # Supprimer l'ancienne image si elle existe
                if product.image:
                    try:
                        product.image.delete(save=False)
                    except Exception as e:
                        logger.warning(f"Erreur lors de la suppression de l'ancienne image: {str(e)}")

                # Sauvegarder la nouvelle image
                product.image = image_file
                product.save()

            except Product.DoesNotExist:
                logger.warning(f"Produit non trouvé: {product_id}")
                return Response(
                    {'error': 'Produit non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ValueError:
                logger.warning(f"ID de produit invalide: {product_id}")
                return Response(
                    {'error': 'Produit non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Si pas de product_id, vérifier si un produit avec le même nom existe déjà
            name = request.data.get('name')
            if name:
                existing_product = Product.objects.filter(name=name).first()
                if existing_product:
                    product = existing_product
                    logger.info(f"Mise à jour du produit existant avec le nom: {name}")
                else:
                    logger.info("Création d'un nouveau produit")
                    product = Product.objects.create(
                        name=name or os.path.splitext(image_file.name)[0].replace('_', ' ').replace('-', ' ').title(),
                        description=request.data.get('description', ''),
                        price=float(request.data.get('price', 0.00)),
                        stock=int(request.data.get('stock', 0)),
                        image=image_file
                    )
            else:
                # Créer un nouveau produit avec le nom du fichier
                base_name = os.path.splitext(image_file.name)[0]
                product = Product.objects.create(
                    name=base_name.replace('_', ' ').replace('-', ' ').title(),
                    description=request.data.get('description', ''),
                    price=float(request.data.get('price', 0.00)),
                    stock=int(request.data.get('stock', 0)),
                    image=image_file
                )
        
        logger.info(f"Image sauvegardée avec succès pour le produit {product.id}")
        
        # Construire l'URL absolue de l'image
        if request.is_secure():
            protocol = 'https'
        else:
            protocol = 'http'
        host = request.get_host()
        image_url = f"{protocol}://{host}{product.image_url}"
        
        # Retour de la réponse avec l'URL
        return Response({
            'message': 'Image téléchargée avec succès',
            'image_url': product.image_url,  # URL relative
            'url': image_url,  # URL absolue
            'product': ProductSerializer(product).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return Response(
            {
                'error': 'Erreur lors du traitement de l\'image',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock < quantity:
            return Response(
                {'error': 'Stock insuffisant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return Response({
            'cart': CartSerializer(cart).data,
            'has_items': cart.items.exists()
        })

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        
        # Check if cart is empty after deletion
        is_empty = not cart.items.exists()
        
        return Response({
            'cart': CartSerializer(cart).data,
            'is_empty': is_empty,
            'message': 'Cart is empty' if is_empty else None
        })

    @action(detail=True, methods=['post'])
    def update_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item')
        quantity = int(request.data.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        if cart_item.product.stock < quantity:
            return Response(
                {'error': 'Stock insuffisant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity <= 0:
            cart_item.delete()
            is_empty = not cart.items.exists()
            return Response({
                'cart': CartSerializer(cart).data,
                'is_empty': is_empty,
                'message': 'Cart is empty' if is_empty else 'Item removed'
            })
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'cart': CartSerializer(cart).data,
            'has_items': True
        })

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        
        if not cart.items.exists():
            return Response(
                {'error': 'Le panier est vide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create orders for each cart item
        orders = []
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuffisant pour {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order = Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
                status='pending'
            )
            orders.append(order)
            
            # Update stock
            item.product.stock -= item.quantity
            item.product.save()
        
        # Empty the cart
        cart.items.all().delete()
        
        return Response({
            'message': 'Commande créée avec succès',
            'orders': OrderSerializer(orders, many=True).data,
            'is_empty': True
        })

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        # Vérifier le stock
        if product.stock < quantity:
            return Response(
                {'error': 'Stock insuffisant'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer la commande
        order = serializer.save(
            user=self.request.user,
            unit_price=product.price
        )

        # Mettre à jour le stock
        product.stock -= quantity
        product.save()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            
            # Créer un panier pour l'utilisateur s'il n'en a pas
            Cart.objects.get_or_create(user=user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': MobileUserSerializer(user).data,
                'is_admin': user.is_staff
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@method_decorator(csrf_exempt, name='dispatch')
class UserRegisterView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any access
    serializer_class = MobileUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Create initial cart for user
            Cart.objects.get_or_create(user=user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
