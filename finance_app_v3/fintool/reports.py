# fintool/reports.py
import pandas as pd
from datetime import datetime

def _get_current_apr(row):
    """Helper function to determine the current APR based on the intro deadline."""
    if 'intro_apr_deadline' in row and pd.notna(row['intro_apr_deadline']):
        try:
            deadline = datetime.strptime(str(row['intro_apr_deadline']), "%Y-%m-%d")
            if datetime.now() < deadline:
                return row.get('intro_apr', row.get('apr'))
        except (ValueError, TypeError):
            pass
    return row.get('apr')

def generate_assets_report(accounts_df):
    """Generates a detailed assets report."""
    if accounts_df.empty or 'financial_type' not in accounts_df.columns: return pd.DataFrame()
    assets_df = accounts_df[accounts_df['financial_type'] == 'asset'].copy()
    if assets_df.empty: return pd.DataFrame(columns=['account_name', 'value', 'monthly_income', 'apy', 'asset_class'])

    total_value = assets_df['value'].sum()
    weighted_apy = (assets_df['value'].fillna(0) * assets_df['apy'].fillna(0)).sum()
    avg_apy = (weighted_apy / total_value) if total_value else 0

    total_row = pd.DataFrame([{'account_name': 'Total Assets', 'value': total_value, 'monthly_income': assets_df['monthly_income'].sum(), 'apy': avg_apy}])
    final_df = pd.concat([assets_df, total_row], ignore_index=True)
    report_columns = ['account_name', 'value', 'monthly_income', 'apy', 'asset_class']
    for col in report_columns:
        if col not in final_df.columns: final_df[col] = None
    return final_df[report_columns]

def generate_liabilities_report(accounts_df):
    """Generates a detailed liabilities report."""
    if accounts_df.empty or 'financial_type' not in accounts_df.columns: return pd.DataFrame()
    liabilities_df = accounts_df[accounts_df['financial_type'] == 'liability'].copy()
    if liabilities_df.empty: return pd.DataFrame(columns=['account_name', 'value', 'monthly_payment', 'current_apr', 'due_day', 'status', 'credit_limit', 'available_credit', 'notes'])

    liabilities_df['current_apr'] = liabilities_df.apply(_get_current_apr, axis=1)
    liabilities_df['available_credit'] = liabilities_df.get('credit_limit', 0) - liabilities_df.get('value', 0)

    total_value = liabilities_df['value'].sum()
    weighted_apr = (liabilities_df['value'].fillna(0) * liabilities_df['current_apr'].fillna(0)).sum()
    avg_apr = (weighted_apr / total_value) if total_value else 0
    
    total_row = pd.DataFrame([{'account_name': 'Total Liabilities', 'value': total_value, 'monthly_payment': liabilities_df['monthly_payment'].sum(), 'current_apr': avg_apr, 'credit_limit': liabilities_df['credit_limit'].sum(), 'available_credit': liabilities_df['available_credit'].sum()}])
    final_df = pd.concat([liabilities_df, total_row], ignore_index=True)
    report_columns = ['account_name', 'value', 'monthly_payment', 'current_apr', 'due_day', 'status', 'credit_limit', 'available_credit', 'notes']
    for col in report_columns:
        if col not in final_df.columns: final_df[col] = None
    return final_df[report_columns]

def generate_budget_report(budget_items_df):
    """Generates a detailed monthly budget report."""
    if budget_items_df.empty: return pd.DataFrame()
    report_df = budget_items_df.copy()
        
    report_df['monthly_cost'] = report_df['amount'] / report_df['period_months']
    report_df['per_paycheck_cost'] = report_df['monthly_cost'] / 2
    
    total_row = pd.DataFrame([{'item_name': 'Total Bills', 'monthly_cost': report_df['monthly_cost'].sum(), 'per_paycheck_cost': report_df['per_paycheck_cost'].sum()}])
    report_df = report_df.sort_values(by='due_day', na_position='last')
    final_df = pd.concat([report_df, total_row], ignore_index=True)
    return final_df[['item_name', 'due_day', 'monthly_cost', 'per_paycheck_cost']]

def generate_savings_report(savings_data):
    """Generates a savings contribution report based on base and paid-off debt rules."""
    contributions = []
    base = savings_data.get('base_contribution', {})
    if base: contributions.append({'contribution_name': base.get('name'), 'monthly_amount': base.get('monthly_amount', 0)})
        
    for debt in savings_data.get('paid_off_debt_contributions', []):
        contributions.append({'contribution_name': debt.get('name'), 'monthly_amount': debt.get('monthly_amount', 0)})

    if not contributions: return pd.DataFrame()
    report_df = pd.DataFrame(contributions)
    report_df['per_paycheck_contribution'] = report_df['monthly_amount'] / 2
    
    total_row = pd.DataFrame([{'contribution_name': 'Total Savings Contributions', 'monthly_amount': report_df['monthly_amount'].sum(), 'per_paycheck_contribution': report_df['per_paycheck_cost'].sum()}])
    final_report_df = pd.concat([report_df, total_row], ignore_index=True)
    return final_report_df

def generate_cashflow_summary(master_accounts_df, budget_items_df, savings_data):
    """
    Generates a high-level summary of monthly income, expenses, and savings.
    This version is hardened against missing data.
    """
    # 1. Calculate Total Income safely
    total_income = 0
    if not master_accounts_df.empty and 'financial_type' in master_accounts_df.columns:
        assets_df = master_accounts_df[master_accounts_df['financial_type'] == 'asset']
        if 'monthly_income' in assets_df.columns:
            total_income = assets_df['monthly_income'].sum()
    
    # 2. Calculate Total Expenses safely
    total_expenses = 0
    # THIS IS THE CORRECTED LOGIC BLOCK:
    if not budget_items_df.empty and 'amount' in budget_items_df.columns and 'period_months' in budget_items_df.columns:
        total_expenses = (budget_items_df['amount'] / budget_items_df['period_months']).sum()
    
    # 3. Calculate Total Savings safely
    base_savings = savings_data.get('base_contribution', {}).get('monthly_amount', 0)
    paid_off_debt_savings = sum(
        item.get('monthly_amount', 0) 
        for item in savings_data.get('paid_off_debt_contributions', [])
    )
    total_savings = base_savings + paid_off_debt_savings
    
    # 4. Calculate the Remainder
    remainder = total_income - total_expenses - total_savings
    
    # 5. Create the final summary DataFrame
    summary_data = {
        'Monthly': [total_income, total_expenses, total_savings, remainder],
        'Half': [(total_income / 2), (total_expenses / 2), (total_savings / 2), (remainder / 2)]
    }
    index_labels = ['Total Income', 'Total Expenses', 'Total Savings', 'Remainder']
    
    summary_df = pd.DataFrame(summary_data, index=index_labels)
    
    return summary_df