from __future__ import annotations
import uuid
import hashlib
from typing import Dict, Optional


class User:
    def __init__(self, username: str, id: Optional[str] = None, password_hash: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.password_hash = password_hash
        self.linked_bank_account = None  # Plaid access token for linked BofA account

    def set_password(self, password: str):
        """Hash and store password."""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        if not self.password_hash:
            return False
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "linked_bank_account": self.linked_bank_account
        }

    @classmethod
    def from_dict(cls, d):
        user = cls(username=d["username"], id=d.get("id"), password_hash=d.get("password_hash"))
        user.linked_bank_account = d.get("linked_bank_account")
        return user


class Account:
    def __init__(self, name: str, balance: float = 0.0, owner_id: Optional[str] = None, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.balance = float(balance)
        self.owner_id = owner_id

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def to_dict(self):
        return {"id": self.id, "name": self.name, "balance": self.balance, "owner_id": self.owner_id}

    @classmethod
    def from_dict(cls, d):
        return cls(name=d["name"], balance=d.get("balance", 0.0), owner_id=d.get("owner_id"), id=d.get("id"))


class Bank:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.users: Dict[str, User] = {}

    def create_user(self, username: str, password: str = "") -> User:
        u = User(username)
        if password:
            u.set_password(password)
        self.users[u.id] = u
        return u

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def list_users(self):
        return list(self.users.values())

    def create_account(self, name: str, initial_deposit: float = 0.0, owner_id: Optional[str] = None) -> Account:
        acc = Account(name, initial_deposit, owner_id)
        self.accounts[acc.id] = acc
        return acc

    def get_account(self, acc_id: str) -> Optional[Account]:
        return self.accounts.get(acc_id)

    def list_accounts(self):
        return list(self.accounts.values())

    def list_accounts_for_user(self, user_id: str):
        return [a for a in self.accounts.values() if a.owner_id == user_id]

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username and password. Returns User if valid, None otherwise."""
        for user in self.users.values():
            if user.username == username and user.check_password(password):
                return user
        return None

    def transfer(self, from_id: str, to_id: str, amount: float):
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same account")
        from_acc = self.get_account(from_id)
        to_acc = self.get_account(to_id)
        if not from_acc or not to_acc:
            raise ValueError("Account not found")
        from_acc.withdraw(amount)
        to_acc.deposit(amount)

    def to_dict(self):
        return {
            "users": [u.to_dict() for u in self.users.values()],
            "accounts": [a.to_dict() for a in self.accounts.values()],
        }

    @classmethod
    def from_dict(cls, d):
        b = cls()
        for ud in d.get("users", []):
            u = User.from_dict(ud)
            b.users[u.id] = u
        for ad in d.get("accounts", []):
            a = Account.from_dict(ad)
            b.accounts[a.id] = a
        return b
