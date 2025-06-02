# E-commerce Application with Django REST API and Kivy Mobile Client

This project consists of a Django REST API backend and a Kivy mobile client frontend, creating a complete e-commerce solution.

## Features

### Backend (Django REST API & GraphQL)
- User authentication with JWT tokens
- Product management with secure image handling
- Shopping cart functionality with real-time updates
- Order management system
- Review and rating system
- AI-powered product generation and descriptions (using OpenAI)
- Secure file upload with MIME type validation
- GraphQL API for flexible data querying
- REST API endpoints for mobile client
- Celery task queue for background processing
- Redis caching for improved performance
- Comprehensive test coverage with pytest

### Mobile Client (Kivy)
- Modern Material Design UI with KivyMD
- Secure user authentication
- Product browsing with image caching
- Shopping cart management
- Product reviews and ratings
- Search functionality with AI suggestions
- Responsive layout with card-based design
- Offline support for basic functionality

## Project Structure
```
project/
├── api/                            # Backend API application
│   ├── migrations/                 # Database migrations
│   ├── __init__.py
│   ├── admin.py                   # Django admin configuration
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Database models
│   ├── serializers.py             # DRF serializers
│   ├── schema.py                  # GraphQL schema
│   ├── tasks.py                   # Celery tasks
│   ├── tests.py                   # Unit tests
│   ├── urls.py                    # API URL routing
│   └── views.py                   # API views and viewsets
│
├── mobile_client/                  # Kivy mobile application
│   ├── screens/                   # Application screens
│   ├── widgets/                   # Custom UI widgets
│   ├── utils/                     # Utility functions
│   ├── __init__.py
│   └── main.py                    # Main application entry
│
├── mobile_app/                     # Django project settings
│   ├── __init__.py
│   ├── asgi.py                    # ASGI configuration
│   ├── celery.py                  # Celery configuration
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Main URL routing
│   └── wsgi.py                    # WSGI configuration
│
├── media/                         # User uploaded files
│   └── products/                  # Product images
│
├── static/                        # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                     # HTML templates
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── LICENSE                       # Project license
├── README.md                     # Project documentation
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Pytest configuration
```

## Prerequisites

- Python 3.12+
- Redis (for Celery task queue and caching)
- OpenAI API key (for AI features)
- Virtual environment (recommended)
- For Windows users: Microsoft Visual C++ Build Tools

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bouyahi-Mohamed/Exam-django.git
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
```env
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///db.sqlite3
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

5. Initialize the database:
```bash
python manage.py makemigrations
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
celery -A mobile_app worker -l info
```

3. Start Celery beat (for scheduled tasks):
```bash
celery -A mobile_app beat -l info
```

4. Run Django development server:
```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000`

### Mobile Client

1. Navigate to the mobile client directory:
```bash
cd mobile_client
```

2. Run the Kivy application:
```bash
python main.py
```

## Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest --cov=.
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Run flake8 for linting

## Security Features

- JWT token authentication
- MIME type validation for uploads
- Secure password handling
- Protected API endpoints
- Error handling and validation
- CORS configuration
- GraphQL query depth limiting
- Rate limiting
- File upload restrictions

## Deployment

### Production Settings

1. Update `.env` file with production settings:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

2. Set up static files:
```bash
python manage.py collectstatic
```

3. Use gunicorn for production:
```bash
gunicorn mobile_app.wsgi:application
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure tests pass and coverage is maintained
5. Submit a Pull Request



## Acknowledgments

- Django REST Framework
- Kivy and KivyMD
- OpenAI
- GraphQL
- All other open-source contributors 