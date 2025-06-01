# E-commerce Application with Django REST API and Kivy Mobile Client

This project consists of a Django REST API backend and a Kivy mobile client frontend, creating a complete e-commerce solution.

## Features

### Backend (Django REST API & GraphQL)
- User authentication with JWT tokens
- Product management with image handling
- Shopping cart functionality
- Order management
- Review system
- AI-powered product generation (using OpenAI)
- Secure file upload with MIME type validation
- GraphQL API for flexible data querying
- REST API endpoints for mobile client

### Mobile Client (Kivy)
- Modern Material Design UI
- User authentication
- Product browsing with image display
- Shopping cart management
- Product reviews
- Search functionality with AI-powered product generation
- Responsive layout with card-based design

## Prerequisites

- Python 3.12+
- Redis (for Celery task queue)
- OpenAI API key (for AI product generation)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash or cmd
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
pipenv shell
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=your_openai_api_key
```

5. Initialize the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the Application

### Backend Server
1. Start Redis server:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A project worker -l info
```

3. Run Django development server:
```bash
python manage.py runserver
```

### Mobile Client
1. Navigate to the mobile client directory:
```bash
cd mobile_client
```

2. Run the Kivy application:
```bash
python main.py
```

## API Documentation

### GraphQL API
Access the GraphQL playground at `/graphql/` when the server is running.

#### Example Queries:
```graphql
# Get all products with reviews
query {
  products {
    id
    name
    price
    description
    imageUrl
    averageRating
    reviews {
      rating
      comment
      user {
        username
      }
    }
  }
}

# Create a new product (admin only)
mutation {
  createProduct(input: {
    name: "New Product"
    price: 99.99
    description: "Product description"
    stock: 10
  }) {
    product {
      id
      name
      price
    }
  }
}

# Add product review
mutation {
  createReview(input: {
    productId: 1
    rating: 5
    comment: "Great product!"
  }) {
    review {
      id
      rating
      comment
    }
  }
}

# Add to cart
mutation {
  addToCart(input: {
    productId: 1
    quantity: 2
  }) {
    cart {
      total
      items {
        product {
          name
        }
        quantity
      }
    }
  }
}
```

### REST API Endpoints

#### Authentication
- POST `/api/v1/users/register/`: Register new user
- POST `/api/v1/users/login/`: Login user

#### Products
- GET `/api/v1/products/`: List all products
- POST `/api/v1/products/`: Create new product
- GET `/api/v1/products/{id}/`: Get product details
- PUT `/api/v1/products/{id}/`: Update product
- DELETE `/api/v1/products/{id}/`: Delete product
- POST `/api/v1/products/{id}/review/`: Add product review
- GET `/api/v1/products/search/`: Search products

#### Cart
- GET `/api/v1/carts/`: Get user's cart
- POST `/api/v1/carts/{id}/add_item/`: Add item to cart
- POST `/api/v1/carts/{id}/remove_item/`: Remove item from cart
- POST `/api/v1/carts/{id}/update_item/`: Update cart item
- POST `/api/v1/carts/{id}/checkout/`: Checkout cart

## Mobile Client Features

### User Interface
- Material Design components
- Responsive card layout
- Image handling with placeholders
- Search functionality
- Shopping cart management
- Product reviews

### Authentication
- User registration
- Login/logout functionality
- Token-based authentication

## Development

### Backend Development
- Django REST framework for API
- GraphQL with Graphene-Django
- JWT authentication
- Celery for asynchronous tasks
- OpenAI integration for product generation
- Secure file handling with python-magic

### Mobile Client Development
- KivyMD for Material Design
- Asynchronous image loading
- State management
- Error handling
- User feedback with toast messages

## Security Features

- JWT token authentication
- MIME type validation for uploads
- Secure password handling
- Protected API endpoints
- Error handling and validation
- CORS configuration
- GraphQL query depth limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 