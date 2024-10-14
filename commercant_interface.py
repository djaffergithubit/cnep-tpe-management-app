import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Menu, filedialog
import mysql.connector
from datetime import datetime
from styles import configure_styles, add_placeholder
import pandas as pd
from rapport_interface import fetch_agency_names
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
        cursor.execute("SHOW INDEX FROM AGENCE WHERE Key_name = 'idx_nom_Agence'")
        if not cursor.fetchone():
            cursor.execute("CREATE INDEX idx_nom_Agence ON AGENCE (nom_Agence)")
            conn.commit()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS Commercant (
            Id_Commercant INT PRIMARY KEY AUTO_INCREMENT,
            Nom_commercial VARCHAR(50),
            Adresse_de_commerce VARCHAR(100),
            Telephone VARCHAR(20),
            type_operateur VARCHAR(50),
            Commune VARCHAR(80),
            Daira VARCHAR(50),
            Wilaya VARCHAR(50),
            Code_postal VARCHAR(50),
            Qualite_Commercant VARCHAR(50),
            Num_Compte VARCHAR(100),
            nom_agence varchar(50) DEFAULT NULL,
            Raison_sociale TEXT,
            Nature_commerce VARCHAR(50),
            Plafond_autorisé FLOAT,
            FOREIGN KEY (nom_agence) REFERENCES AGENCE(nom_Agence) ON DELETE CASCADE ON UPDATE CASCADE
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
        if var_name != "type_operateur" and var_name != "nom_agence":
            var.set("")  # Clear the variable's value
        entry_widget = entry_widgets[var_name]  # Get the associated entry widget
        add_placeholder(entry_widget, var_name.replace("_", " "), placeholder_color, font_size, placeholder_font_size, font_name)

def delete_row(row_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "DELETE FROM Commercant WHERE Id_Commercant = %s"
        cursor.execute(query, (row_id,))
        conn.commit()
        cursor.close()
        conn.close()
        refresh_table()
        messagebox.showinfo("Success", "Row deleted successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")

def run_interface():
    commercant_window = Toplevel()
    commercant_window.title("Interface Commerçant")

    commercant_window.iconbitmap('./icons/app.ico')
    create_table_if_not_exists()

    main_canvas = tk.Canvas(commercant_window)
    main_canvas.grid(row=0, column=0, sticky="nsew")

    # Configure row and column to expand
    commercant_window.grid_rowconfigure(0, weight=1)
    commercant_window.grid_columnconfigure(0, weight=1)

    # Add a vertical scrollbar
    v_scrollbar = tk.Scrollbar(commercant_window, orient="vertical", command=main_canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    # Add a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(commercant_window, orient="horizontal", command=main_canvas.xview)
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
    global variables, entry_widgets, numero_serie_var, constructeur_var, modele_tpe_var, nb_rouleau_papier_var
    global numero_serie_sim_var, nb_vitrophanie_var, batterie_var, bloc_alimentation_var
    global date_installation_var, operateur_telecom_var, tree, refresh_table

    # Set the font sizes to 14
    font_size = 13
    placeholder_font_size = 13

    style, font_name, font_size, placeholder_font_size, placeholder_color = configure_styles()

    commercant_window.grid_columnconfigure(0, weight=1)
    commercant_window.grid_columnconfigure(1, weight=1)
    commercant_window.grid_rowconfigure(0, weight=1)
    commercant_window.grid_rowconfigure(1, weight=0)
    commercant_window.grid_rowconfigure(2, weight=1)

    main_frame = tk.Frame(main_canvas)
    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

    form_frame = ttk.Frame(main_frame)
    form_frame.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    table_frame = ttk.Frame(main_frame, width=1600, height=400)
    table_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
    table_frame.grid_propagate(False)

    left_frame = ttk.Frame(form_frame)
    left_frame.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")

    middle_frame = ttk.Frame(form_frame)
    middle_frame.grid(row=0, column=1, padx=0, pady=10, sticky="nsew")

    right_frame = ttk.Frame(form_frame)
    right_frame.grid(row=0, column=2, padx=0, pady=10, sticky="nsew")

    message_label = ttk.Label(table_frame, text="No Commerçants found.", font=("Helvetica", 12), anchor="center")
    message_label.pack_forget()

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM commercant")
            commercant_count = cursor.fetchone()[0]

            cursor.execute("SELECT * FROM commercant")
            commercants = cursor.fetchall()
            cursor.close()
            conn.close()

            if commercants:
                tree.grid(row=0, column=0, sticky="nsew")  
                message_label.grid_forget()  
                for commercant in commercants:
                    tree.insert('', 'end', values=commercant)

                if commercant_count > 6:
                    y_scrollbar.grid(row=0, column=1, sticky="ns")
                else:
                    y_scrollbar.grid_forget()

                table_h_scrollbar.grid(row=1, column=0, sticky="ew")
            else:
                tree.grid_forget() 
                message_label.grid(row=0, column=0, sticky="nsew") 
                y_scrollbar.grid_forget()
                table_h_scrollbar.grid_forget()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching commercants: {err}")


    fields = [
        ("Nom commercial", "Nom_commercial"),
        ("Adresse de commerce", "Adresse_de_commerce"),
        ("Telephone", "Telephone"),
        ("type operateur", "type_operateur"),
        ("Commune", "Commune"),
        ("Daira", "Daira"),
        ("Wilaya", "Wilaya"),
        ("Code postal", "Code_postal"),
        ("Qualite Commercant", "Qualite_Commercant"),
        ("Num Compte", "Num_Compte"),
        ("nom Agence", "nom_agence"),
        ("Raison sociale", "Raison_sociale"),
        ("Nature commerce", "Nature_commerce"),
        ("Plafond autorisé", "Plafond_autorisé")
    ]

    variables = {}
    left_fields = fields[:5]  
    middle_fields = fields[5:10]
    right_fields = fields[10:]  
    entry_widgets = {}

    def submit_form(is_update=False):
        # Ensure all form fields are updated
        for key in variables.keys():
            variables[key].set(variables[key].get()) 
            if variables[key].get().lower() == key.lower().replace('_', ' '):
                messagebox.showerror("Error", f"Please fill in the {key.replace('_', ' ')} field.")
                return
            
        data = {
            "Nom_commercial": variables["Nom_commercial"].get(),
            "Adresse_de_commerce": variables["Adresse_de_commerce"].get(),
            "Telephone": variables["Telephone"].get(),
            "type_operateur": variables["type_operateur"].get(),
            "Commune": variables["Commune"].get(),
            "Daira": variables["Daira"].get(),
            "Wilaya": variables["Wilaya"].get(),
            "Code_postal": variables["Code_postal"].get(),
            "Qualite_Commercant": variables["Qualite_Commercant"].get(),
            "Num_Compte": variables["Num_Compte"].get(),
            "nom_agence": variables["nom_agence"].get(),
            "Raison_sociale": variables["Raison_sociale"].get(),
            "Nature_commerce": variables["Nature_commerce"].get(),
            "Plafond_autorisé": variables["Plafond_autorisé"].get(),
        }

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            if is_update:
                selected_id = tree.item(tree.selection()[0])['values'][0]  # Get selected ID
                data["selected_id"] = selected_id  # Add selected ID to the data dictionary
                
                query = """
                    UPDATE Commercant
                    SET Nom_commercial=%(Nom_commercial)s, 
                        Adresse_de_commerce=%(Adresse_de_commerce)s, 
                        Telephone=%(Telephone)s, 
                        type_operateur=%(type_operateur)s, 
                        Commune=%(Commune)s, 
                        Daira=%(Daira)s, 
                        Wilaya=%(Wilaya)s, 
                        Code_postal=%(Code_postal)s, 
                        Qualite_Commercant=%(Qualite_Commercant)s, 
                        Num_Compte=%(Num_Compte)s, 
                        nom_agence=%(nom_agence)s, 
                        Raison_sociale=%(Raison_sociale)s, 
                        Nature_commerce=%(Nature_commerce)s,
                        Plafond_autorisé=%(Plafond_autorisé)s
                    WHERE Id_Commercant=%(selected_id)s;

                """
                cursor.execute(query, data)  # Now, data includes all the required parameters
                
            else:
                query = """
                        INSERT INTO Commercant (Nom_commercial, Adresse_de_commerce, Telephone, type_operateur, 
                                        Commune, Daira, Wilaya, Code_postal, Qualite_Commercant, Num_Compte, 
                                        nom_agence, Raison_sociale, Nature_commerce, Plafond_autorisé) 
                        VALUES (%(Nom_commercial)s, %(Adresse_de_commerce)s, %(Telephone)s, 
                                %(type_operateur)s, %(Commune)s, %(Daira)s, %(Wilaya)s, %(Code_postal)s, 
                                %(Qualite_Commercant)s, %(Num_Compte)s, %(nom_agence)s, 
                                %(Raison_sociale)s, %(Nature_commerce)s, %(Plafond_autorisé)s);
                        """
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

    # add a search functionality to search data in the table
    search_var = tk.StringVar()
    search_entry = ttk.Entry(button_frame, textvariable=search_var, font=(font_name, font_size))
    search_entry.grid(row=0, column=3, padx=40, pady=10, ipady=5, ipadx=7, sticky="ew")
    add_placeholder(
        search_entry, "🔍 Search...", placeholder_color, font_size, placeholder_font_size, font_name
    )

    message_label = ttk.Label(table_frame, text="No commerçants found.", font=("Helvetica", 12), anchor="center")
    message_label.pack_forget()

    def search_data(event):
        search_text = search_var.get().strip().lower()
        
        # Clear existing results
        for row in tree.get_children():
            tree.delete(row)
        
        if not search_text:
            refresh_table()
            return
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = """
                SELECT * FROM Commercant 
                WHERE LOWER(Nom_commercial) LIKE %s
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
    agencies = fetch_agency_names()

    for i, (label_text, var_name) in enumerate(left_fields):
        ttk.Label(left_frame, text=label_text).grid(row=i, column=0, padx=2, pady=2, sticky="ew")
        var = tk.StringVar()
        variables[var_name] = var
        if var_name == "type_operateur":
            entry = ttk.Combobox(left_frame, textvariable=var, font=(font_name, font_size))
            entry['values'] = ('Djezzy', 'Mobilis', 'Ooredoo')
            entry.set('Select an option')  # Set the default value
            entry.config(state='readonly')  # Make the combobox readonly
        else:
            entry = ttk.Entry(left_frame, textvariable=var, font=(font_name, font_size))
        entry_widgets[var_name] = entry  # Store the entry widget
        add_placeholder(entry, label_text, placeholder_color, font_size, placeholder_font_size, font_name)
        entry.grid(row=i, column=1, padx=20, pady=9, ipady=3, sticky="ew")

    for i, (label_text, var_name) in enumerate(middle_fields):
        ttk.Label(middle_frame, text=label_text).grid(row=i, column=0, padx=2, pady=2, sticky="ew")
        var = tk.StringVar()
        variables[var_name] = var
        entry = ttk.Entry(middle_frame, textvariable=var, font=(font_name, font_size))
        entry_widgets[var_name] = entry  # Store the entry widget
        add_placeholder(entry, label_text, placeholder_color, font_size, placeholder_font_size, font_name)
        entry.grid(row=i, column=1, padx=20, pady=9, ipady=3, sticky="ew")

    for i, (label_text, var_name) in enumerate(right_fields):
        ttk.Label(right_frame, text=label_text).grid(row=i, column=0, padx=2, pady=2, sticky="ew")
        var = tk.StringVar()
        variables[var_name] = var
        if var_name == "nom_agence":
            entry = ttk.Combobox(right_frame, textvariable=var, font=(font_name, font_size))
            entry['values'] = agencies
            entry.set('Select an option')  # Set the default value
            entry.config(state='readonly')  # Make the combobox readonly
        else:
            entry = ttk.Entry(right_frame, textvariable=var, font=(font_name, font_size))
        entry_widgets[var_name] = entry  # Store the entry widget
        add_placeholder(entry, label_text, placeholder_color, font_size, placeholder_font_size, font_name)
        entry.grid(row=i, column=1, padx=20, pady=9, ipady=3, sticky="ew")


    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    def import_data():
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier Excel", filetypes=[("Fichiers Excel", "*.xlsx")])
        if file_path:
            try:
                df = pd.read_excel(file_path)

                db_columns = [
                    'Nom_commercial', 'Adresse_de_commerce', 'Telephone', 'type_operateur', 
                    'Commune', 'Daira', 'Wilaya', 'Code_postal', 'Qualite_Commercant', 'Num_Compte', 
                    'nom_agence', 'Raison_sociale', 'Nature_commerce', 'Plafond_autorisé'
                ]

                if set(db_columns) != set(df.columns) - {'Id_Commercant'}:
                    messagebox.showerror("Error", "The Excel file columns do not match the database columns.")
                    return

                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                for index, row in df.iterrows():
                    query = """
                        INSERT INTO Commercant (
                            Nom_commercial, Adresse_de_commerce, Telephone, type_operateur, 
                            Commune, Daira, Wilaya, Code_postal, Qualite_Commercant, Num_Compte, 
                            nom_agence, Raison_sociale, Nature_commerce, Plafond_autorisé
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    if row.isnull().values.any():
                        messagebox.showerror("Error", "Please fill in all the fields in the Excel file.")
                        return

                    cursor.execute(query, (
                        row.get('Nom_commercial'), row.get('Adresse_de_commerce'), row.get('Telephone'), 
                        row.get('type_operateur'), row.get('Commune'), row.get('Daira'), row.get('Wilaya'), 
                        row.get('Code_postal'), row.get('Qualite_Commercant'), row.get('Num_Compte'), 
                        row.get('nom_agence'), row.get('Raison_sociale'), row.get('Nature_commerce'), 
                        row.get('Plafond_autorisé')
                    ))

                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Success", "Data imported successfully from Excel!")
                refresh_table()  

            except Exception as e:
                messagebox.showerror("Error", f"Error importing data from Excel: {e}")


    def export_data():
        query = "SELECT * FROM Commercant"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("No Data", "No data available to export.")
            return

        # Create a DataFrame from the table data
        df = pd.DataFrame(rows, columns=[
            "Id_Commercant", "Nom_commercial", "Adresse_de_commerce", "Telephone", "type_operateur", "Commune",
            "Daira", "Wilaya", "Code_postal", "Qualite_Commercant", "Num_Compte", "nom_agence", "Raison_sociale", 
            "Nature_commerce" , "Plafond_autorisé"
        ])


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
    submit_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    clear_button = ttk.Button(button_frame, text="Clear", command=clear_form, style='clear.TButton')
    clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    modify_button = ttk.Button(button_frame, text="Modify", command=modify_form, style='modify.TButton')
    modify_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    import_frame = ttk.Frame(form_frame)
    import_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

    import_button = ttk.Button(import_frame, text="Importer \u2193", command=import_data, style='excel-import.TButton')
    import_button.pack(padx=10, pady=10, fill="x")

    export_button = ttk.Button(import_frame, text="Exporter \u2191", command=export_data, style='excel-import.TButton')
    export_button.pack(padx=10, pady=10, fill="x")

    columns = [
        "ID", "Nom_commercial", "Adresse", "Telephone", "operateur",
        "Commune", "Daira", "Wilaya", "Code_postal", "Qualite_Commercant", "Num_Compte",
        "Agence", "Raison_sociale", "Nature_commerce", "Plafond_autorisé"
    ]

    
    treeview_font_size = 12

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", style="Treeview", height=8)
    tree.grid(row=0, column=0, sticky="nsew")
    tree.tag_configure('row', font=(font_name, treeview_font_size), )

    tree.bind("<Button-3>", on_action_button_click)
                             
    column_widths = {
        "ID": 50,
        "Nom_commercial": 200,
        "Adresse": 150,
        "Telephone": 125,
        "operateur": 110,
        "Commune": 120,
        "Daira": 120,
        "Wilaya": 120,
        "Code_postal": 200,
        "Qualite_Commercant": 200,
        "Num_Compte": 127,
        "Agence": 200,
        "Raison_sociale": 200,
        "Nature_commerce": 200,
        "Plafond_autorisé": 200
    }

# Configure the columns with fixed widths width=column_widths[col],
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
        if total_width > 1600:
            table_h_scrollbar.grid(row=1, column=0, sticky="ew")  # Use grid for positioning
        else:
            table_h_scrollbar.grid_remove()  

    # Bind the event
    tree.bind("<Configure>", adjust_h_scrollbar)

    # Adjust the tree to fill the frame and work with scrollbars
    tree.grid(row=0, column=0, sticky="nsew")
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    # the tree is not displaying

    main_frame.update_idletasks()
    main_frame.update_idletasks()
    window_width = main_frame.winfo_width() + 20  
    commercant_window.geometry(f'{window_width}x900')
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    refresh_table()

    commercant_window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")