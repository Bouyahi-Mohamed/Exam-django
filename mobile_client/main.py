from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, TwoLineIconListItem, IconLeftWidget, ThreeLineIconListItem, OneLineListItem, ThreeLineAvatarListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime
import requests
import json
import os
import mimetypes
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.toast import toast
from api_client import ApiClient
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.icon_definitions import md_icons
from kivy.uix.widget import Widget  # For creating a simple separator
from kivy.uix.image import AsyncImage

# Custom separator widget
class Separator(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        self.background_color = [0.5, 0.5, 0.5, 1]  # Gray color

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        # Main layout with center alignment
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[20, 40, 20, 20],  # More padding at top
            spacing=20
        )
        
        # Content layout for centering
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=None,
            height=dp(600),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Add image
        image_container = RelativeLayout(
            size_hint=(1, None),
            height=200
        )
        
        # Image
        logo = Image(
            source='/home/hamaboxseur/Downloads/2.png',
            size_hint=(None, None),
            size=(200, 200),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        image_container.add_widget(logo)
        
        # Add container to content layout
        content_layout.add_widget(image_container)
        
        # Title
        title = MDLabel(
            text="Connexion",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Form layout
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        # Login form
        self.username_input = MDTextField(
            hint_text="Nom d'utilisateur",
            helper_text="Entrez votre nom d'utilisateur",
            helper_text_mode="on_error",
            size_hint_x=1,
            pos_hint={'center_x': 0.5}
        )
        
        self.password_input = MDTextField(
            hint_text="Mot de passe",
            helper_text="Entrez votre mot de passe",
            helper_text_mode="on_error",
            password=True,
            size_hint_x=1,
            pos_hint={'center_x': 0.5}
        )
        
        # Buttons layout
        buttons_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )
        
        # Login button
        login_button = MDRaisedButton(
            text="Se connecter",
            size_hint_x=1,
            height=dp(50),
            pos_hint={'center_x': 0.5},
            md_bg_color=self.theme_cls.primary_color,
            elevation=2,
            font_size='18sp'
        )
        login_button.bind(on_release=self.login)
        
        # Register button
        register_button = MDFlatButton(
            text="Pas encore inscrit ? Créer un compte",
            size_hint_x=1,
            pos_hint={'center_x': 0.5},
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color
        )
        register_button.bind(on_release=self.go_to_register)
        
        # Add widgets to form layout
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.password_input)
        
        # Add widgets to buttons layout
        buttons_layout.add_widget(login_button)
        buttons_layout.add_widget(register_button)
        
        # Add all widgets to content layout
        content_layout.add_widget(title)
        content_layout.add_widget(form_layout)
        content_layout.add_widget(buttons_layout)
        
        # Add content layout to main layout
        main_layout.add_widget(content_layout)
        
        self.add_widget(main_layout)
    
    def login(self, instance):
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/users/login/",
                json={
                    'username': self.username_input.text,
                    'password': self.password_input.text
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.parent.token = data['access']
                self.parent.username = self.username_input.text
                self.parent.is_admin = data.get('is_admin', False)
                self.parent.current = 'shop'
            else:
                self.show_error_dialog("Échec de la connexion", "Nom d'utilisateur ou mot de passe incorrect.")
        
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))
    
    def go_to_register(self, instance):
        self.parent.current = 'register'
    
    def show_error_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Title
        title = MDLabel(
            text="Inscription",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=50
        )
        
        # Form fields
        self.username_input = MDTextField(
            hint_text="Nom d'utilisateur",
            helper_text="Choisissez un nom d'utilisateur",
            helper_text_mode="on_error",
        )
        
        self.email_input = MDTextField(
            hint_text="Email",
            helper_text="Entrez votre adresse email",
            helper_text_mode="on_error",
        )
        
        self.password_input = MDTextField(
            hint_text="Mot de passe",
            helper_text="Choisissez un mot de passe",
            helper_text_mode="on_error",
            password=True
        )
        
        self.confirm_password_input = MDTextField(
            hint_text="Confirmer le mot de passe",
            helper_text="Confirmez votre mot de passe",
            helper_text_mode="on_error",
            password=True
        )
        
        # Register button
        register_button = MDRaisedButton(
            text="S'inscrire",
            size_hint_x=None,
            width=200,
            pos_hint={'center_x': 0.5}
        )
        register_button.bind(on_release=self.register)
        
        # Login link
        login_button = MDFlatButton(
            text="Déjà inscrit ? Se connecter",
            size_hint_x=None,
            width=200,
            pos_hint={'center_x': 0.5}
        )
        login_button.bind(on_release=self.go_to_login)
        
        # Add widgets to layout
        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.confirm_password_input)
        layout.add_widget(register_button)
        layout.add_widget(login_button)
        
        self.add_widget(layout)
    
    def register(self, instance):
        # Validation
        if not self.username_input.text:
            self.show_error_dialog("Erreur", "Le nom d'utilisateur est requis")
            return
        
        if not self.email_input.text:
            self.show_error_dialog("Erreur", "L'email est requis")
            return
        
        if not self.password_input.text:
            self.show_error_dialog("Erreur", "Le mot de passe est requis")
            return
        
        if self.password_input.text != self.confirm_password_input.text:
            self.show_error_dialog("Erreur", "Les mots de passe ne correspondent pas")
            return
        
        # Send registration request
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/users/register/",
                json={
                    'username': self.username_input.text,
                    'email': self.email_input.text,
                    'password': self.password_input.text
                }
            )
            
            if response.status_code == 201:
                self.show_success_dialog(
                    "Succès",
                    "Inscription réussie ! Vous pouvez maintenant vous connecter.",
                    self.go_to_login
                )
            else:
                error_msg = "Une erreur est survenue"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = "\n".join([
                            f"{k}: {', '.join(v)}" for k, v in error_data.items()
                        ])
                except:
                    pass
                self.show_error_dialog("Erreur", error_msg)
        
        except requests.exceptions.RequestException as e:
            self.show_error_dialog("Erreur de connexion", str(e))
    
    def go_to_login(self, *args):
        self.parent.current = 'login'
    
    def show_error_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_success_dialog(self, title, text, callback):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: (dialog.dismiss(), callback())
                )
            ]
        )
        dialog.open()

