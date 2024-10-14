from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tb
import importlib
from styles import configure_styles

def run_interface_pick():
    pick_window = Toplevel()
    pick_window.title("CNEP")
    pick_window.geometry('1000x700')

    def open_commercant_interface():
        commercant_interface = importlib.import_module('commercant_interface')
        commercant_interface.run_interface()

    def open_tpe_interface():
        tpe_interface = importlib.import_module('tpe_interface')
        tpe_interface.run_interface()

    def open_rapport_interface():
        rapport_interface = importlib.import_module('rapport_interface')
        rapport_interface.run_interface()

    # Apply the global style configuration
    styles = configure_styles()

    # Create a frame to center the content
    main_frame = tb.Frame(pick_window)
    main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Label titre principal
    lab = tb.Label(main_frame, text="CNEP for TPE CONTROL", font=("Montserrat", 28), foreground="red")
    lab.grid(row=0, column=0, pady=20)

    # Create a frame to hold the buttons and center them
    button_frame = tb.Frame(main_frame)
    button_frame.grid(row=1, column=0, pady=20)

    # Use the predefined style for buttons
    tpe = tb.Button(button_frame, text="TPE", width=30, style="Custom.TButton", command=lambda: open_tpe_interface())
    tpe.grid(row=0, column=0, pady=10, ipady=10)

    commercant = tb.Button(button_frame, text="commercant", width=30, style="Custom.TButton", command=lambda: open_commercant_interface())
    commercant.grid(row=1, column=0, pady=10, ipady=10)

    rapport = tb.Button(button_frame, text="rapport", width=30, style="Custom.TButton", command=lambda: open_rapport_interface())
    rapport.grid(row=2, column=0, pady=10, ipady=10)

    # Adjust row and column weights to ensure proper centering
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    pick_window.mainloop()

if __name__ == "__main__":
    print("This interface should not be run directly. Please run the main application.")
