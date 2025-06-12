# fintool/plaid_wrapper.py
"""Wrapper around the Plaid API used by the finance app.

This module provides a thin abstraction over the `plaid-python` SDK so that
other parts of the application do not need to interact with the Plaid client
directly.  All credentials are read from environment variables unless provided
explicitly.

Environment variables used:
    PLAID_CLIENT_ID
    PLAID_SECRET
    PLAID_ENV (optional, defaults to "sandbox")

The Plaid Python package must be installed separately.
"""

from __future__ import annotations

import os
from typing import List, Dict, Any

try:
    from plaid.api import plaid_api
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
except ImportError:  # pragma: no cover - plaid may not be installed in dev env
    plaid_api = None  # type: ignore


class PlaidClientWrapper:
    """Simple wrapper around :class:`plaid_api.PlaidApi`."""

    def __init__(self, client_id: str | None = None, secret: str | None = None, env: str | None = None) -> None:
        if plaid_api is None:
            raise ImportError("plaid-python is required for PlaidClientWrapper")

        self.client_id = client_id or os.getenv("PLAID_CLIENT_ID")
        self.secret = secret or os.getenv("PLAID_SECRET")
        env = env or os.getenv("PLAID_ENV", "sandbox")
        host = plaid_api.Environment.Sandbox if env == "sandbox" else plaid_api.Environment.Production

        configuration = plaid_api.Configuration(
            host=host,
            api_key={"clientId": self.client_id, "secret": self.secret},
        )
        api_client = plaid_api.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def exchange_public_token(self, public_token: str) -> str:
        """Exchange a Link public token for an access token."""
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        return response["access_token"]

    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Return all linked accounts for the given access token."""
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        return response["accounts"]

    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
        count: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return transactions for the specified date range."""
        options = TransactionsGetRequestOptions(count=count, offset=offset)
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=options,
        )
        response = self.client.transactions_get(request)
        return response["transactions"]
