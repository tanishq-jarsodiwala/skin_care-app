from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
from dotenv import load_dotenv
import requests
import json
from typing import Optional
import tempfile
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Skincare Recommendation API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY", "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")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

def calculate_brightness(image_bytes):
    """Calculate average brightness of the uploaded image"""
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert('L')  # Convert to grayscale
        
        # Calculate average brightness
        brightness = sum(img.getdata()) / (img.width * img.height)
        return round(brightness, 2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

def get_skincare_recommendation(goal: str, history: str, brightness: float):
    """Get skincare recommendation using Hugging Face API"""
    
    # Construct prompt for skincare recommendation
    prompt = f"""
    As a skincare expert, provide a recommendation based on:
    - Skincare Goal: {goal}
    - Past Product History: {history}
    - Skin Brightness Score: {brightness}/255 (higher means brighter skin)
    
    Please provide:
    1. A specific skincare routine recommendation
    2. Key ingredients to look for
    3. Products to avoid
    4. Expected timeline for results
    
    Keep the response concise and professional.
    """
    
    # Fallback local recommendation if API fails
    def get_local_recommendation():
        recommendations = {
            "brightening": {
                "routine": "Use Vitamin C serum in morning, Niacinamide serum at night, and always apply SPF 30+",
                "key_ingredients": "Vitamin C, Niacinamide, Alpha Arbutin, Kojic Acid",
                "avoid": "Harsh scrubs, over-exfoliation, products with alcohol",
                "timeline": "4-8 weeks for visible results"
            },
            "anti-aging": {
                "routine": "Retinol at night, Hyaluronic acid serum, and broad-spectrum sunscreen daily",
                "key_ingredients": "Retinol, Peptides, Hyaluronic Acid, Vitamin E",
                "avoid": "Mixing retinol with AHA/BHA, sun exposure without SPF",
                "timeline": "6-12 weeks for visible results"
            },
            "acne": {
                "routine": "Salicylic acid cleanser, Benzoyl peroxide spot treatment, oil-free moisturizer",
                "key_ingredients": "Salicylic Acid, Benzoyl Peroxide, Niacinamide, Tea Tree Oil",
                "avoid": "Over-cleansing, heavy oils, comedogenic ingredients",
                "timeline": "2-6 weeks for improvement"
            }
        }
        
        # Match goal to recommendation
        for key in recommendations.keys():
            if key.lower() in goal.lower():
                return recommendations[key]
        
        # Default recommendation
        return {
            "routine": "Gentle cleanser, moisturizer suited for your skin type, and daily SPF protection",
            "key_ingredients": "Hyaluronic Acid, Ceramides, Niacinamide",
            "avoid": "Harsh ingredients, over-exfoliation",
            "timeline": "4-6 weeks for visible results"
        }
    
    try:
        # Try Hugging Face API first
        headers = {"Authorization": f"Bearer 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"}
        
        # Use a text generation model instead
        api_url = "https://api-inference.huggingface.co/models/gpt2"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                # Clean up the generated text
                recommendation_text = generated_text.replace(prompt, '').strip()
                
                if recommendation_text:
                    return {
                        "recommendation": recommendation_text,
                        "source": "AI Generated"
                    }
        
        # Fallback to local recommendation
        return get_local_recommendation()
        
    except Exception as e:
        print(f"API Error: {e}")
        # Return local recommendation as fallback
        return get_local_recommendation()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Skincare Recommendation API is running!",
        "version": "1.0.0",
        "endpoints": {
            "POST /recommend": "Get skincare recommendations",
            "GET /": "Health check"
        }
    }

@app.post("/recommend")
async def recommend_skincare(
    image: UploadFile = File(..., description="Face image for analysis"),
    goal: str = Form(..., description="Skincare goal (e.g., 'brightening')"),
    history: str = Form(..., description="Past product history (e.g., 'Vitamin C, Niacinamide')")
):
    """
    Main endpoint for skincare recommendations
    
    Args:
        image: Uploaded face image
        goal: Skincare goal
        history: Past product usage history
    
    Returns:
        JSON with brightness score, recommendations, and mock collection link
    """
    
    try:
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image bytes
        image_bytes = await image.read()
        
        # Calculate brightness
        brightness_score = calculate_brightness(image_bytes)
        
        # Get skincare recommendation
        recommendation = get_skincare_recommendation(goal, history, brightness_score)
        
        # Create response
        response = {
            "analysis": {
                "brightness_score": brightness_score,
                "brightness_level": "High" if brightness_score > 200 else "Medium" if brightness_score > 100 else "Low",
                "image_processed": True
            },
            "recommendation": recommendation,
            "user_input": {
                "goal": goal,
                "history": history
            },
            "mock_collection_link": f"https://skincare-collection.com/recommended/{goal.lower().replace(' ', '-')}",
            "status": "success"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)