from pathlib import Path
import json
import customtkinter as ctk
from tkinter import Canvas, PhotoImage, Entry, Button, messagebox
import tkinter as tk
import webbrowser
import hashlib
from nacl.signing import SigningKey
from base58 import b58encode
from mnemonic import Mnemonic
from eth_account import Account
from bit import Key
from tronpy import keys as tron_keys

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.waittime = 500
        self.wraplength = 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0,0,0,0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tw:
            self.tw.destroy()
        self.tw = None

wallet_count_file = OUTPUT_PATH / "wallet_count.json"
def load_wallet_count():
    try:
        with open(wallet_count_file, "r") as f:
            data = json.load(f)
        return data.get("wallet_count", 0)
    except Exception:
        return 0

def save_wallet_count(count):
    with open(wallet_count_file, "w") as f:
        json.dump({"wallet_count": count}, f)

wallet_count = load_wallet_count()
def increment_wallet_count():
    global wallet_count
    wallet_count += 1
    wallet_count_label.configure(text=f"Wallets Generated: {wallet_count}")
    save_wallet_count(wallet_count)

def show_custom_info(wallet_type):
    popup = ctk.CTkToplevel(window)
    popup.title("Wallet Generated")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)
    popup.transient(window)
    popup.grab_set()
    
    label = ctk.CTkLabel(popup, text=f"{wallet_type} Wallet generated successfully.", text_color="green", font=("Arial", 12))
    label.pack(pady=(10,5), padx=10)
    
    frame = ctk.CTkFrame(popup, fg_color="transparent")
    frame.pack(pady=(5,10))
    ctk.CTkLabel(frame, text="Take the time to save this information safely.", font=("Arial", 12)).pack(side="left")
    
    ok_button = ctk.CTkButton(popup, text="OK", command=popup.destroy, fg_color="#E0E0E0",
                              text_color="#000000", hover_color="#A0A0A0", corner_radius=8,
                              width=100, height=40)
    ok_button.pack(pady=(20,10))
    
    w = 500; h = 200
    x = (popup.winfo_screenwidth() - w) // 2
    y = (popup.winfo_screenheight() - h) // 2
    popup.geometry(f"{w}x{h}+{x}+{y}")

