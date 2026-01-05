"""
Gemini AI Manager for chatbot functionality
Handles conversation with Gemini API and provides financial insights
"""

import google.generativeai as genai
from typing import List, Dict
from config.settings import Settings

class GeminiManager:
    """Manages interactions with Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API"""
        try:
            # Configure Gemini API
            genai.configure(api_key=Settings.GEMINI_API_KEY)
            
            # Initialize the model
            self.model = genai.GenerativeModel(Settings.GEMINI_MODEL)
            
            # System instruction for the chatbot
            self.system_instruction = """You are PocketPilot AI, a helpful personal finance assistant.
            
Your role is to:
1. Answer general personal finance questions (budgeting, saving, investing, etc.)
2. Provide insights about the user's receipt data when available
3. Help users understand their spending patterns
4. Offer practical financial advice

Always be:
- Clear and concise
- Friendly and supportive
- Financially responsible in your recommendations
- Honest when you don't have specific user data

When discussing user receipts, analyze the data provided and give specific insights."""
            
            print("✓ Gemini API initialized successfully")
        
        except Exception as e:
            print(f"✗ Gemini initialization error: {e}")
            raise
    
    def generate_response(self, user_message: str, receipt_context: List[Dict] = None) -> str:
        """
        Generate a response using Gemini API
        
        Args:
            user_message: User's input message
            receipt_context: Optional list of receipt data for context
        
        Returns:
            Gemini's response text
        """
        try:
            # Build the prompt with context
            full_prompt = self._build_prompt(user_message, receipt_context)
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
        except Exception as e:
            print(f"✗ Gemini API error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _build_prompt(self, user_message: str, receipt_context: List[Dict] = None) -> str:
        """
        Build a complete prompt with system instruction and context
        
        Args:
            user_message: User's input message
            receipt_context: Optional receipt data for context
        
        Returns:
            Complete prompt string
        """
        prompt_parts = [self.system_instruction]
        
        # Add receipt context if available
        if receipt_context and len(receipt_context) > 0:
            prompt_parts.append("\n\n--- USER'S RECEIPT DATA ---")
            
            # Summarize receipt data
            total_spent = sum(r.get('total_amount', 0) for r in receipt_context)
            categories = {}
            
            for receipt in receipt_context:
                category = receipt.get('category', 'Other')
                amount = receipt.get('total_amount', 0)
                categories[category] = categories.get(category, 0) + amount
            
            prompt_parts.append(f"\nTotal receipts: {len(receipt_context)}")
            prompt_parts.append(f"Total spent: ${total_spent:.2f}")
            prompt_parts.append(f"\nSpending by category:")
            
            for category, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                prompt_parts.append(f"  - {category}: ${amount:.2f}")
            
            # Add recent receipts
            prompt_parts.append(f"\nRecent receipts:")
            for receipt in receipt_context[:5]:  # Show last 5
                merchant = receipt.get('merchant_name', 'Unknown')
                amount = receipt.get('total_amount', 0)
                date = receipt.get('transaction_date', 'Unknown')
                category = receipt.get('category', 'Other')
                prompt_parts.append(f"  - {merchant}: ${amount:.2f} on {date} ({category})")
            
            prompt_parts.append("\n--- END OF RECEIPT DATA ---\n")
        
        # Add user message
        prompt_parts.append(f"\nUser: {user_message}")
        
        return "\n".join(prompt_parts)
    
    def chat(self, messages: List[Dict[str, str]], receipt_context: List[Dict] = None) -> str:
        """
        Handle multi-turn conversation
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            receipt_context: Optional receipt data for context
        
        Returns:
            Gemini's response text
        """
        try:
            # Start a chat session
            chat = self.model.start_chat(history=[])
            
            # Add context as first message if available
            if receipt_context:
                context_message = self._build_context_summary(receipt_context)
                chat.send_message(context_message)
            
            # Process conversation history
            for msg in messages[:-1]:  # All but the last message
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])
            
            # Send the last user message and get response
            last_message = messages[-1]['content']
            response = chat.send_message(last_message)
            
            return response.text
        
        except Exception as e:
            print(f"✗ Gemini chat error: {e}")
            return f"Error: {str(e)}"
    
    def _build_context_summary(self, receipt_context: List[Dict]) -> str:
        """
        Build a summary of receipt context for chat
        
        Args:
            receipt_context: List of receipt dictionaries
        
        Returns:
            Summary string
        """
        if not receipt_context:
            return "No receipt data available."
        
        total_spent = sum(r.get('total_amount', 0) for r in receipt_context)
        categories = {}
        
        for receipt in receipt_context:
            category = receipt.get('category', 'Other')
            amount = receipt.get('total_amount', 0)
            categories[category] = categories.get(category, 0) + amount
        
        summary = f"User has {len(receipt_context)} receipts totaling ${total_spent:.2f}. "
        summary += "Spending by category: " + ", ".join([f"{cat}: ${amt:.2f}" for cat, amt in categories.items()])
        
        return summary