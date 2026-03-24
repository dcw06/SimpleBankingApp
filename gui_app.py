#!/usr/bin/env python3
import tkinter as tk
from tkinter import simpledialog, messagebox
import storage
from bank import Bank
from google_auth import authenticate_with_google
from deposit_service import get_deposit_service

# Professional Color Scheme
PRIMARY_COLOR = "#1E3A8A"      # Deep blue
SECONDARY_COLOR = "#10B981"    # Green
ACCENT_COLOR = "#F59E0B"       # Amber
BG_COLOR = "#F3F4F6"           # Light gray
CARD_BG = "#FFFFFF"            # White
TEXT_COLOR = "#1F2937"         # Dark gray
BORDER_COLOR = "#E5E7EB"       # Light border

# Typography
TITLE_FONT = ("Segoe UI", 24, "bold")
HEADING_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 12)
SMALL_FONT = ("Segoe UI", 10)


def darken_color(hex_color, percent=20):
    """Darken a hex color by percentage for hover effects."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = max(0, int(r * (1 - percent/100)))
    g = max(0, int(g * (1 - percent/100)))
    b = max(0, int(b * (1 - percent/100)))
    return f"#{r:02x}{g:02x}{b:02x}"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Banking App")
        self.root.geometry("600x700")
        self.root.configure(bg=BG_COLOR)
        self.bank: Bank = storage.load_bank()
        self.deposit_service = get_deposit_service(self.bank)
        self.current_user = None
        self.current_frame = None
        self.container = tk.Frame(root, bg=BG_COLOR)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (LoginPage, HomePage, AccountsPage, TransferencePage, DepositPage, WithdrawPage, SettingsPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LoginPage)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        self.current_frame = frame
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def logout(self):
        self.current_user = None
        self.show_frame(LoginPage)

    def on_closing(self):
        """Save all data and close the app."""
        storage.save_bank(self.bank)
        self.root.destroy()


class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_COLOR)
        self.controller = controller
        self.bank = controller.bank

    def create_header(self, text, row=0, fg_color=PRIMARY_COLOR):
        """Create styled page header."""
        header = tk.Label(self, text=text, font=HEADING_FONT, fg=fg_color, bg=BG_COLOR)
        header.grid(row=row, column=0, columnspan=2, pady=(20, 30), padx=20)
        return header

    def create_card_frame(self, row, col, columnspan=2, rowspan=1):
        """Create a card-style frame."""
        card = tk.Frame(self, bg=CARD_BG, relief=tk.FLAT, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.grid(row=row, column=col, columnspan=columnspan, rowspan=rowspan, padx=20, pady=10, sticky="ew")
        return card

    def create_button(self, text, command, row, col, bg_color=PRIMARY_COLOR, width=30):
        """Create styled button with hover effect."""
        btn = tk.Button(
            self, text=text, command=command, width=width,
            bg=bg_color, fg="#000000", font=LABEL_FONT, relief=tk.FLAT,
            padx=10, pady=10, cursor="hand2"
        )
        btn.grid(row=row, column=col, columnspan=2, pady=10, padx=20, sticky="ew")
        
        def on_enter(e):
            btn.config(bg=darken_color(bg_color))
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def create_label(self, text, row, col, font=LABEL_FONT, fg=TEXT_COLOR):
        """Create styled label."""
        lbl = tk.Label(self, text=text, font=font, fg=fg, bg=BG_COLOR)
        lbl.grid(row=row, column=col, pady=8, padx=20, sticky="w")
        return lbl

    def create_entry(self, row, col, show=None):
        """Create styled entry field."""
        entry = tk.Entry(self, width=35, show=show, font=LABEL_FONT, relief=tk.SOLID, bd=1)
        entry.grid(row=row, column=col, columnspan=1, pady=8, padx=20, sticky="ew")
        entry.config(bg=CARD_BG, fg=TEXT_COLOR, insertbackground=PRIMARY_COLOR)
        return entry


class LoginPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.username_entry = None
        self.password_entry = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Header
        header = tk.Label(self, text="💳 Simple Banking App", font=TITLE_FONT, fg=PRIMARY_COLOR, bg=BG_COLOR)
        header.grid(row=0, column=0, pady=(40, 20))
        
        # Card Frame
        card = self.create_card_frame(1, 0, columnspan=2, rowspan=4)
        card.grid_columnconfigure(0, weight=1)
        
        # Separator
        sep = tk.Frame(card, bg=BORDER_COLOR, height=1)
        sep.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Google OAuth Button
        google_btn = tk.Button(card, text="🔐 Sign In with Google", command=self.google_login,
                              bg="#1F2937", fg="white", font=LABEL_FONT, relief=tk.FLAT, 
                              padx=20, pady=15, cursor="hand2")
        google_btn.grid(row=1, column=0, sticky="ew", padx=15, pady=(15, 20))
        
        def on_enter(e):
            google_btn.config(bg="#111827")
        def on_leave(e):
            google_btn.config(bg="#1F2937")
        google_btn.bind("<Enter>", on_enter)
        google_btn.bind("<Leave>", on_leave)
        
        # Info text
        info = tk.Label(card, text="Secure login with your Google account\nOne-click signup - no email verification needed",
                       font=SMALL_FONT, fg=TEXT_COLOR, bg=CARD_BG)
        info.grid(row=2, column=0, padx=15, pady=(0, 15))

    def google_login(self):
        """Authenticate using Google OAuth."""
        self.google_login_btn = tk.Button(self, text="Loading...", state=tk.DISABLED)
        
        # Run in background to avoid freezing UI
        import threading
        def do_login():
            user, error = authenticate_with_google(self.bank)
            if error:
                messagebox.showerror("Login Error", error)
            elif user:
                self.controller.current_user = user
                self.controller.show_frame(HomePage)
            else:
                messagebox.showerror("Login Failed", "Unknown error occurred")
        
        thread = threading.Thread(target=do_login, daemon=True)
        thread.start()


class HomePage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.info_label = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("📊 Dashboard", fg_color="#000000")
        
        # Info Card
        info_card = self.create_card_frame(1, 0)
        info_card.grid_columnconfigure(0, weight=1)
        self.info_label = tk.Label(info_card, text="", font=LABEL_FONT, justify=tk.LEFT, fg="#000000", bg=CARD_BG)
        self.info_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Action Buttons
        self.create_button("💰 View Accounts", lambda: self.controller.show_frame(AccountsPage), 2, 0, PRIMARY_COLOR)
        self.create_button("➕ Deposit", lambda: self.controller.show_frame(DepositPage), 3, 0, SECONDARY_COLOR)
        self.create_button("➖ Withdraw", lambda: self.controller.show_frame(WithdrawPage), 4, 0, ACCENT_COLOR)
        self.create_button("🔄 Transfer", lambda: self.controller.show_frame(TransferencePage), 5, 0, PRIMARY_COLOR)
        self.create_button("⚙️  Settings", lambda: self.controller.show_frame(SettingsPage), 6, 0, SECONDARY_COLOR)
        self.create_button("🚪 Logout", self.controller.logout, 7, 0, "#DC2626")

    def on_show(self):
        user = self.controller.current_user
        if user:
            accounts = self.bank.list_accounts_for_user(user.id)
            total_balance = sum(a.balance for a in accounts)
            text = f"Welcome back, {user.username}!\n\nAccounts: {len(accounts)}\nTotal Balance: ${total_balance:,.2f}"
            self.info_label.config(text=text)


class AccountsPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.accounts_frame = None
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("💳 Your Accounts")
        
        # Scrollable frame
        self.accounts_frame = tk.Frame(self, bg=BG_COLOR)
        self.accounts_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.accounts_frame.grid_columnconfigure(0, weight=1)
        
        self.create_button("← Back to Home", lambda: self.controller.show_frame(HomePage), 2, 0, PRIMARY_COLOR)

    def on_show(self):
        # Clear previous accounts
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
        
        user = self.controller.current_user
        if user:
            accounts = self.bank.list_accounts_for_user(user.id)
            if not accounts:
                lbl = tk.Label(self.accounts_frame, text="No accounts found. Create one in Settings.", 
                              font=LABEL_FONT, fg="#000000", bg=BG_COLOR)
                lbl.grid(row=0, column=0, sticky="w")
            else:
                for idx, acc in enumerate(accounts):
                    card = tk.Frame(self.accounts_frame, bg=CARD_BG, relief=tk.FLAT, 
                                   highlightthickness=1, highlightbackground=BORDER_COLOR)
                    card.grid(row=idx, column=0, sticky="ew", pady=8)
                    card.grid_columnconfigure(0, weight=1)
                    
                    name_lbl = tk.Label(card, text=f"💳 {acc.name}", font=("Segoe UI", 12, "bold"), 
                                       fg=PRIMARY_COLOR, bg=CARD_BG)
                    name_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
                    
                    balance_lbl = tk.Label(card, text=f"Balance: ${acc.balance:,.2f}", font=LABEL_FONT, 
                                          fg=SECONDARY_COLOR, bg=CARD_BG)
                    balance_lbl.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))


class DepositPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.account_dropdown = None
        self.amount_entry = None
        self.accounts = []
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("➕ Deposit Money")
        
        card = self.create_card_frame(1, 0)
        card.grid_columnconfigure(0, weight=1)
        
        tk.Label(card, text="Select Account", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        self.account_dropdown = tk.Listbox(card, height=4, width=40, font=SMALL_FONT, relief=tk.SOLID, bd=1, 
                                          bg=CARD_BG, fg="#000000", selectmode=tk.SINGLE, activestyle="none")
        self.account_dropdown.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.account_dropdown.config(selectbackground=SECONDARY_COLOR, selectforeground="#000000")
        
        tk.Label(card, text="Amount", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))
        self.amount_entry = tk.Entry(card, width=32, font=LABEL_FONT, relief=tk.SOLID, bd=1)
        self.amount_entry.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.create_button("✓ Confirm Deposit", self.do_deposit, 2, 0, SECONDARY_COLOR)
        self.create_button("🏦 Deposit from BofA (Plaid)", self.deposit_from_plaid, 3, 0, "#1F70C1")
        self.create_button("💳 Deposit from WeChat", self.deposit_from_wechat, 4, 0, "#09B83E")
        self.create_button("← Back to Home", lambda: self.controller.show_frame(HomePage), 5, 0, PRIMARY_COLOR)

    def on_show(self):
        self.account_dropdown.delete(0, tk.END)
        self.accounts = []
        user = self.controller.current_user
        if user:
            accounts = self.bank.list_accounts_for_user(user.id)
            self.accounts = accounts
            for a in accounts:
                self.account_dropdown.insert(tk.END, f"{a.name} - ${a.balance:,.2f}")

    def do_deposit(self):
        sel = self.account_dropdown.curselection()
        if not sel:
            messagebox.showerror("Error", "Please select an account")
            return
        try:
            amount = float(self.amount_entry.get().strip() or "0")
            if amount <= 0:
                raise ValueError("Amount must be positive")
            acc = self.accounts[sel[0]]
            acc.deposit(amount)
            storage.save_bank(self.bank)
            messagebox.showinfo("Success", f"Deposited ${amount:,.2f}\nNew balance: ${acc.balance:,.2f}")
            self.amount_entry.delete(0, tk.END)
            self.on_show()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def deposit_from_plaid(self):
        """Deposit from Bank of America via Plaid."""
        sel = self.account_dropdown.curselection()
        if not sel:
            messagebox.showerror("Error", "Please select an account first")
            return
        
        amount_str = simpledialog.askstring("BofA Deposit", "Enter deposit amount ($):")
        if not amount_str:
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Show demo message
            messagebox.showinfo("BofA Setup", 
                              "To deposit from Bank of America:\n\n"
                              "1. Enter your BofA login\n"
                              "2. Authorize Plaid access\n"
                              "3. Select your account\n\n"
                              "For this demo, enter a test account token to continue.")
            
            test_token = simpledialog.askstring("BofA Account", 
                                               "Enter your Plaid public token\n(or press Cancel to skip):")
            if test_token:
                acc = self.accounts[sel[0]]
                success, msg = self.controller.deposit_service.create_deposit_record(
                    user_id=self.controller.current_user.id,
                    account_id=acc.id,
                    amount=amount,
                    source='bofa',
                    source_details={'access_token': test_token}
                )
                if success:
                    storage.save_bank(self.bank)
                    messagebox.showinfo("Success", msg)
                    self.on_show()
                else:
                    messagebox.showerror("Error", msg)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def deposit_from_wechat(self):
        """Deposit from WeChat Pay."""
        sel = self.account_dropdown.curselection()
        if not sel:
            messagebox.showerror("Error", "Please select an account first")
            return
        
        amount_str = simpledialog.askstring("WeChat Deposit", "Enter deposit amount ($):")
        if not amount_str:
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            wechat_id = simpledialog.askstring("WeChat Pay", "Enter your WeChat ID:")
            if wechat_id:
                acc = self.accounts[sel[0]]
                success, msg = self.controller.deposit_service.create_deposit_record(
                    user_id=self.controller.current_user.id,
                    account_id=acc.id,
                    amount=amount,
                    source='wechat',
                    source_details={'wechat_id': wechat_id}
                )
                if success:
                    storage.save_bank(self.bank)
                    messagebox.showinfo("Success", msg)
                    self.on_show()
                else:
                    messagebox.showerror("Error", msg)
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class WithdrawPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.account_dropdown = None
        self.amount_entry = None
        self.accounts = []
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("➖ Withdraw Money")
        
        card = self.create_card_frame(1, 0)
        card.grid_columnconfigure(0, weight=1)
        
        tk.Label(card, text="Select Account", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        self.account_dropdown = tk.Listbox(card, height=4, width=40, font=SMALL_FONT, relief=tk.SOLID, bd=1,
                                          bg=CARD_BG, fg="#000000", selectmode=tk.SINGLE, activestyle="none")
        self.account_dropdown.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.account_dropdown.config(selectbackground=SECONDARY_COLOR, selectforeground="#000000")
        
        tk.Label(card, text="Amount", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))
        self.amount_entry = tk.Entry(card, width=32, font=LABEL_FONT, relief=tk.SOLID, bd=1)
        self.amount_entry.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.create_button("✓ Confirm Withdrawal", self.do_withdraw, 2, 0, ACCENT_COLOR)
        self.create_button("← Back to Home", lambda: self.controller.show_frame(HomePage), 3, 0, PRIMARY_COLOR)

    def on_show(self):
        self.account_dropdown.delete(0, tk.END)
        self.accounts = []
        user = self.controller.current_user
        if user:
            accounts = self.bank.list_accounts_for_user(user.id)
            self.accounts = accounts
            for a in accounts:
                self.account_dropdown.insert(tk.END, f"{a.name} - ${a.balance:,.2f}")

    def do_withdraw(self):
        sel = self.account_dropdown.curselection()
        if not sel:
            messagebox.showerror("Error", "Please select an account")
            return
        try:
            amount = float(self.amount_entry.get().strip() or "0")
            acc = self.accounts[sel[0]]
            acc.withdraw(amount)
            storage.save_bank(self.bank)
            messagebox.showinfo("Success", f"Withdrew ${amount:,.2f}\nNew balance: ${acc.balance:,.2f}")
            self.amount_entry.delete(0, tk.END)
            self.on_show()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class TransferencePage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.from_dropdown = None
        self.to_dropdown = None
        self.amount_entry = None
        self.all_accounts = []
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("🔄 Transfer Money")
        
        card = self.create_card_frame(1, 0)
        card.grid_columnconfigure(0, weight=1)
        
        tk.Label(card, text="From Account", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        self.from_dropdown = tk.Listbox(card, height=3, width=40, font=SMALL_FONT, relief=tk.SOLID, bd=1,
                                       bg=CARD_BG, fg="#000000", selectmode=tk.SINGLE, activestyle="none")
        self.from_dropdown.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.from_dropdown.config(selectbackground=SECONDARY_COLOR, selectforeground="#000000")
        
        tk.Label(card, text="To Account", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))
        self.to_dropdown = tk.Listbox(card, height=3, width=40, font=SMALL_FONT, relief=tk.SOLID, bd=1,
                                     bg=CARD_BG, fg="#000000", selectmode=tk.SINGLE, activestyle="none")
        self.to_dropdown.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.to_dropdown.config(selectbackground=SECONDARY_COLOR, selectforeground="#000000")
        
        tk.Label(card, text="Amount", font=LABEL_FONT, fg="#000000", bg=CARD_BG).grid(row=4, column=0, sticky="w", padx=15, pady=(15, 5))
        self.amount_entry = tk.Entry(card, width=32, font=LABEL_FONT, relief=tk.SOLID, bd=1)
        self.amount_entry.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        self.create_button("✓ Confirm Transfer", self.do_transfer, 2, 0, SECONDARY_COLOR)
        self.create_button("← Back to Home", lambda: self.controller.show_frame(HomePage), 3, 0, PRIMARY_COLOR)

    def on_show(self):
        self.from_dropdown.delete(0, tk.END)
        self.to_dropdown.delete(0, tk.END)
        self.all_accounts = []
        all_accounts = self.bank.list_accounts()
        self.all_accounts = all_accounts
        for a in all_accounts:
            owner = self.bank.get_user(a.owner_id).username if a.owner_id else "Unknown"
            self.from_dropdown.insert(tk.END, f"{a.name} ({owner}) - ${a.balance:,.2f}")
            self.to_dropdown.insert(tk.END, f"{a.name} ({owner}) - ${a.balance:,.2f}")

    def do_transfer(self):
        user = self.controller.current_user
        
        # Check if bank account is linked
        if not user or not user.linked_bank_account:
            messagebox.showerror("Bank Account Required", 
                                "You must link a Bank of America account before transferring money.\n\n"
                                "Go to Settings → Link Bank of America Account")
            return
        
        from_sel = self.from_dropdown.curselection()
        to_sel = self.to_dropdown.curselection()
        if not from_sel or not to_sel:
            messagebox.showerror("Error", "Please select both from and to accounts")
            return
        try:
            amount = float(self.amount_entry.get().strip() or "0")
            from_acc = self.all_accounts[from_sel[0]]
            to_acc = self.all_accounts[to_sel[0]]
            self.bank.transfer(from_acc.id, to_acc.id, amount)
            storage.save_bank(self.bank)
            messagebox.showinfo("Success", f"Transferred ${amount:,.2f}")
            self.amount_entry.delete(0, tk.END)
            self.on_show()
        except ValueError as e:
            messagebox.showerror("Error", str(e))


class SettingsPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.create_header("⚙️  Settings")
        
        card = self.create_card_frame(1, 0)
        card.grid_columnconfigure(0, weight=1)
        
        tk.Label(card, text="Account Management", font=("Segoe UI", 12, "bold"), fg="#000000", bg=CARD_BG).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        create_btn = tk.Button(card, text="+ Create New Account", command=self.create_account, 
                              bg=SECONDARY_COLOR, fg="#000000", font=LABEL_FONT, relief=tk.FLAT, 
                              padx=20, pady=10, cursor="hand2")
        create_btn.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def on_enter(e):
            create_btn.config(bg=darken_color(SECONDARY_COLOR))
        def on_leave(e):
            create_btn.config(bg=SECONDARY_COLOR)
        create_btn.bind("<Enter>", on_enter)
        create_btn.bind("<Leave>", on_leave)
        
        # Bank Account Linking
        tk.Label(card, text="Bank Account Linking", font=("Segoe UI", 12, "bold"), fg="#000000", bg=CARD_BG).grid(row=2, column=0, sticky="w", padx=15, pady=(20, 10))
        
        self.bank_status_label = tk.Label(card, text="Not linked", font=SMALL_FONT, fg="#DC2626", bg=CARD_BG)
        self.bank_status_label.grid(row=3, column=0, sticky="w", padx=15, pady=(0, 10))
        
        link_btn = tk.Button(card, text="🏦 Link Bank of America Account", command=self.link_bank_account, 
                            bg="#1F70C1", fg="#000000", font=LABEL_FONT, relief=tk.FLAT, 
                            padx=20, pady=10, cursor="hand2")
        link_btn.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 20))
        
        def on_enter_bank(e):
            link_btn.config(bg=darken_color("#1F70C1"))
        def on_leave_bank(e):
            link_btn.config(bg="#1F70C1")
        link_btn.bind("<Enter>", on_enter_bank)
        link_btn.bind("<Leave>", on_leave_bank)
        
        self.create_button("← Back to Home", lambda: self.controller.show_frame(HomePage), 5, 0, PRIMARY_COLOR)
    
    def on_show(self):
        """Update bank linking status when page is shown."""
        user = self.controller.current_user
        if user and user.linked_bank_account:
            self.bank_status_label.config(text="✓ Linked", fg=SECONDARY_COLOR)
        else:
            self.bank_status_label.config(text="Not linked", fg="#DC2626")

    def create_account(self):
        name = simpledialog.askstring("Create Account", "Account name:")
        if not name:
            return
        initial = simpledialog.askfloat("Initial Deposit", "Initial amount (0 for none):", minvalue=0.0)
        user = self.controller.current_user
        acc = self.bank.create_account(name, initial or 0.0, owner_id=user.id)
        storage.save_bank(self.bank)
        messagebox.showinfo("Success", f"Account '{acc.name}' created!")
    
    def link_bank_account(self):
        """Link a Bank of America account via Plaid."""
        user = self.controller.current_user
        
        # Show instructions
        result = messagebox.askyesno("Link Bank Account", 
            "To link your Bank of America account:\n\n"
            "1. You will be taken to Plaid Link\n"
            "2. Search for 'Bank of America'\n"
            "3. Enter your BofA credentials\n"
            "4. Authorize the connection\n\n"
            "Continue?")
        
        if not result:
            return
        
        # For now, ask for test token (in production this would be Plaid Link)
        token = simpledialog.askstring("Link BofA Account",
            "Enter your Plaid access token\n(for production, this will be automatic):")
        
        if token:
            user.linked_bank_account = token
            storage.save_bank(self.bank)
            self.on_show()
            messagebox.showinfo("Success", "Bank account linked! You can now transfer money.")
        else:
            messagebox.showwarning("Cancelled", "Bank account linking cancelled.")


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    run()
