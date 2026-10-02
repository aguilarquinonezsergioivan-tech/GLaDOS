import customtkinter as ctk
from tkinter import filedialog
import requests
import threading
import json

# Configuración visual base
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GladosDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("GLaDOS - Centro de Control")
        self.geometry("1000x650")

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=3) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # PANEL IZQUIERDO (Entrada de Datos)
        # ==========================================
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.lbl_dropzone = ctk.CTkLabel(
            self.left_frame, 
            text="GLaDOS v0.1\n\nMódulo de Pruebas", 
            fg_color="gray20", 
            corner_radius=8,
            height=150
        )
        self.lbl_dropzone.pack(padx=20, pady=20, fill="x")
        
        # Botón conectado a la función de leer archivo
        self.btn_upload = ctk.CTkButton(self.left_frame, text="Examinar y Analizar Archivo", command=self.seleccionar_archivo)
        self.btn_upload.pack(padx=20, pady=10, fill="x")

        # ==========================================
        # PANEL DERECHO (Salida y Pensamiento)
        # ==========================================
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=3) 
        self.right_frame.grid_rowconfigure(1, weight=1) 

        self.viewer_frame = ctk.CTkFrame(self.right_frame, fg_color="#0a0a0a", corner_radius=8)
        self.viewer_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.lbl_viewer = ctk.CTkLabel(self.viewer_frame, text="[ Renderizador 3D Inactivo ]", text_color="gray50")
        self.lbl_viewer.pack(expand=True)

        self.terminal_box = ctk.CTkTextbox(self.right_frame, font=("Consolas", 12))
        self.terminal_box.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        
        self.escribir_terminal("Iniciando secuencia de arranque...\n")
        self.escribir_terminal("[SISTEMA] Interfaz cargada. Esperando archivos...\n")

    # ==========================================
    # LÓGICA DEL SISTEMA
    # ==========================================
    def escribir_terminal(self, texto):
        """Función segura para escribir en la terminal de la interfaz"""
        self.terminal_box.configure(state="normal")
        self.terminal_box.insert("end", texto)
        self.terminal_box.see("end") # Auto-scroll hacia abajo
        self.terminal_box.configure(state="disabled")

    def seleccionar_archivo(self):
        """Abre el explorador de archivos y lanza el hilo de la IA"""
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            self.escribir_terminal(f"\n[SISTEMA] Archivo cargado: {filepath}\n")
            self.escribir_terminal("[GLaDOS] Analizando contenido, por favor espera...\n")
            
            # Lanzamos la petición a Ollama en un Hilo separado para no congelar la app
            hilo_ia = threading.Thread(target=self.procesar_con_ia, args=(filepath,))
            hilo_ia.start()

    def procesar_con_ia(self, filepath):
        """Se comunica con el servidor local de Ollama"""
        try:
            # 1. Leer el archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # 2. Preparar el Prompt estructurado
            prompt_maestro = f"""Eres el módulo de análisis de GLaDOS. Analiza el siguiente contenido y devuelve un objeto JSON válido con las claves 'resumen', 'lenguaje_o_formato' y 'accion_sugerida'.
            
            Contenido a analizar:
            {contenido}
            """

            # 3. Hacer la petición a la API local de Ollama
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "qwen2.5-coder:3b",
                "prompt": prompt_maestro,
                "stream": False # Falso para que devuelva la respuesta completa de golpe
            }

            respuesta = requests.post(url, json=payload)
            respuesta_json = respuesta.json()
            texto_ia = respuesta_json.get("response", "Error leyendo la IA.")

            # 4. Imprimir el resultado en la interfaz
            self.escribir_terminal(f"\n[GLaDOS]:\n{texto_ia}\n")

        except Exception as e:
            self.escribir_terminal(f"\n[ERROR CRÍTICO] {str(e)}\n")

if __name__ == "__main__":
    app = GladosDashboard()
    app.mainloop()
