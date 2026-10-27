"""Run with Python 3.12. No images or video leave this process except virtual output."""
import argparse
import queue
import tkinter as tk
from tkinter import ttk


class App:
    def __init__(self, root):
        self.root, self.engine = root, None
        self.closing = False
        self.gestures_active = True
        self.photo = None
        root.title("AnimeCam · tu reunion, otro universo")
        root.geometry("1180x790")
        root.minsize(1000, 720)
        root.configure(bg="#10121b")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", background="#9b86ff", troughcolor="#292c3f", borderwidth=0)
        self.label(root, "ANIMECAM", 27, "#c0adff").pack(anchor="w", padx=28, pady=(24, 0))
        self.label(root, "Un pequeno jutsu para reuniones demasiado normales.", 12, "#969cb6").pack(anchor="w", padx=30, pady=(2, 20))
        content = tk.Frame(root, bg="#10121b")
        content.pack(fill="both", expand=True, padx=28)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        left = tk.Frame(content, bg="#10121b")
        left.grid(row=0, column=0, sticky="nsew")
        self.background_status = self.label(left, "FONDO PENDIENTE · pulsa Capturar fondo y apartate 5 segundos", 12, "#ffcc80")
        self.background_status.pack(anchor="w", pady=(0, 8))
        self.preview = tk.Label(left, bg="#191d2c", fg="#858da9", text="TU ESCENARIO\n\nInicia la webcam para entrar en escena", font=("Segoe UI", 16), width=1, height=1)
        self.preview.pack(fill="both", expand=True)
        self.countdown_overlay = tk.Label(self.preview, bg="#10121b", fg="#ffdc98", font=("Segoe UI", 30, "bold"), padx=25, pady=18)
        self.state = self.label(left, "EN ESPERA", 11, "#b7a7f5")
        self.state.pack(anchor="w", pady=(12, 5))
        self.progress = ttk.Progressbar(left, maximum=1)
        self.progress.pack(fill="x", pady=(0, 10))
        self.tracking = self.label(left, "Deteccion: esperando webcam", 9, "#b7a7f5")
        self.tracking.pack(anchor="w", pady=(0, 5))
        self.label(left, "GOKU · dos dedos junto a la frente     /     CLONES · indices juntos, dos manos\nRASENGAN · palma abierta     /     Sosten 0,6 s y baja las manos antes de repetir.\nProcesamiento local · sin grabacion", 9, "#9da5c1").pack(anchor="w", pady=(0, 4))
        side = tk.Frame(content, bg="#1a1d2b", width=278)
        side.grid(row=0, column=1, sticky="ns", padx=(22, 0))
        side.pack_propagate(False)
        self.label(side, "TU CAMARA", 11, "#a5acc7").pack(anchor="w", padx=18, pady=(18, 8))
        row = tk.Frame(side, bg="#1a1d2b")
        row.pack(fill="x", padx=18)
        self.label(row, "Indice webcam", 11).pack(side="left")
        self.camera = tk.IntVar(value=0)
        tk.Spinbox(row, from_=0, to=9, textvariable=self.camera, width=4, bg="#292d40", fg="white", buttonbackground="#393f58").pack(side="right")
        self.virtual = tk.BooleanVar(value=True)
        tk.Checkbutton(side, text="Enviar a Teams (OBS)", variable=self.virtual, bg="#1a1d2b", fg="#e1e4f4", selectcolor="#292d40", activebackground="#1a1d2b", activeforeground="white").pack(anchor="w", padx=14, pady=8)
        self.start_button = self.button(side, "Iniciar webcam", self.toggle, accent=True)
        self.capture_button = self.button(side, "1  Capturar fondo · 5 s", lambda: self.command("capture"))
        self.label(side, "Apartate durante la cuenta regresiva.\nCamara fija, misma iluminacion.", 9, "#9da5c1").pack(anchor="w", padx=18, pady=(0, 16))
        self.label(side, "TUS TECNICAS", 11, "#a5acc7").pack(anchor="w", padx=18, pady=(5, 8))
        self.button(side, "2  Teletransporte", lambda: self.command("teleport"))
        self.button(side, "3  Kage Bunshin", lambda: self.command("clones"))
        self.button(side, "4  Rasengan", lambda: self.command("rasengan"))
        self.button(side, "0  Volver a normal", lambda: self.command("reset"))
        self.gesture_button = self.button(side, "Pausar gestos", self.toggle_gestures)
        self.status = tk.StringVar(value="Listo. Webcam integrada = 0; prueba 1 o 2 para una USB.")
        tk.Label(root, textvariable=self.status, bg="#10121b", fg="#cbd0e4", anchor="w", wraplength=1100, font=("Segoe UI", 10)).pack(fill="x", padx=28, pady=18)
        for key, action in (("1", "capture"), ("2", "teleport"), ("3", "clones"), ("4", "rasengan"), ("0", "reset")):
            root.bind(key, lambda event, a=action: self.command(a) if event.widget.winfo_class() != "Spinbox" else None)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(30, self.poll)

    @staticmethod
    def label(parent, text, size=11, color="#e5e8f5"):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color, font=("Segoe UI", size), justify="left")

    @staticmethod
    def button(parent, text, command, accent=False):
        b = tk.Button(parent, text=text, command=command, relief="flat", cursor="hand2", bg="#9b86ff" if accent else "#292e44", fg="#10121b" if accent else "#eef0ff", activebackground="#b5a4ff", activeforeground="#10121b", font=("Segoe UI", 10, "bold"), pady=4)
        b.pack(fill="x", padx=18, pady=3)
        return b

    def toggle(self):
        if self.engine:
            self.engine.stop()
            self.start_button.configure(state="disabled", text="Deteniendo...")
            return
        from camera_fx.engine import CameraEngine
        try:
            camera = self.camera.get()
            if camera < 0 or camera > 9:
                raise ValueError()
        except (ValueError, tk.TclError):
            self.status.set("El indice debe ser un numero entre 0 y 9.")
            return
        self.engine = CameraEngine(camera, self.virtual.get())
        self.engine.start()
        self.gestures_active = True
        self.gesture_button.configure(text="Pausar gestos")
        self.start_button.configure(text="Detener webcam")
        self.status.set("Abriendo webcam y modelos locales...")
        self.background_status.configure(text="FONDO PENDIENTE · captura de nuevo al iniciar la webcam", fg="#ffcc80")

    def command(self, action):
        if self.engine:
            self.engine.commands.put(action)
            if action == "capture":
                self.background_status.configure(text="CAPTURA SOLICITADA · apartate del encuadre", fg="#ffcc80")
                self.status.set("Apartate ahora. Espera la cuenta regresiva y el aviso verde FONDO LISTO.")
        else:
            self.status.set("Primero inicia la webcam.")

    def toggle_gestures(self):
        if self.engine:
            self.gestures_active = not self.gestures_active
            self.gesture_button.configure(text="Pausar gestos" if self.gestures_active else "Activar gestos")
            self.command("gestures")

    def poll(self):
        if self.engine:
            while not self.engine.events.empty():
                event = self.engine.events.get_nowait()
                if event != "__stopped__":
                    self.status.set(event)
            try:
                frame, fps, hidden, mode, background, progress, countdown, virtual, tracking = self.engine.frames.get_nowait()
                from PIL import Image, ImageTk
                image = Image.fromarray(frame[:, :, ::-1])
                image.thumbnail((max(320, self.preview.winfo_width()), max(180, self.preview.winfo_height())))
                self.photo = ImageTk.PhotoImage(image)
                self.preview.configure(image=self.photo, text="", width=0)
                text = f"{'INVISIBLE' if hidden else mode.upper()}  /  {fps:.0f} FPS  /  Fondo {'listo' if background else 'pendiente'}  /  {'Teams activo' if virtual else 'Solo vista previa'}"
                if countdown is not None:
                    text = f"APARTATE · Captura de fondo en {countdown}..."
                    self.countdown_overlay.configure(text=f"{countdown if countdown else '...'}\nSAL DEL ENCUADRE")
                    self.countdown_overlay.place(relx=0.5, rely=0.5, anchor="center")
                    self.background_status.configure(text="CAPTURANDO FONDO · espera fuera del encuadre", fg="#ffcc80")
                    self.capture_button.configure(text=f"Capturando... {countdown}", state="disabled")
                else:
                    self.countdown_overlay.place_forget()
                    self.capture_button.configure(text="1  Volver a capturar fondo" if background else "1  Capturar fondo · 5 s", state="normal")
                    self.background_status.configure(text="FONDO LISTO · ya puedes teletransportarte" if background else "FONDO PENDIENTE · pulsa Capturar fondo y apartate 5 segundos", fg="#8ce8b7" if background else "#ffcc80")
                self.tracking.configure(text=tracking)
                self.state.configure(text=text)
                self.progress["value"] = progress
            except queue.Empty:
                pass
            if not self.engine.thread.is_alive():
                self.engine = None
                self.start_button.configure(text="Iniciar webcam", state="normal")
                self.state.configure(text="CAMARA DETENIDA")
                self.countdown_overlay.place_forget()
                self.capture_button.configure(text="1  Capturar fondo · 5 s", state="normal")
        if self.closing and self.engine is None:
            self.root.destroy()
            return
        self.root.after(30, self.poll)

    def close(self):
        self.closing = True
        if self.engine:
            self.engine.stop()
            self.status.set("Cerrando webcam...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AnimeCam para Teams")
    parser.add_argument("--smoke-test", action="store_true", help="Abre y cierra la interfaz sin activar la webcam")
    args = parser.parse_args()
    root = tk.Tk()
    App(root)
    if args.smoke_test:
        root.after(700, root.destroy)
    root.mainloop()
