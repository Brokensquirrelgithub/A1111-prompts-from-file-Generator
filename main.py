import random
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import sys
import platform
import json
import shutil

# Load environment variables
load_dotenv()

# Get the base directory (where this script is located)
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'config' / 'data'
CONFIG_DIR = BASE_DIR / 'config'
PROFILES_DIR = BASE_DIR / 'config' / 'profiles'

# Ensure profiles directory exists
os.makedirs(PROFILES_DIR, exist_ok=True)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# List of categories and their corresponding filenames
categories = [
    "Subject",
    "FacialExpression",
    "Clothing",
    "Situation",
    "Medium",
    "Style",
    "AdditionalDetails",
    "Color",
    "Lighting",
    "Remarks"
]

# Default settings
DEFAULT_SETTINGS = {
    'STEPS': '20',
    'CFG_SCALE': '9.5',
    'SAMPLER': 'DPM++ 2M Karras',
    'WIDTH': '1024',
    'HEIGHT': '1024',
    'SEED': '-1'
}

# Default negative prompt (used if file not found)
DEFAULT_NEGATIVE_PROMPT = 'deformed, ugly, creepy, mutation'

# Prompt template (order of parts)
def build_prompt(parts):
    # Filter out empty parts and join with ", "
    return ", ".join(part for part in parts if part)

def find_case_insensitive_file(base_name):
    """Find a file with case-insensitive matching in the data directory"""
    if not os.path.exists(DATA_DIR):
        return None
        
    target_lower = base_name.lower()
    for file in os.listdir(DATA_DIR):
        if file.lower() == target_lower:
            return DATA_DIR / file
    return None

