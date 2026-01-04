"""
Gemini API Integration for PocketPilot AI
Provides conversational AI capabilities for financial insights and advice
"""

import os
from google import genai
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key. If None, reads from environment variable
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro-001')
        
    def build_context_prompt(self, transactions_df: pd.DataFrame, user_query: str) -> str:
        """
        Build a structured prompt with transaction context
        
        Args:
            transactions_df: DataFrame containing transaction history
            user_query: User's question or query
            
        Returns:
            Formatted prompt string
        """
        # Calculate summary statistics
        total_income = transactions_df[transactions_df['type'] == 'Income']['amount'].sum()
        total_expenses = transactions_df[transactions_df['type'] == 'Expense']['amount'].sum()
        balance = total_income - total_expenses
        
        # Get top spending categories
        expense_df = transactions_df[transactions_df['type'] == 'Expense']
        if not expense_df.empty:
            category_summary = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
            categories_text = "\n".join([f"  - {cat}: ₹{amt:,.2f}" for cat, amt in category_summary.items()])
        else:
            categories_text = "  No expense data available"
        
        # Get recent transactions (last 10)
        recent_transactions = transactions_df.sort_values('date', ascending=False).head(10)
        transactions_text = ""
        for _, row in recent_transactions.iterrows():
            transactions_text += f"  - {row['date'].strftime('%Y-%m-%d')}: {row['type']} of ₹{row['amount']:,.2f} in {row['category']} ({row['merchant']})\n"
        
        # Build prompt
        prompt = f"""You are PocketPilot, a friendly and helpful AI financial assistant for students and young professionals.
        
FINANCIAL SUMMARY:
- Total Income: ₹{total_income:,.2f}
- Total Expenses: ₹{total_expenses:,.2f}
- Current Balance: ₹{balance:,.2f}

TOP SPENDING CATEGORIES:
{categories_text}

RECENT TRANSACTIONS:
{transactions_text}

USER QUESTION: {user_query}

Please provide a helpful, student-friendly response that:
1. Directly answers their question using the transaction data above
2. Provides 3-5 actionable, specific tips or insights
3. Uses a warm, conversational tone
4. Includes relevant emojis for better readability
5. Keeps the response concise (200-300 words)
6. Focuses on practical advice suitable for students/young professionals

Remember: Be encouraging, avoid financial jargon, and make the advice actionable!
"""
        return prompt
    
    def get_financial_insights(self, transactions_df: pd.DataFrame, user_query: str) -> str:
        """
        Get AI-powered financial insights based on transaction history
        
        Args:
            transactions_df: DataFrame containing transaction history
            user_query: User's question
            
        Returns:
            AI-generated response string
        """
        try:
            prompt = self.build_context_prompt(transactions_df, user_query)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error getting insights: {str(e)}\n\nPlease check your API key and try again."
    
    def get_budget_suggestions(self, transactions_df: pd.DataFrame, monthly_income: float) -> str:
        """
        Generate personalized budget suggestions
        
        Args:
            transactions_df: DataFrame containing transaction history
            monthly_income: User's monthly income
            
        Returns:
            Budget suggestions as formatted string
        """
        try:
            expense_df = transactions_df[transactions_df['type'] == 'Expense']
            total_expenses = expense_df['amount'].sum()
            category_breakdown = expense_df.groupby('category')['amount'].sum().to_dict()
            
            prompt = f"""As PocketPilot, a financial advisor for students, create a personalized monthly budget plan.

CURRENT SITUATION:
- Monthly Income: ₹{monthly_income:,.2f}
- Current Total Expenses: ₹{total_expenses:,.2f}
- Spending by Category: {category_breakdown}

Create a budget plan that:
1. Follows the 50-30-20 rule (50% needs, 30% wants, 20% savings)
2. Suggests specific amounts for each major category
3. Identifies areas where the user is overspending
4. Provides 5-7 actionable tips to reduce expenses
5. Is realistic and achievable for a student

Format the response with clear sections, emojis, and specific rupee amounts.
"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error generating budget: {str(e)}"
    
    def analyze_spending_pattern(self, transactions_df: pd.DataFrame) -> str:
        """
        Analyze spending patterns and provide insights
        
        Args:
            transactions_df: DataFrame containing transaction history
            
        Returns:
            Analysis and insights as formatted string
        """
        try:
            # Calculate various metrics
            expense_df = transactions_df[transactions_df['type'] == 'Expense']
            
            if expense_df.empty:
                return "📭 Not enough transaction data to analyze patterns. Start tracking your expenses!"
            
            daily_avg = expense_df.groupby(expense_df['date'].dt.date)['amount'].sum().mean()
            top_category = expense_df.groupby('category')['amount'].sum().idxmax()
            top_category_amount = expense_df.groupby('category')['amount'].sum().max()
            
            # Get weekday vs weekend spending
            expense_df['weekday'] = expense_df['date'].dt.dayofweek
            weekday_spending = expense_df[expense_df['weekday'] < 5]['amount'].sum()
            weekend_spending = expense_df[expense_df['weekday'] >= 5]['amount'].sum()
            
            prompt = f"""As PocketPilot, analyze these spending patterns for a student:

