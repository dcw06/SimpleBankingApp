# Simple Banking App

A full-featured banking application with CLI and GUI support, user authentication, account management, and persistent storage using JSON.

## Features

- **User Authentication**: Create accounts and login with username/password
- **Account Management**: Create multiple accounts per user, view balances
- **Banking Operations**: Deposits, withdrawals, and transfers between accounts
- **Data Persistence**: All data saved to `bank_data.json`
- **Desktop App**: Packaged as a standalone macOS application

## Running the App

### CLI Version
```bash
python3 main.py
```

### GUI Version (Recommended)
```bash
python3 gui_app.py
```

Features in the GUI:
- **Login Page**: Create new account or login with username/password
- **Home Dashboard**: View your account overview and total balance
- **Accounts Page**: See all your accounts and their balances
- **Deposit**: Add money to your accounts
- **Withdraw**: Withdraw money from accounts
- **Transfer**: Send money between your accounts or other users' accounts
- **Settings**: Create new accounts

## Packaging for macOS

To create a standalone macOS app:

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
. .venv/bin/activate
```

2. Install dependencies:
```bash
pip install pyinstaller
```

3. Build the app:
```bash
./build_mac.sh
```

4. Move to Applications (optional):
```bash
mv dist/SimpleBankingApp ~/Desktop/
# or
mv dist/SimpleBankingApp ~/Applications/SimpleBankingApp.app
```

The app is now ready to use as a standalone desktop application.

