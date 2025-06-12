# fintool/__init__.py
"""
This file makes the 'fintool' directory a Python package and
exposes its key functions at the top level for easy access.
"""

from .loaders import load_data
from .projectors import project_future_transactions

# Import the functions that currently exist in reports.py
from .reports import generate_assets_report
from .reports import generate_liabilities_report
from .reports import generate_budget_report
from .reports import generate_savings_report
from .reports import generate_cashflow_summary
from .plaid_wrapper import PlaidClientWrapper


print("✅ Personal finance toolkit 'fintool' initialized.")