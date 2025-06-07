# fintool/models.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Account(BaseModel):
    account_id: str
    account_name: str
    account_type: Literal['checking', 'credit_card', 'investment', 'savings']
    current_balance: float
    last_updated: str

class Transaction(BaseModel):
    id: str
    date: str
    description: str
    amount: float
    account_id: str
    category: str
    status: Literal['posted', 'pending']

class RecurringItem(BaseModel):
    recurring_id: str
    description: str
    amount: float
    category: str
    account_id: str
    frequency: Literal['monthly', 'biweekly', 'annual']
    start_date: str
    day_of_month: int = None # For monthly items

class MasterAccount(BaseModel):
    account_id: str
    account_name: str
    financial_type: Literal['asset', 'liability']
    
    # --- Universal Fields ---
    value: float
    status: Optional[str] = None
    notes: Optional[str] = None

    # --- Asset-Specific Fields ---
    asset_class: Optional[str] = None
    monthly_income: Optional[float] = None
    apy: Optional[float] = None # Annual Percentage Yield
    
    # --- Liability-Specific Fields ---
    liability_class: Optional[str] = None
    monthly_payment: Optional[float] = None # This is your "Monthly Minimum"
    apr: Optional[float] = None # The standard APR
    due_day: Optional[int] = None # Day of the month payment is due
    paying_account_id: Optional[str] = None # The account used to pay the bill
    
    # --- Credit-Card-Specific Fields ---
    credit_limit: Optional[float] = None
    intro_apr: Optional[float] = None
    intro_apr_deadline: Optional[str] = None # Format: "YYYY-MM-DD"

class ExpenseBudget(BaseModel):
    category: str
    budgeted_amount: float

class BudgetItem(BaseModel):
    item_id: str
    item_name: str
    expense_type: Literal['fixed', 'variable'] # Fixed = bill, Variable = estimate
    amount: float # The actual cost of the item when it occurs
    period_months: float # The frequency in months (e.g., 1=monthly, 2=every 2 months, 0.5=twice a month)
    due_day: Optional[int] = None # For fixed bills