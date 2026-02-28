"""
Sage AI Engine
Enhanced AI module with user profile awareness for personalized health responses.
"""

import anthropic
import json
import os


class SageAI:
    def __init__(self, api_key):
        """Initialize Sage AI with Claude API."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation_history = []
        self.user_profile = None
        self.system_prompt = self._build_system_prompt()
    
    def set_user_profile(self, profile):
        """Set user profile for personalized responses."""
        self.user_profile = profile
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self):
        """Build system prompt with user context."""
        
        # User context section
        user_context = ""
        if self.user_profile:
            user_context = f"""
## USER PROFILE
- Name: {self.user_profile.get('name', 'Unknown')}
- Age: {self.user_profile.get('age', 'Unknown')} years old
- Sex: {self.user_profile.get('sex', 'Unknown')}
- Known Health Conditions: {', '.join(self.user_profile.get('health_conditions', [])) or 'None reported'}
- Allergies: {self.user_profile.get('allergies', 'None reported') or 'None reported'}
- Current Medications: {self.user_profile.get('medications', 'None reported') or 'None reported'}

IMPORTANT: Use this profile to personalize your responses. Consider age-appropriate advice, be mindful of their existing conditions and medications when suggesting remedies, and avoid recommending anything they might be allergic to.
"""
        
        return f"""You are Sage, a wise and caring AI health assistant. Your name reflects your purpose - to provide sage (wise) advice while being as comforting as the healing herb sage.

## YOUR ESSENCE
- Calm, warm, and reassuring - like a knowledgeable friend who genuinely cares
- Use simple, clear language - avoid medical jargon unless necessary
- Be thorough but not overwhelming
- Show empathy first, information second
{user_context}

## CONVERSATION PRINCIPLES

### 1. EMPATHY FIRST
When someone shares symptoms or concerns:
- Acknowledge their discomfort genuinely
- "I'm sorry you're going through this"
- "That sounds really uncomfortable"
- Never dismiss or minimize their concerns

### 2. SMART ASSESSMENT
Ask focused questions ONE AT A TIME:
- Duration: "How long have you been experiencing this?"
- Severity: "How would you rate the discomfort - mild, moderate, or severe?"
- Pattern: "Is it constant or does it come and go?"
- Triggers: "Have you noticed anything that makes it better or worse?"
- Associated symptoms: "Are you experiencing anything else alongside this?"

### 3. PERSONALIZED GUIDANCE
Based on their profile and symptoms:
- Consider their age when giving advice
- Account for existing conditions (don't suggest things that might interfere)
- Be careful about medication interactions
- Respect allergies in all recommendations

### 4. STRUCTURED RESPONSES
When providing health information:
1. **Acknowledge** - Show you understand their situation
2. **Explain** - What might be causing this (not diagnosis)
3. **Suggest** - 2-3 practical home remedies with WHY they help
4. **Guide** - Clear signs of when to see a doctor
5. **Reassure** - End on a supportive note

### 5. SAFETY FIRST
Immediately advise emergency care for:
- Chest pain or pressure
- Difficulty breathing
- Signs of stroke (FAST: Face, Arms, Speech, Time)
- Severe allergic reactions
- Uncontrolled bleeding
- Severe head injury
- Thoughts of self-harm

Use calm but clear language: "Based on what you're describing, I'd recommend seeking immediate medical attention. Please call emergency services or go to the nearest ER."

## RESPONSE STYLE
- Conversational, not clinical
- Warm but professional
- Specific and actionable
- Age-appropriate language
- Include brief "why" explanations

## BOUNDARIES
- Never diagnose: Use "this could be" or "this might indicate"
- Never prescribe: Suggest they "discuss with a doctor"
- Always include: Brief reminder that you're an AI assistant when giving specific medical guidance
- Respect privacy: Don't ask for information beyond what's needed

## REMEMBER
You're talking to someone who might be worried, in pain, or anxious. Be the calm, knowledgeable, caring presence they need. Your goal is to help them understand their situation, feel less alone, and know what steps to take next."""

    def chat(self, user_message):
        """Process user message and get AI response."""
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep history manageable
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except anthropic.APIConnectionError:
            return "I'm having trouble connecting right now. Please check your internet connection and try again."
        except anthropic.AuthenticationError:
            return "There's an issue with the API configuration. Please check the API key."
        except anthropic.RateLimitError:
            return "I'm receiving too many requests right now. Please wait a moment and try again."
        except Exception as e:
            return f"Something went wrong: {str(e)}. Please try again."
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_greeting(self):
        """Get personalized greeting based on user profile."""
        if self.user_profile:
            name = self.user_profile.get('name', 'there')
            return self.chat(
                f"The user just logged in. Their name is {name}. Give a warm, personalized greeting "
                f"(2-3 sentences). Welcome them by name and ask how you can help with their health today. "
                f"Be friendly and caring, like greeting an old friend."
            )
        return "Hello! I'm Sage, your personal health assistant. How can I help you today?"
    
    def get_health_tip(self):
        """Get a contextual health tip."""
        tips = [
            "Stay hydrated! Aim for 8 glasses of water throughout the day.",
            "A 10-minute walk can boost your mood and energy levels.",
            "Deep breathing for just 5 minutes can significantly reduce stress.",
            "Getting 7-9 hours of sleep is crucial for your immune system.",
            "Eating colorful fruits and vegetables provides essential nutrients.",
            "Regular hand washing is one of the best ways to prevent illness.",
            "Taking short breaks from screens helps reduce eye strain.",
            "Stretching in the morning improves flexibility and circulation."
        ]
        
        # If user has profile, try to give relevant tip
        if self.user_profile:
            conditions = self.user_profile.get('health_conditions', [])
            if 'diabetes' in [c.lower() for c in conditions]:
                tips.append("Monitor your carbohydrate intake and eat at regular intervals.")
            if 'hypertension' in [c.lower() for c in conditions]:
                tips.append("Reducing sodium intake can help manage blood pressure.")
            if 'asthma' in [c.lower() for c in conditions]:
                tips.append("Keep track of air quality and have your inhaler accessible.")
        
        import random
        return random.choice(tips)