#!/usr/bin/env python3
"""
Simple test script to verify Gemini API integration is working
"""
import os
import sys

# Set API key explicitly
os.environ['GEMINI_API_KEY'] = 'AIzaSyAC4GAYPDRqWj78rcIfiNmoLGi7p9_KgeE'

# Add the server directory to Python path
sys.path.append('/Users/chethan/Desktop/untitled folder/medq-app/server')

try:
    import google.generativeai as genai
    print("✅ Google Generative AI package imported successfully")
    
    # Test if we can configure (this will work even without API key)
    from app.utils.config import get_settings
    print("✅ Settings module imported successfully")
    
    settings = get_settings()
    print(f"✅ Settings loaded. Gemini API key configured: {bool(settings.gemini_api_key)}")
    
    if settings.gemini_api_key and settings.gemini_api_key != "your-gemini-api-key-here":
        # Only test actual API call if we have a real API key
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        print("🧪 Testing API call...")
        response = model.generate_content("Say 'Hello from Gemini!' in one line.")
        print(f"✅ API Response: {response.text}")
        print("🎉 Gemini integration is working perfectly!")
    else:
        print("⚠️  No Gemini API key found. Please add your API key to .env file:")
        print("   GEMINI_API_KEY=your-actual-api-key-here")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Please check your installation and configuration.")
