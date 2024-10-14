import ttkbootstrap as ttk
from tkinter import messagebox, Toplevel
import mysql.connector
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
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color
        self['font'] = ('Montserrat', self.font_size)  

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete('0', 'end')
            self['foreground'] = self.default_fg_color
            self['font'] = ('Montserrat', self.font_size)  

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def open_interface_pick_window():
    try:
        interface_pick = importlib.import_module('interface_pick')
        interface_pick.run_interface_pick()  
    except Exception as e:
        print(f"Failed to import or run interface pick module: {e}")  

def login(username_entry, password_entry, login_window):
    username = username_entry.get()
    password = password_entry.get()
    hashed_password = hash_password(password)
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(query, (username, hashed_password))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo(title="Login Success", message="You successfully logged in.")
            login_window.destroy()  
            open_interface_pick_window()  
        else:
            messagebox.showerror(title="Error", message="Invalid login.")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror(title="Error", message=err)

def run_login_interface():
    login_window = Toplevel()
    login_window.title("Login Form")
    login_window.geometry('1000x700')

    login_window.iconbitmap('./icons/app.ico')
    styles = configure_styles()

    frame = ttk.Frame(login_window, padding="30")

    # Creating widgets with styles applied
    login_label = ttk.Label(frame, text="Sign in to your account", style='Custom.TLabel')
    username_label = ttk.Label(frame, text="Your email", style='Custom.TLabel')
    username_entry = PlaceholderEntry(frame, placeholder="name@company.com", style='Placeholder.TEntry', font_size=12, width=35)
    password_label = ttk.Label(frame, text="Password", style='Custom.TLabel')
    password_entry = PlaceholderEntry(frame, placeholder="Enter password", show="*", style='Placeholder.TEntry', font_size=12, width=35)
    
    # Apply the custom style to the button
    login_button = ttk.Button(frame, text="Sign in", style='Custom.TButton', command=lambda: login(username_entry, password_entry, login_window))

    # Grid configuration
    frame.columnconfigure(0, weight=1)  # Label column
    frame.columnconfigure(1, weight=3)  # Input column

    login_label.grid(row=0, column=0, columnspan=2, pady=40, sticky='w')
    username_label.grid(row=1, column=0, sticky='w', pady=10)
    username_entry.grid(row=2, column=0, columnspan=2, pady=0, sticky='w', ipady=5, ipadx=5)
    password_label.grid(row=3, column=0, sticky='w', pady=10)
    password_entry.grid(row=4, column=0, columnspan=2, pady=0, sticky='w', ipady=5, ipadx=5)
    login_button.grid(row=5, column=0, columnspan=2, pady=35, sticky='ew', ipady=5, ipadx=5)

    frame.pack(expand=True)

    login_window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")
