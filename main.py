import os
import re
import shutil
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class CustomLabelFrame:
    """
    Widget personalizado que simula LabelFrame pero con control total de colores.
    Reemplaza ttk.LabelFrame para evitar problemas de renderizado en Windows.
    """
    def __init__(self, parent, text, padding=10, **kwargs):
        self.parent = parent
        self.text = text
        self.padding = padding
        self.frame = tk.Frame(parent, **kwargs)
        self.border_frame = tk.Frame(self.frame, bg='#cbd5e1')  # Borde gris claro por defecto
        self.inner_frame = tk.Frame(self.border_frame, bg='#e3eef7')  # Interior azul claro por defecto
        self.label = tk.Label(self.border_frame, text=text, font=('Segoe UI', 9, 'bold'))
        
        # Layout
        self.border_frame.pack(fill='both', expand=True, padx=1, pady=1)
        self.label.place(x=10, y=-8)  # Label sobre el borde
        self.inner_frame.pack(fill='both', expand=True, padx=padding, pady=padding)
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        
    def place(self, **kwargs):
        self.frame.place(**kwargs)
        
    def config(self, **kwargs):
        if 'bg' in kwargs or 'background' in kwargs:
            bg = kwargs.get('bg', kwargs.get('background'))
            self.border_frame.config(bg=bg)
            self.frame.config(bg=bg)
        if 'text' in kwargs:
            self.label.config(text=kwargs['text'])
        return self.frame.config(**kwargs)
        
    def winfo_children(self):
        return self.inner_frame.winfo_children()
        
    def winfo_id(self):
        return self.frame.winfo_id()