def load_options(filename):
    """Load lines from a txt file, stripping whitespace and ignoring empty lines"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: File not found: {filename}")
        return []
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return []

def get_unique_filename(base_name):
    """Return filename that does not clash with existing files."""
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    counter = 2
    while True:
        candidate = f"{name}{counter}{ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1

def load_settings():
    """Load settings from config file or use defaults"""
    settings = DEFAULT_SETTINGS.copy()
    settings_file = CONFIG_DIR / 'settings.txt'
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in settings:
                            settings[key] = value
            print(f"Loaded settings from {settings_file}")
        except Exception as e:
            print(f"Error loading settings: {e}. Using default settings.")
    
    return settings

def open_file_explorer(path):
    """Open file explorer at the given path"""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file explorer: {str(e)}")

def open_text_editor(file_path):
    """Open a file in the default text editor"""
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", "-t", file_path])
        else:  # Linux
            subprocess.Popen(["xdg-open", file_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {str(e)}")

class CollapsibleFrame(ttk.LabelFrame):
    def __init__(self, parent, text="", *args, **kwargs):
        ttk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.show = False
        self.title = text
        
        # Header frame with toggle button and label
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X, expand=1)
        
        # Toggle button
        self.toggle_btn = ttk.Label(self.header, text="+", width=3, cursor="hand2")
        self.toggle_btn.pack(side=tk.LEFT, padx=2)
        
        # Title label
        self.title_label = ttk.Label(self.header, text=text, font=('TkDefaultFont', 10, 'bold'))
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=1)
        
        # Content frame (initially hidden)
        self.content = ttk.Frame(self)
        
        # Bind click events
        self.toggle_btn.bind("<Button-1>", self.toggle)
        self.title_label.bind("<Button-1>", self.toggle)
        
        # Add edit button
        self.edit_btn = ttk.Button(self.header, text="✏️", width=3, 
                                 command=self.edit_content)
        self.edit_btn.pack(side=tk.RIGHT, padx=2)
        
    def toggle(self, event=None):
        self.show = not self.show
        if self.show:
            self.content.pack(fill=tk.BOTH, expand=1, pady=(5, 0))
            self.toggle_btn.config(text="−")  # Minus sign
        else:
            self.content.pack_forget()
            self.toggle_btn.config(text="+")
        # Update scroll region after toggling
        if hasattr(self.master, 'update_scroll_region'):
            self.master.update_scroll_region()
    
    def edit_content(self, event=None):
        # Open the file in the default text editor
        app = self.parent.master.master.master # A bit of a hack to get the app instance
        file_path = app.data_dir / f"{self.title}.txt"
        if file_path.exists() or file_path.is_symlink():
            open_text_editor(file_path)
        else:
            # Create the file if it doesn't exist
            try:
                with open(file_path, 'w', encoding='utf-8'):
                    pass
                open_text_editor(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {str(e)}")

class PromptGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A1111 Prompt Generator")
        self.current_profile_path = None
        self.unsaved_changes = False
        # Set the initial data directory to the default one
        self.data_dir = DATA_DIR
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.update_title()

        # Create a menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # Create a File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Profile", command=self.new_profile)
        file_menu.add_command(label="Open Profile", command=self.open_profile)
        file_menu.add_command(label="Save Profile", command=self.save_profile)
        file_menu.add_command(label="Save Profile As...", command=lambda: self.save_profile(save_as=True))
        file_menu.add_command(label="Delete Profile", command=self.delete_profile)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        self.root.geometry("800x900")
        
        # Load settings and categories
        self.settings = load_settings()
        self.categories = categories.copy()
        self.panels = {}
        
        # Create default profile if none exists
        if not any(PROFILES_DIR.iterdir()):
            default_profile = PROFILES_DIR / 'Default'
            default_profile.mkdir(parents=True, exist_ok=True)
            (default_profile / 'data').mkdir(exist_ok=True)
            
            # Create default profile.json
            profile_data = {'categories': categories}
            with open(default_profile / 'profile.json', 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)
                
            # Set as current profile and update UI
            self.current_profile_path = default_profile
            self.data_dir = default_profile / 'data'
            self.categories = categories.copy()  # Ensure categories are loaded
            self.status_var.set(f"Created default profile 'Default'")
        
        # Create main container with canvas and scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the top controls (categories list and buttons)
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create a frame for the scrollable content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a frame to hold the scrollable content
        self.scrollable_frame = ttk.Frame(self.content_frame)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.scrollable_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        
        # Pack the scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas to hold the content
        self.inner_frame = ttk.Frame(self.canvas)
        
        # Add the inner frame to the canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw', tags=("frame",))
        
        # Configure the canvas scrolling
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        def on_canvas_configure(event):
            self.canvas.itemconfig("frame", width=event.width)
            
        self.inner_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mousewheel for scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Store the mouse wheel binding for cleanup
        self._on_mousewheel = on_mousewheel
        
        # Title
        ttk.Label(self.top_frame, text="A1111 Prompt Generator", 
                 font=('Helvetica', 16, 'bold')).pack(pady=(0, 10), fill=tk.X)
        
        # Categories Panel
        self.categories_frame = ttk.LabelFrame(self.top_frame, text="Categories", padding="10")
        self.categories_frame.pack(fill=tk.X, pady=5)
        
        # Buttons Frame - Top Row
        top_btn_frame = ttk.Frame(self.categories_frame)
        top_btn_frame.pack(fill=tk.X, pady=5)
        
        # Add/Remove Buttons - Top Row
        ttk.Button(top_btn_frame, text="+", width=5, command=self.add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_btn_frame, text="-", width=5, command=self.remove_category).pack(side=tk.LEFT, padx=2)
        
        # Status Label - Next to buttons
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(top_btn_frame, textvariable=self.status_var, relief=tk.SUNKEN, 
                 anchor=tk.W, padding=(10, 0)).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        # Categories Listbox with Scrollbar and Reorder Buttons
        list_frame = ttk.Frame(self.categories_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Listbox and Scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.cat_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, height=5)
        self.cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Scrollbar for Listbox
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.cat_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cat_listbox.config(yscrollcommand=scrollbar.set)
        
        # Right side - Reorder Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
        
        # Move Up button
        up_btn = ttk.Button(btn_frame, text="↑", width=3, command=self.move_category_up)
        up_btn.pack(pady=(10, 2), fill=tk.X)
        
        # Move Down button
        down_btn = ttk.Button(btn_frame, text="↓", width=3, command=self.move_category_down)
        down_btn.pack(pady=2, fill=tk.X)
        
        # Bind double click to toggle panel and handle selection
        self.cat_listbox.bind('<Double-1>', self.on_category_select)
        self.cat_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Bind mousewheel to listbox (moved after listbox creation)
        self.cat_listbox.bind("<MouseWheel>", self._on_listbox_scroll)
        
        # Content Panels Frame
        self.panels_frame = ttk.Frame(self.inner_frame)
        self.panels_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Add a frame to fill remaining space at the bottom
        self.bottom_spacer = ttk.Frame(self.inner_frame, height=20)
        self.bottom_spacer.pack(fill=tk.X)
        
        # Action Buttons Frame
        action_frame = ttk.Frame(self.inner_frame)
        action_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Main settings frame
        settings_frame = ttk.Frame(action_frame)
        settings_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # First row - Steps and CFG Scale
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, pady=2)
        
        # Steps
        ttk.Label(row1, text="Steps:").pack(side=tk.LEFT, padx=(0, 2))
        self.steps_var = tk.StringVar(value=str(self.settings.get('STEPS', '20')))
        steps_entry = ttk.Entry(row1, textvariable=self.steps_var, width=4)
        steps_entry.pack(side=tk.LEFT, padx=(0, 10))
        steps_entry.config(validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        
        # CFG Scale
        ttk.Label(row1, text="CFG:").pack(side=tk.LEFT, padx=(0, 2))
        self.cfg_var = tk.StringVar(value=str(self.settings.get('CFG_SCALE', '7')))
        cfg_entry = ttk.Entry(row1, textvariable=self.cfg_var, width=4)
        cfg_entry.pack(side=tk.LEFT, padx=(0, 10))
        cfg_entry.config(validate='key', validatecommand=(self.root.register(self.validate_float), '%P'))
        
        # Sampler
        ttk.Label(row1, text="Sampler:").pack(side=tk.LEFT, padx=(0, 2))
        self.sampler_var = tk.StringVar(value=self.settings.get('SAMPLER', 'DPM++ 2M Karras'))
        
        # Common samplers
        common_samplers = [
            'Euler a', 'Euler', 'LMS', 'Heun', 'DPM2', 'DPM2 a', 'DPM++ 2S a',
            'DPM++ 2M', 'DPM++ 2M Karras', 'DPM++ SDE', 'DPM++ SDE Karras',
            'DPM fast', 'DPM adaptive', 'LMS Karras', 'DPM2 Karras', 'DPM2 a Karras'
        ]
        
        # Sampler combobox with entry
        self.sampler_combo = ttk.Combobox(
            row1, 
            textvariable=self.sampler_var, 
            values=common_samplers,
            width=20
        )
        self.sampler_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Second row - Width, Height, and Generate button
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, pady=2)
        
        # Width
        ttk.Label(row2, text="W:").pack(side=tk.LEFT, padx=(0, 2))
        self.width_var = tk.StringVar(value=str(self.settings.get('WIDTH', '512')))
        width_entry = ttk.Entry(row2, textvariable=self.width_var, width=4)
        width_entry.pack(side=tk.LEFT, padx=(0, 10))
        width_entry.config(validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        
        # Height
        ttk.Label(row2, text="H:").pack(side=tk.LEFT, padx=(0, 2))
        self.height_var = tk.StringVar(value=str(self.settings.get('HEIGHT', '768')))
        height_entry = ttk.Entry(row2, textvariable=self.height_var, width=4)
        height_entry.pack(side=tk.LEFT, padx=(0, 10))
        height_entry.config(validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        
        # Seed
        ttk.Label(row2, text="Seed:").pack(side=tk.LEFT, padx=(0, 2))
        self.seed_var = tk.StringVar(value=str(self.settings.get('SEED', '-1')))
        seed_entry = ttk.Entry(row2, textvariable=self.seed_var, width=8)
        seed_entry.pack(side=tk.LEFT, padx=(0, 10))
        seed_entry.config(validate='key', validatecommand=(self.root.register(self.validate_seed), '%P'))
        
        # Right side - Generate button and prompts
        right_frame = ttk.Frame(action_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generate button
        ttk.Button(right_frame, text="Generate", command=self.generate_prompts).pack(side=tk.LEFT, padx=2)
        
        # Number of prompts entry
        ttk.Label(right_frame, text="Prompts:").pack(side=tk.LEFT, padx=(10, 2))
        self.prompt_count = tk.StringVar(value="100")  # Default value
        count_entry = ttk.Entry(right_frame, textvariable=self.prompt_count, width=5)
        count_entry.pack(side=tk.LEFT, padx=2)
        count_entry.config(validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        
        # Settings button with larger icon
        settings_btn = ttk.Button(
            right_frame, 
            text="⚙", 
            width=3, 
            command=self.open_settings,
            style='Settings.TButton'  # Using a custom style for the settings button
        )
        settings_btn.pack(side=tk.LEFT, padx=(10, 2))
        
        # Configure the settings button style with a larger font
        style = ttk.Style()
        style.configure('Settings.TButton', font=('Helvetica', 20))  # Even larger font for the icon
        
        # Utility Buttons Frame
        util_frame = ttk.Frame(self.inner_frame)
        util_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(util_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(util_frame, text="Open Data Folder", command=self.open_text_files).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Status bar is now in the top button row
        
        # Initialize UI
        self.update_category_list()

    def update_title(self):
        title = "A1111 Prompt Generator"
        if self.current_profile_path:
            title += f" - {self.current_profile_path.name}"
        else:
            title += " - New Profile"
        
        if self.unsaved_changes:
            title += "*"
            
        self.root.title(title)

    def set_unsaved_changes(self, changed=True):
        if self.unsaved_changes != changed:
            self.unsaved_changes = changed
            self.update_title()

    def new_profile(self):
        if self.unsaved_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before proceeding?", default=messagebox.CANCEL)
            if response is None:
                return
            if response:
                self.save_profile()

        self.categories = categories.copy()
        self.current_profile_path = None
        self.data_dir = DATA_DIR  # Reset to default data dir
        self.set_unsaved_changes(False)
        self.update_category_list()
        self.status_var.set("New profile created.")

    def save_profile(self, save_as=False):
        profile_path = self.current_profile_path

        if save_as or not profile_path:
            profile_name = simpledialog.askstring("Save Profile", "Enter a name for the profile:")
            if not profile_name:
                return
            profile_path = PROFILES_DIR / profile_name

        if not profile_path.exists():
            os.makedirs(profile_path / 'data')

        # Save the category list to profile.json
        profile_data = {'categories': self.categories}
        try:
            with open(profile_path / 'profile.json', 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)

            # Copy current .txt files to the profile's data directory
            dest_data_dir = profile_path / 'data'
            for category in self.categories:
                source_file = self.data_dir / f"{category}.txt"
                dest_file = dest_data_dir / f"{category}.txt"
                if source_file.exists() and (not dest_file.exists() or save_as):
                    shutil.copy2(source_file, dest_file)
                elif not source_file.exists() and not dest_file.exists():
                    # Create empty file if it doesn't exist anywhere
                    open(dest_file, 'w').close()

            self.current_profile_path = profile_path
            self.data_dir = dest_data_dir
            self.set_unsaved_changes(False)
            self.status_var.set(f"Profile '{profile_path.name}' saved.")

        except Exception as e:
            messagebox.showerror("Error Saving Profile", f"Could not save profile: {e}")

    def open_profile(self):
        if self.unsaved_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before opening a new profile?", default=messagebox.CANCEL)
            if response is None: return
            if response: self.save_profile()

        profile_path = filedialog.askdirectory(
            initialdir=PROFILES_DIR,
            title="Open Profile"
        )
        if not profile_path:
            return

        profile_path = Path(profile_path)
        profile_json = profile_path / 'profile.json'

        if not profile_json.exists():
            messagebox.showerror("Error", "Selected directory is not a valid profile (missing profile.json).")
            return

        try:
            with open(profile_json, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            self.categories = profile_data.get('categories', [])
            self.current_profile_path = profile_path
            self.data_dir = profile_path / 'data'
            self.set_unsaved_changes(False)
            self.update_category_list()
            self.status_var.set(f"Profile '{profile_path.name}' loaded.")
            self.update_title()  # Update window title with profile name
        except Exception as e:
            messagebox.showerror("Error Opening Profile", f"Could not open profile: {e}")

    def delete_profile(self):
        profile_path = filedialog.askdirectory(
            initialdir=PROFILES_DIR,
            title="Delete Profile"
        )
        if not profile_path:
            return

        profile_path = Path(profile_path)
        if not profile_path.exists():
            messagebox.showerror("Error", "Profile directory not found.")
            return

        response = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the profile '{profile_path.name}' and all its data?")
        if not response:
            return

        try:
            shutil.rmtree(profile_path)
            self.status_var.set(f"Profile '{profile_path.name}' deleted.")
            if profile_path == self.current_profile_path:
                self.new_profile()
        except Exception as e:
            messagebox.showerror("Error Deleting Profile", f"Could not delete profile: {e}")
    
    def move_category_up(self):
        """Move selected category up in the list"""
        selected = self.cat_listbox.curselection()
        if not selected or selected[0] == 0:  # Can't move up if nothing selected or already at top
            return
            
        for i in selected:
            if i > 0:  # Ensure we don't go below 0
                self.set_unsaved_changes()
                # Swap items in the categories list
                self.categories[i], self.categories[i-1] = self.categories[i-1], self.categories[i]
                
        self.update_category_list()
        # Reselect the moved items
        for i in range(len(selected)):
            new_pos = selected[i] - 1 if selected[i] > 0 else 0
            self.cat_listbox.selection_set(new_pos)
        
    def move_category_down(self):
        """Move selected category down in the list"""
        selected = self.cat_listbox.curselection()
        if not selected or selected[-1] == len(self.categories) - 1:  # Can't move down if nothing selected or already at bottom
            return
            
        for i in reversed(selected):  # Process from bottom to avoid index issues
            if i < len(self.categories) - 1:  # Ensure we don't go beyond list length
                self.set_unsaved_changes()
                # Swap items in the categories list
                self.categories[i], self.categories[i+1] = self.categories[i+1], self.categories[i]
                
        self.update_category_list()
        # Reselect the moved items
        for i in range(len(selected)):
            new_pos = selected[i] + 1 if selected[i] < len(self.categories) - 1 else len(self.categories) - 1
            self.cat_listbox.selection_set(new_pos)
    
    def update_category_list(self):
        """Update the listbox and panels with current categories"""
        # Save current selection
        selected = [self.cat_listbox.get(i) for i in self.cat_listbox.curselection()]
        
        # Update listbox
        self.cat_listbox.delete(0, tk.END)
        for cat in self.categories:
            self.cat_listbox.insert(tk.END, cat)
            if cat in selected:  # Restore selection
                self.cat_listbox.selection_set(tk.END)
        
        # Update panels
        self.update_panels()
    
    def update_panels(self):
        """Update the collapsible panels for each category"""
        # Clear existing panels
        for widget in self.panels_frame.winfo_children():
            widget.destroy()
        self.panels = {}
        
        # Create a panel for each category
        for cat in self.categories:
            panel = CollapsibleFrame(self.panels_frame, text=cat, padding="5")
            panel.pack(fill=tk.X, pady=2, padx=5)
            
            # Add text widget to display content
            text_frame = ttk.Frame(panel.content)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            # Text widget with scrollbar
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set,
                                height=8, padx=5, pady=5)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_scroll.config(command=text_widget.yview)
            
            # Make text widget read-only
            text_widget.config(state=tk.NORMAL)
            
            # Load content from file
            file_path = self.data_dir / f"{cat}.txt"
            if file_path.exists() or file_path.is_symlink():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_widget.insert(tk.END, content)
                except Exception as e:
                    text_widget.insert(tk.END, f"Error loading file: {str(e)}")
            else:
                text_widget.insert(tk.END, "[No content. Click the edit button to add content.]")
            
            text_widget.config(state=tk.DISABLED)
            
            # Store reference to the panel
            self.panels[cat] = {
                'frame': panel,
                'text': text_widget
            }
    
    def on_category_select(self, event=None):
        """Handle category selection (double click)"""
        selected = self.cat_listbox.curselection()
        if not selected:
            return
            
        cat = self.cat_listbox.get(selected[0])
        if cat in self.panels:
            # Toggle the panel
            self.panels[cat]['frame'].toggle()
    
    def add_category(self):
        """Add a new category by either creating a new file or linking an existing one"""
        # Create a new dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Category")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Set dialog size and position
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create radio buttons for selection
        var = tk.StringVar(value="new")
        
        # Frame for radio buttons
        radio_frame = ttk.Frame(dialog, padding="10")
        radio_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Create new category file", variable=var, value="new").pack(anchor=tk.W)
        ttk.Radiobutton(radio_frame, text="Link existing text file", variable=var, value="existing").pack(anchor=tk.W)
        
        # Entry for category name
        entry_frame = ttk.Frame(dialog, padding="10")
        entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(entry_frame, text="Category Name:").pack(anchor=tk.W)
        name_entry = ttk.Entry(entry_frame)
        name_entry.pack(fill=tk.X, pady=5)
        
        # File selection button (initially disabled)
        file_frame = ttk.Frame(dialog, padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        file_path = tk.StringVar()
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Text File",
                filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
                initialdir=str(DATA_DIR)
            )
            if filename:
                file_path.set(filename)
                # Set the name entry to the filename without extension
                name = os.path.splitext(os.path.basename(filename))[0]
                name_entry.delete(0, tk.END)
                name_entry.insert(0, name)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=browse_file, state=tk.DISABLED)
        browse_btn.pack(fill=tk.X)
        
        # Toggle file browser based on radio selection
        def toggle_file_browser():
            if var.get() == "existing":
                browse_btn.config(state=tk.NORMAL)
                name_entry.config(state=tk.NORMAL)
            else:
                browse_btn.config(state=tk.DISABLED)
                file_path.set("")
                name_entry.config(state=tk.NORMAL)
        
        var.trace_add('write', lambda *args: toggle_file_browser())
        
        # Button frame
        btn_frame = ttk.Frame(dialog, padding="10")
        btn_frame.pack(fill=tk.X, pady=5)
        
        def on_ok():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a category name")
                return
                
            if var.get() == "existing":
                if not file_path.get():
                    messagebox.showerror("Error", "Please select a text file")
                    return
                # Create a symlink in the data directory
                try:
                    target = Path(file_path.get())
                    if not target.exists():
                        raise FileNotFoundError(f"File not found: {target}")
                        
                    link_path = self.data_dir / f"{name}.txt"
                    if link_path.exists():
                        raise FileExistsError(f"A file named {name}.txt already exists")
                        
                    # Create a relative symlink if possible
                    try:
                        rel_path = os.path.relpath(target, self.data_dir)
                        link_path.symlink_to(rel_path)
                    except (ValueError, OSError):
                        # Fall back to absolute path if relative fails
                        link_path.symlink_to(target)
                        
                    self.status_var.set(f"Linked {name} to {target}")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to link file: {str(e)}")
                    return
            else:
                # Just add to the list without creating a file
                self.status_var.set(f"Added category: {name}")
                
            if name not in self.categories:
                self.categories.append(name)
                self.set_unsaved_changes()
                self.update_category_list()
                
            dialog.destroy()
        
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Set focus to name entry
        name_entry.focus_set()
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def remove_category(self):
        """Remove selected categories"""
        selected = self.cat_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select categories to remove")
            return
            
        # Remove from the end to avoid index shifting
        for i in sorted(selected, reverse=True):
            self.categories.pop(i)
        self.set_unsaved_changes()
        
        self.update_category_list()
        self.status_var.set(f"Removed {len(selected)} categories")
    
    def validate_number(self, value):
        """Validate that the input is a positive integer"""
        if value == "":
            return True
        try:
            return int(value) > 0
        except ValueError:
            return False
            
    def validate_float(self, value):
        """Validate that the input is a positive float"""
        if value == "":
            return True
        try:
            return float(value) > 0
        except ValueError:
            return False
            
    def validate_seed(self, value):
        """Validate seed input (can be -1 or positive integer)"""
        if value == "":
            return True
        try:
            return int(value) == -1 or int(value) >= 0
        except ValueError:
            return False
            
    def generate_prompts(self):
        """Generate prompts based on current settings"""
        # Get the number of prompts to generate
        try:
            num_prompts = int(self.prompt_count.get())
            if num_prompts <= 0:
                raise ValueError("Number of prompts must be positive")
                
            # Update settings from UI
            self.settings['STEPS'] = str(int(float(self.steps_var.get())))
            self.settings['CFG_SCALE'] = str(float(self.cfg_var.get()))
            self.settings['SAMPLER'] = self.sampler_var.get()
            self.settings['WIDTH'] = str(int(float(self.width_var.get())))
            self.settings['HEIGHT'] = str(int(float(self.height_var.get())))
            self.settings['SEED'] = str(int(float(self.seed_var.get())))
            
            # Save settings to file
            settings_file = os.path.join(CONFIG_DIR, "settings.txt")
            with open(settings_file, 'w') as f:
                for key, value in self.settings.items():
                    f.write(f"{key}={value}\n")
                    
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your input values: {str(e)}")
            return
        if not self.categories:
            messagebox.showerror("Error", "No categories selected")
            return
            
        output_file = get_unique_filename("generated_prompts.txt")
        output_dir = BASE_DIR / "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = output_dir / output_file
        
        # Load all category options
        options = {}
        for cat in self.categories:
            base_filename = f"{cat}.txt"
            actual_filename = find_case_insensitive_file(base_filename)
            
            if not actual_filename:
                self.status_var.set(f"Error: Could not find {base_filename}")
                messagebox.showerror("Error", f"Could not find {base_filename}")
                return
                
            try:
                options[cat] = load_options(actual_filename)
                if not options[cat]:
                    raise ValueError(f"No options found in {base_filename}")
            except Exception as e:
                self.status_var.set(f"Error loading {base_filename}")
                messagebox.showerror("Error", f"Error loading {base_filename}: {str(e)}")
                return
        
        # Generate prompts
        num_prompts = 100  # Could be made configurable via UI
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for _ in range(num_prompts):
                    parts = []
                    for cat in self.categories:
                        choice = random.choice(options[cat])
                        parts.append(choice)
                    
                    prompt_text = build_prompt(parts)
                    
                    # Load negative prompt
                    negative_prompt_file = DATA_DIR / "NegativePrompt.txt"
                    try:
                        with open(negative_prompt_file, 'r', encoding='utf-8') as nf:
                            negative_prompt = nf.read().strip()
                    except Exception:
                        negative_prompt = DEFAULT_NEGATIVE_PROMPT
                    
                    # Write prompt in A1111 format
                    line = (
                        f'--prompt "{prompt_text}" \
--negative_prompt "{negative_prompt}" \
--steps {self.settings["STEPS"]} --cfg_scale {self.settings["CFG_SCALE"]} \
--sampler_name "{self.settings["SAMPLER"]}" --seed {self.settings["SEED"]} \
--width {self.settings["WIDTH"]} --height {self.settings["HEIGHT"]}\n'
                    )
                    f.write(line)
            
            self.status_var.set(f"Generated {num_prompts} prompts in {output_path}")
            messagebox.showinfo("Success", f"Successfully generated {num_prompts} prompts!\n\nOutput file:\n{output_path}")
            
        except Exception as e:
            self.status_var.set("Error generating prompts")
            messagebox.showerror("Error", f"Failed to generate prompts: {str(e)}")
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = BASE_DIR / "output"
        os.makedirs(output_dir, exist_ok=True)
        open_file_explorer(output_dir)
    
    def open_text_files(self):
        """Open the data folder with text files"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        open_file_explorer(DATA_DIR)
        
    def open_settings(self):
        """Open the settings file in the default text editor"""
        settings_file = os.path.join(CONFIG_DIR, "settings.txt")
        if not os.path.exists(settings_file):
            # Create default settings if file doesn't exist
            with open(settings_file, 'w') as f:
                f.write("STEPS=20\nCFG_SCALE=7\nSAMPLER=DPM++ 2M Karras\nWIDTH=512\nHEIGHT=768\nSEED=-1")
        open_text_editor(settings_file)
    
    def on_canvas_configure(self, event=None):
        # This method is now handled by the inner functions
        pass
        
    def _on_mousewheel(self, event):
        # This method is now handled by the inner function
        pass
        
    def _on_listbox_scroll(self, event):
        # Handle mouse wheel for the listbox
        if event.num == 4 or event.delta == 120:  # Scroll up
            self.cat_listbox.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta == -120:  # Scroll down
            self.cat_listbox.yview_scroll(1, "units")
        return "break"

def main():
    # Create root window
    root = tk.Tk()
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')  # Use a modern theme
    
    # Create and run the application
    app = PromptGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Import these here to avoid circular imports
    from tkinter import simpledialog
    main()
