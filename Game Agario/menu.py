from customtkinter import*

class ConnectWindow(CTk):
    def __init__(self):
        super().__init__()

        self.name = None
        self.host = None
        self.port = None

        self.title("Agario Launcher")
        self.geometry("300x400")

        CTkLabel(self, text="Connection to Agario: ", font=("Comic Sans MS",20, 'bold')).pack(pady=15,padx=20,anchor='w')

        self.name_entry = CTkEntry(self, placeholder_text="Введіть ім'я")
        self.name_entry.pack(padx=20, anchor='w', fill ='x')

        self.host_entry = CTkEntry(self, placeholder_text="Введіть хост", height=50)
        self.host_entry.pack(padx=20, pady=10, anchor='w', fill='x')

        self.port_entry = CTkEntry(self, placeholder_text="Введіть порт", height=50)
        self.port_entry.pack(padx=20, anchor='w', fill ='x')

        
        CTkButton(self, text="Приєднатися", command=self.open_game, height=50).pack(pady=20) 
    
    def open_game(self):
        self.name = self.name_entry.get()
        self.host = self.host_entry.get()
        self.port = int(self.port_entry.get())
        self.destroy()
        

        
