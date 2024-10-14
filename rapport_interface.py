from tkinter import *
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import mysql.connector
from tkinter import messagebox
from fpdf import FPDF
import time
from styles import configure_styles, add_placeholder
import re
from tkinter import ttk
import tkinter as tk
from dbConfig import db_config

def validate_date_format(date_str):
    """Validate the date format (yyyy-mm-dd)."""
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return re.match(pattern, date_str) is not None

def create_table_if_not_exists():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if the index on AGENCE table already exists
        cursor.execute("SHOW INDEX FROM AGENCE WHERE Key_name = 'idx_nom_Agence'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_nom_Agence ON AGENCE (nom_Agence)")
            conn.commit()
        
        # Create Rapport table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Rapport (
            Numéro_rapport int NOT NULL AUTO_INCREMENT,
            Date_Visite varchar(50) DEFAULT NULL,
            nom_agence varchar(100) DEFAULT NULL,
            nom_prenom varchar(100) DEFAULT NULL,
            raison_soc text,
            num_serie varchar(100) DEFAULT NULL,
            PRIMARY KEY (Numéro_rapport),
            FOREIGN KEY (nom_agence) REFERENCES AGENCE(nom_Agence) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (num_serie) REFERENCES tpe(Numero_Serie) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error creating table: {err}")

def check_num_serie_exists(num_serie):
    """Check if the provided Numéro de Série exists in the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Rapport WHERE num_serie = %s", (num_serie,))
        result = cursor.fetchone()
        return result[0] > 0
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error checking Numéro de Série: {err}")
        return False
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_rapport_data():
    # Placeholder values (you can adjust these based on actual placeholders in your form)
    placeholder_agence = "Select an option"
    placeholder_num_serie = "Select an option"
    placeholder_nom_prenom = "nom et prénom"
    placeholder_raison_soc = "raison sociale"

    # Validate the date format before saving
    date_visite = entry_date_visite.get()
    if not validate_date_format(date_visite):
        messagebox.showerror("Invalid Date", "Please enter the date in the format yyyy-mm-dd.")
        return

    # Retrieve form data
    nom_agence = entry_nom_agence.get()
    nom_prenom = entry_nom_prenom.get().strip()
    raison_soc = text_raison_soc.get("1.0", "end-1c").strip()
    num_serie = entry_num_serie.get()

    # Check if any value equals a placeholder value or is empty
    if nom_agence.lower() == placeholder_agence.lower():
        messagebox.showerror("Invalid Input", "Please select a valid agency.")
        return
    if num_serie.lower() == placeholder_num_serie.lower():
        messagebox.showerror("Invalid Input", "Please select a valid TPE number.")
        return
    if nom_prenom.lower() == placeholder_nom_prenom.lower() or not nom_prenom.lower():
        messagebox.showerror("Invalid Input", "Please enter a valid name")
        return
    if raison_soc.lower() == placeholder_raison_soc.lower() or not raison_soc.lower():
        messagebox.showerror("Invalid Input", "Please enter a valid raison sociale")
        return

    # Data to be saved
    data = {
        'Date_Visite': date_visite,
        'nom_agence': nom_agence,
        'nom_prenom': nom_prenom,
        'raison_soc': raison_soc,
        'num_serie': num_serie
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        insert_query = """INSERT INTO Rapport (Date_Visite, nom_agence, nom_prenom, raison_soc, num_serie)
                          VALUES (%s, %s, %s, %s, %s)"""

        cursor.execute(insert_query, tuple(data.values()))
        conn.commit()
        update_table()
        clear_form()
        messagebox.showinfo("Success", "Rapport data saved successfully!")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def generate_pdf():
    # Placeholder values (adjust based on actual placeholders in your form)
    placeholder_agence = "Select an option"
    placeholder_num_serie = "Select an option"
    placeholder_nom_prenom = "nom et prénom"
    placeholder_raison_soc = "Raison sociale"

    # Validate the date format before proceeding
    date_visite = entry_date_visite.get()
    if not validate_date_format(date_visite):
        messagebox.showerror("Invalid Date", "Please enter the date in the format yyyy-mm-dd.")
        return

    # Retrieve form data
    nom_agence = entry_nom_agence.get()
    nom_prenom = entry_nom_prenom.get().strip()
    raison_soc = text_raison_soc.get("1.0", "end-1c").strip()
    num_serie = entry_num_serie.get()

    # Check if any value equals a placeholder value or is empty
    if nom_agence.lower() == placeholder_agence.lower():
        messagebox.showerror("Invalid Input", "Please select a valid agency.")
        return
    if num_serie.lower() == placeholder_num_serie.lower():
        messagebox.showerror("Invalid Input", "Please select a valid TPE number.")
        return
    if nom_prenom.lower() == placeholder_nom_prenom.lower() or not nom_prenom.lower():
        messagebox.showerror("Invalid Input", "Please enter a valid name")
        return
    if raison_soc.lower() == placeholder_raison_soc.lower() or not raison_soc.lower():
        messagebox.showerror("Invalid Input", "Please enter a valid raison sociale")
        return

    # If all fields are valid, create the PDF
    data = {
        'Date de Visite': date_visite,
        'Nom de l\'agence': nom_agence,
        'Nom et Prénom': nom_prenom,
        'Numéro de série': num_serie,
        'Raison sociale': raison_soc,
    }

    pdf = FPDF()
    pdf.add_page()
    
    # Set title
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Rapport", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    
    # Adding a border around the content
    pdf.set_draw_color(0, 0, 0)
    pdf.rect(10, 20, 190, 260)  # (x, y, width, height)
    
    y = 30
    for key, value in data.items():
        pdf.set_xy(20, y)
        
        if key == "Numéro de série":
            pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)
            y += 10

        elif key == "Raison sociale":
            # Using multi_cell for wrapping text
            pdf.multi_cell(0, 10, txt=f"{key}: {value}", align='L')
            
            # Adjust y position based on the height of the multi-line text
            y += 10 * (value.count('\n') + 1)
            
            # Check if there’s enough space for the next content; if not, add a new page
            if y > 250: 
                pdf.add_page()
                y = 30  

        else:
            # Handle other fields normally
            pdf.cell(0, 10, txt=f"{key}: {value}", ln=True)
            y += 10

    # Generate a unique filename using the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    pdf_file = f"Rapport_{timestamp}.pdf"
    
    pdf.output(pdf_file)
    
    messagebox.showinfo("Success", f"PDF generated successfully: {pdf_file}")

def on_text_focus_in(event):
    """Clear the placeholder text when the text widget gains focus."""
    if text_raison_soc.get("1.0", "end-1c") == "Raison sociale..":
        text_raison_soc.delete("1.0", "end")
        text_raison_soc.config(foreground='white')  

def on_text_focus_out(event):
    """Restore the placeholder text when the text widget loses focus if it's empty."""
    if text_raison_soc.get("1.0", "end-1c").strip() == "":
        text_raison_soc.insert("1.0", "Raison sociale..")
        text_raison_soc.config(foreground='grey')  #