class ProductForm(BoxLayout):
    def __init__(self, product=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [20, 20, 20, 20]
        self.size_hint_y = None
        self.height = dp(500)  # Hauteur fixe pour le formulaire
        
        # Initialiser le gestionnaire de fichiers
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        
        # Titre du formulaire
        title = MDLabel(
            text="Ajouter un produit" if not product else "Modifier le produit",
            halign="center",
            theme_text_color="Primary",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        )
        
        # Scroll pour les champs
        scroll = ScrollView(
            size_hint=(1, None),
            height=dp(400)
        )
        
        # Conteneur pour les champs
        fields_container = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            padding=[0, 10, 0, 10]
        )
        fields_container.bind(minimum_height=fields_container.setter('height'))
        
        # Nom du produit
        self.name_input = MDTextField(
            hint_text="Nom du produit",
            text=product.get('name', '') if product else "",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        
        # Description
        self.description_input = MDTextField(
            hint_text="Description",
            text=product.get('description', '') if product else "",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(96)
        )
        
        # Prix
        self.price_input = MDTextField(
            hint_text="Prix",
            text=str(product.get('price', '')) if product else "",
            input_filter="float",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        
        # Stock
        self.stock_input = MDTextField(
            hint_text="Stock disponible",
            text=str(product.get('stock', '0')) if product else "0",
            input_filter="int",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        
        # Image
        image_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=10
        )
        
        self.image_url_input = MDTextField(
            hint_text="Chemin de l'image",
            text=product.get('image_url', '') if product else "",
            mode="rectangle",
            size_hint_x=0.7,
            readonly=True
        )
        
        upload_button = MDRaisedButton(
            text="Choisir",
            size_hint_x=0.3,
            on_release=self.show_file_manager
        )
        
        image_container.add_widget(self.image_url_input)
        image_container.add_widget(upload_button)
        
        # Ajouter les champs au conteneur
        fields_container.add_widget(self.name_input)
        fields_container.add_widget(MDLabel(size_hint_y=None, height=dp(10)))  # Espacement
        fields_container.add_widget(self.description_input)
        fields_container.add_widget(MDLabel(size_hint_y=None, height=dp(10)))  # Espacement
        fields_container.add_widget(self.price_input)
        fields_container.add_widget(MDLabel(size_hint_y=None, height=dp(10)))  # Espacement
        fields_container.add_widget(self.stock_input)
        fields_container.add_widget(MDLabel(size_hint_y=None, height=dp(10)))  # Espacement
        fields_container.add_widget(image_container)
        
        # Mettre le conteneur dans le scroll
        scroll.add_widget(fields_container)
        
        # Ajouter tous les widgets au formulaire
        self.add_widget(title)
        self.add_widget(scroll)
    
    def show_file_manager(self, instance):
        self.file_manager.show(os.path.expanduser("~"))  # Commencer dans le dossier utilisateur
    
    def select_path(self, path):
        self.image_url_input.text = path
        self.exit_manager()
    
    def exit_manager(self, *args):
        self.file_manager.close()

class ShopScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'shop'
        self.products = []
        self.cart = None
        self.cart_dialog = None
        self.api_client = ApiClient()
        
        # Create main layout
        layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Add top toolbar with buttons
        toolbar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10,
            padding=[0, 0, 10, 0]  # Right padding for the last button
        )
        
        # Add Product button (for admin)
        self.add_product_button = MDRaisedButton(
            text="Add Product",
            size_hint_x=None,
            width=150,
            opacity=0  # Initially hidden
        )
        self.add_product_button.bind(on_release=self.show_product_form)
        
        # Cart button
        self.cart_button = MDRaisedButton(
            text="Cart",
            size_hint_x=None,
            width=100,
            opacity=0  # Initially hidden
        )
        self.cart_button.bind(on_release=self.show_cart)
        
        # Logout button
        logout_button = MDRaisedButton(
            text="Logout",
            size_hint_x=None,
            width=100
        )
        logout_button.bind(on_release=self.logout)
        
        # Add buttons to toolbar
        toolbar.add_widget(self.add_product_button)
        toolbar.add_widget(self.cart_button)
        toolbar.add_widget(logout_button)
        
        # Add search bar
        search_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        self.search_field = MDTextField(
            hint_text="Search products...",
            helper_text="Type to search, AI will create if not found",
            helper_text_mode="on_focus",
            size_hint_x=0.8
        )
        self.search_field.bind(on_text_submit=self.search_products)
        
        search_button = MDRaisedButton(
            text="Search",
            size_hint_x=0.2,
            on_release=lambda x: self.search_products(None)
        )
        
        search_box.add_widget(self.search_field)
        search_box.add_widget(search_button)
        
        # Add products list
        self.products_list = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.products_list)
        
        # Add loading indicator
        self.loading = MDSpinner(
            size_hint=(None, None),
            size=(46, 46),
            pos_hint={'center_x': .5, 'center_y': .5},
            active=False
        )
        
        # Add widgets to layout
        layout.add_widget(toolbar)  # Add toolbar first
        layout.add_widget(search_box)
        layout.add_widget(scroll)
        layout.add_widget(self.loading)
        
        self.add_widget(layout)
        
        # Load initial products
        self.load_products()
    
    def search_products(self, instance):
        query = self.search_field.text
        self.loading.active = True
        self.products_list.clear_widgets()
        
        try:
            response = requests.get(
                f"http://localhost:8000/api/v1/products/search/?query={query}",
                headers={'Authorization': f'Bearer {self.parent.token}'}
            )
            
            print(f"Search Response Status: {response.status_code}")
            print(f"Search Response: {response.text}")
            
            if response.status_code == 200:
                products = response.json()
                self.display_products(products)
            else:
                toast(f"Error searching products: {response.status_code}")
                
        except Exception as e:
            print(f"Search error: {str(e)}")
            toast(f"Error: {str(e)}")
        finally:
            self.loading.active = False
    
    def load_products(self):
        """Load all products"""
        self.loading.active = True
        self.products_list.clear_widgets()
        
        try:
            # Check if token exists
            if not self.parent or not self.parent.token:
                print("No authentication token available")
                self.products_list.add_widget(OneLineListItem(
                    text="Please log in to view products"
                ))
                return
                
            response = requests.get(
                "http://localhost:8000/api/v1/products/",
                headers={'Authorization': f'Bearer {self.parent.token}'}
            )
            
            print(f"Load Products Response Status: {response.status_code}")
            print(f"Load Products Response: {response.text}")
            
            if response.status_code == 200:
                products = response.json()
                self.display_products(products)
            else:
                toast(f"Error loading products: {response.status_code}")
                
        except Exception as e:
            print(f"Load error: {str(e)}")
            toast(f"Error: {str(e)}")
        finally:
            self.loading.active = False
    
    def display_products(self, products):
        """Display products in the list"""
        self.products_list.clear_widgets()
        
        print(f"Displaying {len(products) if products else 0} products")
        
        if not products:
            no_products = OneLineListItem(
                text="No products found"
            )
            self.products_list.add_widget(no_products)
            return
        
        # Add initial spacing
        self.products_list.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(10)
            )
        )
        
        for product in products:
            print(f"Adding product: {product['name']}")
            
            # Create a custom item layout
            item = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(120),
                padding=dp(10),
                spacing=dp(10)
            )
            
            # Image container
            image_container = RelativeLayout(
                size_hint=(None, None),
                size=(dp(100), dp(100))
            )
            
            # Product image
            if product.get('absolute_image_url'):
                product_image = AsyncImage(
                    source=product['absolute_image_url'],
                    size_hint=(1, 1),  # Updated from allow_stretch and keep_ratio
                    pos_hint={'center_x': .5, 'center_y': .5}
                )
            else:
                # Placeholder image
                product_image = MDIconButton(
                    icon="image-off",
                    pos_hint={'center_x': .5, 'center_y': .5},
                    size_hint=(None, None),
                    size=(dp(100), dp(100))
                )
            
            image_container.add_widget(product_image)
            item.add_widget(image_container)
            
            # Product details container
            details = MDBoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5)
            )
            
            # Product name
            details.add_widget(MDLabel(
                text=product['name'],
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            ))
            
            # Product price
            details.add_widget(MDLabel(
                text=f"Prix: {product['price']} TND",
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(20)
            ))
            
            # Product description (truncated)
            description = product.get('description', '')[:50]
            if len(product.get('description', '')) > 50:
                description += "..."
            
            details.add_widget(MDLabel(
                text=description,
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(20)
            ))
            
            item.add_widget(details)
            
            # Create card container with padding
            card_container = MDBoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(140),
                padding=dp(10)
            )
            
            # Make the item clickable
            clickable_item = MDCard(
                orientation='vertical',
                size_hint=(0.9, None),
                height=dp(120),
                elevation=1,
                pos_hint={'center_x': 0.5},
                radius=[dp(10)]  # Adding rounded corners
            )
            clickable_item.add_widget(item)
            clickable_item.bind(on_release=lambda x, p=product: self.show_product_dialog(p))
            
            # Add card to container
            card_container.add_widget(clickable_item)
            
            # Add the container to the list
            self.products_list.add_widget(card_container)
        
        # Add final spacing
        self.products_list.add_widget(
            Widget(
                size_hint_y=None,
                height=dp(10)
            )
        )
        
        print("Finished displaying products")
    
    def on_enter(self):
        self.load_products()
        # Only load cart and show cart button for non-admin users
        if not self.parent.is_admin:
            self.load_cart()
            self.cart_button.opacity = 1
        else:
            self.cart_button.opacity = 0
        self.add_product_button.opacity = 1 if self.parent.is_admin else 0
        self.add_product_button.disabled = not self.parent.is_admin
    
    def load_cart(self):
        try:
            # Check if token exists
            if not self.parent or not self.parent.token:
                print("No authentication token available")
                self.cart = None
                return
                
            response = requests.get(
                "http://localhost:8000/api/v1/carts/",
                headers={'Authorization': f'Bearer {self.parent.token}'}
            )
            
            if response.status_code == 200:
                carts = response.json()
                self.cart = carts[0] if carts else None
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))
    
    def show_product_dialog(self, product):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=dp(400),
            padding=dp(20)
        )
        
        # Product details
        details = MDBoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=dp(100)
        )
        
        details.add_widget(MDLabel(
            text=f"Prix: {product['price']} TND",
            theme_text_color="Primary"
        ))
        
        if product.get('average_rating') is not None:
            details.add_widget(MDLabel(
                text=f"Note moyenne: {product['average_rating']:.1f}/5",
                theme_text_color="Primary"
            ))
        
        details.add_widget(MDLabel(
            text=product.get('description', ''),
            theme_text_color="Secondary"
        ))
        
        content.add_widget(details)
        
        # Reviews section
        reviews_label = MDLabel(
            text="Avis des clients",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(reviews_label)
        
        # Reviews list in a scroll view
        scroll = ScrollView(
            size_hint=(1, None),
            height=dp(200)
        )
        reviews_list = MDList()
        
        if product.get('reviews'):
            for review in product['reviews']:
                review_item = ThreeLineIconListItem(
                    text=f"{review['user_username']} - {review['rating']}/5",
                    secondary_text=review['comment'],
                    tertiary_text=review['created_at'][:10]  # Show only the date
                )
                reviews_list.add_widget(review_item)
        else:
            reviews_list.add_widget(
                OneLineListItem(
                    text="Aucun avis pour le moment"
                )
            )
        
        scroll.add_widget(reviews_list)
        content.add_widget(scroll)
        
        buttons = [
            MDFlatButton(
                text="Annuler",
                on_release=lambda x: dialog.dismiss()
            )
        ]
        
        if self.parent.is_admin:
            buttons.extend([
                MDRaisedButton(
                    text="Modifier",
                    on_release=lambda x: self.show_product_form(None, product)
                ),
                MDRaisedButton(
                    text="Supprimer",
                    on_release=lambda x: self.delete_product(product, dialog)
                )
            ])
        else:
            buttons.extend([
                MDRaisedButton(
                    text="Ajouter au panier",
                    on_release=lambda x: self.add_to_cart(product, dialog)
                ),
                MDRaisedButton(
                    text="Ajouter un avis",
                    on_release=lambda x: self.show_review_form(product, dialog)
                )
            ])
        
        dialog = MDDialog(
            title=product['name'],
            type="custom",
            content_cls=content,
            buttons=buttons,
            size_hint=(0.9, None)
        )
        dialog.open()
    
    def show_review_form(self, product, parent_dialog):
        parent_dialog.dismiss()
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=dp(200),
            padding=dp(20)
        )
        
        # Rating selection using buttons
        rating_label = MDLabel(
            text="Note:",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(30)
        )
        
        rating_box = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=dp(50)
        )
        
        self.selected_rating = 5  # Default rating
        
        for i in range(1, 6):
            rating_btn = MDRaisedButton(
                text=str(i),
                size_hint_x=1/5,
                md_bg_color=self.theme_cls.primary_color if i == 5 else self.theme_cls.primary_light
            )
            rating_btn.rating = i
            rating_btn.bind(on_release=lambda x: self.select_rating(x.rating, rating_box))
            rating_box.add_widget(rating_btn)
        
        # Comment field
        comment_field = MDTextField(
            hint_text="Votre commentaire",
            multiline=True,
            max_height=dp(100)
        )
        
        content.add_widget(rating_label)
        content.add_widget(rating_box)
        content.add_widget(comment_field)
        
        dialog = MDDialog(
            title=f"Ajouter un avis pour {product['name']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Envoyer",
                    on_release=lambda x: self.submit_review(
                        product,
                        self.selected_rating,
                        comment_field.text,
                        dialog
                    )
                )
            ]
        )
        dialog.open()
    
    def select_rating(self, rating, rating_box):
        self.selected_rating = rating
        for child in rating_box.children:
            if isinstance(child, MDRaisedButton):
                child.md_bg_color = (
                    self.theme_cls.primary_color 
                    if child.rating == rating 
                    else self.theme_cls.primary_light
                )
    
    def submit_review(self, product, rating, comment, dialog):
        if not comment.strip():
            toast("Le commentaire est requis")
            return
        
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/products/{product['id']}/review/",
                headers={'Authorization': f'Bearer {self.parent.token}'},
                json={
                    'rating': rating,
                    'comment': comment
                }
            )
            
            if response.status_code == 201:
                dialog.dismiss()
                self.load_products()  # Refresh products to show updated reviews
                toast("Avis ajouté avec succès")
            else:
                error_msg = "Une erreur est survenue"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = error_data.get('error', error_msg)
                except:
                    pass
                toast(error_msg)
        except Exception as e:
            toast(f"Erreur: {str(e)}")
    
    def show_product_form(self, instance, product=None):
        form = ProductForm(product)
        
        dialog = MDDialog(
            title="Modifier le produit" if product else "Ajouter un produit",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Enregistrer",
                    on_release=lambda x: self.save_product(form, product, dialog)
                )
            ]
        )
        dialog.open()
    
    def save_product(self, form, product, dialog):
        # Validation des champs requis
        if not form.name_input.text.strip():
            self.show_error_dialog("Erreur", "Le nom du produit est requis")
            return
            
        try:
            price = float(form.price_input.text or 0)
            if price <= 0:
                self.show_error_dialog("Erreur", "Le prix doit être supérieur à 0")
                return
        except ValueError:
            self.show_error_dialog("Erreur", "Le prix doit être un nombre valide")
            return
            
        try:
            stock = int(form.stock_input.text or 0)
            if stock < 0:
                self.show_error_dialog("Erreur", "Le stock ne peut pas être négatif")
                return
        except ValueError:
            self.show_error_dialog("Erreur", "Le stock doit être un nombre entier")
            return
        
        # Préparer les données du produit
        data = {
            'name': form.name_input.text.strip(),
            'description': form.description_input.text.strip(),
            'price': price,
            'stock': stock,
        }
        
        # Gérer l'upload de l'image si un fichier est sélectionné
        image_path = form.image_url_input.text
        files = None
        if image_path and os.path.isfile(image_path):
            ext = os.path.splitext(image_path)[1].lower()
            allowed_exts = ['.jpg', '.jpeg', '.png', '.gif']
            if ext not in allowed_exts:
                self.show_error_dialog("Erreur", "Type de fichier non supporté. Utilisez JPG, PNG ou GIF")
                return

            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                self.show_error_dialog("Erreur", "Le fichier sélectionné n'est pas une image valide.")
                return

            try:
                # Vérifier la taille et le type du fichier
                file_size = os.path.getsize(image_path)
                file_name = os.path.basename(image_path)
                print(f"Tentative d'upload du fichier: {file_name}, taille: {file_size} bytes")
                
                # Ouvrir et préparer le fichier pour l'upload
                files = {'image': open(image_path, 'rb')}
            except Exception as e:
                error_msg = f"Erreur lors de la préparation de l'image:\n{str(e)}"
                print(error_msg)
                self.show_error_dialog("Erreur", error_msg)
                return
        
        try:
            headers = {'Authorization': f'Bearer {self.parent.token}'}
            # Remove Content-Type header to let requests set it correctly for multipart
            if 'Content-Type' in headers:
                del headers['Content-Type']
            
            if product:
                # Update existing product
                response = requests.put(
                    f"http://localhost:8000/api/v1/products/{product['id']}/",
                    data=data,
                    files=files,
                    headers=headers
                )
            else:
                # Create new product
                response = requests.post(
                    "http://localhost:8000/api/v1/products/",
                    data=data,
                    files=files,
                    headers=headers
                )
            
            # Clean up file handles
            if files:
                files['image'].close()
            
            if response.status_code in [200, 201]:
                dialog.dismiss()
                self.load_products()
                self.show_success_dialog(
                    "Succès",
                    "Produit modifié avec succès" if product else "Produit ajouté avec succès"
                )
            else:
                error_msg = "Une erreur est survenue"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = "\n".join([
                            f"{k}: {', '.join(v)}" for k, v in error_data.items()
                        ])
                except:
                    pass
                self.show_error_dialog("Erreur", error_msg)
        except requests.exceptions.RequestException as e:
            self.show_error_dialog("Erreur de connexion", str(e))
        finally:
            # Ensure file handles are closed
            if files:
                files['image'].close()
    
    def delete_product(self, product, dialog):
        confirm_dialog = MDDialog(
            title="Confirmer la suppression",
            text=f"Êtes-vous sûr de vouloir supprimer le produit '{product['name']}' ?",
            buttons=[
                MDFlatButton(
                    text="Annuler",
                    on_release=lambda x: confirm_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Supprimer",
                    on_release=lambda x: self._perform_delete(product, dialog, confirm_dialog)
                )
            ]
        )
        confirm_dialog.open()
    
    def _perform_delete(self, product, product_dialog, confirm_dialog):
        try:
            response = requests.delete(
                f"http://localhost:8000/api/v1/products/{product['id']}/",
                headers={'Authorization': f'Bearer {self.parent.token}'}
            )
            
            confirm_dialog.dismiss()
            
            if response.status_code == 204:
                product_dialog.dismiss()
                self.load_products()
                self.show_success_dialog(
                    "Succès",
                    "Le produit a été supprimé avec succès"
                )
            else:
                try:
                    error_data = response.json()
                    error_title = error_data.get('error', 'Erreur de suppression')
                    error_detail = error_data.get('detail', 'Impossible de supprimer le produit')
                    
                    # Show error dialog with both title and detailed message
                    error_dialog = MDDialog(
                        title=error_title,
                        text=error_detail,
                        buttons=[
                            MDFlatButton(
                                text="OK",
                                on_release=lambda x: error_dialog.dismiss()
                            )
                        ]
                    )
                    error_dialog.open()
                except ValueError:
                    self.show_error_dialog(
                        "Erreur",
                        "Une erreur est survenue lors de la suppression du produit"
                    )
        except Exception as e:
            self.show_error_dialog(
                "Erreur de connexion",
                f"Impossible de contacter le serveur: {str(e)}"
            )
    
    def add_to_cart(self, product, dialog):
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/carts/{self.cart['id']}/add_item/",
                headers={'Authorization': f'Bearer {self.parent.token}'},
                json={
                    'product': product['id'],
                    'quantity': 1
                }
            )
            
            if response.status_code == 200:
                dialog.dismiss()
                self.load_cart()
                self.show_success_dialog("Succès", "Produit ajouté au panier")
            else:
                self.show_error_dialog("Erreur", "Impossible d'ajouter au panier")
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))
    
    def show_cart(self, instance):
        if not self.cart or not self.cart['items']:
            self.show_empty_cart_message()
            return
        
        # Create dialog content
        content = self.create_cart_content()
        
        # Create and show dialog
        self.cart_dialog = MDDialog(
            title="Votre Panier",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="Fermer",
                    on_release=lambda x: self.cart_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Commander",
                    on_release=self.checkout
                )
            ]
        )
        self.cart_dialog.open()

    def show_empty_cart_message(self):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            adaptive_height=True
        )
        
        # Empty cart icon
        icon = MDIconButton(
            icon="cart-off",
            theme_icon_color="Secondary",
            pos_hint={'center_x': 0.5},
            icon_size=dp(64)
        )
        
        # Empty cart message
        message = MDLabel(
            text="Votre panier est vide",
            theme_text_color="Secondary",
            font_style="H5",
            halign="center"
        )
        
        # Continue shopping button
        continue_button = MDRaisedButton(
            text="Continuer les achats",
            on_release=lambda x: self.dismiss_empty_cart_dialog(),
            pos_hint={'center_x': 0.5}
        )
        
        content.add_widget(icon)
        content.add_widget(message)
        content.add_widget(continue_button)
        
        self.cart_dialog = MDDialog(
            type="custom",
            content_cls=content,
        )
        self.cart_dialog.open()

    def dismiss_empty_cart_dialog(self):
        if self.cart_dialog:
            self.cart_dialog.dismiss()
            self.cart_dialog = None

    def remove_from_cart(self, item):
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/carts/{self.cart['id']}/remove_item/",
                headers={'Authorization': f'Bearer {self.parent.token}'},
                json={'item': item['id']}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.cart = data['cart']
                
                if data.get('is_empty', False):
                    # If cart is empty, show empty cart message
                    if self.cart_dialog:
                        self.cart_dialog.dismiss()
                    self.show_empty_cart_message()
                else:
                    # Refresh cart dialog with updated items
                    if self.cart_dialog:
                        self.cart_dialog.dismiss()
                    self.show_cart(None)
            else:
                self.show_error_dialog("Erreur", "Impossible de retirer l'article")
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))

    def update_cart_item(self, item, new_quantity):
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/carts/{self.cart['id']}/update_item/",
                headers={'Authorization': f'Bearer {self.parent.token}'},
                json={
                    'item': item['id'],
                    'quantity': new_quantity
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.cart = data['cart']
                
                if data.get('is_empty', False):
                    if self.cart_dialog:
                        self.cart_dialog.dismiss()
                    self.show_empty_cart_message()
                else:
                    if self.cart_dialog:
                        self.cart_dialog.dismiss()
                    self.show_cart(None)
            else:
                self.show_error_dialog("Erreur", "Impossible de mettre à jour la quantité")
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))

    def checkout(self, instance):
        try:
            response = requests.post(
                f"http://localhost:8000/api/v1/carts/{self.cart['id']}/checkout/",
                headers={'Authorization': f'Bearer {self.parent.token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if self.cart_dialog:
                    self.cart_dialog.dismiss()
                self.cart = None
                self.show_success_dialog(
                    "Succès",
                    "Votre commande a été créée avec succès"
                )
            else:
                self.show_error_dialog("Erreur", "Impossible de finaliser la commande")
        except Exception as e:
            self.show_error_dialog("Erreur", str(e))
    
    def logout(self, instance):
        # Réinitialiser les informations de l'utilisateur
        self.parent.token = None
        self.parent.username = None
        self.parent.is_admin = False
        # Retourner à l'écran de connexion
        self.parent.current = 'login'
        # Réinitialiser les champs de connexion
        login_screen = self.parent.get_screen('login')
        login_screen.username_input.text = ""
        login_screen.password_input.text = ""
    
    def show_error_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_success_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def create_cart_content(self):
        # Create a scrollable content layout
        scroll = ScrollView(size_hint=(1, None), height=dp(300))
        content = MDList(spacing=dp(10))
        
        # Header
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), 0, dp(10), 0],
            md_bg_color=self.theme_cls.primary_color[:-1] + [0.1]
        )
        
        header.add_widget(MDLabel(
            text="Produit",
            size_hint_x=0.4,
            bold=True
        ))
        header.add_widget(MDLabel(
            text="Quantité",
            size_hint_x=0.2,
            bold=True
        ))
        header.add_widget(MDLabel(
            text="Prix",
            size_hint_x=0.2,
            bold=True
        ))
        header.add_widget(MDLabel(
            text="",  # Space for delete button
            size_hint_x=0.2
        ))
        
        content.add_widget(header)
        content.add_widget(Separator())  # Add separator after header
        
        # Items
        for item in self.cart['items']:
            item_box = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                padding=[dp(10), 0, dp(10), 0]
            )
            
            # Product name
            item_box.add_widget(MDLabel(
                text=item['product_name'],
                size_hint_x=0.4,
                shorten=True,
                shorten_from='right'
            ))
            
            # Quantity with +/- buttons
            quantity_box = MDBoxLayout(
                orientation='horizontal',
                size_hint_x=0.2,
                spacing=dp(5)
            )
            
            minus_button = MDIconButton(
                icon="minus",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.primary_color,
                on_release=lambda x, i=item: self.update_cart_item(i, i['quantity'] - 1)
            )
            
            quantity_label = MDLabel(
                text=str(item['quantity']),
                halign='center'
            )
            
            plus_button = MDIconButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.primary_color,
                on_release=lambda x, i=item: self.update_cart_item(i, i['quantity'] + 1)
            )
            
            quantity_box.add_widget(minus_button)
            quantity_box.add_widget(quantity_label)
            quantity_box.add_widget(plus_button)
            item_box.add_widget(quantity_box)
            
            # Price
            price = float(item['quantity']) * float(item['product_price'])
            item_box.add_widget(MDLabel(
                text=f"{price:.2f} TND",
                size_hint_x=0.2,
                halign='right'
            ))
            
            # Delete button
            button_box = MDBoxLayout(
                size_hint_x=0.2,
                padding=[dp(10), dp(5), 0, dp(5)]
            )
            remove_button = MDIconButton(
                icon="delete",
                theme_icon_color="Custom",
                icon_color=self.theme_cls.error_color,
                on_release=lambda x, i=item: self.remove_from_cart(i)
            )
            button_box.add_widget(remove_button)
            item_box.add_widget(button_box)
            
            content.add_widget(item_box)
            content.add_widget(Separator())  # Add separator after each item
        
        scroll.add_widget(content)
        
        # Footer with total
        footer = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(10)
        )
        
        total_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        total_box.add_widget(MDLabel(
            text="Total:",
            bold=True,
            theme_text_color="Primary",
            size_hint_x=0.6
        ))
        
        total_box.add_widget(MDLabel(
            text=f"{float(self.cart['total']):.2f} TND",
            bold=True,
            theme_text_color="Primary",
            halign='right',
            size_hint_x=0.4
        ))
        
        footer.add_widget(total_box)
        
        # Main container
        main_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(400),
            spacing=dp(10),
            padding=[0, dp(10), 0, dp(10)]
        )
        
        main_box.add_widget(scroll)
        main_box.add_widget(footer)
        
        return main_box