def show_about_info():
    about_popup = ctk.CTkToplevel(window)
    about_popup.title("About/FAQ")
    about_popup.resizable(False, False)
    about_popup.attributes("-topmost", True)
    about_popup.transient(window)
    about_popup.grab_set()

    frame = ctk.CTkFrame(about_popup, fg_color="transparent")
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    ctk.CTkLabel(frame, text="WalletGenerator (Multi-Chain) v1.0", font=("Arial", 12, "bold")).pack(anchor="w")
    ctk.CTkLabel(frame, text="FAQ:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10,0))
    ctk.CTkLabel(frame, text="Q: How do I generate a wallet?\nA: Select a wallet option and click Generate.",
                 font=("Arial", 12), justify="left").pack(anchor="w")
    ctk.CTkLabel(frame, text="Instructions:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10,0))
    ctk.CTkLabel(frame, text="1. Choose a wallet option.\n2. Click Generate.\n3. Save your details.",
                 font=("Arial", 12), justify="left").pack(anchor="w")
    ctk.CTkLabel(frame, text="Credits:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10,0))
    ctk.CTkLabel(frame, text="Developed by Recover\nPowered by Python & CustomTkinter.\n\nFollow me on X:",
                 font=("Arial", 12), justify="left").pack(anchor="w")

    link = ctk.CTkLabel(frame, text="https://x.com/Recoverrr", font=("Arial", 12, "underline"),
                        text_color="blue", justify="left")
    link.pack(anchor="w")
    link.bind("<Enter>", lambda e: link.configure(cursor="hand2"))
    link.bind("<Leave>", lambda e: link.configure(cursor=""))
    link.bind("<Button-1>", lambda e: webbrowser.open("https://x.com/Recoverrr"))

    github = ctk.CTkLabel(frame, text="Github", font=("Arial", 12, "underline"),
                          text_color="blue", justify="left")
    github.pack(anchor="w", pady=(2,0))
    github.bind("<Enter>", lambda e: github.configure(cursor="hand2"))
    github.bind("<Leave>", lambda e: github.configure(cursor=""))
    github.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Recoverrrr"))

    ok = ctk.CTkButton(about_popup, text="OK", command=about_popup.destroy, fg_color="#E0E0E0",
                       text_color="#000000", hover_color="#A0A0A0", corner_radius=8,
                       width=100, height=40)
    ok.pack(pady=(0.5,20))

    w = 500; h = 430
    x = (about_popup.winfo_screenwidth() - w) // 2
    y = (about_popup.winfo_screenheight() - h) // 2
    about_popup.geometry(f"{w}x{h}+{x}+{y}")

window = ctk.CTk()
window.title("WalletGenerator (Multi-Chain)")

w_width, w_height = 700, 380
x = (window.winfo_screenwidth() - w_width) // 2
y = (window.winfo_screenheight() - w_height) // 2
window.geometry(f"{w_width}x{w_height}+{x}+{y}")

canvas = Canvas(window, bg="#FFFFFF", height=380, width=700, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Load images
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(350.0, 190.0, image=image_image_1)
image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
canvas.create_image(350.0, 40.0, image=image_image_2)
image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
canvas.create_image(170.0, 39.0, image=image_image_3)
image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
canvas.create_image(350.0, 99.0, image=image_image_4)

wallet_count_label = ctk.CTkLabel(window, text=f"Wallets Generated: {wallet_count}", font=("Arial", 12, "bold"))
canvas.create_window(20, 88, anchor="nw", window=wallet_count_label)
CreateToolTip(wallet_count_label, "Total wallets generated.")

options = ["Solana", "Ethereum", "Bitcoin", "BNB", "TRON", "SUI"]
dropdown = ctk.CTkOptionMenu(window, values=options, width=200, font=("Terminal", 12),
                             fg_color="#D9D9D9", button_color="#D9D9D9", text_color="#000000")
dropdown.set("Choose Your Wallet")
dropdown.place(x=350, y=140, anchor="center")
CreateToolTip(dropdown, "Select blockchain type.")

image_image_5 = PhotoImage(file=relative_to_assets("image_5.png"))
canvas.create_image(90.0, 191.0, image=image_image_5)
image_image_6 = PhotoImage(file=relative_to_assets("image_6.png"))
canvas.create_image(103.0, 230.0, image=image_image_6)
image_image_7 = PhotoImage(file=relative_to_assets("image_7.png"))
canvas.create_image(109.0, 274.0, image=image_image_7)

entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
canvas.create_image(409.5, 188.0, image=entry_image_1)
entry_1 = Entry(window, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_1.place(x=155.0, y=172.0, width=509.0, height=30.0)
CreateToolTip(entry_1, "Wallet address.")

entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
canvas.create_image(409.5, 228.0, image=entry_image_2)
entry_2 = Entry(window, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_2.place(x=155.0, y=212.0, width=509.0, height=30.0)
CreateToolTip(entry_2, "Mnemonic seed phrase.")

entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
canvas.create_image(409.5, 271.0, image=entry_image_3)
entry_3 = Entry(window, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_3.place(x=155.0, y=255.0, width=509.0, height=30.0)
CreateToolTip(entry_3, "Private/secret key.")

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(window, image=button_image_1, borderwidth=0, highlightthickness=0,
                  command=lambda: generate_wallet(), relief="flat", cursor="hand2")
button_1.place(x=282.0, y=315.0, width=136.0, height=54.0)
CreateToolTip(button_1, "Generate wallet.")

about_button = ctk.CTkButton(window, text="ABOUT/FAQ", command=show_about_info,
                             width=120, fg_color="#E0E0E0", text_color="#000000",
                             hover_color="#A0A0A0", corner_radius=8)
about_button.place(x=10, y=w_height - 40)
CreateToolTip(about_button, "FAQs and credits.")

# Additional images
image_image_9 = PhotoImage(file=relative_to_assets("image_9.png"))
canvas.create_image(440.0, 40.0, image=image_image_9)
image_image_10 = PhotoImage(file=relative_to_assets("image_10.png"))
canvas.create_image(335.0, 35.0, image=image_image_10)
image_image_11 = PhotoImage(file=relative_to_assets("image_11.png"))
canvas.create_image(363.0, 35.0, image=image_image_11)
image_image_13 = PhotoImage(file=relative_to_assets("image_13.png"))
canvas.create_image(391.0, 35.0, image=image_image_13)

def generate_wallet():
    current_selection = dropdown.get()
    if current_selection == "Choose Your Wallet":
        messagebox.showerror("Selection Error", "Select a wallet option.", parent=window)
        return
    elif current_selection == "Ethereum":
        try:
            eth_account = Account.create()
            private_key = eth_account.key.hex()
            address = eth_account.address
            mnemo = Mnemonic("english")
            mnemonic_phrase = mnemo.generate(strength=128)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="normal")
                entry.delete(0, "end")
            entry_1.insert(0, address)
            entry_2.insert(0, mnemonic_phrase)
            entry_3.insert(0, private_key)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="readonly")
            increment_wallet_count()
            show_custom_info("Ethereum")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating Ethereum wallet:\n{e}", parent=window)
        return
    elif current_selection == "Bitcoin":
        try:
            btc_key = Key()
            address = btc_key.address
            wif = btc_key.to_wif()
            mnemo = Mnemonic("english")
            mnemonic_phrase = mnemo.generate(strength=128)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="normal")
                entry.delete(0, "end")
            entry_1.insert(0, address)
            entry_2.insert(0, mnemonic_phrase)
            entry_3.insert(0, wif)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="readonly")
            increment_wallet_count()
            show_custom_info("Bitcoin")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating Bitcoin wallet:\n{e}", parent=window)
        return
    elif current_selection == "BNB":
        try:
            bnb_account = Account.create()
            private_key = bnb_account.key.hex()
            address = bnb_account.address
            mnemo = Mnemonic("english")
            mnemonic_phrase = mnemo.generate(strength=128)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="normal")
                entry.delete(0, "end")
            entry_1.insert(0, address)
            entry_2.insert(0, mnemonic_phrase)
            entry_3.insert(0, private_key)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="readonly")
            increment_wallet_count()
            show_custom_info("BNB")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating BNB wallet:\n{e}", parent=window)
        return
    elif current_selection == "TRON":
        try:
            tron_priv = tron_keys.PrivateKey.random()
            tron_address = tron_priv.public_key.to_base58check_address()
            mnemo = Mnemonic("english")
            mnemonic_phrase = mnemo.generate(strength=128)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="normal")
                entry.delete(0, "end")
            entry_1.insert(0, tron_address)
            entry_2.insert(0, mnemonic_phrase)
            entry_3.insert(0, tron_priv.hex())
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="readonly")
            increment_wallet_count()
            show_custom_info("TRON")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating TRON wallet:\n{e}", parent=window)
        return
    elif current_selection == "SUI":
        try:
            sui_signing_key = SigningKey.generate()
            sui_public_key = sui_signing_key.verify_key.encode()
            sui_address = "0x" + hashlib.blake2b(sui_public_key, digest_size=32).digest()[-20:].hex()
            mnemo = Mnemonic("english")
            mnemonic_phrase = mnemo.generate(strength=128)
            sui_private_key = sui_signing_key.encode().hex()
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="normal")
                entry.delete(0, "end")
            entry_1.insert(0, sui_address)
            entry_2.insert(0, mnemonic_phrase)
            entry_3.insert(0, sui_private_key)
            for entry in (entry_1, entry_2, entry_3):
                entry.config(state="readonly")
            increment_wallet_count()
            show_custom_info("SUI")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating SUI wallet:\n{e}", parent=window)
        return
    elif current_selection not in ["Solana", "Ethereum", "Bitcoin", "BNB", "TRON", "SUI"]:
        messagebox.showerror("Not Implemented", "Wallet generation not implemented for this option.", parent=window)
        return

    try:
        mnemo = Mnemonic("english")
        mnemonic_phrase = mnemo.generate(strength=128)
        seed = mnemo.to_seed(mnemonic_phrase, passphrase="")
        key_seed = seed[:32]
        signing_key = SigningKey(key_seed)
        verify_key = signing_key.verify_key
        public_key = b58encode(verify_key.encode()).decode('utf-8')
        secret_key_bytes = signing_key.encode() + verify_key.encode()
        secret_key_base58 = b58encode(secret_key_bytes).decode('utf-8')
        for entry in (entry_1, entry_2, entry_3):
            entry.config(state="normal")
            entry.delete(0, "end")
        entry_1.insert(0, public_key)
        entry_2.insert(0, mnemonic_phrase)
        entry_3.insert(0, secret_key_base58)
        for entry in (entry_1, entry_2, entry_3):
            entry.config(state="readonly")
        increment_wallet_count()
        show_custom_info("Solana")
    except Exception as e:
        messagebox.showerror("Error", f"Error generating wallet:\n{e}", parent=window)

button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(window, image=button_image_1, borderwidth=0, highlightthickness=0,
                  command=generate_wallet, relief="flat", cursor="hand2")
button_1.place(x=282.0, y=315.0, width=136.0, height=54.0)

about_button = ctk.CTkButton(window, text="ABOUT/FAQ", command=show_about_info,
                             width=120, fg_color="#E0E0E0", text_color="#000000",
                             hover_color="#A0A0A0", corner_radius=8)
about_button.place(x=10, y=w_height - 40)
CreateToolTip(about_button, "FAQs and credits.")

window.resizable(False, False)
window.mainloop()
