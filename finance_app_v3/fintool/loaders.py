import json
import pandas as pd
from .models import Transaction

def load_data():
    """Loads the user's transaction history from transactions.json."""
    
    # This function is now only responsible for loading the transaction ledger.
    # The main master files are loaded directly in the notebook.
    try:
        with open('finance_data/transactions.json', 'r') as f:
            transactions_data = json.load(f)
            # Use the Pydantic model to validate the data
            transactions = [Transaction(**t) for t in transactions_data]
            
    except FileNotFoundError:
        print("⚠️ Warning: 'finance_data/transactions.json' not found. Returning empty list.")
        transactions = []
    except json.JSONDecodeError:
        print("❌ Error: Could not decode 'finance_data/transactions.json'. Is it valid JSON?")
        transactions = []

    # Return empty lists for the deprecated account and recurring items
    # to maintain compatibility with the function's expected output signature.
    return [], transactions, []