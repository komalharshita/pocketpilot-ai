"""
Analytics Service for PocketPilot AI
Provides data processing and financial analysis capabilities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class FinancialAnalytics:
    """Analytics engine for processing transaction data"""
    
    def __init__(self, transactions_df: pd.DataFrame):
        """
        Initialize analytics with transaction data
        
        Args:
            transactions_df: DataFrame with columns: id, type, amount, category, date, merchant, notes
        """
        self.df = transactions_df.copy()
        if not self.df.empty:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values('date')
    
    def get_summary_stats(self, period: Optional[str] = None) -> Dict:
        """
        Calculate summary statistics for a time period
        
        Args:
            period: 'week', 'month', 'quarter', 'year', or None for all time
            
        Returns:
            Dictionary with summary metrics
        """
        df = self._filter_by_period(period)
        
        if df.empty:
            return {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net_balance': 0.0,
                'transaction_count': 0,
                'avg_transaction': 0.0,
                'largest_expense': 0.0,
                'savings_rate': 0.0
            }
        
        income = df[df['type'] == 'Income']['amount'].sum()
        expenses = df[df['type'] == 'Expense']['amount'].sum()
        balance = income - expenses
        
        expense_transactions = df[df['type'] == 'Expense']
        largest_expense = expense_transactions['amount'].max() if not expense_transactions.empty else 0.0
        avg_transaction = df['amount'].mean()
        
        savings_rate = ((income - expenses) / income * 100) if income > 0 else 0.0
        
        return {
            'total_income': round(income, 2),
            'total_expenses': round(expenses, 2),
            'net_balance': round(balance, 2),
            'transaction_count': len(df),
            'avg_transaction': round(avg_transaction, 2),
            'largest_expense': round(largest_expense, 2),
            'savings_rate': round(savings_rate, 2)
        }
    
    def get_category_breakdown(self, transaction_type: str = 'Expense', 
                               period: Optional[str] = None) -> pd.Series:
        """
        Get spending/income breakdown by category
        
        Args:
            transaction_type: 'Expense' or 'Income'
            period: Time period filter
            
        Returns:
            Series with category totals, sorted descending
        """
        df = self._filter_by_period(period)
        filtered = df[df['type'] == transaction_type]
        
        if filtered.empty:
            return pd.Series(dtype=float)
        
        return filtered.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    def get_time_series_data(self, frequency: str = 'D', 
                            transaction_type: Optional[str] = None) -> pd.DataFrame:
        """
        Get time series data for visualization
        
        Args:
            frequency: 'D' (daily), 'W' (weekly), 'M' (monthly)
            transaction_type: Filter by 'Expense', 'Income', or None for both
            
        Returns:
            DataFrame with date and amount columns
        """
        df = self.df.copy()
        
        if transaction_type:
            df = df[df['type'] == transaction_type]
        
        if df.empty:
            return pd.DataFrame(columns=['date', 'amount'])
        
        # Resample by frequency
        df.set_index('date', inplace=True)
        resampled = df['amount'].resample(frequency).sum().reset_index()
        resampled.columns = ['date', 'amount']
        
        return resampled
    
    def get_spending_trends(self, period: str = 'month') -> Dict:
        """
        Analyze spending trends and changes
        
        Args:
            period: Analysis period ('week', 'month')
            
        Returns:
            Dictionary with trend analysis
        """
        current_period = self._filter_by_period(period)
        
        # Get previous period
        if period == 'week':
            days_back = 14
        elif period == 'month':
            days_back = 60
        else:
            days_back = 30
        
        cutoff_date = datetime.now() - timedelta(days=days_back/2)
        previous_period = self.df[
            (self.df['date'] < cutoff_date) & 
            (self.df['date'] >= cutoff_date - timedelta(days=days_back/2))
        ]
        
        current_expenses = current_period[current_period['type'] == 'Expense']['amount'].sum()
        previous_expenses = previous_period[previous_period['type'] == 'Expense']['amount'].sum()
        
        if previous_expenses > 0:
            change_pct = ((current_expenses - previous_expenses) / previous_expenses) * 100
        else:
            change_pct = 0.0
        
        # Category-wise changes
        current_categories = current_period[current_period['type'] == 'Expense'].groupby('category')['amount'].sum()
        previous_categories = previous_period[previous_period['type'] == 'Expense'].groupby('category')['amount'].sum()
        
        category_changes = {}
        for category in current_categories.index:
            current_amt = current_categories.get(category, 0)
            previous_amt = previous_categories.get(category, 0)
            
            if previous_amt > 0:
                change = ((current_amt - previous_amt) / previous_amt) * 100
            else:
                change = 100.0 if current_amt > 0 else 0.0
            
            category_changes[category] = {
                'current': round(current_amt, 2),
                'previous': round(previous_amt, 2),
                'change_pct': round(change, 2)
            }
        
        return {
            'overall_change_pct': round(change_pct, 2),
            'current_total': round(current_expenses, 2),
            'previous_total': round(previous_expenses, 2),
            'category_changes': category_changes,
            'trend': 'increasing' if change_pct > 5 else 'decreasing' if change_pct < -5 else 'stable'
        }
    
    def get_top_merchants(self, limit: int = 10, 
                         transaction_type: str = 'Expense') -> pd.DataFrame:
        """
        Get top merchants by spending
        
        Args:
            limit: Number of merchants to return
            transaction_type: 'Expense' or 'Income'
            
        Returns:
            DataFrame with merchant, total_amount, transaction_count
        """
        df = self.df[self.df['type'] == transaction_type].copy()
        
        if df.empty:
            return pd.DataFrame(columns=['merchant', 'total_amount', 'transaction_count'])
        
        merchant_stats = df.groupby('merchant').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        
        merchant_stats.columns = ['merchant', 'total_amount', 'transaction_count']
        merchant_stats = merchant_stats.sort_values('total_amount', ascending=False).head(limit)
        
        return merchant_stats
    
    def calculate_budget_adherence(self, budget_dict: Dict[str, float]) -> Dict:
        """
        Calculate how well actual spending matches budget
        
        Args:
            budget_dict: Dictionary with category: budget_amount pairs
            
        Returns:
            Dictionary with adherence metrics per category
        """
        actual_spending = self.get_category_breakdown('Expense', period='month')
        
        adherence = {}
        for category, budget in budget_dict.items():
            actual = actual_spending.get(category, 0.0)
            remaining = budget - actual
            pct_used = (actual / budget * 100) if budget > 0 else 0.0
            
            adherence[category] = {
                'budget': budget,
                'actual': round(actual, 2),
                'remaining': round(remaining, 2),
                'percent_used': round(pct_used, 2),
                'status': 'over' if actual > budget else 'under'
            }
        
        return adherence
    
    def detect_unusual_transactions(self, std_multiplier: float = 2.0) -> pd.DataFrame:
        """
        Detect transactions that are unusually large
        
        Args:
            std_multiplier: Number of standard deviations for threshold
            
        Returns:
            DataFrame of unusual transactions
        """
        expenses = self.df[self.df['type'] == 'Expense'].copy()
        
        if expenses.empty or len(expenses) < 3:
            return pd.DataFrame()
        
        mean_amount = expenses['amount'].mean()
        std_amount = expenses['amount'].std()
        threshold = mean_amount + (std_multiplier * std_amount)
        
        unusual = expenses[expenses['amount'] > threshold]
        
        return unusual[['date', 'amount', 'category', 'merchant', 'notes']]
    
    def get_spending_patterns(self) -> Dict:
        """
        Analyze spending patterns (weekday vs weekend, time of day, etc.)
        
        Returns:
            Dictionary with pattern insights
        """
        df = self.df[self.df['type'] == 'Expense'].copy()
        
        if df.empty:
            return {}
        
        # Weekday vs Weekend
        df['weekday'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['weekday'].isin([5, 6])
        
        weekday_spending = df[~df['is_weekend']]['amount'].sum()
        weekend_spending = df[df['is_weekend']]['amount'].sum()
        
        weekday_avg = df[~df['is_weekend']]['amount'].mean()
        weekend_avg = df[df['is_weekend']]['amount'].mean()
        
        # Most common spending day
        day_totals = df.groupby('weekday')['amount'].sum()
        most_expensive_day = day_totals.idxmax() if not day_totals.empty else None
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'weekday_total': round(weekday_spending, 2),
            'weekend_total': round(weekend_spending, 2),
            'weekday_avg_transaction': round(weekday_avg, 2),
            'weekend_avg_transaction': round(weekend_avg, 2),
            'most_expensive_day': day_names[most_expensive_day] if most_expensive_day is not None else 'N/A',
            'weekend_vs_weekday_ratio': round(weekend_spending / weekday_spending, 2) if weekday_spending > 0 else 0
        }
    
    def forecast_monthly_expenses(self) -> Dict:
        """
        Simple forecast of expected monthly expenses based on current trend
        
        Returns:
            Dictionary with forecast data
        """
        df = self.df[self.df['type'] == 'Expense'].copy()
        
        if df.empty:
            return {'forecast': 0.0, 'confidence': 'low'}
        
        # Get expenses for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_data = df[
            (df['date'].dt.month == current_month) & 
            (df['date'].dt.year == current_year)
        ]
        
        if current_month_data.empty:
            # Use average from previous months
            avg_monthly = df.groupby([df['date'].dt.year, df['date'].dt.month])['amount'].sum().mean()
            return {
                'forecast': round(avg_monthly, 2),
                'confidence': 'medium',
                'method': 'historical_average'
            }
        
        # Calculate daily average and project to end of month
        days_so_far = datetime.now().day
        total_so_far = current_month_data['amount'].sum()
        daily_avg = total_so_far / days_so_far
        
        days_in_month = pd.Timestamp(current_year, current_month, 1).days_in_month
        forecast = daily_avg * days_in_month
        
        return {
            'forecast': round(forecast, 2),
            'spent_so_far': round(total_so_far, 2),
            'days_elapsed': days_so_far,
            'daily_average': round(daily_avg, 2),
            'confidence': 'high',
            'method': 'current_month_projection'
        }
    
    def _filter_by_period(self, period: Optional[str]) -> pd.DataFrame:
        """
        Filter dataframe by time period
        
        Args:
            period: 'week', 'month', 'quarter', 'year', or None
            
        Returns:
            Filtered dataframe
        """
        if period is None:
            return self.df
        
        today = datetime.now()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'quarter':
            start_date = today - timedelta(days=90)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            return self.df
        
        return self.df[self.df['date'] >= start_date]
    
    def export_summary_report(self, filepath: str, period: str = 'month'):
        """
        Export a comprehensive summary report to CSV
        
        Args:
            filepath: Output file path
            period: Time period for report
        """
        summary = self.get_summary_stats(period)
        categories = self.get_category_breakdown('Expense', period)
        trends = self.get_spending_trends(period)
        
        report_data = {
            'Metric': [],
            'Value': []
        }
        
        # Add summary stats
        for key, value in summary.items():
            report_data['Metric'].append(key)
            report_data['Value'].append(value)
        
        # Add category breakdown
        report_data['Metric'].append('\nCategory Breakdown')
        report_data['Value'].append('')
        
        for category, amount in categories.items():
            report_data['Metric'].append(f'  {category}')
            report_data['Value'].append(amount)
        
        df_report = pd.DataFrame(report_data)
        df_report.to_csv(filepath, index=False)


# Standalone utility functions

def calculate_expense_ratio(transactions_df: pd.DataFrame, category: str) -> float:
    """
    Calculate what percentage of total expenses a category represents
    
    Args:
        transactions_df: Transaction data
        category: Category name
        
    Returns:
        Percentage as float
    """
    expenses = transactions_df[transactions_df['type'] == 'Expense']
    total = expenses['amount'].sum()
    category_total = expenses[expenses['category'] == category]['amount'].sum()
    
    return (category_total / total * 100) if total > 0 else 0.0


def get_quick_summary(transactions_df: pd.DataFrame) -> str:
    """
    Generate a quick text summary of finances
    
    Args:
        transactions_df: Transaction data
        
    Returns:
        Formatted string summary
    """
    analytics = FinancialAnalytics(transactions_df)
    stats = analytics.get_summary_stats('month')
    
    summary = f"""
    📊 Monthly Financial Summary
    {'='*40}
    💵 Income:        ₹{stats['total_income']:,.2f}
    💸 Expenses:      ₹{stats['total_expenses']:,.2f}
    💰 Balance:       ₹{stats['net_balance']:,.2f}
    📈 Savings Rate:  {stats['savings_rate']:.1f}%
    🔢 Transactions:  {stats['transaction_count']}
    """
    
    return summary


# Example usage
if __name__ == "__main__":
    # Create sample data
    sample_data = {
        'id': range(1, 11),
        'type': ['Expense'] * 8 + ['Income'] * 2,
        'amount': [250, 50, 150, 80, 300, 120, 200, 90, 5000, 2000],
        'category': ['Food', 'Transport', 'Entertainment', 'Food', 
                    'Shopping', 'Transport', 'Food', 'Bills', 
                    'Allowance', 'Freelance'],
        'date': pd.date_range(start='2024-01-01', periods=10),
        'merchant': ['Restaurant A', 'Uber', 'Cinema', 'Cafe B',
                    'Amazon', 'Metro', 'Restaurant C', 'Electricity',
                    'Parent', 'Client'],
        'notes': [''] * 10
    }
    
    df = pd.DataFrame(sample_data)
    analytics = FinancialAnalytics(df)
    
    # Test various functions
    print("Summary Stats:")
    print(analytics.get_summary_stats('month'))
    
    print("\nCategory Breakdown:")
    print(analytics.get_category_breakdown())
    
    print("\nSpending Patterns:")
    print(analytics.get_spending_patterns())
    
    print("\nForecast:")
    print(analytics.forecast_monthly_expenses())