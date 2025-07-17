import google.generativeai as genai
from typing import Dict, Any, List
import json
import re
from datetime import datetime

from app.models.pydantic_models import (
    IntakeData, IntakeStep, MedicalSummaryResponse, StructuredData, Severity
)
from app.utils.config import get_settings

class AIService:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        # Intelligent Medical Assistant Prompt
        self.medical_assistant_prompt = """
You are an intelligent, compassionate, and safety-aware virtual medical assistant.

Your role is to help users who describe their health symptoms or ask general medical questions. You should:

1. Greet users in a calm and caring tone.
2. Ask smart follow-up questions based on the symptoms or message provided.
3. Guide the conversation with 2–3 questions before giving any suggestions.
4. Offer general wellness advice or next steps based on the input.
5. NEVER diagnose or prescribe any medicine.
6. ALWAYS include a clear disclaimer: "This is not a diagnosis. Please consult a licensed medical professional for proper care."
7. If the user mentions emergency symptoms (chest pain, difficulty breathing, unconsciousness, etc.), tell them to seek **IMMEDIATE** medical help.
8. Keep responses concise, clear, and caring.

Example interaction:
User: I feel tired and have body pain.
You: I'm sorry to hear that. How long have you been feeling this way? Do you also have a fever or trouble sleeping?

Your answers must feel human-like, safe, and responsive.
"""

    async def analyze_user_input(self, user_input: str, context: Dict[str, Any] = None) -> IntakeStep:
        """Analyze user input and determine the next step in the medical intake process."""
        try:
            prompt = f"""
            You are a medical AI assistant helping with patient intake. Based on the user's input, determine what medical information to collect next.
            
            User Input: "{user_input}"
            Context: {json.dumps(context or {}, indent=2)}
            
            Return a JSON response with:
            - step: The category of information needed (chief_complaint, symptoms, medical_history, medications, allergies, demographics)
            - question: A clear, empathetic question to ask the patient
            - completed: Boolean indicating if this step is complete
            - data_collected: Any relevant data extracted from the user's input
            
            Be conversational and show empathy. Ask one focused question at a time.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            result = json.loads(response_text)
            
            return IntakeStep(
                step=result.get('step', 'chief_complaint'),
                question=result.get('question', 'Can you tell me what brought you in today?'),
                completed=result.get('completed', False),
                data_collected=result.get('data_collected', {})
            )
            
        except Exception as e:
            # Fallback to default response
            return IntakeStep(
                step='chief_complaint',
                question='Can you tell me what brought you in today?',
                completed=False,
                data_collected={}
            )
    
    async def intelligent_medical_conversation(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Handle intelligent medical conversation using the compassionate AI assistant prompt.
        
        Args:
            user_message: The user's current message
            conversation_history: Previous conversation messages [{"role": "user"/"assistant", "content": "..."}]
            
        Returns:
            Dict containing the assistant's response and any safety flags
        """
        try:
            print(f"DEBUG: Processing medical conversation for message: {user_message}")
            print(f"DEBUG: API Key available: {bool(self.settings.gemini_api_key)}")
            
            # Build conversation context
            context = ""
            if conversation_history:
                context = "\n\nConversation History:\n"
                for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    context += f"{role}: {msg['content']}\n"
            
            # Check for emergency symptoms
            emergency_keywords = [
                "chest pain", "difficulty breathing", "can't breathe", "unconscious", 
                "bleeding heavily", "severe bleeding", "heart attack", "stroke",
                "difficulty speaking", "weakness on one side", "severe headache",
                "sudden vision loss", "severe abdominal pain", "choking"
            ]
            
            is_emergency = any(keyword in user_message.lower() for keyword in emergency_keywords)
            
            # If this is an emergency, provide immediate response
            if is_emergency:
                emergency_response = f"""🚨 **EMERGENCY ALERT** 🚨

Based on your symptoms, you should seek IMMEDIATE medical attention. Please go to the nearest emergency room or call emergency services right away.

If you're experiencing {user_message.lower()}, this could be a serious medical emergency that requires immediate professional care.

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
                
                return {
                    "response": emergency_response,
                    "is_emergency": True,
                    "requires_followup": True,
                    "conversation_complete": False
                }
            
            # Try to use AI, but fall back to rule-based responses if quota exceeded
            try:
                # Construct the prompt
                prompt = f"""
{self.medical_assistant_prompt}

{context}

Current User Message: "{user_message}"

Please respond as the compassionate medical assistant. Remember to:
- Be empathetic and caring
- Ask relevant follow-up questions
- Provide general wellness advice when appropriate
- Include the disclaimer about consulting a medical professional
- If emergency symptoms are mentioned, prioritize immediate medical attention

