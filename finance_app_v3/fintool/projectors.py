# fintool/projectors.py
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List
from .models import Transaction, RecurringItem

def project_future_transactions(recurring_items: List[RecurringItem], days_ahead: int) -> List[Transaction]:
    """Generates a list of future transactions based on recurring rules."""
    projected_transactions = []
    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    for item in recurring_items:
        start_date = datetime.strptime(item.start_date, "%Y-%m-%d")
        
        # Monthly items
        if item.frequency == 'monthly':
            current_date = today.replace(day=item.day_of_month)
            if current_date < today:
                 current_date += relativedelta(months=1)

            while current_date <= end_date:
                if current_date >= start_date:
                    projected_transactions.append(Transaction(
                        id=str(uuid.uuid4()),
                        date=current_date.strftime("%Y-%m-%d"),
                        description=item.description,
                        amount=item.amount,
                        account_id=item.account_id,
                        category=item.category,
                        status="pending"
                    ))
                current_date += relativedelta(months=1)
        
        # Biweekly items (every 14 days)
        elif item.frequency == 'biweekly':
            current_date = start_date
            while current_date <= end_date:
                # Only add dates that are in the future
                if current_date >= today:
                    projected_transactions.append(Transaction(
                        id=str(uuid.uuid4()),
                        date=current_date.strftime("%Y-%m-%d"),
                        description=item.description,
                        amount=item.amount,
                        account_id=item.account_id,
                        category=item.category,
                        status="pending"
                    ))
                # Always advance the date to find the next occurrence
                current_date += timedelta(days=14)

    return projected_transactions