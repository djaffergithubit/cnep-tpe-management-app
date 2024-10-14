import ttkbootstrap as ttkb
from ttkbootstrap import Style

# Existing style configuration
def configure_styles():
    style = Style(theme='darkly')  # Use the theme you prefer
    font_name = "Montserrat"
    font_size = 12
    placeholder_font_size = 12
    placeholder_color = "#9E9E9E"
    background_color = "#363949"

    # Configure the global style
    style.configure('TLabel', font=(font_name, font_size))
    style.configure('TEntry', font=(font_name, font_size))
    style.configure('TButton', font=(font_name, font_size))
    style.configure('TCombobox', font=(font_name, font_size))

    style.configure('success.TButton', background='green', foreground='white')
    style.configure('Custom.TButton', background='#D21312', foreground='white', bordercolor='#D21312', lightcolor='#D21312', borderwidth=2, padding=5)
    style.configure('warning.TButton', background='orange', foreground='black')
    style.configure('info.TButton', background='blue', foreground='white')
    style.configure('Red.TButton', background='#D21312', foreground='white')

    style.configure('primary.TButton', background='#007bff', foreground='white', borderwidth=1, relief='flat')
    style.map('primary.TButton', background=[('active', '#0056b3')], foreground=[('active', 'white')])

    # Excel-themed Button Styles
    style.configure('excel-import.TButton', background='#3b7a57', foreground='white', borderwidth=1, relief='flat')
    style.map('excel-import.TButton', background=[('active', '#2b5a42')], foreground=[('active', 'white')])

    style.configure('excel-export.TButton', background='#4f8c3f', foreground='white', borderwidth=1, relief='flat')
    style.map('excel-export.TButton', background=[('active', '#3e6b2f')], foreground=[('active', 'white')])

    style.configure('submit.TButton', background='#28a745', foreground='white', borderwidth=1, relief='flat')
    style.map('submit.TButton', background=[('active', '#28a745')], foreground=[('active', 'white')])

    style.configure('clear.TButton', background='#FF9800', foreground='white', borderwidth=1, relief='flat')
    style.map('clear.TButton', background=[('active', '#FF9800')], foreground=[('active', 'white')])

    style.configure('modify.TButton', background='#007BFF', foreground='white', borderwidth=1, font_size=20, relief='flat')
    style.map('modify.TButton', background=[('active', '#007BFF')], foreground=[('active', 'white')])

    treeview_font_size = 12
    row_height = 50

    # Set styles for Treeview
    style.configure("Treeview",
                    rowheight=row_height,
                    background=background_color,  # Background color for the Treeview
                    foreground="white",  # Text color
                    fieldbackground=background_color,  # Background color for fields
                    bordercolor="gray",
                    borderwidth=2,
                    font=(font_name, treeview_font_size),
                    # change the table width
                    width=500
                    )

    style.configure("Treeview.Heading",
                    background="#2b2e34",  # Background color for headings
                    foreground="white",  # Text color for headings
                    font=(font_name, treeview_font_size))

    style.map('Custom.TButton', 
              background=[('active', '#D21312')],
              foreground=[('active', 'white')])
    
    style.map('TEntry', 
              bordercolor=[('focus', '#D21312')],  # Border color when focused
              lightcolor=[('focus', '#D21312')],   # Border color when focused
              borderwidth=[('focus', 0)])

    return style, font_name, font_size, placeholder_font_size, placeholder_color

# Function to add placeholder functionality to the entry
def add_placeholder(entry, placeholder_text, placeholder_color, font_size, placeholder_font_size, font_name):
    def on_key_press(event):
        if entry.get() == placeholder_text:
            entry.delete(0, 'end')
            entry.config(style='TEntry')

    def on_key_release(event):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            entry.config(style='Placeholder.TEntry')

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.icursor(0)  # Move cursor to the start

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(style='Placeholder.TEntry')

    style = ttkb.Style()
    style.configure('Placeholder.TEntry', foreground=placeholder_color, font=(font_name, placeholder_font_size))

    entry.insert(0, placeholder_text)
    entry.config(style='Placeholder.TEntry')
    entry.bind("<KeyPress>", on_key_press)
    entry.bind("<KeyRelease>", on_key_release)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