Respond naturally and conversationally.
"""
                
                print(f"DEBUG: Sending prompt to Gemini API...")
                response = self.model.generate_content(prompt)
                print(f"DEBUG: Received response from Gemini API: {response.text[:100]}...")
                
                assistant_response = response.text.strip()
                
                # Ensure disclaimer is included if not already present
                if "not a diagnosis" not in assistant_response.lower() and "consult" not in assistant_response.lower():
                    assistant_response += "\n\n⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."
                
                print(f"DEBUG: Final response: {assistant_response[:100]}...")
                
                return {
                    "response": assistant_response,
                    "is_emergency": is_emergency,
                    "requires_followup": True,
                    "conversation_complete": False
                }
                
            except Exception as api_error:
                print(f"DEBUG: API Error: {str(api_error)}")
                
                # Check if it's a quota exceeded error
                if "quota" in str(api_error).lower() or "429" in str(api_error):
                    # Use fallback rule-based responses
                    return self._get_fallback_medical_response(user_message, conversation_history)
                else:
                    # Re-raise other errors
                    raise api_error
            
        except Exception as e:
            print(f"DEBUG: Error in intelligent_medical_conversation: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            
            # Use fallback response
            return self._get_fallback_medical_response(user_message, conversation_history)
    
    def _get_fallback_medical_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Provide fallback medical responses when AI is unavailable (quota exceeded, etc.)
        """
        message_lower = user_message.lower().strip()
        
        # Handle greetings
        if any(greeting in message_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            response = """Hello! I'm Dr. Sarah, your AI medical assistant. I'm here to help you with your health concerns.

I understand you're reaching out for medical guidance. While I'd love to provide more detailed responses, I'm currently experiencing high usage.

To help you effectively, could you please tell me:
1. What symptoms are you experiencing?
2. How long have you had these symptoms?
3. Are you currently taking any medications?

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
            
        # Handle symptom descriptions
        elif any(symptom in message_lower for symptom in ["pain", "hurt", "ache", "tired", "fever", "sick", "nausea"]):
            response = f"""I'm sorry to hear you're experiencing {user_message.lower()}. That must be concerning for you.

To better understand your situation, could you tell me:
1. How long have you been experiencing these symptoms?
2. On a scale of 1-10, how would you rate the severity?
3. Have you noticed anything that makes it better or worse?

For immediate relief, you might consider:
- Getting adequate rest
- Staying hydrated
- Monitoring your symptoms

However, if your symptoms are severe, getting worse, or you're concerned, please don't hesitate to contact a healthcare provider.

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
            
        # Handle duration questions
        elif any(duration in message_lower for duration in ["day", "week", "month", "hour", "long"]):
            response = f"""Thank you for sharing that information. {user_message} can help me understand your situation better.

Based on what you've told me, here are some general wellness suggestions:
- Monitor your symptoms and how they progress
- Keep track of any triggers or patterns
- Maintain good hydration and nutrition
- Get adequate rest

If your symptoms are persistent, getting worse, or interfering with your daily life, it would be wise to consult with a healthcare provider who can properly evaluate your condition.

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
            
        # Default compassionate response
        else:
            response = f"""I hear you, and I want to help. While I'm currently experiencing high usage and can't provide detailed AI responses, I'm still here to offer support.

For any health concerns like what you've described, I'd recommend:
1. Monitoring your symptoms carefully
2. Noting any changes or patterns
3. Consulting with a healthcare provider if you're concerned

If this is urgent or you're experiencing severe symptoms, please don't hesitate to contact a medical professional or emergency services.

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
        
        return {
            "response": response,
            "is_emergency": False,
            "requires_followup": True,
            "conversation_complete": False,
            "fallback_used": True
        }
    
    async def process_intake_message(self, message: str, current_data: IntakeData) -> Dict[str, Any]:
        """Process user message and extract relevant medical information with intelligent responses"""
        
        print(f"DEBUG: Processing message: '{message}' at step: {current_data.current_step}")
        
        # First, try to extract data intelligently without AI
        extracted_data = self._smart_extract_data(message, current_data.current_step)
        print(f"DEBUG: Extracted data: {extracted_data}")
        
        # Merge extracted data with current data to determine next step
        updated_data = {**current_data.dict(), **extracted_data}
        print(f"DEBUG: Updated data: {updated_data}")
        
        next_step = self._determine_next_step_from_data(updated_data)
        print(f"DEBUG: Next step: {next_step}")
        
        # Build conversation history for context
        conversation_history = []
        if current_data.current_step != "name":  # Not the first interaction
            conversation_history.append({
                "role": "user", 
                "content": message
            })
        
        # Check for emergency symptoms first
        emergency_keywords = [
            "chest pain", "difficulty breathing", "can't breathe", "unconscious", 
            "bleeding heavily", "severe bleeding", "heart attack", "stroke",
            "difficulty speaking", "weakness on one side", "severe headache",
            "sudden vision loss", "severe abdominal pain", "choking"
        ]
        
        is_emergency = any(keyword in message.lower() for keyword in emergency_keywords)
        
        if is_emergency:
            emergency_response = f"""🚨 **EMERGENCY ALERT** 🚨

Based on your symptoms, you should seek IMMEDIATE medical attention. Please go to the nearest emergency room or call emergency services right away.

If you're experiencing {message.lower()}, this could be a serious medical emergency that requires immediate professional care.

⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."""
            
            return {
                "response": emergency_response,
                "extracted_data": extracted_data,
                "next_step": next_step,
                "is_emergency": True
            }
        
        # Try to generate intelligent response
        try:
            response_message = await self._get_intelligent_intake_response(
                message, current_data, next_step, extracted_data, conversation_history
            )
        except Exception as e:
            print(f"DEBUG: Error getting intelligent response: {e}")
            # Fall back to basic contextual response
            response_message = self._get_contextual_response(message, current_data, next_step, extracted_data)
        
        # Remove internal flags from extracted_data before returning
        clean_extracted_data = {k: v for k, v in extracted_data.items() if k != "is_greeting"}
        
        return {
            "response": response_message,
            "extracted_data": clean_extracted_data,
            "next_step": next_step
        }
    
    async def _get_intelligent_intake_response(self, message: str, current_data: IntakeData, next_step: str, extracted_data: Dict, conversation_history: List[Dict[str, str]]) -> str:
        """Generate intelligent, compassionate responses for intake process"""
        
        # Build context about the intake process
        intake_context = f"""
Current intake step: {current_data.current_step}
Next step: {next_step}
Data collected so far: {current_data.dict()}
Just extracted: {extracted_data}
"""
        
        # Try AI first, then fall back to rule-based
        try:
            prompt = f"""
{self.medical_assistant_prompt}

You are helping with a medical intake process. The user is providing information step by step.

{intake_context}

Current User Message: "{message}"

Please respond as the compassionate medical assistant conducting intake. Remember to:
- Be empathetic and caring
- Acknowledge what they've shared
- Guide them to the next step naturally
- Ask relevant follow-up questions when appropriate
- Provide gentle encouragement
- Include the disclaimer about consulting a medical professional

If they've just provided their name, welcome them warmly and ask for their age.
If they've provided age, ask about gender.
If they've provided gender, ask about their main symptoms.
If they've provided symptoms, ask about duration.
If they've provided duration, ask about medications.
If they've provided medications, ask about allergies.
If they've provided allergies, let them know you'll create a summary.

Respond naturally and conversationally.
"""
            
            response = self.model.generate_content(prompt)
            assistant_response = response.text.strip()
            
            # Ensure disclaimer is included for medical content
            if any(medical_word in assistant_response.lower() for medical_word in ["symptom", "pain", "medical", "health", "condition"]):
                if "not a diagnosis" not in assistant_response.lower() and "consult" not in assistant_response.lower():
                    assistant_response += "\n\n⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."
            
            return assistant_response
            
        except Exception as api_error:
            print(f"DEBUG: AI API Error: {str(api_error)}")
            
            # Fall back to enhanced contextual responses
            return self._get_enhanced_contextual_response(message, current_data, next_step, extracted_data)
    
    def _get_enhanced_contextual_response(self, message: str, current_data: IntakeData, next_step: str, extracted_data: Dict) -> str:
        """Enhanced contextual responses with medical intelligence"""
        
        # Handle greetings with warmth
        if extracted_data.get("is_greeting"):
            return """Hello! I'm Dr. Sarah, your AI medical assistant. I'm here to help gather some information before your consultation to ensure your healthcare provider can give you the best possible care.

I'll ask you a few questions to understand your situation better. This is completely confidential and will help make your appointment more efficient.

Let's start - could you please tell me your name?"""
        
        # Enhanced responses for each step based on NEXT step, not current step
        responses = {
            "name": f"Hello! I'm Dr. Sarah, your AI medical assistant. I'm here to help gather some information before your consultation. Let's start - could you please tell me your name?",
            
            "age": f"Thank you, {extracted_data.get('name', '')}. It's good to meet you! I'll be guiding you through some questions to help prepare for your healthcare consultation.\n\nCould you please tell me your age?",
            
            "gender": f"Thank you for sharing that. Now, to help me understand your medical profile better, what's your gender? You can say male, female, or other.",
            
            "symptoms": f"Perfect, thank you. Now, I'd like to understand what brought you here today. Could you describe your main symptoms or health concerns? Please take your time and share as much detail as you're comfortable with.",
            
            "duration": f"I understand you're experiencing {extracted_data.get('symptoms', 'these symptoms')}. That must be concerning for you.\n\nTo help your healthcare provider understand the timeline, how long have you been experiencing these symptoms?",
            
            "medications": f"Thank you for that information. Knowing the timeline helps a lot.\n\nNow, are you currently taking any medications? This includes prescription medications, over-the-counter drugs, vitamins, or supplements. If you're not taking anything, just say 'none'.",
            
            "allergies": f"I've noted that information about your medications.\n\nLastly, do you have any allergies I should know about? This includes food allergies, drug allergies, or environmental allergies. If you don't have any, just say 'none'.",
            
            "summary": f"Perfect! Thank you for providing all that information. You've been very thorough.\n\nI now have everything I need to create a comprehensive summary for your healthcare provider. This will help them understand your situation quickly and focus on addressing your concerns.\n\nWould you like me to generate your medical summary now?",
            
            "complete": "Thank you for using our medical intake system. I hope this helps make your consultation more effective!"
        }
        
        # Use the NEXT step to determine what to ask
        return responses.get(next_step, f"Thank you for that information. Let me know if you have any questions about the next step in your intake process.")
        
        response = responses.get(next_step, "Thank you for that information. Could you please provide more details?")
        
        # Add medical disclaimer for symptom-related responses
        if next_step in ["symptoms", "duration", "medications", "allergies"] and "not a diagnosis" not in response.lower():
            response += "\n\n⚠️ **Important:** This is not a diagnosis. Please consult a licensed medical professional for proper care."
        
        return response
    
    def _smart_extract_data(self, message: str, current_step: str) -> Dict[str, Any]:
        """Extract data using smart pattern matching instead of AI"""
        message_lower = message.lower().strip()
        
        if current_step == "name":
            # Handle common greetings more naturally
            if message_lower in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]:
                # Instead of returning empty, trigger the greeting response
                return {"is_greeting": True}
            # Only extract name if it's not just a greeting
            return {"name": message.strip()}
        
        elif current_step == "age":
            # Extract numbers
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                age = int(numbers[0])
                if 1 <= age <= 150:  # reasonable age range
                    return {"age": age}
            return {}
        
        elif current_step == "gender":
            if any(word in message_lower for word in ["male", "man", "boy", "mail", "mal", "m"]):
                return {"gender": "male"}
            elif any(word in message_lower for word in ["female", "woman", "girl"]):
                return {"gender": "female"}
            elif any(word in message_lower for word in ["other", "non-binary", "prefer not"]):
                return {"gender": "other"}
            return {}
        
        elif current_step == "symptoms":
            if message_lower not in ["", "none", "nothing"]:
                return {"symptoms": message.strip()}
            return {}
        
        elif current_step == "duration":
            if message_lower not in ["", "none"]:
                # Standardize duration format
                duration = message.strip()
                if any(word in message_lower for word in ["day", "week", "month", "year", "hour"]):
                    return {"duration": duration}
                elif any(char.isdigit() for char in message):
                    # Add "days" if just a number
                    return {"duration": f"{duration} days"}
            return {}
        
        elif current_step == "medications":
            if message_lower in ["none", "no", "nothing", "n/a"]:
                return {"medications": "none"}
            elif message_lower not in [""]:
                return {"medications": message.strip()}
            return {}
        
        elif current_step == "allergies":
            if message_lower in ["none", "no", "nothing", "n/a"]:
                return {"allergies": "none"}
            elif message_lower not in [""]:
                return {"allergies": message.strip()}
            return {}
        
        return {}
    
    def _determine_next_step_from_data(self, data: Dict[str, Any]) -> str:
        """Determine next step based on what data we have"""
        # Don't treat greeting as name data
        if data.get("is_greeting"):
            return "name"
        
        if not data.get("name"):
            return "name"
        elif not data.get("age"):
            return "age"
        elif not data.get("gender"):
            return "gender"
        elif not data.get("symptoms"):
            return "symptoms"
        elif not data.get("duration"):
            return "duration"
        elif not data.get("medications"):
            return "medications"
        elif not data.get("allergies"):
            return "allergies"
        else:
            return "summary"
    
    def _get_contextual_response(self, message: str, current_data: IntakeData, next_step: str, extracted_data: Dict) -> str:
        """Generate contextual response based on what was extracted"""
        
        # Handle thank you messages
        if message.lower().strip() in ["thank you", "thanks", "thx"]:
            return "You're welcome! Let me know if you need anything else."
            
        # If we extracted data, acknowledge it and move to next step
        if extracted_data:
            # Handle greetings first
            if extracted_data.get("is_greeting"):
                return "Hello! I'm Dr. Sarah, and I'll be helping you today. Could you please tell me your name?"
                
            responses = {
                "name": f"Nice to meet you, {extracted_data.get('name', '')}! How old are you?",
                "age": f"Thank you! What's your gender - male, female, or other?",
                "gender": "Thank you! Now, could you describe your main symptoms or concerns? Take your time.",
                "symptoms": "I understand. How long have you been experiencing these symptoms?",
                "duration": "Got it. Are you currently taking any medications? If none, just say 'none'.",
                "medications": "Thank you. Do you have any allergies I should know about? If none, just say 'none'.",
                "allergies": "Perfect! Thank you for providing all that information. Let me create a summary for your healthcare provider.",
                "summary": "I've prepared your medical summary. Please let me know if you need anything else.",
                "complete": "I hope this helps! Let me know if you need anything else."
            }
            
            # Get the field that was just extracted
            for field in extracted_data:
                if field in responses:
                    return responses[field]
        
        # Fallback responses for when we need to ask again
        fallback_responses = {
            "name": "I'd like to get your name for the medical records. What should I call you?",
            "age": "Could you please tell me your age?",
            "gender": "What's your gender? You can say male, female, or other.",
            "symptoms": "What symptoms or health concerns brought you in today?",
            "duration": "How long have you been experiencing these symptoms?",
            "medications": "Are you currently taking any medications? If none, just say 'none'.",
            "allergies": "Do you have any allergies I should know about? If none, just say 'none'.",
            "summary": "Let me prepare your medical summary now.",
            "complete": "Your intake is complete!"
        }
        
        return fallback_responses.get(next_step, "Could you please provide that information?")
    
    def _determine_next_step(self, current_data: IntakeData) -> str:
        """Determine the next step in the intake process"""
        step_order = [
            "name", "age", "gender", "symptoms", 
            "duration", "medications", "allergies", "summary"
        ]
        
        # Check what data we have and what's missing
        if not current_data.name:
            return "name"
        elif not current_data.age:
            return "age"
        elif not current_data.gender:
            return "gender"
        elif not current_data.symptoms:
            return "symptoms"
        elif not current_data.duration:
            return "duration"
        elif not current_data.medications:
            return "medications"
        elif not current_data.allergies:
            return "allergies"
        else:
            return "summary"
    
    async def _extract_step_data(self, message: str, current_step: str) -> Dict[str, Any]:
        """Extract specific data based on the current step"""
        
        prompts = {
            "name": f"Extract ONLY the person's name from this message: '{message}'. If it's just a greeting (hi, hello, etc.) with no name, respond with exactly 'GREETING'. Respond with only the name or the word 'GREETING', nothing else.",
            "age": f"Extract ONLY the age number from this message: '{message}'. If no age is mentioned, respond with exactly 'NO_AGE'. Respond with only a number or 'NO_AGE'.",
            "gender": f"Extract ONLY the gender from this message: '{message}'. Respond with only 'male', 'female', 'other', or 'NO_GENDER'.",
            "symptoms": f"Extract and briefly summarize medical symptoms from: '{message}'. If no symptoms mentioned, respond with exactly 'NO_SYMPTOMS'.",
            "duration": f"Extract how long symptoms lasted from: '{message}'. If no duration mentioned, respond with exactly 'NO_DURATION'.",
            "medications": f"Extract medications from: '{message}'. If none mentioned, respond with exactly 'NO_MEDICATIONS'.",
            "allergies": f"Extract allergies from: '{message}'. If none mentioned, respond with exactly 'NO_ALLERGIES'."
        }
        
        if current_step not in prompts:
            return {}
        
        try:
            prompt = prompts[current_step]
            response = self.model.generate_content(prompt)
            extracted_value = response.text.strip()
            
            # Handle different responses
            if extracted_value in ["GREETING", "NO_AGE", "NO_GENDER", "NO_SYMPTOMS", "NO_DURATION", "NO_MEDICATIONS", "NO_ALLERGIES"]:
                # Don't update data, just return empty
                return {}
            
            # Format the extracted data based on step
            if current_step == "age":
                try:
                    age = int(re.search(r'\d+', extracted_value).group())
                    return {"age": age, "current_step": self._determine_next_step_name(current_step)}
                except:
                    return {}
            elif current_step == "gender":
                gender = extracted_value.lower()
                if gender in ["male", "female", "other"]:
                    return {"gender": gender, "current_step": self._determine_next_step_name(current_step)}
                return {}
            else:
                return {current_step: extracted_value, "current_step": self._determine_next_step_name(current_step)}
                
        except Exception as e:
            print(f"Error extracting data for {current_step}: {e}")
            return {}
    
    def _determine_next_step_name(self, current_step: str) -> str:
        """Get the next step name"""
        step_order = [
            "name", "age", "gender", "symptoms", 
            "duration", "medications", "allergies", "summary"
        ]
        
        try:
            current_index = step_order.index(current_step)
            if current_index < len(step_order) - 1:
                return step_order[current_index + 1]
            else:
                return "complete"
        except ValueError:
            return "name"
    
    async def _generate_response(self, message: str, current_data: IntakeData, next_step: str) -> str:
        """Generate appropriate response based on the conversation context"""
        
        # Handle greetings when we're asking for name
        if current_data.current_step == "name" and message.lower().strip() in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]:
            return "Hello! Nice to meet you. What's your name?"
        
        step_questions = {
            "age": "Thank you! How old are you?",
            "gender": "What's your gender? (male/female/other)",
            "symptoms": "Could you describe your main symptoms or concerns? Take your time and be as detailed as you'd like.",
            "duration": "How long have you been experiencing these symptoms?",
            "medications": "Are you currently taking any medications? If none, just say 'none'.",
            "allergies": "Do you have any allergies I should know about? If none, just say 'none'.",
            "summary": "Thank you for sharing all that information. Let me create a summary for your doctor.",
            "complete": "Perfect! I have all the information I need. Redirecting you to the summary page..."
        }
        
        # If we have extracted some data, thank them and move to next question
        if next_step in step_questions and next_step != current_data.current_step:
            return step_questions[next_step]
        
        # If we're stuck on the same step, ask clarifying question
        if current_data.current_step == "name":
            return "I'd like to get your name for the medical records. What should I call you?"
        elif current_data.current_step == "age":
            return "Could you please tell me your age?"
        elif current_data.current_step == "gender":
            return "What's your gender? You can say male, female, or other."
        elif current_data.current_step == "symptoms":
            return "What symptoms or health concerns brought you in today?"
        elif current_data.current_step == "duration":
            return "How long have you been experiencing these symptoms?"
        elif current_data.current_step == "medications":
            return "Are you currently taking any medications?"
        elif current_data.current_step == "allergies":
            return "Do you have any allergies I should know about?"
        
        # Fallback to AI response
        try:
            context = f"""
            You are a friendly medical intake assistant. The patient just said: "{message}"
            Current step: {current_data.current_step}
            Respond briefly and helpfully to guide them to provide the needed information.
            """
            
            response = self.model.generate_content(context)
            return response.text.strip()
        except Exception as e:
            return "Could you please provide that information again?"

    async def _generate_friendly_response(self, message: str, current_data: IntakeData, next_step: str) -> str:
        """Generate a friendly, doctor-like response"""
        
        try:
            context = f"""
            You are Dr. Sarah, a warm and caring family physician. Respond to the patient in a friendly, professional manner.
            
            Patient just said: "{message}"
            Current step: {current_data.current_step}
            Next step needed: {next_step}
            
            Patient info so far:
            - Name: {current_data.name or 'Not provided'}
            - Age: {current_data.age or 'Not provided'}
            - Gender: {current_data.gender or 'Not provided'}
            - Symptoms: {current_data.symptoms or 'Not provided'}
            
            Respond warmly and guide them to the next question. Keep it conversational and caring.
            """
            
            response = self.model.generate_content(context)
            return response.text.strip()
            
        except Exception as e:
            print(f"Error generating friendly response: {e}")
            return self._get_default_friendly_response(next_step, current_data)
    
    def _get_default_friendly_response(self, next_step: str, current_data: IntakeData) -> str:
        """Fallback friendly responses"""
        responses = {
            "name": "Hello! I'm Dr. Sarah. I'm here to help you today. May I have your name please?",
            "age": f"Nice to meet you, {current_data.name or 'there'}! How old are you?",
            "gender": "Thank you! And what's your gender - male, female, or other?",
            "symptoms": "I'd like to understand what's bringing you in today. Can you tell me about your symptoms or concerns?",
            "duration": "I see. How long have you been experiencing these symptoms?",
            "medications": "Thank you for sharing that. Are you currently taking any medications?",
            "allergies": "And do you have any allergies I should be aware of?",
            "summary": "Thank you for providing all that information. Let me summarize what we've discussed and prepare a report for your healthcare provider.",
            "complete": "Perfect! I have everything I need. Your intake is complete."
        }
        return responses.get(next_step, "Thank you. Let's continue with your intake.")
    
    async def generate_medical_summary(self, intake_data: IntakeData) -> MedicalSummaryResponse:
        """Generate a comprehensive medical summary from intake data"""
        try:
            # Create a detailed prompt for medical summary generation
            prompt = f"""
            You are Dr. Sarah, an experienced family physician with 15 years of practice. Create a comprehensive medical summary based on the patient intake information below. Be intelligent, practical, and provide specific recommendations.

            Patient Information:
            - Name: {intake_data.name or 'Not provided'}
            - Age: {intake_data.age or 'Not provided'}
            - Gender: {intake_data.gender or 'Not provided'}
            - Chief Complaint: {intake_data.symptoms or 'Not provided'}
            - Duration: {intake_data.duration or 'Not provided'}
            - Current Medications: {intake_data.medications or 'None reported'}
            - Allergies: {intake_data.allergies or 'None reported'}

            Based on the symptoms, age, and presentation, provide:

            1. **CHIEF COMPLAINT**: Clear statement of the main issue
            2. **HISTORY OF PRESENT ILLNESS**: Detailed analysis of symptoms
            3. **CURRENT MEDICATIONS**: List what they're taking
            4. **ALLERGIES**: Note any allergies
            5. **CLINICAL ASSESSMENT**: Your professional medical opinion about the likely condition(s)
            6. **RECOMMENDED MEDICATIONS**: Suggest specific over-the-counter or prescription medications with dosages
            7. **HOME REMEDIES & LIFESTYLE**: Practical home care suggestions
            8. **WHEN TO SEEK IMMEDIATE CARE**: Red flag symptoms to watch for
            9. **FOLLOW-UP RECOMMENDATIONS**: Specific timeline for follow-up care

            Be specific about:
            - Medication names, dosages, and frequencies
            - Duration of treatment
            - Specific symptoms that would warrant immediate medical attention
            - Practical home remedies that are evidence-based
            - Expected timeline for improvement

            Format as a professional medical note but make it intelligent and actionable.
            """

            # Try to use AI for summary generation
            try:
                response = self.model.generate_content(prompt)
                ai_summary = response.text.strip()
            except Exception as ai_error:
                print(f"AI summary generation failed: {ai_error}")
                # Fallback to intelligent structured summary
                ai_summary = self._generate_intelligent_fallback_summary(intake_data)

            return MedicalSummaryResponse(
                id=1,  # Temporary ID for non-persisted summary
                patient_id=1,  # Temporary patient ID
                summary_text=ai_summary,
                structured_data=StructuredData(
                    chief_complaint=intake_data.symptoms or "Not specified",
                    symptoms=[intake_data.symptoms] if intake_data.symptoms else [],
                    duration=intake_data.duration or "Not specified",
                    severity=self._assess_severity(intake_data.symptoms, intake_data.duration),
                    associated_symptoms=[],
                    medical_history="Patient reported chief complaint as documented",
                    current_medications=[intake_data.medications] if intake_data.medications and intake_data.medications.lower() != 'none' else [],
                    allergies=[intake_data.allergies] if intake_data.allergies and intake_data.allergies.lower() != 'none' else [],
                    recommendations=self._generate_intelligent_recommendations(intake_data)
                ),
                icd_codes=[],
                created_at=datetime.now()
            )

        except Exception as e:
            print(f"Error generating medical summary: {e}")
            return self._generate_emergency_fallback_summary(intake_data)

    def _generate_fallback_summary(self, intake_data: IntakeData) -> str:
        """Generate a structured summary without AI when API is unavailable"""
        return f"""
MEDICAL INTAKE SUMMARY
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

PATIENT INFORMATION:
Name: {intake_data.name or 'Not provided'}
Age: {intake_data.age or 'Not provided'}
Gender: {intake_data.gender or 'Not provided'}

CHIEF COMPLAINT:
{intake_data.symptoms or 'Not specified'}

HISTORY OF PRESENT ILLNESS:
Patient reports {intake_data.symptoms or 'symptoms'} for a duration of {intake_data.duration or 'unspecified time period'}.

CURRENT MEDICATIONS:
{intake_data.medications or 'None reported'}

ALLERGIES:
{intake_data.allergies or 'None reported'}

ASSESSMENT:
Patient presents with chief complaint as documented above. Further evaluation by healthcare provider recommended.

PLAN:
1. Review of symptoms and physical examination
2. Consider appropriate diagnostic workup based on clinical presentation
3. Follow-up as clinically indicated
4. Patient education regarding symptoms and when to seek care

RECOMMENDATIONS:
- Schedule appointment with primary care physician
- Monitor symptoms and return if worsening
- Seek immediate care if symptoms become severe
        """.strip()

    def _generate_intelligent_fallback_summary(self, intake_data: IntakeData) -> str:
        """Generate an intelligent fallback summary with specific recommendations"""
        symptoms = (intake_data.symptoms or "").lower()
        age = intake_data.age or 0
        duration = (intake_data.duration or "").lower()
        
        # Intelligent assessment based on symptoms
        assessment = self._get_intelligent_assessment(symptoms, age, duration)
        medications = self._get_medication_recommendations(symptoms, age)
        home_remedies = self._get_home_remedies(symptoms)
        red_flags = self._get_red_flag_symptoms(symptoms)
        
        return f"""
MEDICAL INTAKE SUMMARY
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

PATIENT INFORMATION:
Name: {intake_data.name or 'Not provided'}
Age: {intake_data.age or 'Not provided'}
Gender: {intake_data.gender or 'Not provided'}

CHIEF COMPLAINT:
{intake_data.symptoms or 'Not specified'}

HISTORY OF PRESENT ILLNESS:
{age}-year-old {intake_data.gender or 'patient'} presents with {intake_data.symptoms or 'symptoms'} for {intake_data.duration or 'unspecified duration'}. {assessment['description']}

CURRENT MEDICATIONS:
{intake_data.medications or 'None reported'}

ALLERGIES:
{intake_data.allergies or 'None reported'}

CLINICAL ASSESSMENT:
{assessment['diagnosis']}

RECOMMENDED MEDICATIONS:
{medications}

HOME REMEDIES & LIFESTYLE RECOMMENDATIONS:
{home_remedies}

WHEN TO SEEK IMMEDIATE CARE:
{red_flags}

FOLLOW-UP RECOMMENDATIONS:
- Follow up with primary care physician within {assessment['follow_up_timeline']}
- Return if symptoms worsen or new symptoms develop
- Expected improvement timeline: {assessment['expected_improvement']}

ADDITIONAL NOTES:
{assessment['additional_notes']}
        """.strip()

    def _assess_severity(self, symptoms: str, duration: str) -> str:
        """Assess severity based on symptoms and duration"""
        if not symptoms:
            return "moderate"
        
        symptoms_lower = symptoms.lower()
        duration_lower = (duration or "").lower()
        
        # Severe symptoms
        if any(word in symptoms_lower for word in ["chest pain", "difficulty breathing", "severe pain", "blood", "fever over 101", "vomiting"]):
            return "severe"
        
        # Mild symptoms
        if any(word in symptoms_lower for word in ["mild", "slight", "minor"]) or any(word in duration_lower for word in ["few hours", "today", "1 day"]):
            return "mild"
        
        return "moderate"

    def _generate_intelligent_recommendations(self, intake_data: IntakeData) -> List[str]:
        """Generate intelligent recommendations based on symptoms"""
        symptoms = (intake_data.symptoms or "").lower()
        age = intake_data.age or 0
        
        recommendations = []
        
        # Common cold/cough recommendations
        if any(word in symptoms for word in ["cold", "cough", "congestion", "runny nose"]):
            recommendations.extend([
                "Stay hydrated - drink plenty of fluids",
                "Use a humidifier or breathe steam from hot shower",
                "Consider over-the-counter decongestants if needed",
                "Get adequate rest (7-9 hours of sleep)",
                "Avoid smoking and secondhand smoke"
            ])
        
        # Fever recommendations
        if "fever" in symptoms:
            recommendations.extend([
                "Monitor temperature regularly",
                "Use fever reducers as directed (acetaminophen or ibuprofen)",
                "Stay hydrated with clear fluids",
                "Rest and avoid strenuous activities"
            ])
        
        # Headache recommendations
        if "headache" in symptoms:
            recommendations.extend([
                "Apply cold or warm compress to head/neck",
                "Stay hydrated",
                "Consider over-the-counter pain relievers",
                "Rest in a quiet, dark room"
            ])
        
        # General recommendations
        recommendations.extend([
            "Follow up with primary care physician within 3-5 days",
            "Return if symptoms worsen or new symptoms develop",
            "Monitor for red flag symptoms requiring immediate care"
        ])
        
        return recommendations

    def _get_intelligent_assessment(self, symptoms: str, age: int, duration: str) -> Dict[str, str]:
        """Get intelligent assessment based on symptoms"""
        if "cold" in symptoms and "cough" in symptoms:
            return {
                "description": "This appears to be consistent with an upper respiratory tract infection (common cold).",
                "diagnosis": "Likely viral upper respiratory infection (common cold) based on symptom presentation and duration.",
                "follow_up_timeline": "3-5 days if symptoms persist or worsen",
                "expected_improvement": "Symptoms typically improve within 7-10 days",
                "additional_notes": "Viral infections are self-limiting but symptom management is important for comfort."
            }
        elif "fever" in symptoms:
            return {
                "description": "Patient presents with fever which may indicate an infectious process.",
                "diagnosis": "Febrile illness - requires further evaluation to determine underlying cause.",
                "follow_up_timeline": "24-48 hours if fever persists",
                "expected_improvement": "Depends on underlying cause",
                "additional_notes": "Monitor temperature and associated symptoms closely."
            }
        elif "headache" in symptoms:
            return {
                "description": "Patient reports headache which could be tension-type or other etiology.",
                "diagnosis": "Headache - likely tension-type based on presentation.",
                "follow_up_timeline": "1 week if headaches persist or worsen",
                "expected_improvement": "Should improve with rest and appropriate treatment",
                "additional_notes": "Consider triggers such as stress, dehydration, or sleep deprivation."
            }
        else:
            return {
                "description": "Patient presents with symptoms requiring clinical evaluation.",
                "diagnosis": "Symptoms require further assessment for proper diagnosis.",
                "follow_up_timeline": "3-5 days",
                "expected_improvement": "Variable depending on underlying condition",
                "additional_notes": "Comprehensive evaluation recommended."
            }

    def _get_medication_recommendations(self, symptoms: str, age: int) -> str:
        """Get medication recommendations based on symptoms and age"""
        if "cold" in symptoms and "cough" in symptoms:
            if age >= 18:
                return """
• Acetaminophen 650mg every 6 hours for aches and fever (max 3000mg/day)
• Ibuprofen 400mg every 6-8 hours for inflammation and pain (max 1200mg/day)
• Pseudoephedrine 30mg every 6 hours for nasal congestion (if no contraindications)
• Dextromethorphan 15mg every 4 hours for dry cough
• Guaifenesin 200-400mg every 4 hours for productive cough
• Lozenges or throat sprays for sore throat
                """.strip()
            else:
                return "Age-appropriate pediatric formulations of acetaminophen or ibuprofen as directed by weight/age charts."
        
        elif "fever" in symptoms:
            return """
• Acetaminophen 650mg every 6 hours (max 3000mg/day)
• Ibuprofen 400mg every 6-8 hours (max 1200mg/day)
• Alternate between acetaminophen and ibuprofen if needed
            """.strip()
        
        elif "headache" in symptoms:
            return """
• Acetaminophen 650mg every 6 hours (max 3000mg/day)
• Ibuprofen 400mg every 6-8 hours (max 1200mg/day)
• Aspirin 500mg every 4-6 hours (if no contraindications)
            """.strip()
        
        return "Consult healthcare provider for appropriate medication recommendations."

    def _get_home_remedies(self, symptoms: str) -> str:
        """Get home remedies based on symptoms"""
        if "cold" in symptoms and "cough" in symptoms:
            return """
• Honey and warm water for cough (1-2 teaspoons of honey in warm water)
• Steam inhalation 2-3 times daily
• Warm salt water gargles (1/2 teaspoon salt in warm water)
• Increase fluid intake (water, herbal teas, clear broths)
• Use a humidifier or vaporizer
• Elevate head while sleeping
• Avoid dairy products which may increase mucus production
            """.strip()
        
        elif "fever" in symptoms:
            return """
• Cool compresses on forehead and wrists
• Lukewarm baths or showers
• Light, breathable clothing
• Increased fluid intake
• Rest in a cool environment
            """.strip()
        
        elif "headache" in symptoms:
            return """
• Apply cold compress to forehead for 15-20 minutes
• Gentle neck and shoulder massage
• Rest in quiet, dark room
• Stay hydrated
• Practice relaxation techniques
• Regular sleep schedule
            """.strip()
        
        return "Rest, hydration, and monitoring of symptoms."

    def _get_red_flag_symptoms(self, symptoms: str) -> str:
        """Get red flag symptoms that require immediate medical attention"""
        if "cold" in symptoms and "cough" in symptoms:
            return """
SEEK IMMEDIATE MEDICAL ATTENTION IF:
• Difficulty breathing or shortness of breath
• Chest pain or pressure
• High fever (>101.5°F/38.6°C) for more than 3 days
• Coughing up blood or pink-tinged sputum
• Severe headache with neck stiffness
• Persistent vomiting
• Signs of dehydration
• Symptoms significantly worsen after initial improvement
            """.strip()
        
        elif "fever" in symptoms:
            return """
SEEK IMMEDIATE MEDICAL ATTENTION IF:
• Temperature >103°F (39.4°C)
• Difficulty breathing
• Severe headache with neck stiffness
• Persistent vomiting
• Signs of dehydration
• Confusion or altered mental state
• Chest pain
            """.strip()
        
        elif "headache" in symptoms:
            return """
SEEK IMMEDIATE MEDICAL ATTENTION IF:
• Sudden, severe headache ("worst headache of life")
• Headache with fever and neck stiffness
• Headache with vision changes
• Headache with confusion or altered mental state
• Headache after head injury
• Progressively worsening headache
            """.strip()
        
        return """
SEEK IMMEDIATE MEDICAL ATTENTION IF:
• Severe or worsening symptoms
• Difficulty breathing
• Chest pain
• High fever
• Severe headache
• Persistent vomiting
• Signs of dehydration
        """.strip()

    def _generate_emergency_fallback_summary(self, intake_data: IntakeData) -> MedicalSummaryResponse:
        """Emergency fallback when all other methods fail"""
        return MedicalSummaryResponse(
            id=1,  # Temporary ID for non-persisted summary
            patient_id=1,  # Temporary patient ID
            summary_text="Medical intake completed. Please review with healthcare provider.",
            structured_data=StructuredData(
                chief_complaint=intake_data.symptoms or "Not specified",
                symptoms=[],
                duration=intake_data.duration or "Not specified",
                severity="moderate",  # Changed from "unknown" to valid enum value
                associated_symptoms=[],
                medical_history="Intake data available",
                current_medications=[],
                allergies=[],
                recommendations=["Review with healthcare provider"]
            ),
            icd_codes=[],
            created_at=datetime.now()
        )
