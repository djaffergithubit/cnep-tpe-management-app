import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Menu, filedialog
import mysql.connector
from datetime import datetime
from styles import configure_styles, add_placeholder
import pandas as pd
from dbConfig import db_config
import openpyxl

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def create_table_if_not_exists():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tpe (
            ID_tpe INT AUTO_INCREMENT PRIMARY KEY,
            Numero_Serie VARCHAR(255) UNIQUE NOT NULL,
            Constructeur VARCHAR(255) NOT NULL,
            Modèle_tpe VARCHAR(255) NOT NULL,
            Nb_rouleau_papier INT NOT NULL,
            Numero_Serie_SIM VARCHAR(255) NOT NULL,
            Nb_Vitrophanie INT NOT NULL,
            Batterie VARCHAR(255) NOT NULL,
            Bloc_alimentation VARCHAR(255) NOT NULL,
            Date_Installation DATE NOT NULL,
            Opérateur_Télécom VARCHAR(255) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error creating table: {err}")

def clear_form():
    for var_name, var in variables.items():     
        if var_name != "Opérateur_Télécom":
            var.set("")  # Clear the variable's value
        entry_widget = entry_widgets[var_name]  # Get the associated entry widget
        if var_name == 'Date_Installation':
            add_placeholder(entry_widget, 'yyyy-mm-dd', placeholder_color, font_size, placeholder_font_size, font_name)
        else:
            add_placeholder(entry_widget, var_name.replace("_", " "), placeholder_color, font_size, placeholder_font_size, font_name)

def delete_row(row_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "DELETE FROM tpe WHERE ID_tpe = %s"
        cursor.execute(query, (row_id,))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_table()
        messagebox.showinfo("Success", "Row deleted successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def run_interface():
    tpe_window = Toplevel()
    tpe_window.title("Interface TPE")

    tpe_window.iconbitmap('./icons/app.ico')
    create_table_if_not_exists()

    main_canvas = tk.Canvas(tpe_window)
    main_canvas.grid(row=0, column=0, sticky="nsew")

    # Configure row and column to expand
    tpe_window.grid_rowconfigure(0, weight=1)
    tpe_window.grid_columnconfigure(0, weight=1)

    # Add a vertical scrollbar
    v_scrollbar = tk.Scrollbar(tpe_window, orient="vertical", command=main_canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    # Add a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(tpe_window, orient="horizontal", command=main_canvas.xview)
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Configure the canvas to work with the scrollbar
    main_canvas.configure(yscrollcommand=v_scrollbar.set,
                          xscrollcommand=h_scrollbar.set)

    # Function to resize the canvas with the window
    def resize_canvas(event):
        main_canvas.config(width=event.width, height=event.height)

    # Bind the resize event to the function
    main_canvas.bind("<Configure>", resize_canvas)

    global style, font_name, font_size, placeholder_font_size, placeholder_color
    global variables, entry_widgets, table_frame, numero_serie_var, constructeur_var, modele_tpe_var, nb_rouleau_papier_var
    global numero_serie_sim_var, nb_vitrophanie_var, batterie_var, bloc_alimentation_var, refresh_table
    global date_installation_var, operateur_telecom_var, tree, columns

    # Set the font sizes to 14
    font_size = 13
    placeholder_font_size = 13

    style, font_name, font_size, placeholder_font_size, placeholder_color = configure_styles()

    tpe_window.grid_columnconfigure(0, weight=1)
    tpe_window.grid_columnconfigure(1, weight=1)
    tpe_window.grid_rowconfigure(0, weight=1)
    tpe_window.grid_rowconfigure(1, weight=0)
    tpe_window.grid_rowconfigure(2, weight=1)

    main_frame = tk.Frame(main_canvas, width=1790)
    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

    form_frame = tk.Frame(main_frame, width=1790)
    form_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    form_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
    form_frame.grid_columnconfigure((0, 1), weight=1)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, columnspan=2, padx=40, pady=0, sticky="ew")

    table_frame = ttk.Frame(main_frame, width=1815, height=400)
    table_frame.grid(row=2, column=0, padx=20, pady=40, sticky="nsew")
    table_frame.grid_propagate(False)

    main_frame.grid_columnconfigure(0, weight=0)  
    main_frame.grid_columnconfigure(1, weight=1)  
    main_frame.grid_rowconfigure(0, weight=1)

    left_frame = ttk.Frame(form_frame)
    left_frame.grid(row=0, column=0, padx=40, pady=10, sticky="nsew")

    right_frame = ttk.Frame(form_frame)
    right_frame.grid(row=0, column=1, padx=40, pady=10, sticky="nsew")

    left_frame.grid_columnconfigure(0, weight=1)
    left_frame.grid_columnconfigure(1, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_columnconfigure(1, weight=1)

    message_label = ttk.Label(table_frame, text="No TPEs found.", font=("Helvetica", 12), anchor="center")
    message_label.pack_forget()

    def refresh_table():
        # Clear any existing data in the table
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM tpe")
            tpe_count = cursor.fetchone()[0]  

            cursor.execute("SELECT * FROM tpe")
            tpes = cursor.fetchall()
            cursor.close()
            conn.close()

            if tpes:
                tree.grid(row=0, column=0, sticky="nsew")  # Use grid for the tree
                message_label.grid_forget()  # Hide the message label
                for tpe in tpes:
                    tree.insert('', 'end', values=tpe)

                if tpe_count > 6:
                    y_scrollbar.grid(row=0, column=1, sticky="ns")
                else:
                    y_scrollbar.grid_forget()

                table_h_scrollbar.grid(row=1, column=0, sticky="ew")
            else:
                tree.grid_forget()  # Hide the table if no data
                message_label.grid(row=0, column=0, sticky="nsew")  # Show "No rapports" message
                y_scrollbar.grid_forget()
                table_h_scrollbar.grid_forget()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching tpes: {err}")

    fields = [
        ("Numero Série", "Numero_Serie"),
        ("Constructeur", "Constructeur"),
        ("Modèle TPE", "Modèle_tpe"),
        ("Nb Rouleau Papier", "Nb_rouleau_papier"),
        ("Numero Série SIM", "Numero_Serie_SIM"),
        ("Nb Vitrophanie", "Nb_Vitrophanie"),
        ("Batterie", "Batterie"),
        ("Bloc Alimentation", "Bloc_alimentation"),
        ("Date Installation", "Date_Installation"),
        ("Opérateur Télécom", "Opérateur_Télécom"),
    ]
    variables = {}
    left_fields = fields[:5]
    right_fields = fields[5:]
    entry_widgets = {}

    def submit_form(is_update=False):
        # Ensure all form fields are updated
        for key in variables.keys():
            variables[key].set(variables[key].get()) 
            if variables[key].get().lower() == key.lower().replace('_', ' '):
                messagebox.showerror("Error", f"Please fill in the {key.replace('_', ' ')} field.")
                return
                
        # get the current value of date installation
        date_installation = variables["Date_Installation"].get()

        if not validate_date(date_installation):
            messagebox.showerror("Error", "Date format should be yyyy-mm-dd")
            return

        data = {
            "Numero_Serie": variables["Numero_Serie"].get(),
            "Constructeur": variables["Constructeur"].get(),
            "Modèle_tpe": variables["Modèle_tpe"].get(),
            "Nb_rouleau_papier": variables["Nb_rouleau_papier"].get(),
            "Numero_Serie_SIM": variables["Numero_Serie_SIM"].get(),
            "Nb_Vitrophanie": variables["Nb_Vitrophanie"].get(),
            "Batterie": variables["Batterie"].get(),
            "Bloc_alimentation": variables["Bloc_alimentation"].get(),
            "Date_Installation": date_installation,
            "Opérateur_Télécom": variables["Opérateur_Télécom"].get(),
        }

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            if is_update:
                selected_id = tree.item(tree.selection()[0])['values'][0]  # Get selected ID
                data["selected_id"] = selected_id  # Add selected ID to the data dictionary
                
                query = """
                UPDATE tpe 
                SET Numero_Serie=%(Numero_Serie)s, Constructeur=%(Constructeur)s, Modèle_tpe=%(Modèle_tpe)s, 
                    Nb_rouleau_papier=%(Nb_rouleau_papier)s, Numero_Serie_SIM=%(Numero_Serie_SIM)s, 
                    Nb_Vitrophanie=%(Nb_Vitrophanie)s, Batterie=%(Batterie)s, Bloc_alimentation=%(Bloc_alimentation)s, 
                    Date_Installation=%(Date_Installation)s, Opérateur_Télécom=%(Opérateur_Télécom)s
                WHERE ID_tpe=%(selected_id)s
                """
                cursor.execute(query, data)  # Now, data includes all the required parameters
                
            else:
                query = ("INSERT INTO tpe (Numero_Serie, Constructeur, Modèle_tpe, Nb_rouleau_papier, "
                        "Numero_Serie_SIM, Nb_Vitrophanie, Batterie, Bloc_alimentation, Date_Installation, "
                        "Opérateur_Télécom) VALUES (%(Numero_Serie)s, %(Constructeur)s, %(Modèle_tpe)s, "
                        "%(Nb_rouleau_papier)s, %(Numero_Serie_SIM)s, %(Nb_Vitrophanie)s, %(Batterie)s, "
                        "%(Bloc_alimentation)s, %(Date_Installation)s, %(Opérateur_Télécom)s)")
                cursor.execute(query, data)
            
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Data submitted successfully!")
            clear_form()
            refresh_table()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

    def modify_row():
        selected_row = tree.item(tree.selection()[0])['values']
        for i, (label_text, var_name) in enumerate(fields):
            i += 1
            if var_name == "Date_Installation":
                date = selected_row[i]
                variables[var_name].set(date)
            else:
                variables[var_name].set(selected_row[i])

            entry_widget = entry_widgets[var_name]
            entry_widget.config(style='TEntry')

    def modify_form():

        if not tree.selection():
            messagebox.showerror("Error", "Please select a row to modify.")
            return

        for key in variables.keys():
            variables[key].set(variables[key].get())
            if variables[key].get().lower() == key.lower().replace('_', ' '):
                messagebox.showerror("Error", f"Please fill in the {key.replace('_', ' ')} field.")
                return

        submit_form(is_update=True)

    def on_action_button_click(event):
        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        selected_row = tree.item(row_id)['values']

        menu = Menu(tree, tearoff=0)
        menu.add_command(label="Modify", command=lambda: modify_row())
        menu.add_command(label="Delete", command=lambda: delete_row(selected_row[0]))  # ID_tpe is the first item
        menu.post(event.x_root, event.y_root)
        
    search_var = tk.StringVar()
    search_entry = ttk.Entry(button_frame, textvariable=search_var, font=(font_name, font_size), width=25)
    search_entry.grid(row=0, column=3, padx=48, pady=0, ipady=5, ipadx=7, sticky="ew")
    add_placeholder(search_entry, "🔍 Search...", placeholder_color, font_size, placeholder_font_size, font_name)

    message_label = ttk.Label(table_frame, text="No TPEs found.", font=("Helvetica", 12), anchor="center")
    message_label.pack_forget()

    def search_data(event):
        search_text = search_var.get().strip().lower()
        
        for row in tree.get_children():
            tree.delete(row)
        
        if not search_text:
            refresh_table()
                        
            entry.insert(0, 'Search...')
            entry.config(style='Placeholder.TEntry')
            return
        
        if entry.get() == 'Search...':
            entry.delete(0, 'end')
            entry.config(style='TEntry')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = """
                SELECT * FROM tpe 
                WHERE LOWER(Numero_Serie) LIKE %s
            """

            cursor.execute(query, ('%' + search_text + '%',))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if rows:
                tree.grid(row=0, column=0, sticky="nsew")  # Use grid for the tree
                message_label.grid_forget()
                table_h_scrollbar.grid(row=1, column=0, sticky="ew")
                for row in rows:
                    tree.insert("", "end", values=row)
            else:
                tree.grid_forget()  
                message_label.grid(row=0, column=0, sticky="nsew")
                table_h_scrollbar.grid_forget()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

    search_entry.bind("<KeyRelease>", search_data)

    for i, (label_text, var_name) in enumerate(left_fields):
        ttk.Label(left_frame, text=label_text).grid(row=i, column=0, padx=0, pady=5, sticky="w")
        var = tk.StringVar()
        variables[var_name] = var
        entry = ttk.Entry(left_frame, textvariable=var, font=(font_name, font_size), width=14)
        entry_widgets[var_name] = entry  # Store the entry widget
        add_placeholder(entry, label_text, placeholder_color, font_size, placeholder_font_size, font_name)
        entry.grid(row=i, column=1, padx=0, pady=10, ipady=4, sticky="ew")

    for i, (label_text, var_name) in enumerate(right_fields):
        ttk.Label(right_frame, text=label_text).grid(row=i, column=0, padx=0, pady=5, sticky="w")
        var = tk.StringVar()
        variables[var_name] = var
        if var_name == "Opérateur_Télécom":
            entry = ttk.Combobox(right_frame, textvariable=var, font=(font_name, font_size), width=15)
            entry['values'] = ('Djezzy', 'Mobilis', 'Ooredoo')
            entry.set('Select an option')  # Set the default value
            entry.config(state='readonly')  # Make the combobox readonly
        else:
            entry = ttk.Entry(right_frame, textvariable=var, font=(font_name, font_size), width=15)
        entry_widgets[var_name] = entry  # Store the entry widget
        if var_name == "Date_Installation":
            add_placeholder(entry, 'yyyy-mm-dd', placeholder_color, font_size, placeholder_font_size, font_name)    
        else:
            add_placeholder(entry, label_text, placeholder_color, font_size, placeholder_font_size, font_name)
        entry.grid(row=i, column=1, padx=0, pady=10, ipady=4, sticky="ew")


    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    def import_data():
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier Excel", filetypes=[("Fichiers Excel", "*.xlsx")])
        if file_path:
            try:
                df = pd.read_excel(file_path)

                db_columns = [
                    'Numero_Serie', 'Constructeur', 'Modèle_tpe', 'Nb_rouleau_papier', 'Numero_Serie_SIM',
                    'Nb_Vitrophanie', 'Batterie', 'Bloc_alimentation', 'Date_Installation', 'Opérateur_Télécom'
                ]

                if set(db_columns) != set(df.columns) - {'ID_tpe'}:
                    messagebox.showerror("Error", "The Excel file columns do not match the database columns.")
                    return

                if 'Date_Installation' in df.columns:
                    df['Date_Installation'] = pd.to_datetime(df['Date_Installation'], errors='coerce')

                df['Date_Installation'] = df['Date_Installation'].dt.strftime('%Y-%m-%d')

                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                for index, row in df.iterrows():
                    query = """
                    INSERT INTO tpe (Numero_Serie, Constructeur, Modèle_tpe, Nb_rouleau_papier, Numero_Serie_SIM,
                                    Nb_Vitrophanie, Batterie, Bloc_alimentation, Date_Installation, Opérateur_Télécom)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    if row.isnull().values.any():
                        messagebox.showerror("Error", "Please fill in all the fields in the Excel file.")
                        return                    

                    cursor.execute(query, (
                        row.get('Numero_Serie'), row.get('Constructeur'), row.get('Modèle_tpe'),
                        row.get('Nb_rouleau_papier'), row.get('Numero_Serie_SIM'), row.get('Nb_Vitrophanie'),
                        row.get('Batterie'), row.get('Bloc_alimentation'), row.get('Date_Installation'),
                        row.get('Opérateur_Télécom')
                    ))

                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Success", "Data imported successfully from Excel!")
                refresh_table()  # Refresh the table to show the imported data

            except Exception as e:
                messagebox.showerror("Error", f"Error importing data from Excel: {e}")


    def export_data():
        query = "SELECT * FROM tpe"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("No Data", "No data available to export.")
            return

        # Create a DataFrame from the table data
        df = pd.DataFrame(rows, columns=[
            "ID_tpe", "Numero_Serie", "Constructeur", "Modèle_tpe", "Nb_rouleau_papier", "Numero_Serie_SIM",
            "Nb_Vitrophanie", "Batterie", "Bloc_alimentation", "Date_Installation", "Opérateur_Télécom"
        ])

        # Convert Date_Installation column to datetime type
        df['Date_Installation'] = pd.to_datetime(df['Date_Installation'], errors='coerce')

        # Convert datetime column to string format
        df['Date_Installation'] = df['Date_Installation'].dt.strftime('%Y-%m-%d')  # or any other format you prefer

        # Define file path and name
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="tpe_data.xlsx"
        )

        if file_path:
            # Save the DataFrame to an Excel file
            try:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                    worksheet = writer.sheets['Data']
                    
                    # worksheet.column_dimensions['A'].width = 10  # Set width of column A
                    for col in worksheet.columns:
                        col_letter = openpyxl.utils.get_column_letter(col[0].column)
                        worksheet.column_dimensions[col_letter].width = 15
                        
                messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")


    submit_button = ttk.Button(button_frame, text="Submit", command=submit_form, style='submit.TButton')
    submit_button.grid(row=0, column=0, padx=10, pady=0, sticky="ew")

    clear_button = ttk.Button(button_frame, text="Clear", command=clear_form, style='clear.TButton')
    clear_button.grid(row=0, column=1, padx=10, pady=0, sticky="ew")

    modify_button = ttk.Button(button_frame, text="Modify", command=modify_form, style='modify.TButton')
    modify_button.grid(row=0, column=2, padx=10, pady=0, sticky="ew")

    import_frame = ttk.Frame(form_frame)
    import_frame.grid(row=0, column=2, padx=40, pady=10, sticky="nsew")

    import_button = ttk.Button(import_frame, text="Importer \u2193", command=import_data, style='excel-import.TButton')
    import_button.pack(padx=10, pady=10, fill="x")

    export_button = ttk.Button(import_frame, text="Exporter \u2191", command=export_data, style='excel-import.TButton')
    export_button.pack(padx=10, pady=10, fill="x")

    columns = ["ID", "Numero_Serie", "Constructeur", "Modèle_tpe", "Nb_rouleau_papier",
               "Numero_Serie_SIM", "Nb_Vitrophanie", "Batterie", "Bloc_alimentation",
               "Date_Installation", "Opérateur_Télécom"]
    
    treeview_font_size = 12
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", style="Treeview", height=8)
    tree.grid(row=0, column=0, sticky="nsew")
    tree.tag_configure('row', font=(font_name, treeview_font_size), )

    tree.bind("<Button-3>", on_action_button_click)

    # Set the width for each column
    column_widths = {
        "ID": 40,
        "Numero_Serie": 200,
        "Constructeur": 200,
        "Modèle_tpe": 200,
        "Nb_rouleau_papier": 200,
        "Numero_Serie_SIM": 200,
        "Nb_Vitrophanie": 200,
        "Batterie": 200,
        "Bloc_alimentation": 200,
        "Date_Installation": 200,
        "Opérateur_Télécom": 200,
    }

    # Configure the columns with fixed widths
    for col in columns:
        tree.column(col, width=column_widths[col], anchor="center")
        tree.heading(col, text=col.replace("_", " "))
    
    for row in tree.get_children():
        tree.item(row, tags=('row',), style='Treeview')

    table_h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    y_scrollbar = tk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(xscrollcommand=table_h_scrollbar.set, yscrollcommand=y_scrollbar.set)

    def adjust_h_scrollbar(event):
        total_width = sum(tree.column(col, width=None) for col in columns)
        if total_width > 1500:
            table_h_scrollbar.grid(row=1, column=0, sticky="ew")  # Use grid for positioning
        else:
            table_h_scrollbar.grid_remove()

    tree.bind("<Configure>", adjust_h_scrollbar)
    
    tree.grid(row=0, column=0, sticky="nsew")
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)
    # table_frame.config(width=1790)

    main_frame.update_idletasks()
    window_width = main_frame.winfo_width() + 20  
    tpe_window.geometry(f'{window_width}x900')

    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    refresh_table()

    tpe_window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")
