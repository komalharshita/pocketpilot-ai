"""
Gemini AI Service - Intelligent chatbot with receipt context
Uses Google Gemini API for conversational AI
"""

import streamlit as st
from typing import List, Dict

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiService:
    """
    Service for AI chat functionality using Gemini API
    Provides context-aware responses about receipts
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai not installed")
        
        # Get API key from secrets
        try:
            self.api_key = st.secrets.get("GEMINI_API_KEY", "")
            
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in secrets")
            
            # Initialize client
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-1.5-flash"
            
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {str(e)}")
    
    def chat(
        self, 
        user_message: str, 
        receipts: List[Dict],
        chat_history: List[Dict] = None
    ) -> str:
        """
        Generate AI response with receipt context
        
        Args:
            user_message: User's question
            receipts: List of receipt data for context
            chat_history: Previous conversation (optional)
            
        Returns:
            AI response string
        """
        try:
            # Build context from receipts
            context = self._build_receipt_context(receipts)
            
            # Create system prompt with context
            system_prompt = f"""You are a helpful AI assistant for PocketPilot, a receipt management app.

Your role:
- Help users understand their spending and receipts
- Provide clear, concise answers about their data
- Be friendly and supportive

User's Receipt Data:
{context}

Guidelines:
- Keep responses brief and helpful (2-4 sentences)
- Use ₹ for Indian Rupees when mentioning amounts
- If asked about specific receipts, reference the data above
- If data is insufficient, mention it politely
- Be conversational and natural

Important: You have access to the user's receipt data shown above. Use it to answer their questions accurately."""

            # Build conversation
            conversation = system_prompt + "\n\n"
            
            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    conversation += f"{role}: {msg['content']}\n\n"
            
            # Add current question
            conversation += f"User: {user_message}\n\nAssistant:"
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=conversation
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return "I couldn't generate a response. Please try rephrasing."
                
        except Exception as e:
            error_msg = str(e).lower()
            
            if 'api' in error_msg and 'key' in error_msg:
                return "⚠️ API key error. Please check configuration."
            elif 'quota' in error_msg:
                return "⚠️ API quota exceeded. Please try again later."
            elif 'rate' in error_msg:
                return "⚠️ Too many requests. Please wait a moment."
            else:
                return f"❌ Error: {str(e)[:100]}"
    
    def _build_receipt_context(self, receipts: List[Dict]) -> str:
        """
        Build formatted context string from receipts
        
        Args:
            receipts: List of receipt dictionaries
            
        Returns:
            Formatted context string
        """
        if not receipts:
            return "No receipts available yet."
        
        # Calculate summary statistics
        total_amount = sum(r.get('amount', 0) for r in receipts)
        total_count = len(receipts)
        
        # Get merchant list
        merchants = [r.get('merchant', 'Unknown') for r in receipts]
        unique_merchants = list(set(merchants))
        
        # Build context string
        context = f"""Receipt Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total Receipts: {total_count}
💰 Total Amount: ₹{total_amount:,.2f}
🏪 Unique Merchants: {len(unique_merchants)}

Recent Receipts:
"""
        
        # Add individual receipts (most recent 10)
        sorted_receipts = sorted(
            receipts,
            key=lambda x: x.get('uploaded_at', ''),
            reverse=True
        )
        
        for i, receipt in enumerate(sorted_receipts[:10], 1):
            merchant = receipt.get('merchant', 'Unknown')
            amount = receipt.get('amount', 0)
            date = receipt.get('date', 'N/A')
            items = receipt.get('items', [])
            
            context += f"\n{i}. {merchant}"
            context += f"\n   Amount: ₹{amount:,.2f}"
            context += f"\n   Date: {date}"
            
            if items:
                context += f"\n   Items: {', '.join(items[:3])}"
                if len(items) > 3:
                    context += f" (+{len(items)-3} more)"
            context += "\n"
        
        context += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return context
