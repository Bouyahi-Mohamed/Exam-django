import requests
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
import json

class ApiClient:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api/v1'  # Updated to include v1
        self.token = None
        
    def login(self, email, password, on_success=None, on_error=None):
        """
        Authenticate user with email and password
        """
        url = f"{self.base_url}/users/login/"
        data = {
            'email': email,
            'password': password
        }
        
        def success_callback(request, result):
            self.token = result.get('access')  # Updated to match JWT token field
            if on_success:
                on_success(result)
                
        def error_callback(request, error):
            if on_error:
                on_error(error)
                
        UrlRequest(
            url,
            on_success=success_callback,
            on_error=error_callback,
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
    def register(self, email, password, on_success=None, on_error=None):
        """
        Register a new user
        """
        url = f"{self.base_url}/users/"
        data = {
            'email': email,
            'password': password
        }
        
        def success_callback(request, result):
            if on_success:
                on_success(result)
                
        def error_callback(request, error):
            if on_error:
                on_error(error)
                
        UrlRequest(
            url,
            on_success=success_callback,
            on_error=error_callback,
            req_body=json.dumps(data),
            req_headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
    def search_products(self, query, on_success=None, on_error=None):
        """
        Search for products, including AI-generated ones
        """
        url = f"{self.base_url}/products/search/?query={query}"
        
        def success_callback(request, result):
            if on_success:
                on_success(result)
                
        def error_callback(request, error):
            if on_error:
                on_error(error)
        
        headers = self.get_headers()
        
        UrlRequest(
            url,
            on_success=success_callback,
            on_error=error_callback,
            req_headers=headers,
            method='GET'
        )
        
    def get_headers(self):
        """
        Get headers with authentication token
        """
        headers = {
            'Content-Type': 'application/json'
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers 