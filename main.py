#!/usr/bin/env python3
from bank import Bank
import storage
import sys
from typing import Optional


def prompt_float(prompt: str) -> float:
	while True:
		try:
			return float(input(prompt).strip() or "0")
		except ValueError:
			print("Please enter a valid number.")


def choose_account(bank: Bank, prompt_text: str = "Choose account by number: "):
	accounts = bank.list_accounts()
	if not accounts:
		print("No accounts available.")
		return None
	for i, a in enumerate(accounts, 1):
		owner = bank.get_user(a.owner_id).username if a.owner_id and bank.get_user(a.owner_id) else "(no owner)"
		print(f"{i}. {a.name} ({a.id}) - Owner: {owner} - Balance: {a.balance:.2f}")
	while True:
		try:
			choice = int(input(prompt_text).strip())
			if 1 <= choice <= len(accounts):
				return accounts[choice - 1]
		except ValueError:
			pass
		print("Invalid choice.")


def choose_user(bank: Bank, prompt_text: str = "Choose user by number: ") -> Optional[object]:
	users = bank.list_users()
	if not users:
		print("No users available.")
		return None
	for i, u in enumerate(users, 1):
		print(f"{i}. {u.username} ({u.id})")
	while True:
		try:
			choice = int(input(prompt_text).strip())
			if 1 <= choice <= len(users):
				return users[choice - 1]
		except ValueError:
			pass
		print("Invalid choice.")


def main():
	bank = storage.load_bank()
	current_user: Optional[object] = None
	print("Simple Banking App — Basic CLI")
	while True:
		print("\nOptions:")
		print("0) Create user")
		print("0.1) Switch user")
		print("1) Create account")
		print("2) Deposit")
		print("3) Withdraw")
		print("4) Transfer")
		print("5) Show balance")
		print("6) List accounts")
		print("7) Save and exit")
		choice = input("Select an option: ").strip()
		if choice == "0":
			uname = input("Username: ").strip()
			if uname:
				u = bank.create_user(uname)
				print(f"Created user {u.username} with id {u.id}")
		elif choice == "0.1":
			u = choose_user(bank)
			if u:
				current_user = u
				print(f"Switched to user {u.username}")
		elif choice == "1":
			name = input("Account name: ").strip()
			init = prompt_float("Initial deposit (0 for none): ")
			owner_id = current_user.id if current_user else None
			acc = bank.create_account(name, init, owner_id=owner_id)
			print(f"Created account {acc.name} with id {acc.id}")
		elif choice == "2":
			acc = choose_account(bank, "Deposit to which account number: ")
			if acc:
				amt = prompt_float("Amount to deposit: ")
				try:
					acc.deposit(amt)
					print(f"Deposited {amt:.2f}. New balance {acc.balance:.2f}")
				except ValueError as e:
					print(e)
		elif choice == "3":
			acc = choose_account(bank, "Withdraw from which account number: ")
			if acc:
				amt = prompt_float("Amount to withdraw: ")
				try:
					acc.withdraw(amt)
					print(f"Withdrew {amt:.2f}. New balance {acc.balance:.2f}")
				except ValueError as e:
					print(e)
		elif choice == "4":
			print("From account:")
			from_acc = choose_account(bank, "From which account number: ")
			if from_acc:
				print("To account:")
				to_acc = choose_account(bank, "To which account number: ")
				if to_acc:
					amt = prompt_float("Amount to transfer: ")
					try:
						bank.transfer(from_acc.id, to_acc.id, amt)
						print("Transfer completed.")
					except ValueError as e:
						print(e)
		elif choice == "5":
			acc = choose_account(bank, "Show balance for which account number: ")
			if acc:
				print(f"{acc.name} balance: {acc.balance:.2f}")
		elif choice == "6":
			accounts = bank.list_accounts()
			if not accounts:
				print("No accounts.")
			else:
				for a in accounts:
					owner = bank.get_user(a.owner_id).username if a.owner_id and bank.get_user(a.owner_id) else "(no owner)"
					print(f"- {a.name} ({a.id}) Owner: {owner}: {a.balance:.2f}")
		elif choice == "7" or choice.lower() in ("q", "exit"):
			storage.save_bank(bank)
			print("Saved. Goodbye.")
			sys.exit(0)
		else:
			print("Unknown option.")


if __name__ == "__main__":
	main()
