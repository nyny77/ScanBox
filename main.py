import tkinter as tk
import os
import os
from tkinter import ttk, filedialog, messagebox, simpledialog, font
from ttkthemes import ThemedTk
import game_parser
import file_operations 
import exporter      
import csv
import PIL
from PIL import Image, ImageTk # Ajout pour l'aperçu d'image
from tkinter.ttk import Notebook # Pour les onglets Image/Vidéo
import vlc
import logging
import logging.handlers # Pour RotatingFileHandler
import threading
import queue
import configparser
import sys # Ajout pour PyInstaller
import platform # Ajout pour la détection de plateforme


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # sys._MEIPASS is not set; we are not running from a PyInstaller bundle
        base_path = os.path.dirname(os.path.abspath(__file__)) # Use script's directory
    return os.path.join(base_path, relative_path)


# Liste des systèmes pour la Combobox
SYSTEM_DEFINITIONS = sorted([
    {'display_name': "240p Test Suite", 'internal_name': "240ptestsuite", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "3DO Interactive Multiplayer", 'internal_name': "3do", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amiga 1200", 'internal_name': "amiga1200", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amiga 600", 'internal_name': "amiga600", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amiga CD32", 'internal_name': "amigacd32", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amiga CDTV", 'internal_name': "amigacdtv", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amstrad CPC", 'internal_name': "amstradcpc", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Amstrad GX4000", 'internal_name': "gx4000", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Apple II", 'internal_name': "apple2", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Apple IIgs", 'internal_name': "apple2gs", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Arduboy", 'internal_name': "arduboy", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari 2600", 'internal_name': "atari2600", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari 5200", 'internal_name': "atari5200", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari 7800", 'internal_name': "atari7800", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari 800", 'internal_name': "atari800", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari Jaguar", 'internal_name': "jaguar", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari Lynx", 'internal_name': "lynx", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atari ST/STE", 'internal_name': "atarist", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Atomiswave", 'internal_name': "atomiswave", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "BBC Micro", 'internal_name': "bbcmicro", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "BK (Elektronika)", 'internal_name': "bk", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "ColecoVision", 'internal_name': "colecovision", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Commodore 64", 'internal_name': "c64", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Commodore VIC-20", 'internal_name': "vic20", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "DICE", 'internal_name': "dice", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "DOS (DOSBox)", 'internal_name': "dos", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Daphne (Laserdisc)", 'internal_name': "daphne", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Dragon 32/64", 'internal_name': "dragon", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "EasyRPG", 'internal_name': "easyrpg", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Fairchild Channel F", 'internal_name': "channelf", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Famicom Disk System", 'internal_name': "fds", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "FinalBurn Neo (FBNeo)", 'internal_name': "fbneo", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Game & Watch", 'internal_name': "gw", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Game Boy", 'internal_name': "gb", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Game Boy Advance", 'internal_name': "gba", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Game Boy Color", 'internal_name': "gbc", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Intellivision", 'internal_name': "intellivision", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "LowRes NX", 'internal_name': "lowresnx", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Lutro", 'internal_name': "lutro", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "MAME", 'internal_name': "mame", 'ignore_name_patterns': ["neogeo", "pgm", "cvs", "stvbios", "skns", "decocass", "isgsm", "konamigx", "taitofx1"], 'ignore_path_extensions': []},
    {'display_name': "MSX1", 'internal_name': "msx1", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "MSX2", 'internal_name': "msx2", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "MSX Turbo R", 'internal_name': "msxturbor", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Macintosh", 'internal_name': "macintosh", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Mega Duck", 'internal_name': "megaduck", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Moonlight", 'internal_name': "moonlight", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "NEC PC-8801", 'internal_name': "pc88", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "NEC PC-9801", 'internal_name': "pc98", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "NEC PC-FX", 'internal_name': "pcfx", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "NEC PC-FXGA / MultiVision", 'internal_name': "multivision", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Neo Geo", 'internal_name': "neogeo", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Neo Geo CD", 'internal_name': "neogeocd", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Neo Geo Pocket", 'internal_name': "ngp", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Neo Geo Pocket Color", 'internal_name': "ngpc", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo 64", 'internal_name': "n64", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo 64DD", 'internal_name': "64dd", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo DS", 'internal_name': "nds", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo Entertainment System (NES/Famicom)", 'internal_name': "nes", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo GameCube", 'internal_name': "gamecube", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Nintendo Wii", 'internal_name': "wii", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Odyssey 2 / Videopac", 'internal_name': "o2em", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "OpenBOR", 'internal_name': "openbor", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Oric Atmos", 'internal_name': "oricatmos", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PC Engine / TurboGrafx-16", 'internal_name': "pcengine", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PC Engine CD", 'internal_name': "pcenginecd", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PC Engine SuperGrafx", 'internal_name': "supergrafx", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PICO-8", 'internal_name': "pico8", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Palm OS", 'internal_name': "palm", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Philips CD-i", 'internal_name': "cdi", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Philips VG 5000", 'internal_name': "vg5000", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PlayStation (Sony PSX)", 'internal_name': "psx", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PlayStation 2 (Sony PS2)", 'internal_name': "ps2", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "PlayStation Portable (Sony PSP)", 'internal_name': "psp", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Pokemon Mini", 'internal_name': "pokemini", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Ports", 'internal_name': "ports", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "SAM Coupé", 'internal_name': "samcoupe", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Satellaview", 'internal_name': "satellaview", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "ScummVM", 'internal_name': "scummvm", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega 32X", 'internal_name': "sega32x", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega CD / Mega-CD", 'internal_name': "segacd", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Dreamcast", 'internal_name': "dreamcast", 'ignore_name_patterns': ["zzz(notgame):"], 'ignore_path_extensions': [".bin"]},
    {'display_name': "Sega Game Gear", 'internal_name': "gamegear", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Master System", 'internal_name': "mastersystem", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Megadrive / Genesis", 'internal_name': "megadrive", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Naomi", 'internal_name': "naomi", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Naomi 2", 'internal_name': "naomi2", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Naomi GD-ROM", 'internal_name': "naomigd", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Pico", 'internal_name': "pico", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega SG-1000", 'internal_name': "sg1000", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sega Saturn", 'internal_name': "saturn", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sharp X1", 'internal_name': "x1", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sharp X68000", 'internal_name': "x68000", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sinclair ZX81", 'internal_name': "zx81", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Solarus", 'internal_name': "solarus", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Spectravideo", 'internal_name': "spectravideo", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "SuFami Turbo", 'internal_name': "sufami", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Super Cassette Vision", 'internal_name': "scv", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Super Nintendo (SNES/SFC)", 'internal_name': "snes", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Sammy Hikaru", 'internal_name': "hikaru", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "TI-99/4A", 'internal_name': "ti994a", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "TIC-80", 'internal_name': "tic80", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "TRS-80 Color Computer", 'internal_name': "trs80coco", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Taito Type X", 'internal_name': "taitox", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Thomson TO7 / TO8", 'internal_name': "thomson", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Uzebox", 'internal_name': "uzebox", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Vectrex", 'internal_name': "vectrex", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Videopac+ / Odyssey3", 'internal_name': "videopacplus", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Virtual Boy", 'internal_name': "virtualboy", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Visual Pinball", 'internal_name': "vpinball", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "WASM-4", 'internal_name': "wasm4", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Watara Supervision", 'internal_name': "supervision", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Watara Supervision (PC V2)", 'internal_name': "pcv2", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Wonderswan", 'internal_name': "wswan", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Wonderswan Color", 'internal_name': "wswanc", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Xbox (Original)", 'internal_name': "xbox", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "Z-machine", 'internal_name': "zmachine", 'ignore_name_patterns': [], 'ignore_path_extensions': []},
    {'display_name': "ZX Spectrum", 'internal_name': "zxspectrum", 'ignore_name_patterns': [], 'ignore_path_extensions': []}
], key=lambda x: x['display_name'])
# Assurez-vous d'avoir Pillow installé: pip install Pillow
SETTINGS_FILE = resource_path("scanbox_settings.ini")

class ScanBoxApp(ThemedTk): # Hérite de ThemedTk pour les thèmes
    def __init__(self):
        self._setup_logging() # CONFIGURATION DU LOGGING EN PREMIER
        ThemedTk.__init__(self, theme="plastik")  # Initialise ThemedTk (et donc tk.Tk) avec un thème
        
        logging.debug(f"Tcl auto_path AVANT TOUTE MODIFICATION: {self.tk.eval('set auto_path')}")
        logging.debug(f"Tcl package names AVANT TOUTE MODIFICATION: {self.tk.eval('package names')}")

        self.title("ScanBox V1")
        self.geometry("950x750")
        self.state('zoomed')

        self.root_roms_folder_path = tk.StringVar() # Renommé
        self.selected_system_var = tk.StringVar()   # Pour la Combobox
        self.system_display_to_internal_map = {system_def['display_name']: system_def['internal_name'] for system_def in SYSTEM_DEFINITIONS}
        self.system_internal_to_definition_map = {system_def['internal_name']: system_def for system_def in SYSTEM_DEFINITIONS}
        self.games_data = []
        self.tree_item_to_game_map = {} # Pour mapper les IDs d'éléments de l'arbre aux données de jeu
        self.show_missing_only_var = tk.BooleanVar()
        self.image_preview_label = None
        self.image_preview_frame = None # Ce sera l'onglet image
        self.default_game_image_tk = None
        try:
            self.vlc_instance = vlc.Instance()
            self.player = self.vlc_instance.media_player_new()
            logging.info("Instance VLC et lecteur initialisés avec succès.")
            # La configuration de l'état audio initial de VLC (mute/volume) sera faite via self.after
        except Exception as e: # Attraper une exception générique car le type exact peut varier
            logging.warning(f"Impossible d'initialiser VLC (librairie python-vlc ou VLC lui-même manquant/incorrect ?): {e}. La fonctionnalité vidéo sera désactivée.")
            self.vlc_instance = None
            self.player = None
        self.video_frame_id = None

        self.current_tree_colors = {
            'image_present': 'green',
            'image_missing': 'red',
            'video_present': 'green',
            'video_missing': 'red',
            'default_fg': 'black',
            'tree_bg': 'white' # Fond du treeview en mode clair
        }
        self.preview_notebook = None # Pour accéder au Notebook plus tard
        self.current_video_path = None # Garder une trace de la vidéo chargée
        self.video_message_label = None # Label pour messages dans l'onglet vidéo
        self.selected_game_data = None # Données du jeu actuellement sélectionné dans le Treeview
        self.drag_drop_instruction_label = None # Initialiser l'attribut
        self.analysis_queue = queue.Queue()
        self.mute_button = None
        self.video_muted = False # Initialisation de l'état du mute vidéo (souhait : son activé)
        self.icon_sound_on = "🔊"
        self.icon_sound_off = "🔇"
        self.default_volume = 80 # Volume par défaut pour VLC au démarrage

        # Variables pour le tri du Treeview
        self.sort_column_key = None
        self.sort_reverse_order = False

        self.style = ttk.Style(self) # Initialize ttk.Style object for the app
        self.selection_debounce_timer = None # Pour le debouncing de la sélection
        self.image_cache = {} # Cache pour les PhotoImage

        self._setup_logging()
        self.setup_ui()
        self._load_settings()
        # self.center_window() will call update_idletasks internally.
        # Center the window when it's first mapped to the screen.
        self.bind("<Map>", self.center_window_on_map_once)

        # Appliquer les paramètres audio initiaux à VLC après que la boucle Tkinter soit prête
        self.after(500, self.apply_initial_vlc_audio_settings)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

    def on_mute_button_raw_click(self, event):
        logging.debug("on_mute_button_raw_click: Raw <Button-1> event detected on mute button.")

    def _sort_by_column(self, column_key):
        logging.debug(f"Tentative de tri par colonne : {column_key}")

        if self.sort_column_key == column_key:
            self.sort_reverse_order = not self.sort_reverse_order
        else:
            self.sort_column_key = column_key
            self.sort_reverse_order = False # Par défaut, tri ascendant

        if not self.games_data:
            logging.debug("Aucune donnée de jeu à trier.")
            return

        try:
            if column_key == "rating":
                def get_rating_sort_key(game):
                    rating_value = game.get('rating')
                    if isinstance(rating_value, (int, float)):
                        return rating_value
                    return -1
                self.games_data.sort(key=get_rating_sort_key, reverse=self.sort_reverse_order)
                logging.info(f"Jeux triés par note, ordre inversé : {self.sort_reverse_order}")
            elif column_key == "game_name":
                self.games_data.sort(key=lambda game: str(game.get("game_name", "")).lower(), reverse=self.sort_reverse_order)
                logging.info(f"Jeux triés par nom, ordre inversé : {self.sort_reverse_order}")
            else:
                self.games_data.sort(key=lambda game: str(game.get(column_key, "")), reverse=self.sort_reverse_order)
                logging.info(f"Jeux triés par {column_key}, ordre inversé : {self.sort_reverse_order}")
            self.refresh_treeview()
        except Exception as e:
            logging.error(f"Erreur lors du tri par la colonne {column_key}: {e}")
            messagebox.showerror("Erreur de Tri", f"Une erreur est survenue lors du tri : {e}")

    def _set_controls_state(self, new_state):
        """Enable or disable main UI controls."""
        # Convert boolean to tk.NORMAL or tk.DISABLED
        state_val = tk.NORMAL if new_state else tk.DISABLED

        if hasattr(self, 'folder_select_button'):
            self.folder_select_button.config(state=tk.NORMAL) # This button should always be enabled
        if hasattr(self, 'system_combobox'):
            if new_state:
                self.system_combobox.config(state='readonly') # Enable to readonly
            else:
                self.system_combobox.config(state=tk.DISABLED) # Disable

        if hasattr(self, 'analyze_button'):
            # Special handling for analyze_button: only enable if new_state is true 
            # AND a system is selected AND there are systems in the combobox.
            can_analyze = new_state and self.selected_system_var.get() and self.system_combobox['values']
            self.analyze_button.config(state=tk.NORMAL if can_analyze else tk.DISABLED)
            if can_analyze:
                logging.debug(f"Bouton Analyser activé car état général={new_state}, système sélectionné='{self.selected_system_var.get()}', systèmes disponibles.")
            else:
                logging.debug(f"Bouton Analyser désactivé. État général={new_state}, système sélectionné='{self.selected_system_var.get()}', systèmes disponibles? {'Oui' if self.system_combobox['values'] else 'Non'}.")

        if hasattr(self, 'copy_button'):
            self.copy_button.config(state=state_val)
        if hasattr(self, 'delete_button'):
            self.delete_button.config(state=state_val)
        if hasattr(self, 'export_button'):
            self.export_button.config(state=state_val)
        if hasattr(self, 'clean_orphans_button'):
            self.clean_orphans_button.config(state=state_val)
        # Add other controls if needed
        logging.debug(f"Controls state set to: {'NORMAL' if new_state else 'DISABLED'}")

    def _setup_logging(self):
        # Vérifier si les handlers de logging ont déjà été configurés pour éviter les doublons
        if not hasattr(ScanBoxApp, '_logging_configured'):
            log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
            root_logger = logging.getLogger() # Obtenir le logger racine
            root_logger.setLevel(logging.DEBUG) # Définir le niveau le plus bas pour le logger racine

            # Vider les handlers existants pour éviter les duplications si cette méthode est appelée plusieurs fois
            # (ce qui semble être le cas d'après les logs de console dupliqués)
            if root_logger.hasHandlers():
                root_logger.handlers.clear()

            # Handler pour la console (niveau INFO)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(logging.INFO)
            root_logger.addHandler(console_handler)

            # Handler pour un fichier simple (niveau DEBUG)
            try:
                log_file_path = os.path.join(os.path.dirname(__file__), 'scanbox.log')
                # Rétablissement du RotatingFileHandler
                # 5MB par fichier, garde 3 fichiers de backup
                file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
                file_handler.setFormatter(log_formatter)
                file_handler.setLevel(logging.DEBUG)
                root_logger.addHandler(file_handler)
                logging.info(f"Logging configuré. Les logs DEBUG sont enregistrés dans {log_file_path}")
                ScanBoxApp._logging_configured = True # Marquer comme configuré
            except Exception as e:
                # Si la configuration du fichier de log échoue, au moins la console fonctionnera
                logging.error(f"Impossible de configurer le logging fichier: {e}")
        else:
            logging.info("Configuration du logging déjà effectuée, skip.")

    def select_root_roms_folder(self): # Renommé
        """Ouvre une boîte de dialogue pour sélectionner le dossier racine des ROMs de Recalbox."""
        folder_selected = filedialog.askdirectory(title="Sélectionner le dossier 'roms' de Recalbox")
        if folder_selected:
            self.root_roms_folder_path.set(folder_selected)
            self._update_system_combobox_filter() # Mettre à jour la liste des systèmes
            self._save_settings() # Sauvegarder le chemin sélectionné

    def on_system_selected(self, *args): # *args est nécessaire pour le callback de trace
        selected_display_name = self.selected_system_var.get()
        if selected_display_name:
            logging.info(f"Système sélectionné: {selected_display_name}")
            # L'état du bouton Analyser est géré par _set_controls_state, 
            # qui devrait être appelé si nécessaire, ou la logique est déjà là.
            # On s'assure que les contrôles sont dans un état cohérent.
            self._set_controls_state(True) # Assumer que si un système est sélectionné, les contrôles doivent être actifs
        else:
            logging.info("Sélection du système effacée.")
            self._set_controls_state(False) # Désactiver les contrôles si aucun système n'est sélectionné
        
        self._save_settings() # Sauvegarder le choix (ou l'absence de choix)

    def on_delete_key_press(self, event):
        """Gère l'appui sur la touche Suppr pour supprimer les jeux sélectionnés."""
        logging.debug("Touche Suppr pressée.")
        self.delete_selected_games_wrapper()

    def _update_system_combobox_filter(self):
        root_folder = self.root_roms_folder_path.get()
        
        available_systems_display_names = []
        button_state = tk.DISABLED # Default to disabled

        if root_folder and os.path.isdir(root_folder):
            logging.debug(f"Filtering system combobox for root folder: {root_folder}")
            for system_def in SYSTEM_DEFINITIONS:
                display_name = system_def['display_name']
                internal_name = system_def['internal_name']
                gamelist_path = os.path.join(root_folder, internal_name, "gamelist.xml")
                if os.path.exists(gamelist_path):
                    available_systems_display_names.append(display_name)
            
            if available_systems_display_names:
                button_state = tk.NORMAL # Enable button if systems found
            else:
                logging.info(f"No systems with gamelist.xml found in {root_folder}")
                # self.update_status("Aucun système avec gamelist.xml trouvé.", 0) # Optional message
        else:
            # No valid root folder selected yet. Combobox remains empty, button disabled.
            logging.debug("Root folder not set or invalid. System combobox empty, analyze button disabled.")

        current_selected_system = self.selected_system_var.get()
        if hasattr(self, 'system_combobox'): # Ensure combobox exists
            self.system_combobox['values'] = available_systems_display_names # Update values
        
        if available_systems_display_names:
            if current_selected_system in available_systems_display_names:
                self.selected_system_var.set(current_selected_system) 
            else:
                self.selected_system_var.set(available_systems_display_names[0])
        else:
            self.selected_system_var.set("") 
        
        if hasattr(self, 'analyze_button'): # Ensure button exists
            self.analyze_button.config(state=button_state)

    def setup_ui(self):
        # --- Cadre Supérieur pour les Contrôles Principaux ---
        controls_frame = ttk.Frame(self, padding="10")
        controls_frame.pack(side="top", fill="x", pady=5, padx=10)

        # Sélection dossier ROMS racine
        self.folder_select_button = ttk.Button(controls_frame, text="Dossier Roms Racine", command=self.select_root_roms_folder)
        self.folder_select_button.pack(side="left", padx=(0, 5))
        self.folder_path_label = ttk.Entry(controls_frame, textvariable=self.root_roms_folder_path, width=40, state="readonly")
        self.folder_path_label.pack(side="left", expand=True, fill="x", padx=5)

        # Sélection Système
        system_label = ttk.Label(controls_frame, text="Système:")
        system_label.pack(side="left", padx=(10,0))
        self.system_combobox = ttk.Combobox(controls_frame, textvariable=self.selected_system_var, values=[], width=35, state="readonly") # Init with empty values
        self.system_combobox.pack(side="left", padx=5)

        self.analyze_button = ttk.Button(controls_frame, text="Analyser Système", command=self.analyze_games_wrapper, state=tk.DISABLED) # Start disabled
        self.analyze_button.pack(side="left", padx=5)

        
        self.status_label = ttk.Label(controls_frame, text="Prêt.", anchor="e")
        self.status_label.pack(side="right", padx=5)

        # --- Cadre Central pour TreeView et Filtre ---
        # --- Cadre Central Principal --- 
        main_content_frame = ttk.Frame(self, padding="10")
        main_content_frame.pack(expand=True, fill="both", padx=10)

        # --- Cadre pour TreeView et Filtre (à gauche) ---
        left_frame = ttk.Frame(main_content_frame)
        left_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))

        self.filter_checkbox = ttk.Checkbutton(left_frame, text="Afficher jeux sans image/tag uniquement", 
                                          variable=self.show_missing_only_var, command=self.refresh_treeview)
        self.filter_checkbox.pack(anchor="w", pady=(0,5))

        tree_container_frame = ttk.Frame(left_frame) # Conteneur pour Treeview et Scrollbar
        tree_container_frame.pack(expand=True, fill="both")

        columns = ("system", "game_name", "rom_path", "image_status", "video_status", "rating")
        self.games_tree = ttk.Treeview(tree_container_frame, columns=columns, show="headings", selectmode="extended")
        
        self.games_tree.heading("system", text="Système")
        self.games_tree.column("system", width=100, stretch=tk.NO, anchor="w")
        self.games_tree.heading("game_name", text="Nom du Jeu", command=lambda: self._sort_by_column("game_name"))
        self.games_tree.column("game_name", width=300, anchor="w")
        self.games_tree.heading("rom_path", text="Fichier ROM") # Changement d'en-tête
        self.games_tree.column("rom_path", width=250, anchor="w")

        self.games_tree.heading("image_status", text="Statut Image", command=lambda: self._sort_by_column("image_status"))
        self.games_tree.column("image_status", width=100, stretch=tk.NO, anchor="center")
        self.games_tree.heading("video_status", text="Statut Vidéo", command=lambda: self._sort_by_column("video_status"))
        self.games_tree.column("video_status", width=100, stretch=tk.NO, anchor="center")

        self.games_tree.heading("rating", text="Rating", anchor=tk.W, command=lambda: self._sort_by_column("rating"))
        self.games_tree.column("rating", width=90, stretch=tk.NO, anchor="center")

        # Appliquer le style initial du Treeview au démarrage en utilisant self.style
        # style = ttk.Style() # Removed, use self.style initialized in __init__
        initial_tree_bg = self.current_tree_colors.get('tree_bg', self.style.lookup('TFrame', 'background'))
        self.style.configure("Treeview",
                        # foreground=self.current_tree_colors['default_fg'], # Supprimé pour permettre aux tags de fonctionner
                        background=initial_tree_bg,
                        fieldbackground=initial_tree_bg,
                        font=('TkDefaultFont', 11)) # Augmentation de la taille de la police
        sel_fg_initial = 'SystemHighlightText' # Couleur du texte pour l'élément sélectionné
        sel_bg_initial = 'SystemHighlight'   # Couleur de fond pour l'élément sélectionné
        self.style.map("Treeview",
                  foreground=[('selected', sel_fg_initial)], # Ne pas spécifier de fg pour !selected ici
                  background=[('selected', sel_bg_initial), ('!selected', initial_tree_bg)])
        self.style.configure("Treeview.Heading", 
                        foreground=self.current_tree_colors['default_fg'], 
                        background=self.style.lookup('TButton', 'background'),
                        font=('TkDefaultFont', 10, 'bold'))
        self.style.map("Treeview.Heading",
                  background=[('active', self.style.lookup('TButton', 'selectbackground'))],
                  foreground=[('active', self.style.lookup('TButton', 'foreground'))])

        # Définition des tags pour la coloration des lignes APRÈS la configuration du style général
        # Les lignes suivantes sont commentées pour l'Option B (pas de coloration spécifique des symboles)
        # self.games_tree.tag_configure('image_present', foreground=self.current_tree_colors['image_present'])
        # self.games_tree.tag_configure('image_missing', foreground=self.current_tree_colors['image_missing'])
        # self.games_tree.tag_configure('video_present', foreground=self.current_tree_colors['video_present'])
        # self.games_tree.tag_configure('video_missing', foreground=self.current_tree_colors['video_missing'])

        tree_scrollbar_y = ttk.Scrollbar(tree_container_frame, orient="vertical", command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        tree_scrollbar_y.pack(side="right", fill="y")
        self.games_tree.pack(side="left", expand=True, fill="both")
        self.games_tree.bind("<<TreeviewSelect>>", self.on_game_select)
        self.games_tree.bind("<Delete>", self.on_delete_key_press) # Ajout pour la touche Suppr

        # --- Cadre Inférieur pour les Actions ---
        actions_frame = ttk.LabelFrame(self, text="Actions sur Sélection", padding="10")
        actions_frame.pack(side="bottom", fill="x", pady=(5,0), padx=10)

        self.move_button = ttk.Button(actions_frame, text="Déplacer ROMs...", command=self.move_selected_games_wrapper)
        self.move_button.pack(side="left", padx=5, pady=5)

        self.copy_button = ttk.Button(actions_frame, text="Copier ROMs...", command=self.copy_selected_games_wrapper)
        self.copy_button.pack(side="left", padx=5, pady=5)

        self.delete_button = ttk.Button(actions_frame, text="Supprimer ROMs...", command=self.delete_selected_games_wrapper)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.clean_orphans_button = ttk.Button(actions_frame, text="Rafraichir la liste", command=self.clean_orphaned_games_wrapper)
        self.clean_orphans_button.pack(side="left", padx=5, pady=5)
        self.export_button = ttk.Button(actions_frame, text="Exporter Liste...", command=self.export_game_list_wrapper)
        self.export_button.pack(side="left", padx=5, pady=5) # Placement corrigé
        # --- Cadre pour les Aperçus (à droite) ---
        # Assurez-vous que main_content_frame est bien le parent prévu ici.
        # Si main_content_frame n'est pas accessible ici, cette partie devra être révisée.
        self.preview_pane_right = ttk.Frame(main_content_frame, width=350)
        self.preview_pane_right.pack(side="right", fill="both", expand=True, padx=(5,0))
        self.preview_pane_right.pack_propagate(False)

        self.preview_notebook = ttk.Notebook(self.preview_pane_right)

        # Onglet Image
        self.image_preview_frame = ttk.Frame(self.preview_notebook)
        self.image_preview_label = ttk.Label(self.image_preview_frame, text="Aucun aperçu d'image.", anchor="center", relief="sunken")
        self.image_preview_label.pack(expand=True, fill="both", padx=5, pady=5)
        self.preview_notebook.add(self.image_preview_frame, text="Image")

        # Onglet Vidéo
        self.video_tab_frame = ttk.Frame(self.preview_notebook) # Ce frame sera utilisé par set_hwnd
        self.video_tab_frame.configure(relief="sunken") # Pour visualiser le cadre
        # Le label de message pour la vidéo
        self.video_message_label = ttk.Label(self.video_tab_frame, text="Sélectionnez un jeu pour voir la vidéo.", anchor="center")
        self.video_message_label.pack(expand=True, fill="both", padx=5, pady=5)
        # self.video_muted = False # Moved to __init__
        # Faulty mute_button creation removed from here.
        self.preview_notebook.add(self.video_tab_frame, text="Vidéo")

        self.preview_notebook.pack(expand=True, fill="both", pady=(0,5))
        
        # --- Bouton Mute ---
        # Now created with self.preview_pane_right as parent, after notebook is packed.
        if hasattr(self, 'preview_pane_right') and self.preview_pane_right:
            initial_mute_icon = self.icon_sound_on if not self.video_muted else self.icon_sound_off
            self.mute_button = ttk.Button(self.preview_pane_right, text=initial_mute_icon, command=self.toggle_video_mute, style="Mute.TButton")
            # Configure a specific style for the mute button with a larger font
            button_style = ttk.Style()
            button_style.configure("Mute.TButton", font=('TkDefaultFont', 16))
            if self.mute_button: # Check if button creation was successful
                self.mute_button.bind("<Button-1>", self.on_mute_button_raw_click)
                self.mute_button.pack(side="bottom", pady=5)
        else:
            logging.error("setup_ui: self.preview_pane_right was not defined before attempting to create mute_button.")
        self.preview_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Style pour les onglets du Notebook d'aperçu
        # Utiliser self.style qui est déjà un objet ttk.Style
        self.style.configure('Preview.TNotebook', tabposition='n') # 'n' for North (top)
        self.style.configure('Preview.TNotebook.Tab', padding=[10, 5], font=('TkDefaultFont', 10))
        self.style.map('Preview.TNotebook.Tab',
            font=[('selected', ('TkDefaultFont', 11, 'bold'))],
            background=[('selected', self.style.lookup('TButton', 'selectbackground')), ('!selected', self.style.lookup('TFrame', 'background'))],
            foreground=[('selected', 'black'), ('!selected', 'black')] # Texte en noir pour assurer la visibilité
        )
        self.preview_notebook.configure(style='Preview.TNotebook')

        # self.export_button.pack(side="right", padx=5, pady=5) # Supprimé car incorrectement placé

        # --- Barre de Progression ---
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(side="bottom", fill="x", pady=(0,5), padx=10) # pady ajusté

        # --- Footer pour Copyright ---
        footer_frame = ttk.Frame(self, padding="2")
        footer_frame.pack(side="bottom", fill="x", pady=(0,5), padx=10) 
        copyright_label = ttk.Label(footer_frame, text="By Nyny77", anchor="center") # Remis
        copyright_label.pack(pady=(0, 2)) # Remis

        # Initialiser le filtre de la combobox des systèmes
        self._update_system_combobox_filter()

    def update_status(self, message, progress_value=None):
        """Met à jour le label de statut et la barre de progression."""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
        if hasattr(self, 'progress_bar') and progress_value is not None:
            self.progress_bar['value'] = progress_value
        self.update_idletasks() # Forcer la mise à jour de l'UI

    def analyze_games_wrapper(self):
        root_roms_dir = self.root_roms_folder_path.get()
        selected_display_name = self.selected_system_var.get()

        if not root_roms_dir or not os.path.isdir(root_roms_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier racine de ROMs Recalbox valide.")
            return
        
        if not selected_display_name:
            messagebox.showerror("Erreur", "Veuillez sélectionner un système à analyser.")
            return

        selected_system_internal_name = self.system_display_to_internal_map.get(selected_display_name)
        if not selected_system_internal_name: # Devrait être impossible
            messagebox.showerror("Erreur", f"Nom de système interne non trouvé pour '{selected_display_name}'.")
            return

        self._set_controls_state(False) # Disable controls
        self.update_status(f"Lancement de l'analyse pour: {selected_display_name}...", 0)
        self.progress_bar['value'] = 0
        self.progress_bar.start() # Start indeterminate progress bar

        # Démarrer l'analyse dans un thread séparé
        analysis_thread = threading.Thread(
            target=self._perform_analysis_in_thread,
            args=(root_roms_dir, selected_display_name, selected_system_internal_name),
            daemon=True # Permet à l'application de se fermer même si le thread est en cours
        )
        analysis_thread.start()

        # Commencer à vérifier la file d'attente pour les résultats
        self.after(100, self._check_analysis_queue)

    def _perform_analysis_in_thread(self, root_roms_dir, selected_display_name, selected_system_internal_name):
        try:
            self.analysis_queue.put({'status': 'progress', 'message': f"Analyse de {selected_display_name} en cours...", 'value': 10})
            
            system_roms_path = os.path.join(root_roms_dir, selected_system_internal_name)
            gamelist_file_path = os.path.join(system_roms_path, "gamelist.xml")

            if not os.path.exists(gamelist_file_path):
                self.analysis_queue.put({
                    'status': 'error',
                    'title': "Fichier manquant",
                    'message': f"gamelist.xml non trouvé pour {selected_display_name} dans {system_roms_path}."
                })
                return

            self.analysis_queue.put({'status': 'progress', 'message': f"Lecture de gamelist.xml pour {selected_display_name}...", 'value': 30})
            system_def = self.system_internal_to_definition_map.get(selected_system_internal_name, {})
            ignore_names = system_def.get('ignore_name_patterns', [])
            ignore_extensions = system_def.get('ignore_path_extensions', [])
            parsed_games = game_parser.parse_gamelist(gamelist_file_path, 
                                                      selected_system_internal_name, 
                                                      system_roms_path, 
                                                      ignore_name_patterns=ignore_names, 
                                                      ignore_path_extensions=ignore_extensions)
            
            self.analysis_queue.put({'status': 'progress', 'message': f"Traitement des données pour {selected_display_name}...", 'value': 80})
            
            if parsed_games:
                self.analysis_queue.put({'status': 'complete', 'data': parsed_games, 'system_name': selected_display_name})
            else:
                logging.info(f"Aucun jeu trouvé ou erreur mineure lors de l'analyse de {gamelist_file_path} pour {selected_display_name}.")
                self.analysis_queue.put({'status': 'complete', 'data': [], 'system_name': selected_display_name, 'info_message': f"Aucun jeu trouvé dans gamelist.xml pour {selected_display_name}."})
        
        except Exception as e:
            logging.error(f"Erreur majeure dans le thread d'analyse pour {selected_display_name}: {e}", exc_info=True)
            self.analysis_queue.put({
                'status': 'error',
                'title': "Erreur d'Analyse (Thread)",
                'message': f"Une erreur critique est survenue lors de l'analyse de {selected_display_name}:\n{type(e).__name__}: {e}"
            })

    def _check_analysis_queue(self):
        try:
            message = self.analysis_queue.get_nowait() # Récupérer un message sans bloquer
            
            if message['status'] == 'progress':
                self.update_status(message['message'], message.get('value'))
                self.after(100, self._check_analysis_queue) # Continuer à vérifier
            
            elif message['status'] == 'error':
                self.progress_bar.stop()
                self.progress_bar['value'] = 0
                messagebox.showerror(message['title'], message['message'])
                self.update_status(f"Échec de l'analyse: {message.get('system_name', '')}. Prêt.", 0)
                self._set_controls_state(True) # Réactiver les contrôles
            
            elif message['status'] == 'complete':
                self.progress_bar.stop()
                self.progress_bar['value'] = 100
                
                self.games_data.clear()
                self.tree_item_to_game_map.clear()
                self.reset_previews()
                
                self.games_data.extend(message['data'])
                self.refresh_treeview() # Rafraîchir avec les nouvelles données
                
                num_games = len(self.games_data)
                system_name = message.get('system_name', 'le système')
                completion_message = f"Analyse de {system_name} terminée. {num_games} jeux trouvés."
                if 'info_message' in message:
                    messagebox.showinfo("Info Analyse", message['info_message'])
                    if num_games == 0 : completion_message = message['info_message'] # Override if no games
                
                self.update_status(completion_message, 100)
                self._set_controls_state(True) # Réactiver les contrôles
                
                if not self.games_data and 'info_message' not in message: # Double check if no games and no specific info message
                    messagebox.showinfo("Info", f"Analyse de {system_name} terminée, mais aucun jeu n'a été trouvé.")

        except queue.Empty: # Pas de message dans la file
            self.after(100, self._check_analysis_queue) # Continuer à vérifier
        except Exception as e:
            logging.error(f"Erreur inattendue dans _check_analysis_queue: {e}", exc_info=True)
            self.progress_bar.stop()
            self.progress_bar['value'] = 0
            messagebox.showerror("Erreur Interne", f"Une erreur interne est survenue lors du traitement des résultats d'analyse: {e}")
            self.update_status("Erreur interne. Prêt.", 0)
            self._set_controls_state(True)

    def load_default_image(self):
        """Charge ou crée une image par défaut pour l'aperçu et la met en cache."""
        DEFAULT_IMAGE_CACHE_KEY = "__DEFAULT_IMAGE__"
        if DEFAULT_IMAGE_CACHE_KEY in self.image_cache:
            self.default_game_image_tk = self.image_cache[DEFAULT_IMAGE_CACHE_KEY]
        else:
            try:
                default_pil_image = Image.new('RGB', (200, 150), color = 'lightgrey')
                # from PIL import ImageDraw
                # draw = ImageDraw.Draw(default_pil_image)
                # draw.text((10, 10), "Aucun aperçu", fill="black")
                self.default_game_image_tk = ImageTk.PhotoImage(default_pil_image)
                self.image_cache[DEFAULT_IMAGE_CACHE_KEY] = self.default_game_image_tk
            except ImportError:
                logging.error("Pillow (PIL) n'est pas installé. L'aperçu d'image ne fonctionnera pas.")
                self.default_game_image_tk = None 
            except Exception as e:
                logging.error(f"Erreur lors du chargement de l'image par défaut: {e}")
                self.default_game_image_tk = None
        
        if self.image_preview_label:
            if self.default_game_image_tk:
                self.image_preview_label.config(image=self.default_game_image_tk, text='')
                self.image_preview_label.image = self.default_game_image_tk
            else:
                self.image_preview_label.config(image='', text="Pillow manquant ou erreur")
                self.image_preview_label.image = None

    def _process_selection_change(self):
        selected_item = self.games_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            game_data = self.tree_item_to_game_map.get(item_id)
            self.selected_game_data = game_data # Stocker les données du jeu sélectionné

            if game_data:
                # Déterminer l'onglet actif et mettre à jour l'aperçu en conséquence
                try:
                    if self.preview_notebook and self.preview_notebook.winfo_exists() and self.preview_notebook.select():
                        selected_tab_index = self.preview_notebook.index(self.preview_notebook.select())
                        # 0 = Image, 1 = Vidéo
                        if selected_tab_index == 0:  # Onglet Image actif
                            self.display_game_image(game_data)
                            if self.player and self.player.is_playing(): # Si une vidéo jouait, l'arrêter
                                self.player.stop()
                                self.player.set_media(None) # Détacher le média actuel
                                # S'assurer que le message de l'onglet vidéo est réinitialisé s'il n'est pas visible
                                if self.video_message_label and hasattr(self.video_message_label, 'winfo_ismapped') and not self.video_message_label.winfo_ismapped():
                                    self.video_message_label.config(text="Sélectionnez un jeu pour voir la vidéo.")
                                    self.video_message_label.pack(expand=True, fill="both")
                        elif selected_tab_index == 1:  # Onglet Vidéo actif
                            self.display_game_video(game_data)
                        else: # Fallback si l'index de l'onglet est inattendu
                            self.display_game_image(game_data)
                    else:
                        # Notebook non prêt ou aucun onglet sélectionné, afficher l'image par défaut
                        self.display_game_image(game_data)
                except tk.TclError: # Erreur Tcl (ex: onglet non trouvable)
                    self.display_game_image(game_data) # Fallback
            else:
                # game_data est None (ex: item_id non trouvé dans le mappage)
                self.selected_game_data = None
                self.reset_previews()
        else:
            # Aucun item sélectionné dans le Treeview
            self.selected_game_data = None
            self.reset_previews()

    def on_game_select(self, event):
        if self.selection_debounce_timer is not None:
            self.after_cancel(self.selection_debounce_timer)
        self.selection_debounce_timer = self.after(250, self._process_selection_change) # 250ms de délai

    def display_game_image(self, game_data):
        """Affiche l'image du jeu dans le panneau d'aperçu."""
        if not hasattr(self, 'image_preview_label') or self.image_preview_label is None:
            logging.debug("display_game_image: image_preview_label non prêt.")
            return

        try:
            if game_data and 'image_path' in game_data and game_data['image_path']:
                image_path = game_data['image_path']
                if os.path.exists(image_path) and os.path.getsize(image_path) > 0: # Vérifier aussi la taille
                    pil_image = Image.open(image_path)

                    # Ensure Tkinter has processed layout changes for the label
                    self.image_preview_label.update_idletasks()
                    preview_width = self.image_preview_label.winfo_width()
                    preview_height = self.image_preview_label.winfo_height()
                    logging.debug(f"display_game_image: Initial label dimensions: {preview_width}x{preview_height}")

                    if preview_width <= 1 or preview_height <= 1:
                        logging.warning(f"display_game_image: image_preview_label too small or not yet drawn ({preview_width}x{preview_height}). Attempting to use frame size or fallback.")
                        # Fallback to frame size if label size is invalid
                        if hasattr(self, 'image_preview_frame') and self.image_preview_frame is not None:
                            self.image_preview_frame.update_idletasks()
                            preview_width = self.image_preview_frame.winfo_width()
                            preview_height = self.image_preview_frame.winfo_height()
                            logging.debug(f"display_game_image: Using frame dimensions as fallback: {preview_width}x{preview_height}")
                            if preview_width <= 1 or preview_height <= 1:
                                logging.warning(f"display_game_image: Frame dimensions also too small. Using default 200x200.")
                                preview_width = 200
                                preview_height = 200
                        else:
                            # This case should ideally not happen if UI is set up correctly
                            logging.warning(f"display_game_image: image_preview_frame not available. Using default 200x200.")
                            preview_width = 200
                            preview_height = 200
                    
                    img_width, img_height = pil_image.size
                    logging.debug(f"display_game_image: Original image size: {img_width}x{img_height}")
                    logging.debug(f"display_game_image: Final target preview area for calculation: {preview_width}x{preview_height}")

                    if img_width == 0 or img_height == 0: # Prevent division by zero
                        logging.error("display_game_image: Original image has zero dimension.")
                        # Display default image instead of raising an error that stops the flow
                        if self.default_game_image_tk:
                            self.image_preview_label.config(image=self.default_game_image_tk, text='')
                            self.image_preview_label.image = self.default_game_image_tk
                        else:
                            self.image_preview_label.config(image='', text="Erreur: Image vide")
                            self.image_preview_label.image = None
                        return # Exit the function as we can't process a zero-dimension image
                    
                    aspect_ratio = img_width / img_height

                    # Calculate new dimensions to fit within preview_width and preview_height while maintaining aspect ratio
                    new_width = preview_width
                    new_height = int(new_width / aspect_ratio)

                    if new_height > preview_height:
                        new_height = preview_height
                        new_width = int(new_height * aspect_ratio)
                    
                    # Ensure new_width does not exceed preview_width (can happen if aspect_ratio adjustment for height makes width too large)
                    if new_width > preview_width:
                        new_width = preview_width
                        new_height = int(new_width / aspect_ratio)


                    if new_width > 0 and new_height > 0:
                        image_cache_key = (image_path, new_width, new_height)
                        if image_cache_key in self.image_cache:
                            tk_image = self.image_cache[image_cache_key]
                            logging.debug(f"display_game_image: Image trouvée dans le cache: {image_cache_key}")
                        else:
                            logging.debug(f"display_game_image: Resizing image to: {new_width}x{new_height} for {image_path}")
                            pil_image_resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            tk_image = ImageTk.PhotoImage(pil_image_resized)
                            self.image_cache[image_cache_key] = tk_image
                            logging.debug(f"display_game_image: Image ajoutée au cache: {image_cache_key}")
                        
                        self.image_preview_label.config(image=tk_image, text='')
                        self.image_preview_label.image = tk_image
                        return
                    else:
                        logging.warning(f"display_game_image: Calculated new dimensions are invalid ({new_width}x{new_height}). Displaying default image.")
                else: # image_path not found or zero size
                    logging.debug(f"display_game_image: Image path '{game_data.get('image_path', 'N/A')}' not found, zero size, or not specified. Displaying default.")
            else: # No game_data or no image_path
                logging.debug("display_game_image: No game_data or image_path. Displaying default image.")

            # Fallback to default image if any of the above conditions were not met or led to this point
            if self.default_game_image_tk:
                self.image_preview_label.config(image=self.default_game_image_tk, text='')
                self.image_preview_label.image = self.default_game_image_tk
            else:
                self.image_preview_label.config(image='', text="Aucun aperçu disponible")
                self.image_preview_label.image = None

        except ImportError: # Specifically for Pillow
            logging.error("display_game_image: Pillow (PIL) n'est pas installé.")
            self.image_preview_label.config(image='', text="Pillow (PIL) requis")
            self.image_preview_label.image = None
        except Exception as e:
            logging.error(f"Erreur lors de l'affichage de l'image '{game_data.get('image_path', 'N/A') if game_data else 'N/A'}': {type(e).__name__}: {e}", exc_info=True)
            if self.default_game_image_tk:
                self.image_preview_label.config(image=self.default_game_image_tk, text='')
                self.image_preview_label.image = self.default_game_image_tk
            else:
                self.image_preview_label.config(image='', text="Erreur image")
                self.image_preview_label.image = None

    def reset_previews(self):
        self.display_game_image(None) # Réinitialise l'image
        self.display_game_video(None) # Réinitialise la vidéo

    def toggle_video_mute(self):
        """Active/désactive le son de la vidéo VLC."""
        logging.debug("toggle_video_mute: Mute button clicked.")
        if not hasattr(self, 'player') or self.player is None:
            logging.warning("toggle_video_mute: VLC player instance is not available.")
            return
        
        player_state = self.player.get_state()
        logging.debug(f"toggle_video_mute: Player state: {player_state}")

        try:
            if not hasattr(self, 'video_muted'):
                self.video_muted = False
                logging.debug("toggle_video_mute: Initialized self.video_muted to False.")
            
            current_mute_status_vlc = self.player.audio_get_mute() # 0 if not muted, 1 if muted, -1 on error
            logging.debug(f"toggle_video_mute: Current VLC mute status (audio_get_mute): {current_mute_status_vlc}, self.video_muted (internal state): {self.video_muted}")

            if self.video_muted:
                logging.debug("toggle_video_mute: Attempting to unmute.")
                self.player.audio_set_mute(False)
                self.video_muted = False
                self.mute_button.config(text=self.icon_sound_on)
                logging.info("toggle_video_mute: Video unmuted. Button icon updated.")
            else:
                logging.debug("toggle_video_mute: Attempting to mute.")
                self.player.audio_set_mute(True)
                self.video_muted = True
                self.mute_button.config(text=self.icon_sound_off)
                logging.info("toggle_video_mute: Video muted. Button icon updated.")
            
            # Verify actual VLC mute status after operation
            new_mute_status_vlc = self.player.audio_get_mute()
            logging.debug(f"toggle_video_mute: New VLC mute status (audio_get_mute): {new_mute_status_vlc}, self.video_muted now: {self.video_muted}")

        except Exception as e:
            # import logging # Already imported at module level
            logging.error(f"Erreur lors du mute/unmute VLC: {e}", exc_info=True)

    def display_game_video(self, game_data):
        if not self.player: # Vérifier si le lecteur VLC a été initialisé
            if hasattr(self, 'video_message_label') and self.video_message_label: # S'assurer que video_message_label existe
                self.video_message_label.config(text="VLC n'est pas installé ou n'a pas pu être initialisé.\nLa lecture vidéo est désactivée.")
                if not self.video_message_label.winfo_ismapped(): # Afficher le label s'il est caché
                    self.video_message_label.pack(expand=True, fill="both")
            else:
                # Ce cas est peu probable si setup_ui est bien appelé, mais c'est une sécurité
                logging.error("display_game_video: video_message_label non disponible pour afficher l'erreur VLC.")
            self.current_video_path = None # Réinitialiser au cas où
            return

        # S'assurer que le message label est disponible (pour les autres messages)
        if not self.video_message_label:
            # Si le label n'a jamais été créé (ce qui ne devrait pas arriver si setup_ui est bien appelé)
            self.video_message_label = ttk.Label(self.video_tab_frame, text="Vidéo non disponible.", anchor="center")
            self.video_message_label.pack(expand=True, fill="both")

        if game_data is None:
            if self.player.is_playing():
                self.player.stop()
            self.video_message_label.config(text="Sélectionnez un jeu pour voir la vidéo.")
            if not self.video_message_label.winfo_ismapped(): # S'il était caché
                self.video_message_label.pack(expand=True, fill="both")
            self.current_video_path = None
            return

        video_path = game_data.get('video_path')
        
        # Cacher le message label par défaut si on va tenter de jouer une vidéo
        if self.video_message_label.winfo_ismapped():
            self.video_message_label.pack_forget()

        if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            if self.current_video_path == video_path and self.player.is_playing():
                # Déjà en train de jouer cette vidéo, ne rien faire pour éviter de relancer
                return 

            try:
                media = self.vlc_instance.media_new(video_path)
                self.player.set_media(media)
                # Il est crucial que video_tab_frame soit visible et ait une taille avant set_hwnd
                self.video_tab_frame.update_idletasks() 
                self.player.set_hwnd(self.video_tab_frame.winfo_id())
                self.player.play()
                self.current_video_path = video_path
            except Exception as e:
                logging.error(f"Erreur lors de la lecture de la vidéo avec VLC: {e}")
                self.current_video_path = None
                if self.player.is_playing():
                    self.player.stop()
                self.video_message_label.config(text=f"Erreur VLC: Impossible de lire la vidéo.")
                if not self.video_message_label.winfo_ismapped():
                    self.video_message_label.pack(expand=True, fill="both")
        else:
            if self.player.is_playing():
                self.player.stop()
            
            status_message = "Vidéo non trouvée ou invalide."
            if not video_path:
                status_message = "Chemin vidéo non spécifié pour ce jeu."
            elif not os.path.exists(video_path):
                status_message = f"Fichier vidéo non trouvé:\n{os.path.basename(video_path)}"
            elif os.path.getsize(video_path) == 0:
                status_message = f"Fichier vidéo vide:\n{os.path.basename(video_path)}"

            self.video_message_label.config(text=status_message)
            if not self.video_message_label.winfo_ismapped():
                self.video_message_label.pack(expand=True, fill="both")
            self.current_video_path = None

    def on_tab_changed(self, event):
        # Assurer que les attributs nécessaires existent
        if not hasattr(self, 'selected_game_data') or not hasattr(self, 'player') or \
           not hasattr(self, 'preview_notebook') or not self.preview_notebook.winfo_exists():
            logging.debug("on_tab_changed: Attributs manquants ou notebook non prêt.")
            return

        try:
            selected_tab_widget = self.preview_notebook.select()
            if not selected_tab_widget: # Aucun onglet sélectionné (peut arriver brièvement)
                logging.debug("on_tab_changed: Aucun onglet sélectionné.")
                return
            selected_tab_index = self.preview_notebook.index(selected_tab_widget)
        except tk.TclError:
            logging.warning("on_tab_changed: Erreur Tcl lors de la récupération de l'onglet sélectionné.")
            return # Impossible de déterminer l'onglet

        # 0 = Image, 1 = Vidéo
        if selected_tab_index == 1:  # Onglet Vidéo est devenu actif
            logging.debug("on_tab_changed: Onglet Vidéo sélectionné.")
            if self.selected_game_data:
                self.display_game_video(self.selected_game_data)
            else:
                # Pas de jeu sélectionné, display_game_video(None) gère l'arrêt et le message.
                self.display_game_video(None) 
                
        elif selected_tab_index == 0:  # Onglet Image est devenu actif
            logging.debug("on_tab_changed: Onglet Image sélectionné.")
            if self.player.is_playing():
                logging.debug("on_tab_changed: Arrêt de la vidéo car l'onglet Image est actif.")
                self.player.stop()
                # Après avoir arrêté la vidéo, s'assurer que le message de l'onglet vidéo est affiché
                if hasattr(self, 'video_message_label') and self.video_message_label and \
                   self.video_message_label.winfo_exists() and not self.video_message_label.winfo_ismapped():
                    self.video_message_label.config(text="Sélectionnez un jeu pour voir la vidéo.")
                    self.video_message_label.pack(expand=True, fill="both")
            
            # Afficher l'image du jeu actuellement sélectionné (ou par défaut si None)
            self.display_game_image(self.selected_game_data)
        else:
            logging.warning(f"on_tab_changed: Index d'onglet inattendu: {selected_tab_index}")


    def _save_settings(self):
        config = configparser.ConfigParser()
        # Essayer de lire la configuration existante pour la préserver
        if os.path.exists(SETTINGS_FILE):
            try:
                config.read(SETTINGS_FILE)
            except configparser.Error as e:
                logging.error(f"Erreur de lecture du fichier de paramètres {SETTINGS_FILE} lors de la tentative de sauvegarde: {e}. Une nouvelle configuration sera créée.")
                config = configparser.ConfigParser() # Réinitialiser en cas d'erreur de lecture

        # Section [Paths]
        current_roms_folder = self.root_roms_folder_path.get()
        if current_roms_folder:
            if 'Paths' not in config:
                config.add_section('Paths')
            config.set('Paths', 'last_roms_folder', current_roms_folder)
        elif 'Paths' in config and config.has_option('Paths', 'last_roms_folder'):
            config.remove_option('Paths', 'last_roms_folder')
            if not config.options('Paths'): # Si la section devient vide
                config.remove_section('Paths')

        # Section [Selection]
        selected_system_display = self.selected_system_var.get()
        if selected_system_display:
            if 'Selection' not in config:
                config.add_section('Selection')
            config.set('Selection', 'last_selected_system_display_name', selected_system_display)
        elif 'Selection' in config and config.has_option('Selection', 'last_selected_system_display_name'):
            config.remove_option('Selection', 'last_selected_system_display_name')
            if not config.options('Selection'): # Si la section devient vide
                config.remove_section('Selection')

        # Écrire seulement si la configuration n'est pas vide
        if config.sections():
            try:
                with open(SETTINGS_FILE, 'w') as configfile:
                    config.write(configfile)
                logging.info(f"Paramètres sauvegardés dans {SETTINGS_FILE}")
            except IOError as e:
                logging.error(f"Erreur lors de la sauvegarde des paramètres dans {SETTINGS_FILE}: {e}")
        elif os.path.exists(SETTINGS_FILE): # Si la config est vide mais le fichier existe, le supprimer
            try:
                os.remove(SETTINGS_FILE)
                logging.info(f"Fichier de paramètres {SETTINGS_FILE} vidé et supprimé car aucune configuration à sauvegarder.")
            except OSError as e:
                logging.error(f"Erreur lors de la suppression du fichier de paramètres vide {SETTINGS_FILE}: {e}")

    def _load_settings(self):
        config = configparser.ConfigParser()
        if not os.path.exists(SETTINGS_FILE):
            logging.info(f"Fichier de paramètres {SETTINGS_FILE} non trouvé. Aucun paramètre à charger.")
            self._set_controls_state(False) # Assurer que les contrôles sont désactivés si pas de settings
            self._update_system_combobox_filter() # Mettre à jour pour afficher "Aucun système"
            return

        try:
            read_files = config.read(SETTINGS_FILE)
            if not read_files:
                logging.warning(f"Le fichier de paramètres {SETTINGS_FILE} est vide ou illisible. Aucun paramètre chargé.")
                self._set_controls_state(False)
                self._update_system_combobox_filter()
                return

            folder_loaded = False
            if config.has_section('Paths') and config.has_option('Paths', 'last_roms_folder'):
                last_folder = config.get('Paths', 'last_roms_folder')
                if os.path.isdir(last_folder):
                    self.root_roms_folder_path.set(last_folder)
                    logging.info(f"Dernier dossier ROMs chargé: {last_folder}")
                    self._update_system_combobox_filter() # Crucial: peuple la combobox
                    folder_loaded = True
                else:
                    logging.warning(f"Chemin ROMs sauvegardé '{last_folder}' n'est pas un dossier valide. Ignoré.")
            else:
                logging.info(f"Aucun chemin 'last_roms_folder' trouvé dans {SETTINGS_FILE}.")
            
            if not folder_loaded:
                # Si aucun dossier n'a été chargé, s'assurer que la combobox est vide et les contrôles désactivés
                self._update_system_combobox_filter() # Pour afficher "Aucun système" etc.
                self._set_controls_state(False)

            system_loaded_successfully = False
            if folder_loaded and config.has_section('Selection') and config.has_option('Selection', 'last_selected_system_display_name'):
                last_system_display = config.get('Selection', 'last_selected_system_display_name')
                if last_system_display and hasattr(self, 'system_combobox') and self.system_combobox:
                    available_systems = self.system_combobox['values'] 
                    if last_system_display in available_systems:
                        self.selected_system_var.set(last_system_display) # Ceci va déclencher on_system_selected
                        # on_system_selected s'occupera de _save_settings et _set_controls_state
                        logging.info(f"Dernier système sélectionné '{last_system_display}' restauré et appliqué.")
                        system_loaded_successfully = True # Le set va appeler on_system_selected qui gère _set_controls_state
                    else:
                        logging.warning(f"Système sauvegardé '{last_system_display}' non disponible dans la liste actuelle pour '{self.root_roms_folder_path.get()}'. Ignoré.")
                        # self.selected_system_var.set('') # Optionnel: effacer la sélection si non trouvée
            elif folder_loaded:
                logging.info(f"Aucune information 'last_selected_system_display_name' trouvée dans {SETTINGS_FILE} pour le dossier chargé.")
            
            # Si un dossier a été chargé mais pas un système spécifique, s'assurer que les contrôles sont actifs
            # mais qu'aucun système n'est présélectionné (sauf si on_system_selected a été appelé).
            if folder_loaded and not system_loaded_successfully:
                 self._set_controls_state(True) # Activer les contrôles généraux car un dossier est chargé
                 # self.selected_system_var.set('') # Assurer qu'aucun système n'est sélectionné si non restauré
                 # L'appel à on_system_selected via set() gère déjà le bouton Analyser

        except (configparser.Error, IOError) as e:
            logging.error(f"Erreur lors du chargement des paramètres depuis {SETTINGS_FILE}: {e}")
            self._set_controls_state(False)
            self._update_system_combobox_filter()

    def on_closing(self):
        """Gère la fermeture de l'application."""
        logging.info("WM_DELETE_WINDOW : Exécution de on_closing.")
        try:
            if self.player:
                logging.info("Arrêt du lecteur VLC.")
                self.player.stop()
        except Exception as e:
            logging.error(f"Erreur lors de l'arrêt du lecteur VLC: {e}", exc_info=True)
        
        try:
            if self.vlc_instance:
                logging.info("Libération de l'instance VLC.")
                self.vlc_instance.release()
        except Exception as e:
            logging.error(f"Erreur lors de la libération de l'instance VLC: {e}", exc_info=True)
        
        try:
            logging.info("Appel de self.destroy() pour fermer la fenêtre principale.")
            self.destroy()
        except Exception as e:
            logging.error(f"Erreur lors de self.destroy(): {e}", exc_info=True)
        logging.info("on_closing terminé.")

    def refresh_treeview(self):
        """Rafraîchit le Treeview avec les données actuelles, en appliquant les filtres."""
        for i in self.games_tree.get_children():
            self.games_tree.delete(i)
        self.tree_item_to_game_map.clear() # Vider la map après avoir vidé l'arbre
        
        show_missing = self.show_missing_only_var.get()
        problematic_count_for_status_bar = 0 # Initialiser le compteur
        current_display_data = [] # Utiliser un nom de variable local distinct
        for game in self.games_data:
            if show_missing:
                if 'image manquante' in game.get('image_status', '') or \
                   'balise image absente' in game.get('image_status', '') or \
                   'vidéo manquante' in game.get('video_status', '') or \
                   'balise vidéo absente' in game.get('video_status', ''):
                    current_display_data.append(game)
            else:
                current_display_data.append(game)
        
        for game_idx, game in enumerate(current_display_data): # Itérer sur la liste filtrée
            # Statut Image
            image_status_text = game.get('image_status', 'N/A')
            status_symbol_image = "?"
            tag_image = ''
            if "image présente" in image_status_text:
                status_symbol_image = "✔"  # Revenir au symbole standard
                tag_image = 'image_present'
            elif "image manquante" in image_status_text or "balise image absente" in image_status_text:
                status_symbol_image = "✖"
                tag_image = 'image_missing'

            # Statut Vidéo
            video_status_text = game.get('video_status', 'N/A')
            status_symbol_video = "?"
            tag_video = ''
            if "vidéo présente" in video_status_text:
                status_symbol_video = "✔"  # Revenir au symbole standard
                tag_video = 'video_present'
            elif "vidéo manquante" in video_status_text or "balise vidéo absente" in video_status_text:
                status_symbol_video = "✖"
                tag_video = 'video_missing'
            
            # Rating
            game_rating = game.get('rating')
            rating_display = "N/A"
            if game_rating is not None and isinstance(game_rating, (float, int)):
                try:
                    num_stars = round(float(game_rating) * 5)
                    if 0 <= num_stars <= 5:
                        rating_display = '★' * num_stars + '☆' * (5 - num_stars)
                    else:
                        rating_display = "Err" # Should not happen if rating is 0-1
                except (ValueError, TypeError):
                    rating_display = "Err"
            elif game_rating is not None: # It's not None, but not a number
                rating_display = "Err"
        
            item_id = f"item_{game_idx}_{game.get('game_name', 'unknown_game')}"
            rom_filename = os.path.basename(game.get('rom_path', 'N/A'))

            values = (
                game.get('system', 'N/A'), 
                game.get('game_name', 'N/A'), 
                rom_filename, 
                status_symbol_image,
                status_symbol_video,
                rating_display
            )
            
            # La logique de coloration des lignes via les tags est supprimée pour l'Option B.
            # final_tag_to_apply = ()
            # if tag_image == 'image_missing' or tag_video == 'video_missing':
            #     # Si un élément est manquant, la ligne est taguée comme 'missing'
            #     # (les tags 'image_missing' et 'video_missing' sont configurés en rouge)
            #     if tag_image == 'image_missing': 
            #         final_tag_to_apply = (tag_image,)
            #     elif tag_video == 'video_missing': 
            #         final_tag_to_apply = (tag_video,)
            # elif tag_image == 'image_present' and tag_video == 'video_present':
            #     # Si tout est présent, la ligne est taguée comme 'present'
            #     # (le tag 'image_present' est configuré en vert, 'video_present' aussi)
            #     final_tag_to_apply = ('image_present',) # ou ('video_present',), les deux sont verts
            # elif tag_image == 'image_present': # Un seul est explicitement présent, l'autre N/A ou non manquant
            #     final_tag_to_apply = (tag_image,)
            # elif tag_video == 'video_present': # Un seul est explicitement présent, l'autre N/A ou non manquant
            #     final_tag_to_apply = (tag_video,)

            if tag_image == 'image_missing' or tag_video == 'video_missing' or \
               "balise image absente" in image_status_text or "balise vidéo absente" in video_status_text:
                problematic_count_for_status_bar += 1

            # Temporairement sans tags pour tester la fluidité du scroll
            item_id = self.games_tree.insert("", tk.END, values=values)
            # self.games_tree.item(item_id, tags=tags_tuple) # Garder la logique de tags si on veut la remettre facilement
            self.tree_item_to_game_map[item_id] = game
        
        count_displayed = len(current_display_data)
        self.update_status(f"{len(current_display_data)} jeux affichés ({problematic_count_for_status_bar} avec problèmes).")

        # Automatically select the first game in the list
        children = self.games_tree.get_children()
        if children:
            first_item_id = children[0]
            self.games_tree.selection_set(first_item_id)
            self.games_tree.see(first_item_id)   # Ensure the selected item is visible
            self.games_tree.focus(first_item_id) # Set focus to the selected item
            self.games_tree.focus_set()          # Ensure the Treeview widget itself has focus
            # Manually trigger the selection event to update previews
            self.games_tree.event_generate("<<TreeviewSelect>>")

    def sort_treeview_by_column(self, column_id):
        """Trie le Treeview en fonction de la colonne sélectionnée."""
        
        # Définir une fonction de mappage pour le tri des statuts
        # "présent" < "manquant" < "?"
        def status_sort_key(status_text_value):
            if not isinstance(status_text_value, str): # S'assurer que c'est une chaîne
                return 2 # Mettre les non-chaînes à la fin
            if "présente" in status_text_value or "présent" in status_text_value : # Gère "Image présente" et "Vidéo présent"
                return 0  # Présent en premier
            elif "manquante" in status_text_value or "manquant" in status_text_value or "absente" in status_text_value:
                return 1  # Manquant ensuite
            return 2  # Inconnu/N/A ou autre en dernier

        # La clé dans game_data est la même que column_id ("image_status" ou "video_status")
        data_key_to_sort_by = column_id 
        
        sort_lambda = lambda game: status_sort_key(game.get(data_key_to_sort_by, ''))

        # Logique d'inversion du tri
        if self.sort_column_key == column_id:
            self.sort_reverse_order = not self.sort_reverse_order
        else:
            self.sort_column_key = column_id
            self.sort_reverse_order = False # Par défaut, tri ascendant pour une nouvelle colonne

        # Trier self.games_data
        try:
            self.games_data.sort(key=sort_lambda, reverse=self.sort_reverse_order)
        except Exception as e:
            print(f"Erreur pendant le tri : {e}") # Pour le débogage
            # Gérer l'erreur ou simplement ne pas trier si la clé n'est pas trouvée
            return

        # Rafraîchir le Treeview pour afficher les données triées
        self.refresh_treeview()

    def get_selected_games_data(self):
        selected_items_ids = self.games_tree.selection()
        if not selected_items_ids:
            return []
        
        selected_games_data = []
        for item_id in selected_items_ids:
            # Utiliser la map pour récupérer les données complètes du jeu
            game_data = self.tree_item_to_game_map.get(item_id)
            if game_data:
                selected_games_data.append(game_data)
            else:
                # Cela ne devrait pas arriver si la map est correctement maintenue
                print(f"Avertissement : Jeu non trouvé dans tree_item_to_game_map pour l'ID d'élément {item_id}")
        return selected_games_data

    def _perform_file_op(self, op_name, op_func, selected_games_data, needs_dest=False, operation_name_fr=""):
        if not selected_games_data:
            messagebox.showinfo(operation_name_fr, "Aucun jeu sélectionné.")
            return

        destination_base_folder = None
        if needs_dest:
            destination_base_folder = filedialog.askdirectory(title=f"Choisir le dossier de destination pour {operation_name_fr.lower()}")
            if not destination_base_folder:
                messagebox.showinfo(operation_name_fr, f"{operation_name_fr} annulé(e).")
                return

        if op_name == "supprimer":
            confirm_msg = f"Êtes-vous sûr de vouloir supprimer définitivement {len(selected_games_data)} jeu(x) sélectionné(s) ? Cette action est irréversible."
            if len(selected_games_data) == 1:
                game_display_name = selected_games_data[0].get('game_name', selected_games_data[0].get('rom_path', 'le jeu'))
                confirm_msg = f"Êtes-vous sûr de vouloir supprimer définitivement '{game_display_name}' ? Cette action est irréversible."
            
            if not messagebox.askyesno(f"Confirmation de {operation_name_fr}", confirm_msg):
                messagebox.showinfo(operation_name_fr, f"{operation_name_fr} annulée.")
                return # Prevent accidental delete if not confirmed

    def _perform_file_op(self, op_name, op_func, selected_games_data, operation_name_fr, needs_dest=False, destination_base_folder=None):
        success_count = 0
        fail_count = 0
        results_details = []

        # Sécurité : si une destination est requise mais absente, on arrête tout de suite
        if needs_dest and not destination_base_folder:
            messagebox.showerror("Erreur", "Dossier de destination non spécifié pour l'opération.")
            return

        # Store original indices from self.games_data for removal if op is 'déplacer' or 'supprimer'
        # This is different from original_focus_index which is for Treeview selection restoration.
        indices_in_self_games_data_to_remove = []

        original_focus_iid = None
        original_focus_index_in_tree = -1

        if op_name in ["déplacer", "supprimer"]:
            selected_iids = self.games_tree.selection()
            if selected_iids:
                original_focus_iid = selected_iids[0]
                try:
                    # Get all current iids in the order they appear in the tree
                    all_tree_iids = self.games_tree.get_children('')
                    original_focus_index_in_tree = all_tree_iids.index(original_focus_iid)
                except ValueError:
                    original_focus_index_in_tree = -1 # Should not happen if iid is from selection

            self.update_status(f"{operation_name_fr} en cours...", 0)
            total_ops = len(selected_games_data)

        total_ops = len(selected_games_data)

        for i, game_data_from_selection in enumerate(selected_games_data):
            source_path = game_data_from_selection.get('full_rom_path')
            game_name_display = game_data_from_selection.get('game_name', os.path.basename(source_path) if source_path else 'Inconnu')

            if not source_path or not os.path.exists(source_path):
                results_details.append(f"Échec {operation_name_fr.lower()} '{game_name_display}': Fichier source '{source_path}' non trouvé ou invalide.")
                fail_count += 1
            else:
                try:
                    if needs_dest:
                        filename = os.path.basename(source_path)
                        destination_full_path = os.path.join(destination_base_folder, filename)
                        op_func(source_path, destination_full_path) # move_game_file or copy_game_file
                        results_details.append(f"Succès {operation_name_fr.lower()} '{game_name_display}': {source_path} -> {destination_full_path}")
                        if op_name == "déplacer":
                            # Find original index in self.games_data to mark for removal
                            for idx, original_game_in_data in enumerate(self.games_data):
                                if original_game_in_data.get('full_rom_path') == source_path:
                                    if idx not in indices_in_self_games_data_to_remove:
                                        indices_in_self_games_data_to_remove.append(idx)
                                    break
                    else: # Suppression
                        op_func(source_path) # delete_game_file
                        results_details.append(f"Succès {operation_name_fr.lower()} '{game_name_display}': {source_path} supprimé.")
                        # Remove from gamelist.xml as well
                        gamelist_path = game_data_from_selection.get('gamelist_path')
                        rom_path_from_xml = game_data_from_selection.get('rom_path')
                        xml_removed = False
                        if gamelist_path and rom_path_from_xml:
                            try:
                                from file_operations import remove_game_from_gamelist
                                xml_removed = remove_game_from_gamelist(gamelist_path, rom_path_from_xml)
                                if xml_removed:
                                    results_details.append(f"Entrée supprimée de {os.path.basename(gamelist_path)}.")
                                else:
                                    results_details.append(f"Aucune entrée correspondante à supprimer dans {os.path.basename(gamelist_path)}.")
                            except Exception as e:
                                results_details.append(f"Erreur suppression XML ({gamelist_path}): {e}")
                        else:
                            results_details.append("Impossible de déterminer le chemin gamelist.xml ou le chemin ROM XML pour la suppression persistante.")
                        for idx, original_game_in_data in enumerate(self.games_data):
                            if original_game_in_data.get('full_rom_path') == source_path:
                                if idx not in indices_in_self_games_data_to_remove:
                                    indices_in_self_games_data_to_remove.append(idx)
                                break
                        success_count += 1
                except Exception as e:
                    results_details.append(f"Échec {operation_name_fr.lower()} '{game_name_display}' ({source_path}): {e}")
                    fail_count += 1
            
            self.update_status(f"{operation_name_fr} {i+1}/{total_ops}...", int(((i+1)/total_ops)*100))

        # Post-operation processing (removing from self.games_data and refreshing tree)
        if op_name in ["déplacer", "supprimer"] and indices_in_self_games_data_to_remove:
            indices_in_self_games_data_to_remove.sort(reverse=True)
            for index_to_remove in indices_in_self_games_data_to_remove:
                if 0 <= index_to_remove < len(self.games_data):
                    del self.games_data[index_to_remove]
            
            self.refresh_treeview() # Treeview is rebuilt here

            # Attempt to restore selection
            if original_focus_index_in_tree != -1:
                all_new_tree_iids = self.games_tree.get_children('')
                if all_new_tree_iids:
                    # Try to select the item at the same index, or the last item if index is out of bounds
                    target_idx_in_new_tree = min(original_focus_index_in_tree, len(all_new_tree_iids) - 1)
                    if target_idx_in_new_tree >= 0:
                        iid_to_select_after_refresh = all_new_tree_iids[target_idx_in_new_tree]
                        self.games_tree.selection_set(iid_to_select_after_refresh)
                        self.games_tree.focus(iid_to_select_after_refresh)
                        self.games_tree.see(iid_to_select_after_refresh)
                        # Manually trigger on_game_select because selection_set might not always trigger it
                        # if the selection hasn't actually changed (e.g. if it was already the only item)
                        self.on_game_select(None) # Pass None as event, or mock an event if needed by handler
                else:
                    # Tree is now empty
                    self.selected_game_data = None
                    self.reset_previews()
            else:
                # No specific item was focused, or tree was empty before op
                # If tree is not empty now, maybe select the first item by default?
                if not self.games_tree.get_children(''):
                    self.selected_game_data = None
                    self.reset_previews()
                else:
                    # For now, just clear previews if tree becomes empty or selection is lost.
                    if not self.games_tree.selection():
                        self.selected_game_data = None
                        self.reset_previews()

        self.update_status(f"{operation_name_fr} terminé.", 100 if total_ops > 0 else 0)

        # Afficher les résultats
        summary_message_title = f"Résultat {operation_name_fr}"
        summary_message_content = f"""{operation_name_fr} terminé(e).\nSuccès : {success_count}\nÉchecs : {fail_count}\n\n"""
        summary_message_content += "\n".join(results_details)
        
        if op_name in ["supprimer", "déplacer", "copier"]:
            if success_count > 0 or fail_count > 0:
                # Suppress the detailed results window, show only a simple messagebox
                messagebox.showinfo(summary_message_title, f"{operation_name_fr} terminée.\nSuccès : {success_count}\nÉchecs : {fail_count}")
        else:
            if success_count > 0 or fail_count > 0:
                self.show_results_in_new_window(summary_message_title, summary_message_content)
            elif not selected_games_data: # Already handled by the initial check, but as a fallback
                pass # No message needed if no games were selected and initial check passed (should not happen)
            else: # No operations attempted (e.g., all sources missing, or other logic error)
                messagebox.showinfo(operation_name_fr, "Aucune opération pertinente effectuée (ex: fichiers sources manquants ou aucune sélection valide)." if total_ops > 0 else "Aucun jeu sélectionné pour l'opération.")

    def show_results_in_new_window(self, title, content):
        results_window = tk.Toplevel(self) # Correction: self est l'instance principale de la fenêtre
        results_window.title(title)
        results_window.geometry("600x400")
        text_area = tk.Text(results_window, wrap="word", height=20, width=80)
        scrollbar = ttk.Scrollbar(results_window, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        text_area.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        text_area.insert(tk.END, content)
        text_area.config(state="disabled") # Make it read-only
        ttk.Button(results_window, text="OK", command=results_window.destroy).pack(pady=5)

    def move_selected_games_wrapper(self):
        selected_games = self.get_selected_games_data()
        if not selected_games:
            messagebox.showinfo("Déplacement", "Aucun jeu sélectionné.")
            return
        destination_base_folder = filedialog.askdirectory(title="Choisir le dossier de destination")
        if not destination_base_folder:
            messagebox.showinfo("Déplacement", "Aucun dossier de destination sélectionné.")
            return
        if hasattr(file_operations, 'move_game_file'):
            self._perform_file_op("déplacer", file_operations.move_game_file, selected_games, needs_dest=True, destination_base_folder=destination_base_folder, operation_name_fr="Déplacement")

    def copy_selected_games_wrapper(self):
        selected_games = self.get_selected_games_data()
        if not selected_games:
            messagebox.showinfo("Copie", "Aucun jeu sélectionné.")
            return
        destination_base_folder = filedialog.askdirectory(title="Choisir le dossier de destination")
        if not destination_base_folder:
            messagebox.showinfo("Copie", "Aucun dossier de destination sélectionné.")
            return
        if hasattr(file_operations, 'copy_game_file'):
            self._perform_file_op("copier", file_operations.copy_game_file, selected_games, needs_dest=True, destination_base_folder=destination_base_folder, operation_name_fr="Copie")
        else:
            messagebox.showerror("Erreur", "La fonction de copie est manquante (file_operations.py).")

    def delete_selected_games_wrapper(self):
        selected_games = self.get_selected_games_data()
        if not selected_games:
            messagebox.showinfo("Suppression", "Aucun jeu sélectionné.")
            return
        confirm = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer les jeux sélectionnés ? Cette action est irréversible.")
        if not confirm:
            return
        if hasattr(file_operations, 'delete_game_file'):
            self._perform_file_op("supprimer", file_operations.delete_game_file, selected_games, needs_dest=False, operation_name_fr="Suppression")
        else:
            messagebox.showerror("Erreur", "La fonction de suppression est manquante (file_operations.py).")

    def clean_orphaned_games_wrapper(self):
        root_roms_dir = self.root_roms_folder_path.get()
        selected_display_name = self.selected_system_var.get()
        if not root_roms_dir or not os.path.isdir(root_roms_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier racine de ROMs Recalbox valide.")
            return
        if not selected_display_name:
            messagebox.showerror("Erreur", "Veuillez sélectionner un système à nettoyer.")
            return
        selected_system_internal_name = self.system_display_to_internal_map.get(selected_display_name)
        if not selected_system_internal_name:
            messagebox.showerror("Erreur", f"Nom de système interne non trouvé pour '{selected_display_name}'.")
            return
        system_roms_path = os.path.join(root_roms_dir, selected_system_internal_name)
        gamelist_file_path = os.path.join(system_roms_path, "gamelist.xml")
        try:
            removed_count = file_operations.clean_orphaned_entries_in_gamelist(gamelist_file_path, system_roms_path)
            messagebox.showinfo("Rafraîchissement terminé", f"{removed_count} jeux orphelins supprimés du gamelist.xml.")
            # Rafraîchir la liste en relançant l'analyse
            self.analyze_games_wrapper()
        except FileNotFoundError:
            messagebox.showerror("Erreur", f"gamelist.xml non trouvé pour {selected_display_name}.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du nettoyage des jeux orphelins : {e}")

    def export_game_list_wrapper(self):
        if not self.games_data:
            messagebox.showinfo("Exporter Liste", "Aucune donnée de jeu à exporter.")
            return

        # Demander à l'utilisateur de choisir un répertoire de destination
        export_directory = filedialog.askdirectory(title="Choisir le dossier pour sauvegarder les exports")
        if not export_directory: # L'utilisateur a annulé
            messagebox.showinfo("Exporter Liste", "Exportation annulée.")
            return

        self.update_status("Exportation en cours...", 0)
        # Filtrer les jeux si "Afficher jeux sans image/tag uniquement" est coché
        data_to_export = self.games_data
        if self.show_missing_only_var.get():
            data_to_export = [
                game for game in self.games_data 
                if game.get('image_status', '').startswith("balise image absente") or \
                   game.get('image_status', '').startswith("image manquante") or \
                   game.get('image_status', '').startswith("image présente (vide)")
            ]
        if not data_to_export:
            messagebox.showinfo("Exporter Liste", "Aucun jeu (correspondant au filtre actuel) à exporter.")
            self.update_status("Prêt.", 0)
            return
        try:
            export_results = exporter.export_data_to_files(
                data_to_export,
                export_directory,
                export_format="all",
                filename_prefix="RecalboxGameManager_Export"
            )
            self.update_status("Exportation terminée.", 100)
            exported_files_messages = []
            if export_results:
                if export_results.get('csv'):
                    exported_files_messages.append(f"CSV: {export_results['csv']}")
                if export_results.get('xml'):
                    exported_files_messages.append(f"XML: {export_results['xml']}")
            if exported_files_messages:
                messagebox.showinfo("Exportation Réussie", "Fichiers exportés avec succès :\n" + "\n".join(exported_files_messages) + f"\n\nDans le dossier : {export_directory}")
            else:
                messagebox.showerror("Erreur d'Exportation", "L'exportation a échoué. Aucun fichier n'a été créé.")
        except Exception as e:
            self.update_status("Erreur lors de l'exportation.", 0)
            messagebox.showerror("Erreur d'Exportation", f"Une erreur est survenue : {e}")
        if not self.games_data:
            messagebox.showinfo("Exporter Liste", "Aucune donnée de jeu à exporter.")
            return

        # Demander à l'utilisateur de choisir un répertoire de destination
        export_directory = filedialog.askdirectory(title="Choisir le dossier pour sauvegarder les exports")
        if not export_directory: # L'utilisateur a annulé
            messagebox.showinfo("Exporter Liste", "Exportation annulée.")
            return

        self.update_status("Exportation en cours...", 0)
        
        # Filtrer les jeux si "Afficher jeux sans image/tag uniquement" est coché
        data_to_export = self.games_data
        if self.show_missing_only_var.get():
            data_to_export = [
                game for game in self.games_data 
                if game.get('image_status', '').startswith("balise image absente") or \
                   game.get('image_status', '').startswith("image manquante") or \
                   game.get('image_status', '').startswith("image présente (vide)")
            ]
        
        if not data_to_export:
            messagebox.showinfo("Exporter Liste", "Aucun jeu (correspondant au filtre actuel) à exporter.")
            self.update_status("Prêt.", 0)
            return

        try:
            # On passe maintenant export_directory à la fonction
            export_results = exporter.export_data_to_files(
                data_to_export, 
                export_directory, # Nouveau paramètre
                export_format="all", # ou "csv", "xml"
                filename_prefix="RecalboxGameManager_Export" 
            )
            
            self.update_status("Exportation terminée.", 100)
            
            exported_files_messages = []
            if export_results:
                if export_results.get('csv'):
                    exported_files_messages.append(f"CSV: {export_results['csv']}")
                if export_results.get('xml'):
                    exported_files_messages.append(f"XML: {export_results['xml']}")
            
            if exported_files_messages:
                messagebox.showinfo("Exportation Réussie", "Fichiers exportés avec succès :\n" + "\n".join(exported_files_messages) + f"\n\nDans le dossier : {export_directory}")
            else:
                messagebox.showerror("Erreur d'Exportation", "L'exportation a échoué. Aucun fichier n'a été créé.")

        except Exception as e:
            self.update_status("Erreur lors de l'exportation.", 0)
            messagebox.showerror("Erreur d'Exportation", f"Une erreur est survenue : {e}")

    def _internal_export_csv(self, games_list, export_dir):
        """Fallback CSV export if exporter module or its function is not available."""
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        filepath = os.path.join(export_dir, "recalbox_games_export.csv")
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['system', 'game_name', 'rom_path', 'image_status', 'full_rom_path', 'gamelist_path']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(games_list)
            messagebox.showinfo("Export CSV (Interne)", f"Liste exportée vers {filepath}")
        except IOError as e:
            messagebox.showerror("Erreur Export CSV (Interne)", f"Impossible d'écrire le fichier CSV : {e}")

    def center_window(self, width_offset=0, height_offset=0):
        toplevel = self.winfo_toplevel()
        # Il est crucial que la fenêtre ait une taille définie avant de la centrer.
        # update_idletasks() s'assure que la géométrie initiale est calculée.
        toplevel.update_idletasks() 
        
        width = toplevel.winfo_width()
        height = toplevel.winfo_height()
        
        # Si la largeur/hauteur est toujours 1 (taille par défaut avant affichage/contenu),
        # le centrage pourrait ne pas être idéal. Envisagez de définir une taille minimale
        # ou une géométrie initiale pour 'root' si cela pose problème.
        # Pour l'instant, nous utilisons la taille calculée.

        screen_width = toplevel.winfo_screenwidth()
        screen_height = toplevel.winfo_screenheight()

        x = (screen_width // 2) - (width // 2) + width_offset
        y = (screen_height // 2) - (height // 2) + height_offset

        toplevel.geometry(f'{width}x{height}+{x}+{y}')
        logging.debug(f"Window centered using center_window method: {width}x{height}+{x}+{y}")

    def center_window_on_map_once(self, event=None):
        """Centers the window on the screen when it's first mapped, then unbinds."""
        self.center_window()
        # Unbind after the first call to prevent recentering if the window is unmapped/remapped.
        self.unbind("<Map>")
        logging.debug("Window centered on first map event and <Map> event unbound.")

    def apply_initial_vlc_audio_settings(self):
        if hasattr(self, 'player') and self.player:
            try:
                logging.debug("apply_initial_vlc_audio_settings: Tentative de régler l'audio VLC sur non-sourdine et volume par défaut.")
                
                self.player.audio_set_mute(False)  # Tenter de désactiver la sourdine
                self.player.audio_set_volume(self.default_volume)  # Tenter de régler le volume
                
                # Vérifier l'état réel de VLC après les tentatives
                actual_mute = self.player.audio_get_mute()  # 0 = non-sourdine, 1 = sourdine
                actual_volume = self.player.audio_get_volume()
                logging.info(f"apply_initial_vlc_audio_settings: État VLC après tentative - Sourdine: {actual_mute}, Volume: {actual_volume}")

                # Déterminer si VLC est effectivement en sourdine (explicitement ou volume à 0)
                is_effectively_muted_vlc = (actual_mute == 1 or actual_volume == 0)
                
                # self.video_muted est initialement False (on veut le son)
                # Si l'état effectif de VLC ne correspond pas à notre état souhaité (non-sourdine), mettre à jour l'état de l'application et le bouton.
                if is_effectively_muted_vlc != self.video_muted:
                    if is_effectively_muted_vlc:
                        logging.warning("apply_initial_vlc_audio_settings: VLC est effectivement en sourdine malgré les tentatives. Mise à jour de l'état de l'application.")
                        self.video_muted = True # Mettre à jour l'état interne
                    else:
                        # Cela ne devrait pas arriver si self.video_muted est False initialement et que VLC est bien non-sourdine
                        logging.info("apply_initial_vlc_audio_settings: VLC est non-sourdine. État de l'application confirmé.")
                        self.video_muted = False # Confirmer l'état interne

                    if hasattr(self, 'mute_button') and self.mute_button:
                        self.mute_button.config(text=self.icon_sound_on if not self.video_muted else self.icon_sound_off)
                        logging.debug(f"apply_initial_vlc_audio_settings: Icône du bouton de sourdine mise à jour pour refléter l'état réel de VLC.")
                else:
                    logging.debug("apply_initial_vlc_audio_settings: L'état de l'application (self.video_muted) est cohérent avec l'état effectif de VLC.")

            except Exception as e:
                logging.error(f"Erreur durant apply_initial_vlc_audio_settings: {e}", exc_info=True)
        else:
            logging.debug("apply_initial_vlc_audio_settings: Lecteur VLC non disponible. Ignoré.")

if __name__ == "__main__":
    app = ScanBoxApp() # ScanBoxApp est maintenant la fenêtre racine
    # Initialiser le style ttk après la création de app (qui est la racine)
    # style = ttk.Style(app) # Removed, self.style is initialized and used within ScanBoxApp
    # Code pour définir le thème 'clam' (commenté ou supprimé précédemment)
    app.mainloop()