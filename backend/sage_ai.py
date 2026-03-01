"""
Sage AI Engine
Handles AI-powered health conversations using Claude API.
"""

import anthropic
import base64
import os

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')


class SageAI:
    def __init__(self):
        """Initialize Sage AI with Claude API."""
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history = []
        self.user_profile = None
        self.system_prompt = self._build_system_prompt()
    
    def set_user_profile(self, profile):
        """Set user profile for personalized responses."""
        self.user_profile = profile
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self):
        """Build system prompt with user context."""
        
        user_context = ""
        if self.user_profile:
            name = self.user_profile.get('name', 'there')
            conditions = self.user_profile.get('conditions', [])
            allergies = self.user_profile.get('allergies', '')
            medications = self.user_profile.get('medications', '')
            
            user_context = f"""

## USER HEALTH PROFILE
- Name: {name}
- Existing Conditions: {', '.join(conditions) if conditions else 'None'}
- Allergies: {allergies if allergies else 'None'}
- Medications: {medications if medications else 'None'}

Use this to personalize responses. Never recommend anything they're allergic to. Consider drug interactions.
"""
        
        return f"""You are Sage, a friendly health assistant who chats like a caring friend, NOT a doctor or textbook.

## YOUR STYLE
- Chat like a warm, supportive friend who happens to know about health
- Keep responses SHORT (2-4 sentences max)
- Ask only ONE follow-up question per response
- Use casual, simple language
- Show empathy first, advice second
- Use emojis occasionally but don't overdo it

## STRICT RULES
1. NEVER write long paragraphs or walls of text
2. NEVER give multiple suggestions at once - space them out over the conversation
3. NEVER use bullet points or lists in your first response
4. NEVER sound like a medical document
5. ALWAYS be conversational and warm
6. For emergencies (chest pain, breathing issues, stroke signs) → immediately say "Please call 108/112 right away!"

## GOOD RESPONSE EXAMPLES

User: "I have a headache"
Good: "Oh no, headaches are the worst! 😔 How long have you had it? Just started or been going on for a while?"

User: "Since morning"
Good: "That's tough, dealing with it all day. Is it more of a throbbing pain or like a tight pressure around your head?"

User: "Throbbing"
Good: "Got it. Have you been able to drink enough water today? Dehydration is sneaky and often causes throbbing headaches."

## BAD RESPONSE (never do this)
"Here are several things you can try: 1) Drink water 2) Rest in a dark room 3) Take pain relievers 4) Apply cold compress 5) Massage your temples. Also, headaches can be caused by stress, dehydration, lack of sleep..."

## CONVERSATION FLOW
1. First response: Show empathy + ask ONE clarifying question
2. Second response: Acknowledge their answer + ask another question OR give ONE simple tip
3. Build up advice gradually through conversation
4. Only suggest seeing a doctor after understanding the situation
{user_context}
"""

    def chat(self, user_message):
        """Process user message and get AI response."""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep conversation history manageable (last 20 messages)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,  # Shorter responses
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except anthropic.APIError as e:
            print(f"Anthropic API error: {e}")
            return "I'm having trouble connecting right now. Please try again in a moment."
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I encountered an error. Please try again."
    
    def clear_history(self):
        """Clear conversation history for new chat."""
        self.conversation_history = []
    
    def analyze_image(self, image_data, file_ext, user_message=""):
        """Analyze an image using Claude's vision capability."""
        
        # Convert to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine media type
        media_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_types.get(file_ext, 'image/jpeg')
        
        # Build the message with image
        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_image
                    }
                },
                {
                    "type": "text",
                    "text": user_message if user_message else "Please look at this image and help me understand what you see. If it's health-related, provide relevant information."
                }
            ]
        }
        
        # Add to history (text only for history)
        self.conversation_history.append({
            "role": "user",
            "content": f"[Shared an image] {user_message}"
        })
        
        try:
            # Create messages list with image
            messages_with_image = self.conversation_history[:-1] + [image_message]
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,  # Allow slightly longer for image analysis
                system=self.system_prompt + "\n\n## IMAGE ANALYSIS\nWhen analyzing health-related images:\n- Describe what you observe clearly\n- Be helpful but don't diagnose\n- For skin conditions, rashes, injuries - suggest seeing a doctor if concerning\n- For prescriptions/reports - help explain the content\n- Stay conversational and supportive",
                messages=messages_with_image
            )
            
            assistant_message = response.content[0].text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            print(f"Image analysis error: {e}")
            return "I had trouble analyzing that image. Could you describe what you'd like me to look at, or try uploading again?"
    
    def get_greeting(self):
        """Get a personalized greeting."""
        if self.user_profile and self.user_profile.get('name'):
            name = self.user_profile['name'].split()[0]  # First name only
            return f"Hello {name}! I'm Sage, your personal health assistant. How are you feeling today?"
        return "Hello! I'm Sage, your personal health assistant. How can I help you today?"


# Singleton instance for the app
_sage_instances = {}

def get_sage_instance(user_id, user_profile=None):
    """Get or create a Sage AI instance for a user."""
    if user_id not in _sage_instances:
        _sage_instances[user_id] = SageAI()
    
    if user_profile:
        _sage_instances[user_id].set_user_profile(user_profile)
    
    return _sage_instances[user_id]

def clear_sage_instance(user_id):
    """Clear a user's Sage AI instance."""
    if user_id in _sage_instances:
        del _sage_instances[user_id]


def generate_chat_title(first_message):
    """Generate a meaningful short title for a chat session based on the first message."""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{
                "role": "user",
                "content": f"""Generate a very short title (2-4 words max) for a health chat that starts with this message: "{first_message}"

Examples:
- "I have a headache" → "Headache Help"
- "My stomach hurts" → "Stomach Pain"
- "I feel very tired" → "Fatigue Issues"
- "I have a fever and cold" → "Cold & Fever"
- "Can you help me sleep better" → "Sleep Problems"

Just respond with the short title, nothing else."""
            }]
        )
        
        title = response.content[0].text.strip()
        # Clean up and limit length
        title = title.replace('"', '').replace("'", "")[:50]
        return title if title else "Health Chat"
        
    except Exception as e:
        print(f"Error generating title: {e}")
        # Fallback: use first few words of message
        words = first_message.split()[:4]
        return ' '.join(words)[:50] if words else "Health Chat"