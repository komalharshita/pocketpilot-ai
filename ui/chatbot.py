"""
Gemini AI Chatbot UI component
Interactive financial assistant powered by Google Gemini
"""

import gradio as gr
from services.gemini_manager import GeminiManager
from services.firebase_manager import FirebaseManager
from typing import List, Tuple

def create_chatbot_tab(gemini_manager: GeminiManager, firebase_manager: FirebaseManager):
    """
    Create the chatbot tab interface
    
    Args:
        gemini_manager: Initialized GeminiManager instance
        firebase_manager: Initialized FirebaseManager instance
    
    Returns:
        Gradio column component
    """
    
    def respond(message: str, chat_history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Generate chatbot response
        
        Args:
            message: User's input message
            chat_history: List of (user_msg, bot_msg) tuples
        
        Returns:
            Tuple of (empty_string, updated_chat_history)
        """
        try:
            if not message or message.strip() == "":
                return "", chat_history
            
            # Fetch receipt context for personalized responses
            receipts = firebase_manager.get_all_receipts()
            
            # Generate response using Gemini
            bot_response = gemini_manager.generate_response(message, receipts)
            
            # Update chat history
            chat_history.append((message, bot_response))
            
            return "", chat_history
        
        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            chat_history.append((message, error_response))
            return "", chat_history
    
    def clear_chat():
        """Clear chat history"""
        return []
    
    with gr.Column() as chatbot_tab:
        gr.Markdown("# 💬 Financial Assistant")
        gr.Markdown("Ask questions about personal finance or your spending patterns")
        
        # Chatbot interface
        chatbot = gr.Chatbot(
            label="PocketPilot AI",
            height=500,
            bubble_full_width=False,
            avatar_images=(None, "🤖")
        )
        
        # Input row
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask me anything about personal finance or your receipts...",
                label="Your Message",
                scale=4,
                lines=1
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Clear button
        clear_btn = gr.Button("🗑️ Clear Conversation", variant="secondary")
        
        # Example questions
        with gr.Accordion("💡 Example Questions", open=False):
            gr.Markdown("""
### General Finance Questions
- How should I start building an emergency fund?
- What's the 50/30/20 budgeting rule?
- How can I reduce my monthly expenses?
- What are the best ways to save for retirement?

### Questions About Your Receipts
- How much have I spent this month?
- What's my biggest spending category?
- Show me my recent grocery purchases
- What's my average transaction amount?

### Financial Tips
- Give me tips for saving money on groceries
- How can I improve my credit score?
- What should I know about investing?
            """)
        
        # Connect submit button and enter key
        submit_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        # Connect clear button
        clear_btn.click(
            fn=clear_chat,
            outputs=[chatbot]
        )
    
    return chatbot_tab