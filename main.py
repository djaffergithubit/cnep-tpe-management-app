import ttkbootstrap as ttk
from tkinter import Tk
from styles import configure_styles
from register import RegisterInterface
from login_interface import LoginInterface
from interface_pick import InterfacePick
from tpe_interface import TpeInterface

class MainApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Application")
        self.geometry("1000x700")
        self.resizable(False, False)

        # Set the icon for the main Tk window
        self.iconbitmap('./icons/app.ico')
        
        # Configure styles
        self.style = configure_styles()

        self.frames = {}
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames["RegisterInterface"] = RegisterInterface(parent=container, controller=self)
        self.frames["LoginInterface"] = LoginInterface(parent=container, controller=self)
        self.frames["InterfacePick"] = InterfacePick(parent=container, controller=self)
        self.frames["tpeInterface"] = TpeInterface(parent=container, controller=self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginInterface")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
