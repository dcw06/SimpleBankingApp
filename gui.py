#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog, messagebox
import storage
from bank import Bank


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Banking App")
        self.bank: Bank = storage.load_bank()
        self.current_user = None

        frame = tk.Frame(root)
        frame.pack(padx=12, pady=12)

        tk.Button(frame, text="Create User", width=20, command=self.create_user).pack(pady=2)
        tk.Button(frame, text="Switch User", width=20, command=self.switch_user).pack(pady=2)
        tk.Button(frame, text="Create Account", width=20, command=self.create_account).pack(pady=2)
        tk.Button(frame, text="Deposit", width=20, command=self.deposit).pack(pady=2)
        tk.Button(frame, text="Withdraw", width=20, command=self.withdraw).pack(pady=2)
        tk.Button(frame, text="Transfer", width=20, command=self.transfer).pack(pady=2)
        tk.Button(frame, text="List Accounts", width=20, command=self.list_accounts).pack(pady=2)
        tk.Button(frame, text="Save and Quit", width=20, command=self.save_and_quit).pack(pady=6)

        self.status = tk.Label(root, text="No user", anchor="w")
        self.status.pack(fill="x", padx=12)

    def create_user(self):
        uname = simpledialog.askstring("Create User", "Username:")
        if uname:
            u = self.bank.create_user(uname)
            messagebox.showinfo("User Created", f"Created {u.username}\nID: {u.id}")

    def switch_user(self):
        users = self.bank.list_users()
        if not users:
            messagebox.showinfo("No users", "No users exist. Create one first.")
            return
        choices = [f"{u.username} ({u.id})" for u in users]
        sel = simpledialog.askinteger("Switch User", "User number (1-%d):" % len(choices))
        if sel and 1 <= sel <= len(choices):
            self.current_user = users[sel - 1]
            self.status.config(text=f"Current user: {self.current_user.username}")

    def create_account(self):
        name = simpledialog.askstring("Account Name", "Account name:")
        if not name:
            return
        initial = simpledialog.askfloat("Initial Deposit", "Amount:", minvalue=0.0)
        owner_id = self.current_user.id if self.current_user else None
        acc = self.bank.create_account(name, initial or 0.0, owner_id=owner_id)
        messagebox.showinfo("Account Created", f"{acc.name}\nID: {acc.id}")

    def _choose_account(self, prompt="Choose account number:"):
        accounts = self.bank.list_accounts()
        if not accounts:
            messagebox.showinfo("No accounts", "No accounts available.")
            return None
        choices = [f"{a.name} - Owner: {self.bank.get_user(a.owner_id).username if a.owner_id and self.bank.get_user(a.owner_id) else '(no owner)'} - {a.balance:.2f}" for a in accounts]
        sel = simpledialog.askinteger(prompt, "Account number (1-%d):" % len(choices))
        if sel and 1 <= sel <= len(choices):
            return accounts[sel - 1]
        return None

    def deposit(self):
        acc = self._choose_account("Deposit to which account?")
        if not acc:
            return
        amt = simpledialog.askfloat("Amount", "Amount to deposit:")
        if amt:
            try:
                acc.deposit(amt)
                messagebox.showinfo("Deposited", f"New balance: {acc.balance:.2f}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def withdraw(self):
        acc = self._choose_account("Withdraw from which account?")
        if not acc:
            return
        amt = simpledialog.askfloat("Amount", "Amount to withdraw:")
        if amt:
            try:
                acc.withdraw(amt)
                messagebox.showinfo("Withdrawn", f"New balance: {acc.balance:.2f}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def transfer(self):
        from_acc = self._choose_account("Transfer from which account?")
        if not from_acc:
            return
        to_acc = self._choose_account("Transfer to which account?")
        if not to_acc:
            return
        amt = simpledialog.askfloat("Amount", "Amount to transfer:")
        if amt:
            try:
                self.bank.transfer(from_acc.id, to_acc.id, amt)
                messagebox.showinfo("Transferred", "Transfer completed")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def list_accounts(self):
        accounts = self.bank.list_accounts()
        if not accounts:
            messagebox.showinfo("Accounts", "No accounts.")
            return
        text = []
        for a in accounts:
            owner = self.bank.get_user(a.owner_id).username if a.owner_id and self.bank.get_user(a.owner_id) else "(no owner)"
            text.append(f"{a.name} ({a.id})\nOwner: {owner}\nBalance: {a.balance:.2f}\n")
        messagebox.showinfo("Accounts", "\n".join(text))

    def save_and_quit(self):
        storage.save_bank(self.bank)
        self.root.quit()


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    run()
