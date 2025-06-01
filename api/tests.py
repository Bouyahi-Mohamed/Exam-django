from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Product, MobileUser
import os
import magic
from django.conf import settings

class ProductImageUploadTests(TestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = MobileUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Créer un client API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Créer un produit de test
        self.product = Product.objects.create(
            name='Test Product',
            price=99.99,
            stock=10
        )
        
        # Préparer le chemin pour les fichiers de test
        self.test_files_dir = os.path.join(settings.BASE_DIR, 'api', 'test_files')
        os.makedirs(self.test_files_dir, exist_ok=True)
        
        # URL de l'endpoint
        self.upload_url = '/api/v1/products/upload_image/'
        
        # Créer un fichier JPEG de test
        self.jpeg_content = b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0C\x14\r\x0C\x0B\x0B\x0C\x19\x12\x13\x0F\x14\x1D\x1A\x1F\x1E\x1D\x1A\x1C\x1C $.\' ",#\x1C\x1C(7),01444\x1F\'9=82<.342\xFF\xDB\x00C\x01\t\t\t\x0C\x0B\x0C\x18\r\r\x182!\x1C!22222222222222222222222222222222222222222222222222\xFF\xC0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0B\xFF\xC4\x00\xB5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xA1\x08#B\xB1\xC1\x15R\xD1\xF0$3br\x82\t\n\x16\x17\x18\x19\x1A%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFF\xC4\x00\x1F\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0B\xFF\xC4\x00\xB5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xA1\xB1\xC1\t#3R\xF0\x15br\xD1\n\x16$4\xE1%\xF1\x17\x18\x19\x1A&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9\xCA\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xF9\xFE\x8A(\xAF\xF4\x0C\xFF\x00\x1F\x0F\xFF\xD9'
        self.jpeg_path = os.path.join(self.test_files_dir, 'test.jpg')
        with open(self.jpeg_path, 'wb') as f:
            f.write(self.jpeg_content)
        
        # Créer un fichier PNG de test
        self.png_content = b'\x89PNG\r\n\x1A\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1F\x15\xC4\x89\x00\x00\x00\nIDATx\x9Cc\x00\x00\x00\x02\x00\x01\xE5\x27\xDE\xFC\x00\x00\x00\x00IEND\xAEB`\x82'
        self.png_path = os.path.join(self.test_files_dir, 'test.png')
        with open(self.png_path, 'wb') as f:
            f.write(self.png_content)
    
    def tearDown(self):
        # Nettoyer les fichiers de test
        if os.path.exists(self.test_files_dir):
            for file in os.listdir(self.test_files_dir):
                os.remove(os.path.join(self.test_files_dir, file))
            os.rmdir(self.test_files_dir)
    
    def test_upload_jpeg_success(self):
        """Test l'upload d'une image JPEG valide"""
        with open(self.jpeg_path, 'rb') as image_file:
            response = self.client.post(
                self.upload_url,
                {
                    'image': image_file,
                    'product_id': self.product.id
                },
                format='multipart'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('image_url', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Image téléchargée avec succès')
        
        # Vérifier que l'image a été sauvegardée
        self.product.refresh_from_db()
        self.assertTrue(self.product.image)
    
    def test_upload_png_success(self):
        """Test l'upload d'une image PNG valide"""
        with open(self.png_path, 'rb') as image_file:
            response = self.client.post(
                self.upload_url,
                {
                    'image': image_file,
                    'product_id': self.product.id
                },
                format='multipart'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('image_url', response.data)
    
    def test_upload_without_image(self):
        """Test la requête sans image"""
        response = self.client.post(
            self.upload_url,
            {'product_id': self.product.id},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Aucune image fournie')
    
    def test_upload_invalid_product_id(self):
        """Test l'upload avec un ID de produit invalide"""
        with open(self.jpeg_path, 'rb') as image_file:
            response = self.client.post(
                self.upload_url,
                {
                    'image': image_file,
                    'product_id': 99999  # ID inexistant
                },
                format='multipart'
            )
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Produit non trouvé')
    
    def test_upload_without_product_id(self):
        """Test l'upload sans ID de produit (création automatique)"""
        with open(self.jpeg_path, 'rb') as image_file:
            response = self.client.post(
                self.upload_url,
                {'image': image_file},
                format='multipart'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('product', response.data)
        self.assertIn('image_url', response.data)
    
    def test_upload_invalid_file_type(self):
        """Test l'upload d'un fichier non-image"""
        # Créer un faux fichier texte
        text_content = b'This is not an image'
        text_file = SimpleUploadedFile(
            'test.txt',
            text_content,
            content_type='text/plain'
        )
        
        response = self.client.post(
            self.upload_url,
            {
                'image': text_file,
                'product_id': self.product.id
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Type de fichier non autorisé')
    
    def test_upload_corrupted_image(self):
        """Test l'upload d'une image corrompue"""
        corrupted_content = b'Not a valid image content'
        corrupted_file = SimpleUploadedFile(
            'corrupted.jpg',
            corrupted_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(
            self.upload_url,
            {
                'image': corrupted_file,
                'product_id': self.product.id
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
