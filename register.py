import ttkbootstrap as ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import errorcode
import hashlib
import importlib
from styles import configure_styles
from dbConfig import db_config

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', font_size=18, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.font_size = font_size
        self.default_fg_color = self['foreground']
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color
            self['font'] = ('Montserrat', self.font_size)

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete('0', 'end')
            self['foreground'] = self.default_fg_color
            self['font'] = ('Montserrat', self.font_size)

    def foc_out(self, *args):
        self.check_placeholder()

    def check_placeholder(self):
        if not self.get():
            self.put_placeholder()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror(title="Error", message="Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror(title="Error", message="Database does not exist")
        else:
            messagebox.showerror(title="Error", message=err)
    else:
        conn.close()

create_tables()  # Create tables if they don't exist

def open_login_window(event=None):
    window.withdraw()
    try:
        login_interface = importlib.import_module('login_interface')
        login_interface.run_login_interface()
    except Exception as e:
        print(f"Failed to import or run login interface: {e}")

def register():
    email = email_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if email == email_entry.placeholder or username == username_entry.placeholder or password == password_entry.placeholder:
        messagebox.showerror(title="Error", message="Please fill in all fields.")
        return

    if '@' not in email:
        messagebox.showerror(title="Error", message="Invalid email address. Please include '@'.")
        return

    hashed_password = hash_password(password)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, hashed_password, email))
        conn.commit()
        messagebox.showinfo(title="Registration Success", message="You have successfully registered.")
        cursor.close()
        conn.close()
        open_login_window()
    except mysql.connector.Error as err:
        messagebox.showerror(title="Error", message=err)

window = ttk.Window(themename="darkly")
window.title("Registration Form")
window.geometry('1000x700')

# Set the icon for the ttk.Window
window.iconbitmap('./icons/app.ico')

styles = configure_styles()

frame = ttk.Frame(window, padding="30")

register_label = ttk.Label(frame, text="Create your Account", style='Custom.TLabel', anchor="center")
username_label = ttk.Label(frame, text="Username", style='Custom.TLabel')
username_entry = PlaceholderEntry(frame, placeholder="Enter username", style='Placeholder.TEntry', font_size=12, width=35)
password_label = ttk.Label(frame, text="Password", style='Custom.TLabel')
password_entry = PlaceholderEntry(frame, placeholder="Enter password", show="*", style='Placeholder.TEntry', font_size=12, width=35)
email_label = ttk.Label(frame, text="Email", style='Custom.TLabel')
email_entry = PlaceholderEntry(frame, placeholder="Enter email", style='Placeholder.TEntry', font_size=12, width=35)

register_button = ttk.Button(frame, text="Register", style='Custom.TButton', command=register)
login_label = ttk.Label(frame, text="Don't you have an account yet? login here", foreground="red", anchor="center")

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=3)

register_label.grid(row=0, column=0, columnspan=2, pady=30, sticky='ew')
email_label.grid(row=1, column=0, sticky='W', pady=20)
email_entry.grid(row=2, column=0, columnspan=2, pady=0, sticky='W', ipady=5, ipadx=5)
username_label.grid(row=3, column=0, sticky='W', pady=20)
username_entry.grid(row=4, column=0, columnspan=2, pady=0, sticky='W', ipady=5, ipadx=5)
password_label.grid(row=5, column=0, sticky='W', pady=20)
password_entry.grid(row=6, column=0, columnspan=2, pady=0, sticky='W', ipady=5, ipadx=5)
register_button.grid(row=7, column=0, columnspan=2, pady=35, sticky='ew', ipady=5, ipadx=5)
login_label.grid(row=8, column=0, columnspan=2, pady=30, sticky='ew', ipady=5, ipadx=5)
login_label.bind("<Button-1>", open_login_window)

frame.pack(expand=True)

window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")
