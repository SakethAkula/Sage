"""
Sage AI Engine with Vector RAG (Semantic Search)
Handles AI-powered health conversations using Claude API and mathematical embeddings.
"""

import anthropic
import base64
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

class SageAI:
    def __init__(self):
        """Initialize Sage AI with Claude API and load Vector knowledge base."""
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history = []
        self.user_profile = None
        
        # Load the Semantic Embedding Model (Lightweight, perfect for Cloud Run)
        print("Loading Semantic Vector Model (MiniLM)...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load JSON and build the In-Memory Vector Store
        self.knowledge_base = self._load_knowledge_base()
        self._build_vector_store()
        
        self.system_prompt_base = self._build_base_system_prompt()
    
    def _load_knowledge_base(self):
        """Loads the verified medical data."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_dir, 'data', 'health_knowledge.JSON')
            with open(kb_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load knowledge base: {e}")
            return {"topics": []}

    def _build_vector_store(self):
        """Converts the JSON text into Mathematical Vectors (Embeddings)"""
        self.topic_texts = []
        self.topic_data = []
        
        for topic in self.knowledge_base.get("topics", []):
            text_to_embed = f"{topic['name']}. Keywords: {' '.join(topic.get('keywords', []))}"
            self.topic_texts.append(text_to_embed)
            self.topic_data.append(topic)
            
        if self.topic_texts:
            print("Encoding Knowledge Base into Vectors...")
            self.topic_embeddings = self.embedder.encode(self.topic_texts)
        else:
            self.topic_embeddings = []

    def _retrieve_context(self, user_message):
        """Vector RAG Retrieval: Finds context using Cosine Similarity."""
        if len(self.topic_texts) == 0:
            return []

        user_embedding = self.embedder.encode([user_message])
        similarities = cosine_similarity(user_embedding, self.topic_embeddings)[0]
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score > 0.40:
            print(f"Vector Match Found: {self.topic_data[best_idx]['name']} (Confidence: {round(best_score*100, 2)}%)")
            return [self.topic_data[best_idx]]
            
        return []

    def set_user_profile(self, profile):
        """Set user profile for personalized responses."""
        self.user_profile = profile
        self.system_prompt_base = self._build_base_system_prompt()
    
    def _build_base_system_prompt(self):
        """Build the static part of the system prompt."""
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

## STRICT RULES
1. NEVER write long paragraphs or walls of text
2. NEVER give multiple suggestions at once
3. NEVER use bullet points or lists in your first response
4. ALWAYS be conversational and warm
5. For emergencies (chest pain, breathing issues, stroke signs) → immediately say "Please call 108/112 right away!"
6. MEDICAL GROUNDING (VECTOR RAG): If 'RETRIEVED MEDICAL KNOWLEDGE' is provided below, you MUST prioritize these verified facts. You MAY use your extensive medical knowledge to explain these points naturally, but do not contradict the retrieved safety guidelines.
{user_context}
"""

    def chat(self, user_message):
        """Process user message using Vector RAG and get AI response."""
        retrieved_topics = self._retrieve_context(user_message)
        
        rag_context = ""
        if retrieved_topics:
            rag_context = "\n\n## RETRIEVED MEDICAL KNOWLEDGE (Use this safely to anchor your response):\n"
            for topic in retrieved_topics:
                rag_context += f"- Topic: {topic['name']}\n"
                rag_context += f"- Common Causes: {', '.join(topic['common_causes'])}\n"
                rag_context += f"- Safe Home Remedies: {', '.join(topic['home_remedies'])}\n"
                rag_context += f"- When to see a doctor: {', '.join(topic['when_to_see_doctor'])}\n"
        
        dynamic_system_prompt = self.system_prompt_base + rag_context
        
        self.conversation_history.append({"role": "user", "content": user_message})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,
                system=dynamic_system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            return assistant_message
            
        except anthropic.APIError as e:
            print(f"Anthropic API error: {e}")
            return "I'm having trouble connecting right now. Please try again in a moment."
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I encountered an error. Please try again."
    
    def clear_history(self):
        self.conversation_history = []
    
    def analyze_image(self, image_data, file_ext, user_message=""):
        base64_image = base64.b64encode(image_data).decode('utf-8')
        media_types = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'webp': 'image/webp'}
        media_type = media_types.get(file_ext, 'image/jpeg')
        
        image_message = {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}},
                {"type": "text", "text": user_message if user_message else "Please look at this image and help me understand what you see."}
            ]
        }
        
        self.conversation_history.append({"role": "user", "content": f"[Shared an image] {user_message}"})
        
        try:
            messages_with_image = self.conversation_history[:-1] + [image_message]
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                system=self.system_prompt_base + "\n\n## IMAGE ANALYSIS\nDescribe what you observe clearly. Be helpful but don't diagnose.",
                messages=messages_with_image
            )
            assistant_message = response.content[0].text
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            return assistant_message
            
        except Exception as e:
            print(f"Image analysis error: {e}")
            return "I had trouble analyzing that image. Could you try uploading again?"

    def get_greeting(self):
        if self.user_profile and self.user_profile.get('name'):
            name = self.user_profile['name'].split()[0]
            return f"Hello {name}! I'm Sage, your personal health assistant. How are you feeling today?"
        return "Hello! I'm Sage, your personal health assistant. How can I help you today?"

_sage_instances = {}

def get_sage_instance(user_id, user_profile=None):
    if user_id not in _sage_instances:
        _sage_instances[user_id] = SageAI()
    if user_profile:
        _sage_instances[user_id].set_user_profile(user_profile)
    return _sage_instances[user_id]

def clear_sage_instance(user_id):
    if user_id in _sage_instances:
        del _sage_instances[user_id]

def generate_chat_title(first_message):
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": f"""Generate a very short title (2-4 words max) for a health chat that starts with this message: "{first_message}" Just respond with the short title, nothing else."""}]
        )
        title = response.content[0].text.strip().replace('"', '').replace("'", "")[:50]
        return title if title else "Health Chat"
    except Exception as e:
        words = first_message.split()[:4]
        return ' '.join(words)[:50] if words else "Health Chat"