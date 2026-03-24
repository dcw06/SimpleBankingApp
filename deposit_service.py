#!/usr/bin/env python3
"""
Plaid integration for linking bank accounts and transferring money to the app.
Supports Bank of America, WeChat, and other payment methods.
"""

import requests
import json
from datetime import datetime

# Plaid Configuration
PLAID_CLIENT_ID = "69c1bfed5d1f75000c279377"
PLAID_SECRET = "c3127a4d191befaf478276369df1e8"
PLAID_ENV = "sandbox"  # Use 'sandbox' for testing, 'production' for live
# TODO: Switch to 'production' after requesting production credentials from Plaid dashboard

PLAID_AUTH_URL = f"https://{PLAID_ENV}.plaid.com/auth/get"
PLAID_TOKEN_URL = f"https://{PLAID_ENV}.plaid.com/item/public_token/exchange"
PLAID_ACCOUNTS_URL = f"https://{PLAID_ENV}.plaid.com/accounts/balance/get"
PLAID_TRANSACTIONS_URL = f"https://{PLAID_ENV}.plaid.com/transactions/get"
PLAID_TRANSFER_URL = f"https://{PLAID_ENV}.plaid.com/transfer/authorization/create"
PLAID_TRANSFER_CREATE_URL = f"https://{PLAID_ENV}.plaid.com/transfer/create"

# Destination account for transfers (TODO: Update with your app's bank account details)
TRANSFER_DESTINATION = {
    'account_number': 'YOUR_APP_ACCOUNT_NUMBER',
    'routing_number': 'YOUR_APP_ROUTING_NUMBER',
    'account_type': 'checking'  # or 'savings'
}


