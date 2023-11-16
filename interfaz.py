import tkinter as tk
from tkinter import filedialog, Text, Menu, PanedWindow, Button, Scrollbar, font

global_terminal = None

def custom_print(terminal, *args, is_error=False, is_success=False, **kwargs):
    if terminal is None:
        print(*args, **kwargs)
        return
    
    terminal.config(state="normal")
    content = '\n '+' '.join(map(str, args)) + '\n'

    start_position = terminal.index(tk.END)  # posición inicial antes de la inserción
    terminal.insert(tk.END, content)
    end_position = terminal.index(tk.END)  # posición final después de la inserción

    if is_error:
        terminal.tag_add("error", start_position, end_position)
    
    elif is_success:
        terminal.tag_add("success", start_position, end_position)

    # Regresar el color a normal
    terminal.tag_add("continue", end_position, tk.END)

    
    terminal.config(state="disabled")
    terminal.see("end")
    terminal.update_idletasks()


def get_global_terminal():
    return global_terminal

def set_global_terminal(terminal):
    global global_terminal
    global_terminal = terminal

class Interfaz(tk.Tk):
    def __init__(self, Parser):
        super().__init__()
        self.Parser = Parser
        self.title("IDE de Yapl/COOL")

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

        # Títulos para los cuadros de texto
        self.titulo_editor = tk.Label(self.frame_editor, text="Editor", bg=self.color_fondo, fg=self.color_texto, font=self.fuente)
        self.titulo_editor.pack(side=tk.TOP, fill=tk.X)
        self.titulo_terminal = tk.Label(self.paned_window, text="Terminal", bg="black", fg="white", font=self.fuente)
        self.titulo_TDC = tk.Label(self.paned_window, text="Código de Tres Direcciones", bg="white", fg="black", font=self.fuente)
        self.titulo_MIPS = tk.Label(self.paned_window, text="Código MIPS", bg="white", fg="black", font=self.fuente)
    


        self.menu.add_command(label="Ejecutar", command=self.ejecutar_parser)

        self.frame_texto = tk.Frame(self.frame_editor)
        self.frame_texto.pack(expand=1, fill=tk.BOTH)

        self.line_number_canvas = tk.Canvas(self.frame_texto, width=30, bg=self.color_fondo)
        self.line_number_canvas.pack(side=tk.LEFT, fill=tk.Y)

        self.line_numbers = Text(self.line_number_canvas, bg=self.color_fondo, fg=self.color_texto, width=3, height=1, padx=5, font=self.fuente, bd=0, highlightthickness=0, state=tk.DISABLED)
        # self.line_numbers = Text(self.line_number_canvas, bg=self.color_fondo, fg=self.color_texto, width=4, height=1, padx=5, font=self.fuente, bd=0, highlightthickness=0, state=tk.DISABLED, anchor='center', spacing1=0, spacing2=0, spacing3=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.scroll_y = Scrollbar(self.frame_texto, orient=tk.VERTICAL)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_y.config(command=self.on_text_and_canvas_scroll)

        self.area_texto = Text(self.frame_texto, wrap=tk.WORD, bg=self.color_fondo, fg=self.color_texto, insertbackground='white', font=self.fuente, yscrollcommand=self.scroll_y.set)
        self.area_texto.pack(expand=1, fill=tk.BOTH)
        self.area_texto.bind("<Tab>", self.on_tab_pressed)
        self.area_texto.bind("<<Change>>", lambda event: self.update_line_numbers())
        self.area_texto.bind("<Return>", lambda event: self.update_line_numbers())
        self.area_texto.bind("<MouseWheel>", lambda event: self.update_line_numbers())
        self.area_texto.bind("<BackSpace>", lambda event: self.update_line_numbers())
        self.area_texto.bind("<KeyRelease>", lambda event: self.update_line_numbers())
        self.area_texto.bind("<Configure>", lambda event: self.update_view_lines())
        
        # Terminal
        self.terminal = Text(self.paned_window, bg="black", fg="white")
        self.terminal.config(state=tk.DISABLED)
        self.terminal.tag_configure("error", foreground="red")
        self.terminal.tag_configure("success", foreground="green")
        self.terminal.tag_configure("continue", foreground="white")

        self.TDC_visible = False  # Variable para rastrear la visibilidad del tercer espacio

        self.TDC = Text(self.paned_window, bg="white", fg="black")  # Nuevo espacio de texto
        self.TDC.config(state=tk.DISABLED)  # Desactivado por defecto

        self.MIPS_visible = False  # Variable para rastrear la visibilidad del cuarto espacio

        self.MIPS = Text(self.paned_window, bg="#282a36", fg="#f8f8f2")  # Nuevo espacio de texto para MIPS
        self.MIPS.config(state=tk.DISABLED)  # Desactivado por defecto

        set_global_terminal(self.terminal)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=10)

        self.show_terminal_button = Button(self.buttons_frame, text="Mostrar Terminal", command=self.toggle_terminal)
        self.show_terminal_button.grid(row=0, column=0, padx=5)  # padx añade un pequeño espacio entre los botones

        self.clean_terminal_button = Button(self.buttons_frame, text="Limpiar Terminal", command=self.clean_terminal)
        self.clean_terminal_button.grid(row=0, column=1, padx=5)

        self.show_TDC_button = Button(self.buttons_frame, text="Mostrar Codigo de Tres direcciones", command=self.toggle_TDC)
        self.show_TDC_button.grid(row=0, column=2, padx=5)  # Nuevo botón para mostrar/ocultar el tercer espacio

        self.show_MIPS_button = Button(self.buttons_frame, text="Mostrar código MIPS", command=self.toggle_MIPS)
        self.show_MIPS_button.grid(row=0, column=3, padx=5)  # Nuevo botón para mostrar/ocultar el espacio de MIPS


        self.is_terminal_visible = False

    def toggle_TDC(self):
        if self.TDC_visible:
            self.paned_window.forget(self.TDC)
            self.show_TDC_button.config(text="Mostrar Codigo de Tres direcciones")
        else:
            self.paned_window.add(self.TDC, width=300)
            self.show_TDC_button.config(text="Esconder Codigo de Tres direcciones")
        
        self.TDC_visible = not self.TDC_visible

    def update_TDC(self, content):
        self.TDC.config(state=tk.NORMAL)
        self.TDC.delete(1.0, tk.END)
        self.TDC.insert(tk.END, content)
        self.TDC.config(state=tk.DISABLED)

        self.toggle_TDC()

    def toggle_MIPS(self):
        if self.MIPS_visible:
            self.paned_window.forget(self.MIPS)
            self.show_MIPS_button.config(text="Mostrar código MIPS")
        else:
            self.paned_window.add(self.MIPS, width=300)
            self.show_MIPS_button.config(text="Esconder código MIPS")
        
        self.MIPS_visible = not self.MIPS_visible

    def update_MIPS(self, content):
        self.MIPS.config(state=tk.NORMAL)
        self.MIPS.delete(1.0, tk.END)
        self.MIPS.insert(tk.END, content)
        self.MIPS.config(state=tk.DISABLED)

        self.toggle_MIPS()

    def update_line_numbers(self):
        line_count = self.area_texto.index(tk.END).split('.')[0]
        lines = [str(i) for i in range(1, int(line_count))]

        max_width = 3 
        centered_lines = []

        for line in lines:
            padding = (max_width - len(line)) // 2  # Calcula cuántos espacios añadir
            centered_line =  line + ' ' * padding 
            centered_lines.append(centered_line)

        content = "\n".join(centered_lines)

        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, content)
        self.line_numbers.config(state=tk.DISABLED)
        self.update_view_lines()
    
    def update_view_lines(self):
        text_yview = self.area_texto.yview()
        self.line_numbers.yview_moveto(text_yview[0])

    def clean_terminal(self):
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)
        self.terminal.config(state=tk.DISABLED)  
    
    def ejecutar_parser(self):
        with open(self.current_file_path, 'w') as file:
            file.write(self.area_texto.get(1.0, tk.END))
        
        if self.current_file_path:
            parser = self.Parser(self.current_file_path, self)
        else:
            self.guardar_archivo()

    def on_text_and_canvas_scroll(self, *args):
        self.area_texto.yview(*args)
        self.line_number_canvas.yview(*args)

    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(initialdir="./archivos/", title="Abrir", filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))
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
            self.paned_window.forget(self.titulo_terminal)
            self.show_terminal_button.config(text="Mostrar Terminal")
        else:
            self.paned_window.add(self.titulo_terminal, height=30)
            self.paned_window.add(self.terminal, width=300)
            self.show_terminal_button.config(text="Esconder Terminal")
        self.is_terminal_visible = not self.is_terminal_visible
    
    def on_tab_pressed(self, event):
        event.widget.insert(tk.INSERT, "    ")  # Inserta cuatro espacios
        return "break"  # Esto previene el comportamiento predeterminado de la tecla Tab


    # def sync_scrolling(self, *args):
    #     self.line_numbers.yview_moveto(args[0])
