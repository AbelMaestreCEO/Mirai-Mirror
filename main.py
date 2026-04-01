import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class MiraiMirror:
    def __init__(self, root):
        self.root = root
        self.root.title("Mirai Mirror")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Configurar icono (debe existir icon.ico en la misma carpeta)
        try:
            self.root.iconbitmap("icon.ico")  # Para Windows
        except:
            pass
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        self.organize_photos = tk.BooleanVar(value=True)
        self.organize_videos = tk.BooleanVar(value=True)
        
        # Configurar estilo
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Configura el estilo visual con tonos azules"""
        style = ttk.Style()
        
        # Colores azules (paleta minimalista)
        self.colors = {
            'bg_primary': '#f0f5fa',      # Fondo claro azulado
            'bg_secondary': '#e3eef7',    # Fondo secundario
            'accent': '#2563eb',          # Azul primario brillante
            'accent_dark': '#1e40af',     # Azul oscuro para hover
            'text_primary': '#1e293b',    # Texto oscuro
            'text_secondary': '#64748b',  # Texto gris
            'success': '#10b981',         # Verde para éxito
            'warning': '#f59e0b',         # Naranja para advertencia
            'error': '#ef4444',           # Rojo para errores
            'border': '#cbd5e1',          # Borde suave
        }
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Frame principal
        style.configure('TFrame', background=self.colors['bg_primary'])
        style.configure('TLabelFrame', background=self.colors['bg_primary'], 
                       bordercolor=self.colors['border'],
                       fieldbackground=self.colors['bg_secondary'])
        style.configure('TLabelframe.Label', foreground=self.colors['text_primary'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Labels
        style.configure('TLabel', background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'),
                       foreground=self.colors['accent'],
                       background=self.colors['bg_primary'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['bg_primary'])
        
        # Buttons
        style.configure('TButton', font=('Segoe UI', 10, 'bold'),
                       padding=(15, 10), borderwidth=0)
        style.configure('Primary.TButton', background=self.colors['accent'],
                       foreground='white', borderwidth=0)
        style.map('Primary.TButton', background=[('active', self.colors['accent_dark'])])
        
        # Checkbuttons
        style.configure('TCheckbutton', background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        # Entries
        style.configure('TEntry', fieldbackground='white',
                       foreground=self.colors['text_primary'],
                       borderwidth=1, relief='solid',
                       bordercolor=self.colors['border'])
        
        # Text widget (log)
        style.configure('Log.TFrame', background=self.colors['bg_secondary'])
        
    def create_widgets(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === HEADER CON LOGO Y TÍTULO ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Logo (puedes reemplazar con tu propio icono)
        # Si tienes un PNG, puedes usar PhotoImage
        try:
            # Intenta cargar un icono PNG si existe
            logo = tk.PhotoImage(file="logo.png")
            logo_label = ttk.Label(header_frame, image=logo)
            logo_label.image = logo  # Mantener referencia
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except:
            # Fallback: emoji como logo
            logo_label = ttk.Label(header_frame, text="🪞", font=('Segoe UI', 24))
            logo_label.grid(row=0, column=0, padx=(0, 10))
        
        # Título
        title_label = ttk.Label(header_frame, text="Mirai Mirror", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=1, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, 
                                   text="Organizador Universal de Medios",
                                   style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # === SELECCIÓN DE CARPETA ===
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Label(folder_frame, text="📂 Carpeta de Archivos:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.entry_folder = ttk.Entry(folder_frame, textvariable=self.source_folder, 
                                      width=50, style='TEntry')
        self.entry_folder.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Explorar...", 
                               command=self.browse_folder, width=12)
        browse_btn.grid(row=0, column=2)
        
        # === OPCIONES ===
        option_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="15")
        option_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Primera fila: Tipos de archivos
        ttk.Checkbutton(option_frame, text="📷 Fotos (Telegram & WhatsApp)", 
                       variable=self.organize_photos).grid(
            row=0, column=0, sticky=tk.W, padx=15, pady=5
        )
        ttk.Checkbutton(option_frame, text="🎬 Videos (Telegram)", 
                       variable=self.organize_videos).grid(
            row=0, column=1, sticky=tk.W, padx=15, pady=5
        )
        
        # Segunda fila: Modo prueba
        ttk.Checkbutton(option_frame, text="🧪 Modo Prueba (solo análisis)", 
                       variable=self.dry_run).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=15, pady=5
        )
        
        # === BOTÓN PRINCIPAL ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        action_btn = ttk.Button(btn_frame, text="🚀 Iniciar Organización", 
                               command=self.organize_files, 
                               style='Primary.TButton', width=25)
        action_btn.pack()
        
        # === LOG ===
        log_frame = ttk.LabelFrame(main_frame, text="Registro de Actividad", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, 
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'],
                                font=('Consolas', 9),
                                bd=0, highlightthickness=0,
                                padx=10, pady=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                  command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Configurar tags para colores en el log
        self.log_text.tag_config('info', foreground=self.colors['text_primary'])
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        self.log_text.tag_config('error', foreground=self.colors['error'])
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Selecciona la carpeta con los archivos")
        if folder:
            self.source_folder.set(folder)
            self.log_text.insert(tk.END, f"📂 Carpeta seleccionada: {folder}\n", 'info')
            self.log_text.see(tk.END)

    def parse_telegram_photo(self, filename):
        pattern = r'photo_\d+@(\d{2})-(\d{2})-(\d{4})_(\d{2})-(\d{2})-(\d{2})'
        match = re.search(pattern, filename)
        if match:
            day, month, year, hour, minute, second = match.groups()
            try:
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            except ValueError:
                return None
        return None

    def parse_telegram_video(self, filename):
        pattern = r'[A-Z0-9-]+-VIDEO-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})'
        match = re.search(pattern, filename)
        if match:
            year, month, day, hour, minute, second = match.groups()
            try:
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            except ValueError:
                return None
        return None

    def parse_whatsapp_image(self, filename):
        pattern = r'WhatsApp Image (\d{4}-\d{2}-\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})'
        match = re.search(pattern, filename)
        if match:
            date_str, hour, minute, second = match.groups()
            try:
                return datetime.strptime(f"{date_str} {hour.zfill(2)}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return None

    def parse_date_from_filename(self, filename, file_type='photo'):
        if file_type == 'photo':
            date = self.parse_telegram_photo(filename)
            if date:
                return date
            return self.parse_whatsapp_image(filename)
        elif file_type == 'video':
            return self.parse_telegram_video(filename)
        return None

    def organize_files(self):
        source_path = Path(self.source_folder.get())
        
        if not source_path.exists() or not source_path.is_dir():
            messagebox.showerror("Error", "La carpeta seleccionada no es válida.")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"🔍 Iniciando escaneo en: {source_path}\n", 'info')
        self.log_text.insert(tk.END, f"📅 Fecha sistema: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n", 'info')
        self.log_text.insert(tk.END, f"{'='*60}\n", 'info')
        
        photo_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv'}
        
        organized_photos = {}
        organized_videos = {}
        stats = {'photos': 0, 'videos': 0, 'errors': 0, 'whatsapp': 0, 'telegram': 0, 'skipped': 0}
        
        for item in source_path.iterdir():
            if not item.is_file():
                continue
                
            ext = item.suffix.lower()
            detected_source = "Desconocido"
            
            if ext in photo_extensions and self.organize_photos.get():
                file_type = 'photo'
                stats['photos'] += 1
                if 'photo_' in item.name:
                    detected_source = "Telegram"
                    stats['telegram'] += 1
                elif 'WhatsApp Image' in item.name:
                    detected_source = "WhatsApp"
                    stats['whatsapp'] += 1
            elif ext in video_extensions and self.organize_videos.get():
                file_type = 'video'
                stats['videos'] += 1
                if '-VIDEO-' in item.name:
                    detected_source = "Telegram"
                    stats['telegram'] += 1
            else:
                stats['skipped'] += 1
                continue
            
            date = self.parse_date_from_filename(item.name, file_type)
            
            if date:
                date_key = date.strftime('%Y-%m-%d')
                if file_type == 'photo':
                    if date_key not in organized_photos:
                        organized_photos[date_key] = []
                    organized_photos[date_key].append((item, detected_source))
                else:
                    if date_key not in organized_videos:
                        organized_videos[date_key] = []
                    organized_videos[date_key].append((item, detected_source))
            else:
                stats['errors'] += 1
                self.log_text.insert(tk.END, f"⚠️ Fallo parseo: {item.name}\n", 'warning')
        
        self.log_text.insert(tk.END, f"\n📊 ANÁLISIS COMPLETADO:\n", 'info')
        self.log_text.insert(tk.END, f"   Total Fotos: {stats['photos']} (Telegram: {stats['telegram']}, WhatsApp: {stats['whatsapp']})\n", 'info')
        self.log_text.insert(tk.END, f"   Total Videos: {stats['videos']}\n", 'info')
        self.log_text.insert(tk.END, f"   Fechas Únicas Fotos: {len(organized_photos)}\n", 'info')
        self.log_text.insert(tk.END, f"   Fechas Únicas Videos: {len(organized_videos)}\n", 'info')
        self.log_text.insert(tk.END, f"   Errores: {stats['errors']}\n", 'warning' if stats['errors'] > 0 else 'info')
        self.log_text.insert(tk.END, f"{'='*60}\n\n", 'info')
        
        if self.dry_run.get():
            self.log_text.insert(tk.END, "🧪 MODO PRUEBA: Se mostrará qué pasaría, pero nada se moverá.\n", 'warning')
        else:
            self.log_text.insert(tk.END, "🚀 EJECUTANDO: Moviendo archivos...\n", 'success')
        
        total_moved = 0
        
        if organized_photos:
            self.log_text.insert(tk.END, "📷 ORGANIZANDO FOTOS:\n", 'info')
            for date_key, files in sorted(organized_photos.items()):
                target_folder = source_path / "Photos" / date_key
                count = len(files)
                sources = set(src for _, src in files)
                
                self.log_text.insert(tk.END, f"   📁 {date_key} ({count} archivos) - Origen: {', '.join(sources)}\n", 'info')
                
                if not self.dry_run.get():
                    try:
                        target_folder.mkdir(parents=True, exist_ok=True)
                        for file, _ in files:
                            shutil.move(str(file), str(target_folder / file.name))
                            total_moved += 1
                    except Exception as e:
                        self.log_text.insert(tk.END, f"      ❌ Error moviendo: {str(e)}\n", 'error')
                        stats['errors'] += 1
        
        if organized_videos:
            self.log_text.insert(tk.END, "\n🎬 ORGANIZANDO VIDEOS:\n", 'info')
            for date_key, files in sorted(organized_videos.items()):
                target_folder = source_path / "Videos" / date_key
                count = len(files)
                
                self.log_text.insert(tk.END, f"   📁 {date_key} ({count} archivos)\n", 'info')
                
                if not self.dry_run.get():
                    try:
                        target_folder.mkdir(parents=True, exist_ok=True)
                        for file, _ in files:
                            shutil.move(str(file), str(target_folder / file.name))
                            total_moved += 1
                    except Exception as e:
                        self.log_text.insert(tk.END, f"      ❌ Error moviendo: {str(e)}\n", 'error')
                        stats['errors'] += 1
        
        self.log_text.see(tk.END)
        
        msg_title = "Modo Prueba" if self.dry_run.get() else "¡Completado!"
        msg_body = (f"Análisis finalizado.\n"
                   f"Carpetas Fotos: {len(organized_photos)}\n"
                   f"Carpetas Videos: {len(organized_videos)}\n")
        
        if not self.dry_run.get():
            msg_body += f"Archivos movidos: {total_moved}"
        else:
            msg_body += "(Nada se ha movido aún)"
            
        messagebox.showinfo(msg_title, msg_body)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiraiMirror(root)
    root.mainloop()