class MiraiMirror:
    def __init__(self, root):
        self.root = root
        self.root.title("Mirai Mirror")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        # Configurar icono
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Variables
        self.source_folder = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        self.organize_photos = tk.BooleanVar(value=True)
        self.organize_videos = tk.BooleanVar(value=True)
        self.current_theme = "light"
        
        # Cargar tema guardado
        self.load_theme_preference()
        
        # Configurar estilos
        self.setup_styles()
        
        # Ahora sí crear widgets
        self.create_widgets()
        
    def load_theme_preference(self):
        """Carga el tema preferido del usuario"""
        config_file = Path("mirai_mirror_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', 'light')
            except:
                self.current_theme = "light"
        else:
            self.current_theme = "light"
    
    def save_theme_preference(self):
        """Guarda el tema preferido del usuario"""
        config_file = Path("mirai_mirror_config.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f, indent=2)
        except Exception as e:
            print(f"Error guardando tema: {e}")
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_theme_preference()
        self.apply_theme()
    
    def setup_styles(self):
        """Define las paletas de colores para ambos temas"""
        self.colors = {
            'light': {
                'bg_primary': '#f0f5fa',
                'bg_secondary': '#e3eef7',
                'border_color': '#cbd5e1',
                'accent': '#2563eb',
                'accent_dark': '#1e40af',
                'text_primary': '#1e293b',
                'text_secondary': '#64748b',
                'btn_bg': '#f0f5fa',
                'btn_fg': '#2563eb',
                'btn_hover': '#dbeafe',
                'entry_bg': 'white',
                'scroll_bg': '#cbd5e1',
                'check_bg': '#e3eef7',
                'check_fg': '#1e293b',
            },
            'dark': {
                'bg_primary': '#0f172a',
                'bg_secondary': '#1e293b',
                'border_color': '#334155',
                'accent': '#3b82f6',
                'accent_dark': '#60a5fa',
                'text_primary': '#f1f5f9',
                'text_secondary': '#94a3b8',
                'btn_bg': '#1e293b',
                'btn_fg': '#3b82f6',
                'btn_hover': '#334155',
                'entry_bg': '#1e293b',
                'scroll_bg': '#334155',
                'check_bg': '#1e293b',
                'check_fg': '#f1f5f9',
            }
        }
    
    def apply_theme(self):
        """Aplica el tema a TODA la interfaz"""
        colors = self.colors[self.current_theme]
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos ttk (SOLO VÍA STYLE)
        style.configure('TFrame', background=colors['bg_primary'])
        style.configure('TLabel', background=colors['bg_primary'], foreground=colors['text_primary'])
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=colors['accent'], background=colors['bg_primary'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11), foreground=colors['text_secondary'], background=colors['bg_primary'])
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=(15, 10), borderwidth=0, background=colors['btn_bg'], foreground=colors['btn_fg'])
        style.configure('Primary.TButton', background=colors['accent'], foreground='white', borderwidth=0)
        style.map('Primary.TButton', background=[('active', colors['accent_dark'])])
        style.map('TButton', background=[('active', colors['btn_hover'])])
        style.configure('TCheckbutton', background=colors['check_bg'], foreground=colors['check_fg'], font=('Segoe UI', 10), indicatorcolor=colors['accent'])
        style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['text_primary'], borderwidth=1, relief='solid', bordercolor=colors['border_color'])
        style.configure('TScrollbar', background=colors['scroll_bg'], troughcolor=colors['bg_primary'], arrowcolor=colors['text_primary'])
        
        # Actualizar CustomLabelFrames (SOLO los Frames, NO los ttk widgets internos)
        self.update_custom_labelframes(colors)
        
        # Actualizar Text widget (tk.Text SÍ acepta .config())
        self.log_text.config(
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            insertbackground=colors['text_primary'],
            selectbackground=colors['accent'],
            selectforeground='white'
        )
        
        # NOTA: NO intentamos configurar ttk.Scrollbar directamente
        # El Style ya se encarga de eso en la línea anterior: style.configure('TScrollbar', ...)
        
        # Actualizar Entry (ttk.Entry SÍ acepta .config() para bg/fg en algunos casos, pero mejor vía Style)
        # Si falla, confiamos en el Style
        try:
            self.entry_folder.config(
                bg=colors['entry_bg'],
                fg=colors['text_primary']
            )
        except:
            pass  # Si falla, el Style ya lo configuró
        
        # Actualizar botón de tema
        self.theme_button.config(text="🌙" if self.current_theme == "light" else "☀️")
    
    def update_custom_labelframes(self, colors):
        """Actualiza los CustomLabelFrames con los nuevos colores"""
        # Actualizar frame de configuración
        self.config_frame.border_frame.config(bg=colors['border_color'])
        self.config_frame.inner_frame.config(bg=colors['bg_secondary'])
        self.config_frame.frame.config(bg=colors['bg_primary'])
        self.config_frame.label.config(fg=colors['text_primary'], bg=colors['bg_primary'])
        
        # Actualizar frame de registro
        self.log_frame.border_frame.config(bg=colors['border_color'])
        self.log_frame.inner_frame.config(bg=colors['bg_secondary'])
        self.log_frame.frame.config(bg=colors['bg_primary'])
        self.log_frame.label.config(fg=colors['text_primary'], bg=colors['bg_primary'])
    
    def create_widgets(self):
        colors = self.colors[self.current_theme]
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === HEADER ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Logo
        try:
            logo = tk.PhotoImage(file="logo.png")
            logo_label = ttk.Label(header_frame, image=logo)
            logo_label.image = logo
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except:
            logo_label = ttk.Label(header_frame, text="🪞", font=('Segoe UI', 24))
            logo_label.grid(row=0, column=0, padx=(0, 10))
        
        # Título
        title_label = ttk.Label(header_frame, text="Mirai Mirror", style='Title.TLabel')
        title_label.grid(row=0, column=1, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Organizador Universal de Medios", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # Botón de tema
        self.theme_button = ttk.Button(
            header_frame, 
            text="🌙" if self.current_theme == "light" else "☀️",
            command=self.toggle_theme,
            width=5
        )
        self.theme_button.grid(row=0, column=2, sticky=tk.E)
        
        # === SELECCIÓN DE CARPETA ===
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Label(folder_frame, text="📂 Carpeta de Archivos:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.entry_folder = ttk.Entry(folder_frame, textvariable=self.source_folder, width=50)
        self.entry_folder.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(folder_frame, text="Explorar...", command=self.browse_folder, width=12)
        browse_btn.grid(row=0, column=2)
        
        # === OPCIONES (CustomLabelFrame) ===
        self.config_frame = CustomLabelFrame(main_frame, text="Configuración", padding=15, bg=colors['bg_primary'])
        self.config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Checkbuttons (dentro de inner_frame)
        self.cb_photos = ttk.Checkbutton(self.config_frame.inner_frame, text="📷 Fotos (Telegram & WhatsApp)", variable=self.organize_photos)
        self.cb_photos.grid(row=0, column=0, sticky=tk.W, padx=15, pady=5)
        
        self.cb_videos = ttk.Checkbutton(self.config_frame.inner_frame, text="🎬 Videos (Telegram)", variable=self.organize_videos)
        self.cb_videos.grid(row=0, column=1, sticky=tk.W, padx=15, pady=5)
        
        self.cb_dryrun = ttk.Checkbutton(self.config_frame.inner_frame, text="🧪 Modo Prueba (solo análisis)", variable=self.dry_run)
        self.cb_dryrun.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=15, pady=5)
        
        # === BOTÓN PRINCIPAL ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        action_btn = ttk.Button(btn_frame, text="🚀 Iniciar Organización", command=self.organize_files, style='Primary.TButton', width=25)
        action_btn.pack()
        
        # === LOG (CustomLabelFrame) ===
        self.log_frame = CustomLabelFrame(main_frame, text="Registro de Actividad", padding=10, bg=colors['bg_primary'])
        self.log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.log_frame.inner_frame.columnconfigure(0, weight=1)
        self.log_frame.inner_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(
            self.log_frame.inner_frame, 
            height=10, 
            width=80, 
            font=('Consolas', 9),
            bg=colors['bg_secondary'],
            fg=colors['text_primary'],
            bd=0, 
            highlightthickness=0,
            padx=10, 
            pady=10
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar (NO configuramos colores aquí, el Style lo hace)
        self.scrollbar = ttk.Scrollbar(self.log_frame.inner_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        
        # Tags para colores en el log
        self.log_text.tag_config('info', foreground=colors['text_primary'])
        self.log_text.tag_config('success', foreground='#10b981')
        self.log_text.tag_config('warning', foreground='#f59e0b')
        self.log_text.tag_config('error', foreground='#ef4444')
        
        # Aplicar tema inicial
        self.apply_theme()
    
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