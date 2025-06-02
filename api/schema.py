import graphene
from graphene_django import DjangoObjectType
from .models import Product, Order, Cart, ProductReview, MobileUser
from graphql_jwt.decorators import login_required
from django.core.exceptions import PermissionDenied

class UserType(DjangoObjectType):
    class Meta:
        model = MobileUser
        fields = ('id', 'username', 'email', 'is_staff')

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "image", "is_ai_generated")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'quantity', 'unit_price', 'total_price', 'status', 'created_at')

class CartType(DjangoObjectType):
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total')

class ProductReviewType(DjangoObjectType):
    class Meta:
        model = ProductReview
        fields = ('id', 'product', 'user', 'rating', 'comment', 'created_at')

class Query(graphene.ObjectType):
    # Product queries
    products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    all_products = graphene.List(ProductType)

    # Order queries
    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.Int(required=True))
    
    # Cart query
    cart = graphene.Field(CartType)
    
    # Reviews queries
    product_reviews = graphene.List(ProductReviewType, product_id=graphene.Int(required=True))

    @login_required
    def resolve_products(self, info):
        return Product.objects.all()

    @login_required
    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)

    @login_required
    def resolve_orders(self, info):
        user = info.context.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @login_required
    def resolve_order(self, info, id):
        user = info.context.user
        order = Order.objects.get(pk=id)
        if user.is_staff or order.user == user:
            return order
        raise PermissionDenied("You don't have permission to view this order")

    @login_required
    def resolve_cart(self, info):
        return Cart.objects.get(user=info.context.user)

    @login_required
    def resolve_product_reviews(self, info, product_id):
        return ProductReview.objects.filter(product_id=product_id)

    def resolve_all_products(root, info):
        return Product.objects.all()

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, input):
        if not info.context.user.is_staff:
            raise PermissionDenied("Only staff members can create products")
        
        product = Product.objects.create(
            name=input.name,
            description=input.description,
            price=input.price,
            stock=input.stock
        )
        return CreateProduct(product=product)

class CreateReviewInput(graphene.InputObjectType):
    product_id = graphene.Int(required=True)
    rating = graphene.Int(required=True)
    comment = graphene.String(required=True)

class CreateReview(graphene.Mutation):
    class Arguments:
        input = CreateReviewInput(required=True)

    review = graphene.Field(ProductReviewType)

    @login_required
    def mutate(self, info, input):
        user = info.context.user
        product = Product.objects.get(pk=input.product_id)
        
        if ProductReview.objects.filter(user=user, product=product).exists():
            raise Exception("You have already reviewed this product")
        
        review = ProductReview.objects.create(
            user=user,
            product=product,
            rating=input.rating,
            comment=input.comment
        )
        return CreateReview(review=review)

class AddToCartInput(graphene.InputObjectType):
    product_id = graphene.Int(required=True)
    quantity = graphene.Int(required=True)

class AddToCart(graphene.Mutation):
    class Arguments:
        input = AddToCartInput(required=True)

    cart = graphene.Field(CartType)

    @login_required
    def mutate(self, info, input):
        user = info.context.user
        cart = Cart.objects.get(user=user)
        product = Product.objects.get(pk=input.product_id)
        
        if product.stock < input.quantity:
            raise Exception("Insufficient stock")
        
        cart_item, created = cart.items.get_or_create(
            product=product,
            defaults={'quantity': input.quantity}
        )
        
        if not created:
            cart_item.quantity += input.quantity
            cart_item.save()
        
        return AddToCart(cart=cart)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_review = CreateReview.Field()
    add_to_cart = AddToCart.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)