class PlaidClient:
    """Interface to Plaid API for bank integrations."""
    def __init__(self):
        self.client_id = PLAID_CLIENT_ID
        self.secret = PLAID_SECRET
        self.environment = PLAID_ENV
    
    def exchange_public_token(self, public_token):
        """
        Exchange Plaid public token for access token.
        This is done server-side after user links their bank account.
        """
        try:
            payload = {
                'client_id': self.client_id,
                'secret': self.secret,
                'public_token': public_token
            }
            response = requests.post(PLAID_TOKEN_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token'), None
        except Exception as e:
            return None, f"Failed to exchange token: {str(e)}"
    
    def get_account_balance(self, access_token):
        """Get current balance from linked bank account."""
        try:
            payload = {
                'client_id': self.client_id,
                'secret': self.secret,
                'access_token': access_token
            }
            response = requests.post(PLAID_ACCOUNTS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if 'accounts' in data and len(data['accounts']) > 0:
                account = data['accounts'][0]
                balance = account.get('balances', {}).get('current', 0)
                return balance, None
            return 0, "No accounts found"
        except Exception as e:
            return 0, f"Failed to get balance: {str(e)}"
    
    def get_recent_transactions(self, access_token, days_back=30):
        """Get recent transactions from linked account."""
        try:
            from datetime import datetime, timedelta
            end_date = datetime.now().date().isoformat()
            start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
            
            payload = {
                'client_id': self.client_id,
                'secret': self.secret,
                'access_token': access_token,
                'start_date': start_date,
                'end_date': end_date
            }
            response = requests.post(PLAID_TRANSACTIONS_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            return data.get('transactions', []), None
        except Exception as e:
            return [], f"Failed to get transactions: {str(e)}"
    
    def get_deposit_data(self, access_token):
        """
        Get deposit-specific data from bank (BofA, etc).
        Returns account info and recent activity.
        """
        balance, balance_error = self.get_account_balance(access_token)
        transactions, trans_error = self.get_recent_transactions(access_token)
        
        data = {
            'balance': balance,
            'balance_error': balance_error,
            'transactions': transactions,
            'transactions_error': trans_error,
            'institution': 'Bank of America'  # Auto-detected in real implementation
        }
        
        return data
    
    def create_transfer(self, access_token, amount, account_id):
        """
        Create a real ACH transfer from linked bank account to app account.
        Uses Plaid Transfer API to move funds.
        
        Args:
            access_token: User's Plaid access token
            amount: Transfer amount in dollars
            account_id: User's source bank account ID from Plaid
        
        Returns: (transfer_id, error) or (None, error_msg)
        """
        try:
            payload = {
                'access_token': access_token,
                'account_id': account_id,
                'type': 'debit',  # Money goes OUT of user's bank account
                'network': 'ach',
                'amount': str(amount),
                'description': 'Deposit to SimpleBankingApp',
                'user': {
                    'legal_name': 'SimpleBankingApp User'
                },
                'client_id': self.client_id,
                'secret': self.secret
            }
            
            response = requests.post(PLAID_TRANSFER_CREATE_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            transfer_id = data.get('transfer_id')
            if transfer_id:
                return transfer_id, None
            else:
                error = data.get('error_message', 'Unknown error')
                return None, error
                
        except Exception as e:
            return None, f"Transfer creation failed: {str(e)}"
    
    def get_transfer_status(self, transfer_id):
        """
        Check status of a transfer.
        
        Returns: status (pending, posted, failed) or None
        """
        try:
            payload = {
                'client_id': self.client_id,
                'secret': self.secret,
                'transfer_id': transfer_id
            }
            
            response = requests.post(
                f"https://{self.environment}.plaid.com/transfer/get",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get('transfer', {}).get('status'), None
        except Exception as e:
            return None, f"Failed to get transfer status: {str(e)}"


class DepositService:
    """Handle deposits from external sources into the app."""
    
    def __init__(self, bank_obj):
        self.bank = bank_obj
        self.plaid = PlaidClient()
        self.deposits = []  # Track deposit history
        self.pending_transfers = {}  # Track ACH transfers in progress
    
    def create_deposit_record(self, user_id, account_id, amount, source, source_details=None):
        """
        Record a deposit from external source.
        
        Args:
            user_id: ID of user making deposit
            account_id: Target account in app
            amount: Amount to deposit (in dollars)
            source: 'bofa' | 'wechat' | 'manual'
            source_details: Dict with source-specific info
        
        Returns: (success, message)
        """
        try:
            if amount <= 0:
                return False, "Deposit amount must be positive"
            
            # Get the target account
            account = None
            for acc in self.bank.list_accounts():
                if acc.id == account_id and acc.owner_id == user_id:
                    account = acc
                    break
            
            if not account:
                return False, "Account not found"
            
            # Process deposit based on source
            if source == 'bofa':
                success, msg = self._process_bofa_deposit(amount, source_details)
            elif source == 'wechat':
                success, msg = self._process_wechat_deposit(amount, source_details)
            else:
                success, msg = False, "Unknown deposit source"
            
            if not success:
                return False, msg
            
            # Credit the account
            account.deposit(amount)
            
            # Record deposit history
            self.deposits.append({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'account_id': account_id,
                'amount': amount,
                'source': source,
                'source_details': source_details or {},
                'status': 'completed'
            })
            
            return True, f"Successfully deposited ${amount:.2f} from {source.upper()}"
            
        except Exception as e:
            return False, f"Deposit error: {str(e)}"
    
    def _process_bofa_deposit(self, amount, details):
        """Process deposit from Bank of America via Plaid Transfer API."""
        try:
            if not details or not details.get('access_token'):
                return False, "BofA account not linked"
            
            access_token = details['access_token']
            account_id = details.get('account_id')
            
            # Verify balance is available
            balance, error = self.plaid.get_account_balance(access_token)
            if error:
                return False, f"Could not verify balance: {error}"
            if balance < amount:
                return False, f"Insufficient funds. Available: ${balance:.2f}"
            
            # Create real ACH transfer via Plaid Transfer API
            transfer_id, error = self.plaid.create_transfer(
                access_token=access_token,
                amount=amount,
                account_id=account_id
            )
            
            if error:
                return False, f"Transfer failed: {error}"
            
            if not transfer_id:
                return False, "Transfer creation returned no ID"
            
            # Store transfer ID for status tracking
            if not hasattr(self, 'pending_transfers'):
                self.pending_transfers = {}
            self.pending_transfers[transfer_id] = {
                'amount': amount,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            return True, ""
            
        except Exception as e:
            return False, f"BofA processing error: {str(e)}"
    
    def _process_wechat_deposit(self, amount, details):
        """Process deposit from WeChat Pay."""
        try:
            if not details or not details.get('wechat_id'):
                return False, "WeChat account not linked"
            
            # In production, this would integrate with WeChat Pay API
            # For now, just validate the amount
            if amount <= 0:
                return False, "Invalid amount"
            
            # Log the pending WeChat transaction
            # In real implementation, would create payment URL
            return True, ""
        except Exception as e:
            return False, f"WeChat processing error: {str(e)}"
    
    def get_deposit_history(self, user_id):
        """Get all deposits for a user."""
        return [d for d in self.deposits if d['user_id'] == user_id]
    
    def check_pending_transfers(self):
        """
        Check status of all pending ACH transfers.
        Updates deposit records when transfers complete.
        """
        completed = []
        for transfer_id, info in list(self.pending_transfers.items()):
            status, error = self.plaid.get_transfer_status(transfer_id)
            
            if error:
                continue  # Will retry next time
            
            if status in ['posted', 'completed']:
                info['status'] = 'completed'
                completed.append(transfer_id)
            elif status == 'failed':
                info['status'] = 'failed'
                completed.append(transfer_id)
        
        # Remove completed transfers from pending
        for transfer_id in completed:
            del self.pending_transfers[transfer_id]
        
        return completed


# Singleton instance
_deposit_service = None

def get_deposit_service(bank_obj):
    """Get or create the deposit service."""
    global _deposit_service
    if _deposit_service is None:
        _deposit_service = DepositService(bank_obj)
    return _deposit_service
