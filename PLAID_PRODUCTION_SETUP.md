# Plaid Production Setup Guide

## Step 1: Request Production Credentials

1. Go to https://dashboard.plaid.com
2. Log in with your Plaid account
3. Navigate to **Settings → Team Settings → API Keys**
4. Click **Request Production Access**
5. Fill out the application form:
   - **App Name**: SimpleBankingApp
   - **Use Case**: Personal finance app with bank account linking and ACH transfers
   - **Expected Monthly Active Users**: 1 (testing)
   - **Countries**: United States
   - **Planned Features**: Account verification, ACH transfers to app account

6. Plaid will review (typically 1-3 business days)
7. Once approved, you'll receive:
   - **Production Client ID** (different from sandbox)
   - **Production Secret** (different from sandbox)

## Step 2: Update Code for Production

Once approved, update `deposit_service.py`:

```python
PLAID_ENV = "production"  # Changed from "sandbox"
PLAID_CLIENT_ID = "YOUR_PRODUCTION_CLIENT_ID"
PLAID_SECRET = "YOUR_PRODUCTION_SECRET"
```

## Step 3: Set Up Transfer Destination

For ACH transfers to work, you need a destination bank account where deposits go.

### Option A: Open a Business Bank Account
- Many banks offer ACH receiving capability
- Typical banks: Chase, Bank of America, Stripe Treasury
- Once you have an account, update in `deposit_service.py`:

```python
TRANSFER_DESTINATION = {
    'account_number': 'YOUR_ACCOUNT_NUMBER',
    'routing_number': 'YOUR_ROUTING_NUMBER',
    'account_type': 'checking'  # or 'savings'
}
```

### Option B: Use a Payment Processor
- **Stripe Connect**: Built-in Plaid integration
- **Dwolla**: Specializes in ACH transfers
- **Plaid Deposit**: Works with Plaid sandbox for testing

## Step 4: Test with Sandbox First

Before going production:
1. Keep sandbox credentials in your code initially
2. Test the full Plaid Link flow locally
3. Link a test BofA account (use `user_good` / `pass_good` in Plaid sandbox)
4. Verify transfers appear as "pending" in transfer history
5. Check transfer status using `check_pending_transfers()`

## Step 5: Switch to Production

When ready:
1. Update `PLAID_ENV = "production"`
2. Update `PLAID_CLIENT_ID` and `PLAID_SECRET` with production values
3. Update `TRANSFER_DESTINATION` with your actual bank account
4. Users can now link their real BofA accounts
5. Real ACH transfers will move money from their account → yours

## Testing Checklist

- [ ] Production credentials received from Plaid
- [ ] Destination bank account set up
- [ ] `TRANSFER_DESTINATION` configured in code
- [ ] `PLAID_ENV` set to `"production"`
- [ ] User can click "Link Bank Account" in Settings
- [ ] Plaid Link modal opens in browser
- [ ] User selects Bank of America
- [ ] User authenticates with their BofA credentials
- [ ] App receives access token successfully
- [ ] "✓ Linked" status appears in Settings
- [ ] User can initiate deposit from BofA
- [ ] Transfer appears in pending transfers list
- [ ] Status updates to "posted" after ACH processing (1-2 business days)
- [ ] Money arrives in your destination account

## Important Security Notes

⚠️ **NEVER hardcode secrets in your code for distribution**

For a production app:
- Store `PLAID_CLIENT_ID` and `PLAID_SECRET` as environment variables
- Store `PLAID_SECRET` server-side only (never in client code)
- Never commit credentials to version control

In your actual app (when deploying):
```python
import os

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID', '69c1bfed5d1f75000c279377')
PLAID_SECRET = os.getenv('PLAID_SECRET', 'c3127a4d191befaf478276369df1e8')
```

## Troubleshooting

**"Transfer creation failed: invalid_access_token"**
- Token may be expired or invalid
- User may need to re-link their account

**"Transfer creation failed: insufficient_funds"**
- User's bank account balance is too low
- Check with `get_account_balance()`

**"Invalid client_id or secret"**
- You're using sandbox credentials in production mode
- Update to correct production values

**"Account not found"**
- The account_id passed doesn't exist in the linked bank account
- Make sure you're using account IDs from Plaid, not your app's account IDs
