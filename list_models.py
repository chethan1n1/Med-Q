#!/usr/bin/env python3
"""
List available Gemini models
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyAC4GAYPDRqWj78rcIfiNmoLGi7p9_KgeE'

import google.generativeai as genai

try:
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    print("Available Gemini models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
            
except Exception as e:
    print(f"Error: {e}")