def fetch_agency_names():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT nom_Agence FROM AGENCE")
        agencies = cursor.fetchall()
        conn.close()
        return [agency[0] for agency in agencies]
    except mysql.connector.Error as err:
        return []

def delete_row(row_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "DELETE FROM Rapport WHERE Numéro_rapport = %s"
        cursor.execute(query, (row_id,))
        conn.commit()
        cursor.close()
        conn.close()
        update_table()
        messagebox.showinfo("Success", "Row deleted successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def run_interface():
    rapport_window = Toplevel()
    rapport_window.title("Interface Rapport")

    rapport_window.iconbitmap('./icons/app.ico')
    create_table_if_not_exists()

    main_canvas = tk.Canvas(rapport_window)
    main_canvas.grid(row=0, column=0, sticky="nsew")

    # Configure row and column to expand
    rapport_window.grid_rowconfigure(0, weight=1)
    rapport_window.grid_columnconfigure(0, weight=1)

    # Add a vertical scrollbar
    v_scrollbar = tk.Scrollbar(rapport_window, orient="vertical", command=main_canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    # Add a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(rapport_window, orient="horizontal", command=main_canvas.xview)
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Configure the canvas to work with the scrollbar
    main_canvas.configure(yscrollcommand=v_scrollbar.set,
                          xscrollcommand=h_scrollbar.set)

    # Function to resize the canvas with the window
    def resize_canvas(event):
        main_canvas.config(width=event.width, height=event.height)

    # Bind the resize event to the function
    main_canvas.bind("<Configure>", resize_canvas)
    global entry_date_visite, entry_nom_agence, tree, entry_nom_prenom, y_scrollbar
    global text_raison_soc, entry_num_serie , clear_form, update_table

    # Set the font sizes to 14
    font_size = 13
    placeholder_font_size = 13

    style, font_name, font_size, placeholder_font_size, placeholder_color = configure_styles()

    rapport_window.grid_columnconfigure(0, weight=1)
    rapport_window.grid_columnconfigure(1, weight=1)
    rapport_window.grid_rowconfigure(0, weight=1)
    rapport_window.grid_rowconfigure(1, weight=0)
    rapport_window.grid_rowconfigure(2, weight=1)

    main_frame = tk.Frame(main_canvas)
    main_frame.pack(fill=Y, anchor="center")
    main_canvas.create_window((0, 0), window=main_frame, anchor="w")

    form_frame = Frame(main_frame, width=1875, height=500)
    form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  
    form_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
    form_frame.grid_columnconfigure((0, 1), weight=1)
    form_frame.grid_propagate(False)

    table_frame = ttk.Frame(main_frame, width=1545, height=400)
    table_frame.grid(row=2, column=0, columnspan=2, padx=70, sticky="nsew")
    table_frame.grid_propagate(False)

    left_frame = ttk.Frame(form_frame)
    left_frame.grid(row=0, column=0, padx=40, pady=10, sticky="nsew")

    right_frame = ttk.Frame(form_frame)
    right_frame.grid(row=0, column=1, padx=40, pady=10, sticky="nsew")

    left_frame.grid_columnconfigure(0, weight=1)
    left_frame.grid_columnconfigure(1, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_columnconfigure(1, weight=1)

    message_label = Label(table_frame, text="No rapports found.", font=("Helvetica", 12), anchor="center")
    message_label.pack_forget()

    def update_table():
        # Clear any existing data in the table
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT count(*) FROM Rapport")
            count = cursor.fetchone()[0]

            cursor.execute("SELECT * FROM Rapport")
            rapports = cursor.fetchall()
            cursor.close()
            conn.close()

            if rapports:
                tree.grid(row=0, column=0, sticky="nsew")
                message_label.grid_forget()  
                for rapport in rapports:
                    tree.insert('', 'end', values=rapport)
                
                if count > 7:
                    y_scrollbar.grid(row=0, column=1, sticky="ns")
                else:
                    y_scrollbar.grid_forget()
            else:
                tree.grid_forget()  
                message_label.grid(row=0, column=0, sticky="nsew")  
                y_scrollbar.grid_forget()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching rapports: {err}")

    labels = [
        "Date de Visite", "Nom de l'agence", "Nom et Prénom"
        , "Numéro de série", "Raison sociale"
    ]

    left_fields = labels[:4]
    right_fields = labels[4:]

    
    entries = [
        'entry_date_visite', 'entry_nom_agence', 'entry_nom_prenom',
         'entry_num_serie', 'text_raison_soc'
    ]

    entry_font = ("Helvetica", 12)  
    text_font = ("Helvetica", 12)   
    button_font = ("Helvetica", 12) 

    def fetch_serie_num():
       try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT Numero_Serie FROM tpe")
        nums_serie = cursor.fetchall()
        conn.close()
        return [num[0] for num in nums_serie]  # Correctly extracting Numero_Serie from the fetched tuples
       except mysql.connector.Error as err:
        return []
    
    def clear_form():
        """Clear all form fields and reset to default values."""
        
        # Clear text and entry fields and reset placeholders
        for widget in form_frame.winfo_children():
            if isinstance(widget, tb.Entry):
                widget.delete(0, 'end')  # Clear entry field
                placeholder_text = widget.get() if widget.get() else 'yyyy-mm-dd' 
                add_placeholder(widget, placeholder_text, placeholder_color, font_size, placeholder_font_size, font_name)
            elif isinstance(widget, Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", "Text..")
                widget.config(foreground='grey')
            elif isinstance(widget, ttk.Combobox):
                widget.set('Select an option')  
        
    agency_names = fetch_agency_names()
    nums_serie = fetch_serie_num()

    def on_action_button_click(event):
        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        selected_row = tree.item(row_id)['values']

        menu = Menu(tree, tearoff=0)
        menu.add_command(label="Delete", command=lambda: delete_row(selected_row[0])) 
        menu.post(event.x_root, event.y_root)

    for i, label in enumerate(left_fields):
        lbl = tb.Label(left_frame, text=label, font=("Helvetica", 12), foreground="white", background="#222222")
        lbl.grid(row=i, column=0, padx=10, sticky="W")

        if label == "Date de Visite":
            entry_date_visite = tb.Entry(left_frame, width=50, font=entry_font)
            entry_date_visite.grid(row=i, column=1, padx=10, pady=10, ipady=5, sticky="W")
            add_placeholder(entry_date_visite, 'yyyy-mm-dd', placeholder_color, font_size, placeholder_font_size, font_name)
            
        elif label == "Nom de l'agence":
            entry_nom_agence = ttk.Combobox(left_frame, font=entry_font, width=49)
            entry_nom_agence['values'] = agency_names
            entry_nom_agence.set('Select an option')  # Set the default value
            entry_nom_agence.config(state='readonly')  # Make the combobox readonly
            entry_nom_agence.grid(row=i, column=1, padx=10, pady=20, ipady=5, sticky="W")

        elif label == "Numéro de série":
            entry_num_serie = ttk.Combobox(left_frame, font=entry_font, width=49)
            entry_num_serie['values'] = nums_serie  # Set the fetched Numero_Serie values
            entry_num_serie.set('Select an option')  # Set the default value
            entry_num_serie.config(state='readonly')  # Make the combobox readonly
            entry_num_serie.grid(row=i, column=1, padx=10, pady=20, ipady=5, sticky="W")


        else:
            entry = tb.Entry(left_frame, width=50, font=entry_font)
            entry.grid(row=i, column=1, padx=10, pady=10, ipady=5, sticky="W")
            add_placeholder(entry, label.replace("_", " "), placeholder_color, font_size, placeholder_font_size, font_name)
            globals()[entries[i]] = entry

    for i, label in enumerate(right_fields):
        if label == "Raison sociale":
            # Create and place the label for "Raison sociale"
            lbl = tb.Label(right_frame, text=label, font=("Helvetica", 12), foreground="white", background="#222222")
            lbl.grid(row=i * 2, column=0, padx=10, pady=5, sticky="W")

            # Set the Text widget with adjusted height to match left side
            text_raison_soc = Text(right_frame, width=50, height=14, wrap=WORD, font=text_font, bg="#f0f0f0", fg="white")
            text_raison_soc.grid(row=i * 2 + 1, column=0, padx=10, pady=10, ipady=5, sticky="W")

            # Set placeholder behavior
            text_raison_soc.insert("1.0", "Raison sociale..")
            text_raison_soc.config(foreground='grey')  
            text_raison_soc.bind("<FocusIn>", on_text_focus_in)
            text_raison_soc.bind("<FocusOut>", on_text_focus_out)


    # Apply font size to buttons using ttkbootstrap's styling
    style = tb.Style()
    style.configure("Custom.TButton", font=button_font)

    # Save Button
    save_button = ttk.Button(left_frame, text="Save", style="Custom.TButton", width=50, command=save_rapport_data)
    save_button.grid(row=len(labels), column=1, padx=10, pady=10, ipady=5, sticky="W")

    # Generate PDF Button
    pdf_button = ttk.Button(left_frame, text="Generate PDF", style="Custom.TButton", width=50, command=generate_pdf)
    pdf_button.grid(row=len(labels) + 1, column=1, padx=10, pady=20, ipady=5, sticky="W")

    columns = ("Numéro_rapport", "Date_Visite", "nom_agence", "nom_prenom", "raison_soc", "num_serie")
    
    treeview_font_size = 12
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", style="Treeview", height=8)
    tree.grid(row=0, column=0)
    tree.tag_configure('row', font=(font_name, treeview_font_size), )
    tree.bind("<Button-3>", on_action_button_click)

    # Set the width for each column
    column_widths = {
        "Numéro_rapport": 200,
        "Date_Visite": 283,
        "nom_agence": 283,
        "nom_prenom": 283,
        "raison_soc": 283,
        "num_serie": 200
    }

    # Configure the columns with fixed widths
    for col in columns:
        tree.column(col, width=column_widths[col], anchor="center")
        tree.heading(col, text=col.replace("_", " "), anchor="center")
    
    for row in tree.get_children():
        tree.item(row, tags=('row',), style='Treeview')

    y_scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=y_scrollbar.set)
    update_table()
    
    tree.grid(row=0, column=0)
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    main_frame.update_idletasks()
    window_width = main_frame.winfo_width() + 20  
    rapport_window.geometry(f'{window_width}x900')

    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    update_table()
    rapport_window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")
