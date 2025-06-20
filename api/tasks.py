import openai
from django.conf import settings
from .models import Product
from celery import shared_task
import json
import time

openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

@shared_task
def generate_product_with_ai(prompt="Génère un produit e-commerce réaliste au format JSON."):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant qui génère des produits e-commerce réalistes au format JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content)
        product = Product.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            price=data.get("price", 10.0),
            stock=data.get("stock", 10),
            is_ai_generated=True,
            ai_source="openai-gpt-3.5-turbo"
        )
        return product.id

    except openai.OpenAIError as e:
        # Gestion spécifique des erreurs OpenAI
        if hasattr(e, 'status_code') and e.status_code == 429:
            print("Erreur OpenAI : quota dépassé (429).")
        else:
            print(f"Erreur OpenAI : {e}")
        return None
    except Exception as e:
        print("Erreur parsing ou création produit IA :", e)
        return None

def generate_product_image(prompt):
    try:
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers={
                'Authorization': f'Bearer {settings.OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'n': 1,
                'size': '1024x1024',
                'response_format': 'url'
            }
        )
        
        response.raise_for_status()
        return response.json()['data'][0]['url']
        
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return ""

@shared_task
def cleanup_unused_ai_products():
    """
    Periodically clean up AI-generated products that haven't been purchased
    """
    # Delete AI products with no orders after 30 days
    threshold = timezone.now() - timezone.timedelta(days=30)
    Product.objects.filter(
        is_ai_generated=True,
        created_at__lt=threshold,
        orders__isnull=True
    ).delete()

@shared_task
def process_gesture_data(gesture_data_id):
    try:
        gesture_data = GestureData.objects.get(id=gesture_data_id)
        
        # Convert data points to numpy array for processing
        data_points = np.array([
            [point['x'], point['y'], point['z']]
            for point in gesture_data.data_points
        ])
        
        # Preprocess data
        normalized_data = preprocess_gesture_data(data_points)
        
        # Use LangChain for gesture classification
        llm = OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = PromptTemplate(
            input_variables=["gesture_data"],
            template="""
            Analyze the following gesture data points and classify the gesture type:
            {gesture_data}
            Provide the classification and confidence score.
            """
        )
        
        result = llm(prompt.format(gesture_data=normalized_data.tolist()))
        
        # Parse LLM response and update gesture data
        classification = parse_llm_response(result)
        
        gesture_data.gesture_type = classification['type']
        gesture_data.confidence_score = classification['confidence']
        gesture_data.processed = True
        gesture_data.save()
        
        # Notify user about processed gesture
        notify_user_about_gesture.delay(gesture_data.id)
        
    except GestureData.DoesNotExist:
        print(f"GestureData with id {gesture_data_id} not found")
    except Exception as e:
        print(f"Error processing gesture data: {str(e)}")

def preprocess_gesture_data(data_points):
    # Normalize the data
    mean = np.mean(data_points, axis=0)
    std = np.std(data_points, axis=0)
    normalized_data = (data_points - mean) / std
    
    # Apply smoothing
    window_size = 5
    smoothed_data = np.apply_along_axis(
        lambda x: np.convolve(x, np.ones(window_size)/window_size, mode='valid'),
        axis=0,
        arr=normalized_data
    )
    
    return smoothed_data

def parse_llm_response(response):
    # Parse the LLM response to extract gesture type and confidence
    # This is a simplified version - you might need to adjust based on actual response format
    lines = response.strip().split('\n')
    gesture_type = lines[0].split(':')[-1].strip()
    confidence = float(lines[1].split(':')[-1].strip())
    
    return {
        'type': gesture_type,
        'confidence': confidence
    }

@shared_task
def send_push_notification(device_token_id, title, message):
    try:
        device_token = DeviceToken.objects.get(id=device_token_id)
        
        if device_token.token_type == 'FCM':
            # Firebase Cloud Messaging
            fcm_api_url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                'Authorization': f'key={settings.FCM_SERVER_KEY}',
                'Content-Type': 'application/json'
            }
            payload = {
                'to': device_token.token,
                'notification': {
                    'title': title,
                    'body': message
                }
            }
            response = requests.post(fcm_api_url, json=payload, headers=headers)
            response.raise_for_status()
            
        elif device_token.token_type == 'APN':
            # Apple Push Notification
            # Implement APN logic here
            pass
            
        device_token.last_used = timezone.now()
        device_token.save()
        
    except DeviceToken.DoesNotExist:
        print(f"DeviceToken with id {device_token_id} not found")
    except Exception as e:
        print(f"Error sending push notification: {str(e)}")

@shared_task
def notify_user_about_gesture(gesture_data_id):
    try:
        gesture_data = GestureData.objects.get(id=gesture_data_id)
        user = gesture_data.user
        
        # Get user's active device tokens
        device_tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        )
        
        notification_title = "Gesture Processed"
        notification_message = (
            f"Your {gesture_data.gesture_type} gesture has been processed "
            f"with {gesture_data.confidence_score:.2%} confidence."
        )
        
        # Send notification to all user's devices
        for device_token in device_tokens:
            send_push_notification.delay(
                device_token.id,
                notification_title,
                notification_message
            )
            
    except GestureData.DoesNotExist:
        print(f"GestureData with id {gesture_data_id} not found")
    except Exception as e:
        print(f"Error notifying user about gesture: {str(e)}")

@shared_task
def demo_long_task(product_id):
    # Simule un traitement long
    time.sleep(10)
    print(f"Traitement asynchrone terminé pour le produit {product_id}")
    return f"Produit {product_id} traité"