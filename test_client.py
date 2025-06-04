import requests
import json
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image (100x100 pixels, light gray)
    img = Image.new('RGB', (100, 100), color=(200, 200, 200))
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_api():
    """Test the skincare recommendation API"""
    
    # API endpoint
    url = "http://localhost:8000/recommend"
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare the request
    files = {
        'image': ('test_image.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'goal': 'brightening',
        'history': 'Vitamin C serum, Niacinamide, Sunscreen SPF 30'
    }
    
    try:
        print("Testing API...")
        print(f"URL: {url}")
        print(f"Goal: {data['goal']}")
        print(f"History: {data['history']}")
        print("-" * 50)
        
        # Make the request
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print("\n📊 ANALYSIS RESULTS:")
            print(f"Brightness Score: {result['analysis']['brightness_score']}")
            print(f"Brightness Level: {result['analysis']['brightness_level']}")
            
            print("\n💡 RECOMMENDATIONS:")
            if isinstance(result['recommendation'], dict):
                for key, value in result['recommendation'].items():
                    print(f"{key.title()}: {value}")
            else:
                print(result['recommendation'])
            
            print(f"\n🔗 Collection Link: {result['mock_collection_link']}")
            
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("Make sure the server is running on localhost:8000")
        print("Run: python main.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🧪 TESTING SKINCARE RECOMMENDATION API")
    print("=" * 50)
    
    print("\n1. Testing Health Check...")
    test_health_check()
    
    print("\n2. Testing Recommendation Endpoint...")
    test_api()