SPENDING METRICS:
- Average daily spending: ₹{daily_avg:,.2f}
- Top spending category: {top_category} (₹{top_category_amount:,.2f})
- Weekday spending: ₹{weekday_spending:,.2f}
- Weekend spending: ₹{weekend_spending:,.2f}

Provide:
1. Key observations about their spending habits
2. Comparison of weekday vs weekend spending with insights
3. Pattern identification (e.g., impulse purchases, regular bills)
4. 5 specific, actionable recommendations to improve spending habits
5. Positive reinforcement for good habits (if any)

Keep it friendly, encouraging, and student-focused with emojis and clear formatting.
"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error analyzing patterns: {str(e)}"
    
    def get_savings_goal_plan(self, 
                              transactions_df: pd.DataFrame, 
                              goal_amount: float, 
                              target_months: int) -> str:
        """
        Create a savings plan to reach a financial goal
        
        Args:
            transactions_df: DataFrame containing transaction history
            goal_amount: Target savings amount
            target_months: Number of months to achieve goal
            
        Returns:
            Personalized savings plan
        """
        try:
            income_df = transactions_df[transactions_df['type'] == 'Income']
            expense_df = transactions_df[transactions_df['type'] == 'Expense']
            
            avg_monthly_income = income_df['amount'].sum() / max(1, len(income_df))
            avg_monthly_expenses = expense_df['amount'].sum() / max(1, len(expense_df))
            monthly_savings_needed = goal_amount / target_months
            
            prompt = f"""As PocketPilot, create a realistic savings plan for a student's financial goal.

GOAL DETAILS:
- Target Amount: ₹{goal_amount:,.2f}
- Timeline: {target_months} months
- Required Monthly Savings: ₹{monthly_savings_needed:,.2f}

CURRENT FINANCES:
- Average Monthly Income: ₹{avg_monthly_income:,.2f}
- Average Monthly Expenses: ₹{avg_monthly_expenses:,.2f}

Create a plan that includes:
1. Assessment of feasibility
2. Month-by-month savings milestones
3. Specific expense categories to reduce with amounts
4. Alternative income ideas suitable for students
5. Motivational tips to stay on track
6. What to do if they miss a month

Make it practical, encouraging, and achievable!
"""
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error creating savings plan: {str(e)}"


# Standalone functions for easy integration

def get_quick_insight(transactions_df: pd.DataFrame, query: str, api_key: Optional[str] = None) -> str:
    """
    Quick function to get AI insights without instantiating the class
    
    Args:
        transactions_df: Transaction data
        query: User question
        api_key: Optional API key
        
    Returns:
        AI response
    """
    try:
        client = GeminiClient(api_key)
        return client.get_financial_insights(transactions_df, query)
    except Exception as e:
        return f"⚠️ Could not connect to Gemini API: {str(e)}\n\nPlease ensure your API key is set correctly."


def generate_monthly_report(transactions_df: pd.DataFrame, api_key: Optional[str] = None) -> str:
    """
    Generate a comprehensive monthly financial report
    
    Args:
        transactions_df: Transaction data for the month
        api_key: Optional API key
        
    Returns:
        Formatted monthly report
    """
    try:
        client = GeminiClient(api_key)
        query = "Generate a comprehensive monthly financial report with insights, achievements, and recommendations for next month."
        return client.get_financial_insights(transactions_df, query)
    except Exception as e:
        return f"⚠️ Could not generate report: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'type': ['Expense', 'Expense', 'Income', 'Expense'],
        'amount': [250.0, 50.0, 5000.0, 150.0],
        'category': ['Food', 'Transport', 'Allowance', 'Entertainment'],
        'date': pd.date_range(start='2024-01-01', periods=4),
        'merchant': ['Restaurant', 'Uber', 'Parent', 'Movie']
    }
    
    df = pd.DataFrame(sample_data)
    
    try:
        client = GeminiClient()
        response = client.get_financial_insights(df, "How much did I spend on food this month?")
        print("Response:", response)
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure to set GOOGLE_API_KEY in your environment variables")