class ShopApp(MDApp):
    def build(self):
        self.title = "Sesame Shop"  # Set application title
        self.theme_cls.primary_palette = "Blue"  # Main color
        self.theme_cls.accent_palette = "Amber"  # Secondary color
        self.theme_cls.theme_style = "Light"     # Light theme
        self.theme_cls.material_style = "M3"     # Material Design 3
        
        sm = MDScreenManager()
        sm.token = None
        sm.username = None
        sm.is_admin = False
        
        sm.add_widget(RegisterScreen())
        sm.add_widget(LoginScreen())
        sm.add_widget(ShopScreen())
        
        sm.current = 'login'  # Set LoginScreen as the first screen
        
        return sm

if __name__ == '__main__':
    ShopApp().run()

import requests
import os

def create_product(form, user_token):
    data = {
        'name': form.name_input.text.strip(),
        'description': form.description_input.text.strip(),
        'price': form.price_input.text.strip(),
        'stock': form.stock_input.text.strip(),
    }
    image_path = form.image_url_input.text.strip()
    headers = {'Authorization': f'Bearer {user_token}'}

    if image_path and os.path.isfile(image_path):
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            response = requests.post(
                "http://localhost:8000/api/v1/products/",
                data=data,
                files=files,
                headers=headers
            )
    else:
        response = requests.post(
            "http://localhost:8000/api/v1/products/",
            data=data,
            headers=headers
        )

    print("Status:", response.status_code)
    print("Response:", response.text)