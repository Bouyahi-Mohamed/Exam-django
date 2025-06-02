from rest_framework import serializers
from .models import MobileUser, DeviceToken, GestureData, Product, Order, CartItem, Cart, ProductReview
from django.core.validators import RegexValidator
import re

class MobileUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = MobileUser
        fields = ('id', 'username', 'email', 'phone_number', 'password',
                 'device_id', 'is_verified', 'last_login_ip')
        read_only_fields = ('device_id', 'is_verified', 'last_login_ip')

    def validate_phone_number(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value

    def create(self, validated_data):
        user = MobileUser.objects.create_user(**validated_data)
        return user

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ('id', 'user', 'token', 'token_type', 'is_active', 'last_used')
        read_only_fields = ('last_used',)

    def validate_token(self, value):
        token_type = self.initial_data.get('token_type')
        if token_type == 'FCM' and not value.startswith('fcm:'):
            raise serializers.ValidationError("Invalid FCM token format")
        elif token_type == 'APN' and not value.startswith('apn:'):
            raise serializers.ValidationError("Invalid APN token format")
        return value

class GestureDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GestureData
        fields = ('id', 'user', 'gesture_type', 'data_points',
                 'confidence_score', 'timestamp', 'processed')
        read_only_fields = ('processed',)

    def validate_confidence_score(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Confidence score must be between 0 and 1")
        return value

    def validate_data_points(self, value):
        required_keys = {'x', 'y', 'z', 'timestamp'}
        if not isinstance(value, list):
            raise serializers.ValidationError("Data points must be a list")
        for point in value:
            if not isinstance(point, dict):
                raise serializers.ValidationError("Each data point must be an object")
            if not all(key in point for key in required_keys):
                raise serializers.ValidationError(f"Each data point must contain {required_keys}")
        return value

class ProductReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'user_username', 'rating', 'comment', 'created_at')
        read_only_fields = ('user',)

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    absolute_image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'image',
            'image_url', 'absolute_image_url', 'average_rating', 'reviews', 'is_ai_generated'
        ]
        extra_kwargs = {
            'image': {'write_only': True, 'required': False}
        }

    def get_image_url(self, obj):
        return obj.image.url if obj.image else ""

    def get_absolute_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return ""

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        return [
            {
                'id': review.id,
                'user': review.user.id,
                'user_username': review.user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at
            }
            for review in reviews
        ]

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price', 'status', 'created_at')
        read_only_fields = ('unit_price', 'total_price', 'status')

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'updated_at')