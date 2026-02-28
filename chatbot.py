"""
MediBot - AI Healthcare Chatbot
Main chatbot interface powered by Claude AI.
"""

from ai_engine import AIEngine


class MediBot:
    def __init__(self, api_key):
        """Initialize MediBot with AI engine."""
        print("\n🔄 Initializing MediBot...")
        self.ai = AIEngine(api_key)
        self.user_name = None
        print("✓ AI Engine ready")
        
    def greet(self):
        """Display welcome message and get user's name."""
        print("\n" + "="*60)
        print("  🏥 MediBot - AI Healthcare Assistant")
        print("  Powered by Claude AI")
        print("="*60)
        print("\nHello! I'm MediBot, your AI health assistant.")
        print("I can help you with:")
        print("  • Understanding your symptoms")
        print("  • Suggesting home remedies")
        print("  • Advising when to see a doctor")
        print("\nCommands: 'tip' - health tip | 'clear' - new session | 'quit' - exit")
        print("-" * 60)
        
        # Get user's name
        self.user_name = input("\nWhat's your name? ").strip()
        if not self.user_name:
            self.user_name = "Friend"
        
        # AI-powered personalized greeting
        greeting = self.ai.chat(
            f"The user's name is {self.user_name}. Give a brief, warm greeting "
            f"(2-3 sentences) and ask how you can help with their health today."
        )
        print(f"\nMediBot: {greeting}\n")
    
    def handle_command(self, user_input):
        """Handle special commands. Returns True if command handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit', 'bye', 'goodbye']:
            farewell = self.ai.chat(
                f"User {self.user_name} is leaving. Give a brief, caring goodbye "
                f"(1-2 sentences) reminding them to take care."
            )
            print(f"\nMediBot: {farewell}\n")
            return 'quit'
        
        if command == 'tip':
            tip = self.ai.get_health_tip()
            print(f"\nMediBot: 💡 Health Tip: {tip}\n")
            return True
        
        if command == 'clear':
            self.ai.clear_history()
            print("\nMediBot: ✓ Started a new conversation. How can I help you?\n")
            return True
        
        if command == 'help':
            print("\nMediBot: I can help you with:")
            print("  • Describe any symptoms you're experiencing")
            print("  • Ask health questions")
            print("  • Get home remedy suggestions")
            print("  • Know when to see a doctor")
            print("\nJust tell me what's bothering you!\n")
            return True
        
        return False
    
    def chat(self):
        """Main chat loop."""
        self.greet()
        
        while True:
            try:
                user_input = input(f"{self.user_name}: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nMediBot: Take care! 🏥\n")
                break
            
            if not user_input:
                continue
            
            # Check for commands
            cmd_result = self.handle_command(user_input)
            if cmd_result == 'quit':
                break
            if cmd_result:
                continue
            
            # Get AI response
            response = self.ai.chat(user_input)
            print(f"\nMediBot: {response}\n")


def main():
    """Main entry point."""
    # API Key
    API_KEY = "YOUR-APIKEY-HERE"
    
    try:
        bot = MediBot(api_key=API_KEY)
        bot.chat()
    except Exception as e:
        print(f"\n❌ Error starting MediBot: {e}")
        print("Make sure you have installed: pip install anthropic")


if __name__ == "__main__":
    main()