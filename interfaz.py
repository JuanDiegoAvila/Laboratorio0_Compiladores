import tkinter as tk
from tkinter import filedialog, Text, Menu, PanedWindow, Button, Scrollbar, font

global_terminal = None

def custom_print(terminal, *args, **kwargs):
    if terminal is None:
        raise ValueError("La terminal no ha sido inicializada.")
    terminal.config(state="normal")
    content = ' '.join(map(str, args)) + '\n'
    terminal.insert(tk.END, content)
    terminal.config(state="disabled")
    terminal.see("end")

def get_global_terminal():
    return global_terminal

def set_global_terminal(terminal):
    global global_terminal
    global_terminal = terminal

class Interfaz(tk.Tk):
    def __init__(self, Parser):
        super().__init__()
        self.Parser = Parser
        self.title("Editor con Terminal")

        self.current_file_path = None

        # Configuraciones visuales para el editor
        self.fuente = font.Font(family='consolas', size=12)
        self.color_fondo = "#282a36"
        self.color_texto = "#f8f8f2"

        # PanedWindow para separar el editor y la terminal
        self.paned_window = PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        # Editor de texto
        self.frame_editor = tk.Frame(self.paned_window)
        self.paned_window.add(self.frame_editor, stretch='always')

        self.menu = Menu(self, bg=self.color_fondo, fg=self.color_texto)
        self.config(menu=self.menu)

        self.menu_archivo = Menu(self.menu, bg=self.color_fondo, fg=self.color_texto)
        self.menu.add_cascade(label="Archivo", menu=self.menu_archivo)
        self.menu_archivo.add_command(label="Abrir", command=self.abrir_archivo)
        self.menu_archivo.add_command(label="Guardar", command=self.guardar_archivo)
        self.menu_archivo.add_command(label="Salir", command=self.quit)

        self.menu.add_command(label="Ejecutar", command=self.ejecutar_parser)

        self.frame_texto = tk.Frame(self.frame_editor)
        self.frame_texto.pack(expand=1, fill=tk.BOTH)

        self.scroll_y = Scrollbar(self.frame_texto, orient=tk.VERTICAL)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.area_texto = Text(self.frame_texto, wrap=tk.WORD, bg=self.color_fondo, fg=self.color_texto, insertbackground='white', font=self.fuente, yscrollcommand=self.scroll_y.set)
        self.area_texto.pack(expand=1, fill=tk.BOTH)

        self.scroll_y.config(command=self.area_texto.yview)

        # Terminal
        self.terminal = Text(self.paned_window, bg="black", fg="white")
        self.terminal.config(state=tk.DISABLED)

        set_global_terminal(self.terminal)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=10)

        self.show_terminal_button = Button(self.buttons_frame, text="Mostrar Terminal", command=self.toggle_terminal)
        self.show_terminal_button.grid(row=0, column=0, padx=5)  # padx añade un pequeño espacio entre los botones

        self.clean_terminal_button = Button(self.buttons_frame, text="Limpiar Terminal", command=self.clean_terminal)
        self.clean_terminal_button.grid(row=0, column=1, padx=5)

        self.is_terminal_visible = False

    def clean_terminal(self):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.config(state=tk.DISABLED)  
    
    def ejecutar_parser(self):
        self.guardar_archivo()
        if self.current_file_path:
            parser = self.Parser(self.current_file_path)
        else:
            # Puedes mostrar un mensaje de error o alguna indicación si no hay archivo actual.
            pass


    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(title="Abrir", filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))
        if archivo:
            self.current_file_path = archivo
            self.area_texto.delete(1.0, tk.END)
            with open(archivo, 'r') as file:
                self.area_texto.insert(tk.INSERT, file.read())

    def guardar_archivo(self):
        if self.current_file_path:
            with open(self.current_file_path, 'w') as file:
                file.write(self.area_texto.get(1.0, tk.END))
        else:
            
            archivo = filedialog.asksaveasfilename(title="Guardar como", defaultextension=".txt", filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))
            if archivo:
                self.current_file_path = archivo
                with open(archivo, 'w') as file:
                    file.write(self.area_texto.get(1.0, tk.END))

    def toggle_terminal(self):
        if self.is_terminal_visible:
            self.paned_window.forget(self.terminal)
            self.show_terminal_button.config(text="Mostrar Terminal")
        else:
            self.paned_window.add(self.terminal, width=300)
            self.show_terminal_button.config(text="Esconder Terminal")
        self.is_terminal_visible = not self.is_terminal_visible
