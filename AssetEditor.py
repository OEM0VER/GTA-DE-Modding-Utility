import os
import sys
import json
import copy
import subprocess
import shutil
import ctypes
from ctypes import windll
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk

def get_script_directory():
    if getattr(sys, "frozen", False):
        # Compiled EXE is inside Files/.Resources
        # Go back to the Main Folder
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(sys.executable)
            )
        )

    # Running as a Python script
    return os.path.dirname(os.path.abspath(__file__))

DEFAULT_OUTPUT_FOLDER = os.path.join(
    get_script_directory(),
    "Files",
    ".MaterialCreation",
    ".CreatedMats"
)

OUTPUT_FOLDER_FILE = os.path.join(
    get_script_directory(),
    "Files",
    "mat_output_folder.txt"
)

UASSETGUI_PATH = os.path.join(
    get_script_directory(),
    "Files",
    ".Resources",
    "UAssetGUI.exe"
)

MESH_EDITOR_POSITION_PATH = os.path.join(
    get_script_directory(),
    "Files",
    "MeshEditor_window_Position.txt"
)

WINDOW_WIDTH = 680
WINDOW_HEIGHT = 370


def load_output_folder():
    if os.path.exists(OUTPUT_FOLDER_FILE):
        try:
            with open(OUTPUT_FOLDER_FILE, "r", encoding="utf-8") as f:
                saved_folder = f.read().strip()

            if saved_folder:
                return saved_folder
        except Exception:
            pass

    return DEFAULT_OUTPUT_FOLDER


def save_output_folder(folder):
    try:
        with open(OUTPUT_FOLDER_FILE, "w", encoding="utf-8") as f:
            f.write(folder)
    except Exception:
        pass

# ============================================================
# Window Position
# ============================================================

POSITION_FILE = os.path.join(
    get_script_directory(),
    "Files",
    "mat_creation_window_position.txt"
)

DUMMY_POSITION_FILE = os.path.join(
    get_script_directory(),
    "Files",
    "mat_dummy_window_position.txt"
)

GAME_POSITION_FILE = os.path.join(
    get_script_directory(),
    "Files",
    "mat_game_window_position.txt"
)

EDITOR_POSITION_FILE = os.path.join(
    get_script_directory(),
    "Files",
    "mat_editor_window_position.txt"
)


def save_window_position():
    x = root.winfo_x()
    y = root.winfo_y()

    try:
        os.makedirs(
            os.path.dirname(POSITION_FILE),
            exist_ok=True
        )

        with open(POSITION_FILE, "w") as f:
            f.write(f"{x},{y}")

    except Exception as e:
        print(f"[WARNING] Could not save window position: {e}")


def load_window_position():
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, "r") as f:
                pos = f.read().strip().split(",")

            if len(pos) == 2:
                return int(pos[0]), int(pos[1])

        except Exception as e:
            print(f"[WARNING] Could not load window position: {e}")

    return None

def save_child_window_position(
    window,
    position_file
):

    try:

        x = window.winfo_x()
        y = window.winfo_y()

        os.makedirs(
            os.path.dirname(position_file),
            exist_ok=True
        )

        with open(
            position_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"{x},{y}"
            )

    except Exception:

        pass


def load_child_window_position(
    window,
    position_file
):

    if not os.path.exists(
        position_file
    ):

        return

    try:

        with open(
            position_file,
            "r",
            encoding="utf-8"
        ) as f:

            position = f.read().strip()

        x, y = map(
            int,
            position.split(",")
        )

        window.geometry(
            f"+{x}+{y}"
        )

    except Exception:

        pass

# ============================================================
# Asset Manager
# ============================================================

root = tk.Tk()
root.withdraw()

root.title("Asset Manager")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)

# ============================================================
# Load Pricedown Font
# ============================================================

PRICEDOWN_FONT_PATH = os.path.join(
    get_script_directory(),
    "Files",
    ".Resources",
    "pricedown bl.otf"
)

PRICEDOWN_FAMILY = None

if os.path.exists(PRICEDOWN_FONT_PATH):
    try:
        result = windll.gdi32.AddFontResourceW(
            PRICEDOWN_FONT_PATH
        )

        if result:
            print("[LOG] Pricedown font loaded successfully!")

            # Give Windows/Tkinter a moment to update
            root.update_idletasks()

            # Find the actual family name Windows registered.
            # This avoids guessing whether it is called
            # "Pricedown", "Pricedown BL", etc.
            for family in tkFont.families(root):
                if "pricedown" in family.lower():
                    PRICEDOWN_FAMILY = family
                    break

            if PRICEDOWN_FAMILY:
                print(
                    f"[LOG] Pricedown family detected: "
                    f"{PRICEDOWN_FAMILY}"
                )
            else:
                print(
                    "[WARNING] Pricedown loaded, but Tkinter "
                    "could not find the font family."
                )

        else:
            print(
                "[WARNING] Windows could not load the "
                "Pricedown font."
            )

    except Exception as e:
        print(
            f"[WARNING] Could not load Pricedown font: {e}"
        )

else:
    print(
        f"[WARNING] Pricedown font not found:\n"
        f"{PRICEDOWN_FONT_PATH}"
    )

# ============================================================
# Pricedown Tkinter Font
# ============================================================

if PRICEDOWN_FAMILY:
    PRICEDOWN_FONT = tkFont.Font(
        root=root,
        family=PRICEDOWN_FAMILY,
        size=30
    )
else:
    PRICEDOWN_FONT = tkFont.Font(
        root=root,
        family="Arial",
        size=20
    )

# Load previous window position
saved_position = load_window_position()

if saved_position:
    x, y = saved_position
    root.geometry(
        f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}"
    )
else:
    # Centre the window on first launch
    root.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - WINDOW_WIDTH) // 2
    y = (screen_height - WINDOW_HEIGHT) // 2

    root.geometry(
        f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}"
    )

def on_close():
    save_window_position()

    if os.path.exists(PRICEDOWN_FONT_PATH):
        try:
            windll.gdi32.RemoveFontResourceW(
                PRICEDOWN_FONT_PATH
            )
        except Exception:
            pass

    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)


# ============================================================
# Application Icon
# ============================================================

ICON_PATH = os.path.join(
    get_script_directory(),
    "Files",
    ".Resources",
    "ICON.ico"
)

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)


# ============================================================
# Dark Theme
# ============================================================

style = ThemedStyle(root)
style.set_theme("black")

style.configure(
    "TButton",
    anchor="center"
)

# ============================================================
# Main Button Hover Style
# ============================================================

style.configure(
    "Main.TButton",
    background="#555555",
    foreground="white"
)

style.map(
    "Main.TButton",
    background=[
        ("active", "#FF69B4")
    ],
    foreground=[
        ("active", "white")
    ]
)

# Dark window background
root.configure(bg="#1e1e1e")

style.configure(
    "TFrame",
    background="#1e1e1e"
)

style.configure(
    "TLabel",
    background="#1e1e1e",
    foreground="white"
)


# ============================================================
# Button Functions
# ============================================================

def new_dummy_material():
    print("[LOG] New Dummy Material selected")

    dummy_window = tk.Toplevel(root)
    dummy_window.withdraw()
    
    dummy_window.title("New Dummy Materials")
    dummy_window.geometry("550x590")
    dummy_window.resizable(False, False)
    dummy_window.configure(bg="#1e1e1e")

    load_child_window_position(
        dummy_window,
        DUMMY_POSITION_FILE
    )

    # Use the same application icon
    if os.path.exists(ICON_PATH):
        dummy_window.iconbitmap(ICON_PATH)

    # Use the same application icon
    if os.path.exists(ICON_PATH):
        dummy_window.iconbitmap(ICON_PATH)

    # --------------------------------------------------------
    # Output Folder
    # --------------------------------------------------------

    output_folder_var = tk.StringVar(
        value=load_output_folder()
    )

    include_game_structure_var = tk.BooleanVar(
        value=False
    )

    output_frame = ttk.Frame(dummy_window)
    output_frame.pack(
        fill="x",
        padx=25,
        pady=(20, 10)
    )

    output_label = ttk.Label(
        output_frame,
        text="Output Folder"
    )

    output_label.pack(
        anchor="w"
    )

    output_entry_frame = ttk.Frame(output_frame)
    output_entry_frame.pack(
        fill="x",
        pady=(3, 0)
    )

    output_entry = ttk.Entry(
        output_entry_frame,
        textvariable=output_folder_var
    )

    output_entry.pack(
        side="left",
        fill="x",
        expand=True
    )

    setup_entry_undo(output_entry)

    def browse_output_folder():

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:

            output_folder_var.set(folder)
            save_output_folder(folder)

    browse_button = ttk.Button(
        output_entry_frame,
        text="Browse",
        command=browse_output_folder
    )

    browse_button.pack(
        side="left",
        padx=(8, 0)
    )

    browse_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    browse_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(cursor="")
    )

    # --------------------------------------------------------
    # Game Folder Structure
    # --------------------------------------------------------

    game_structure_check = ttk.Checkbutton(
        output_frame,
        text="Include game folder structure",
        variable=include_game_structure_var
    )

    game_structure_check.pack(
        anchor="w",
        pady=(6, 0)
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title_label = ttk.Label(
        dummy_window,
        text="New Dummy Materials",
        font=PRICEDOWN_FONT
    )

    title_label.pack(pady=(25, 20))

    # --------------------------------------------------------
    # Material Entry Area
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Scrollable Material Entry Area
    # --------------------------------------------------------

    materials_container = ttk.Frame(dummy_window)
    materials_container.pack(
        fill="both",
        expand=True,
        padx=(30, 0)
    )

    materials_canvas = tk.Canvas(
        materials_container,
        bg="#1e1e1e",
        highlightthickness=0
    )

    materials_scrollbar = ttk.Scrollbar(
        materials_container,
        orient="vertical",
        command=materials_canvas.yview
    )

    materials_frame = ttk.Frame(
        materials_canvas
    )

    materials_window = materials_canvas.create_window(
        (0, 0),
        window=materials_frame,
        anchor="nw"
    )

    materials_canvas.configure(
        yscrollcommand=materials_scrollbar.set
    )

    def resize_materials_frame(event):

        materials_canvas.itemconfigure(
            materials_window,
            width=event.width
        )

    materials_canvas.bind(
        "<Configure>",
        resize_materials_frame
    )

    materials_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    materials_scrollbar.pack(
        side="right",
        fill="y"
    )

    material_entries = []

    def update_scroll_region(event=None):
        materials_canvas.configure(
            scrollregion=materials_canvas.bbox("all")
        )

    materials_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    def on_mousewheel(event):
        materials_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    materials_canvas.bind(
        "<Enter>",
        lambda event: materials_canvas.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )
    )

    materials_canvas.bind(
        "<Leave>",
        lambda event: materials_canvas.unbind_all(
            "<MouseWheel>"
        )
    )

    def add_material():

        # ====================================================
        # Material Box
        # ====================================================

        material_number = len(material_entries) + 1

        row_frame = ttk.LabelFrame(
            materials_frame,
            text=f"Material {material_number}"
        )

        row_frame.pack(
            fill="x",
            padx=5,
            pady=8
        )

        # ====================================================
        # Material Information
        # ====================================================

        material_info_frame = ttk.Frame(
            row_frame
        )

        material_info_frame.pack(
            fill="x",
            padx=10,
            pady=(8, 5)
        )

        material_info_frame.columnconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # Material Name
        # ----------------------------------------------------

        name_label = ttk.Label(
            material_info_frame,
            text="Material Name:"
        )

        name_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=6
        )

        name_entry = ttk.Entry(
            material_info_frame
        )

        name_entry.insert(
            0,
            "MI_"
        )

        name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=6
        )

        setup_entry_undo(
            name_entry
        )

        # ----------------------------------------------------
        # Material Package Path
        # ----------------------------------------------------

        name_path_label = ttk.Label(
            material_info_frame,
            text="Package Path:"
        )

        name_path_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=6
        )

        name_path_entry = ttk.Entry(
            material_info_frame
        )

        name_path_entry.insert(
            0,
            "/Game/ViceCity/Vehicles/"
        )

        name_path_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=6
        )

        setup_entry_undo(
            name_path_entry
        )

        # ====================================================
        # Texture Box Helper
        # ====================================================

        def create_texture_box(
            title,
            default_name,
            default_path
        ):

            texture_box = ttk.LabelFrame(
                row_frame,
                text=title
            )

            texture_box.pack(
                fill="x",
                padx=10,
                pady=5
            )

            texture_box.columnconfigure(
                1,
                weight=1
            )

            # ------------------------------------------------
            # Texture Name
            # ------------------------------------------------

            texture_name_label = ttk.Label(
                texture_box,
                text="Texture Name:"
            )

            texture_name_label.grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=6
            )

            texture_name_entry = ttk.Entry(
                texture_box
            )

            texture_name_entry.insert(
                0,
                default_name
            )

            texture_name_entry.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=(0, 10),
                pady=6
            )

            setup_entry_undo(
                texture_name_entry
            )

            # ------------------------------------------------
            # Package Path
            # ------------------------------------------------

            texture_path_label = ttk.Label(
                texture_box,
                text="Package Path:"
            )

            texture_path_label.grid(
                row=1,
                column=0,
                sticky="w",
                padx=10,
                pady=6
            )

            texture_path_entry = ttk.Entry(
                texture_box
            )

            texture_path_entry.insert(
                0,
                default_path
            )

            texture_path_entry.grid(
                row=1,
                column=1,
                sticky="ew",
                padx=(0, 10),
                pady=6
            )

            setup_entry_undo(
                texture_path_entry
            )

            return (
                texture_name_entry,
                texture_path_entry
            )

        # ====================================================
        # Base Colour
        # ====================================================

        base_entry, base_path_entry = create_texture_box(
            "Base Color (_BC)",
            "T_",
            "/Game/ViceCity/Textures/Vehicle/"
        )

        # ====================================================
        # Normal
        # ====================================================

        normal_entry, normal_path_entry = create_texture_box(
            "Normal (_N)",
            "T_",
            "/Game/ViceCity/Textures/Vehicle/"
        )

        # ====================================================
        # Packed
        # ====================================================

        packed_entry, packed_path_entry = create_texture_box(
            "Packed (_P)",
            "T_",
            "/Game/ViceCity/Textures/Vehicle/"
        )

        # ====================================================
        # Add / Remove Buttons
        # ====================================================

        buttons_frame = ttk.Frame(
            row_frame
        )

        buttons_frame.pack(
            anchor="e",
            padx=10,
            pady=(5, 10)
        )

        remove_button = ttk.Button(
            buttons_frame,
            text="−",
            width=4
        )

        remove_button.pack(
            side="left",
            padx=(0, 5)
        )

        remove_button.bind(
            "<Enter>",
            set_hand_cursor
        )

        remove_button.bind(
            "<Leave>",
            lambda event: event.widget.configure(
                cursor=""
            )
        )

        add_button = ttk.Button(
            buttons_frame,
            text="+",
            width=4,
            command=add_material
        )

        add_button.pack(
            side="left"
        )

        add_button.bind(
            "<Enter>",
            set_hand_cursor
        )

        add_button.bind(
            "<Leave>",
            lambda event: event.widget.configure(
                cursor=""
            )
        )

        # ====================================================
        # Store Material Data
        # ====================================================

        material_data = {
            "frame": row_frame,

            "name": name_entry,
            "name_path": name_path_entry,

            "base": base_entry,
            "base_path": base_path_entry,

            "normal": normal_entry,
            "normal_path": normal_path_entry,

            "packed": packed_entry,
            "packed_path": packed_path_entry,

            "remove_button": remove_button
        }

        material_entries.append(
            material_data
        )

        # ====================================================
        # Remove Material
        # ====================================================

        def remove_material():

            if len(material_entries) <= 1:
                return

            material_entries.remove(
                material_data
            )

            row_frame.destroy()

        remove_button.configure(
            command=remove_material
        )

        # ====================================================
        # Disable Minus On First Material
        # ====================================================

        if len(material_entries) == 1:

            remove_button.configure(
                state="disabled"
            )

    # First material row
    add_material()

    # --------------------------------------------------------
    # Create Button
    # --------------------------------------------------------

    def create_materials():
        # Location of the template material
        template_path = os.path.join(
            get_script_directory(),
            "Files",
            ".MaterialCreation",
            ".TemplateMats",
            "MI_whee_treadA.json"
        )

        if not os.path.exists(template_path):
            messagebox.showerror(
                "Template Missing",
                "The dummy material template could not be found:\n\n"
                f"{template_path}"
            )
            return

        # Get all material information
        materials = []

        for material_index, material in enumerate(
            material_entries,
            start=1
        ):
            material_name = material["name"].get().strip()
            material_path = material["name_path"].get().strip()

            base_name = material["base"].get().strip()
            base_package_path = material["base_path"].get().strip()

            normal_name = material["normal"].get().strip()
            normal_package_path = material["normal_path"].get().strip()

            packed_name = material["packed"].get().strip()
            packed_package_path = material["packed_path"].get().strip()


            # ------------------------------------------------
            # Generate default dummy material name
            # ------------------------------------------------

            if material_name == "MI_":

                if material_index == 1:
                    material_name = "MI_DummyMaterial"
                else:
                    material_name = (
                        f"MI_DummyMaterial{material_index}"
                    )


            # ------------------------------------------------
            # Keep material path as the package DIRECTORY
            # ------------------------------------------------

            # material_path stays as entered by the user.
            #
            # Example:
            # /Game/ViceCity/Vehicles/
            #
            # The actual material asset path is created later
            # as:
            # /Game/ViceCity/Vehicles/MI_whee2_sport64


            # ------------------------------------------------
            # Keep original template names when only the
            # prefix is left in the field
            # ------------------------------------------------

            if material_name == "MI_":
                material_name = "MI_whee_treadA"

            if base_name == "T_":
                base_name = "T_Whee_Rubber_BC"

            if normal_name == "T_":
                normal_name = "T_Whee_Rubber_N"

            if packed_name == "T_":
                packed_name = "T_whee_treadA_P"


            # ------------------------------------------------
            # Validate Material / Texture Naming
            # ------------------------------------------------

            if not material_name:
                messagebox.showwarning(
                    "Missing Material Name",
                    "Please enter a material name for every material."
                )
                return

            # Material must start with MI_
            if not material_name.startswith("MI_"):
                messagebox.showerror(
                    "Invalid Material Name",
                    f"Invalid material name:\n\n"
                    f"{material_name}\n\n"
                    f"Material names must start with \"MI_\".\n\n"
                    f"Example:\n"
                    f"MI_MyMaterial"
                )
                return


            # ------------------------------------------------
            # Texture Naming Validation
            # ------------------------------------------------

            texture_names = [
                ("Base Colour", base_name, "_BC"),
                ("Normal", normal_name, "_N"),
                ("Packed", packed_name, "_P")
            ]

            for texture_type, texture_name, required_suffix in texture_names:

                if not texture_name:
                    messagebox.showwarning(
                        "Missing Texture Name",
                        f"PLEASE ENTER A {texture_type.upper()} TEXTURE NAME\n\n"
                        f"for: {required_suffix} texture"
                    )
                    return

                # Must start with T_
                if not texture_name.startswith("T_"):
                    messagebox.showerror(
                        "Invalid Texture Name",
                        f"Invalid {texture_type} texture name:\n\n"
                        f"{texture_name}\n\n"
                        f"{texture_type} texture names must start with "
                        f"\"T_\".\n\n"
                        f"Example:\n"
                        f"T_MyTexture{required_suffix}"
                    )
                    return

                # Must have correct suffix
                if not texture_name.upper().endswith(
                    required_suffix
                ):
                    messagebox.showerror(
                        "Invalid Texture Suffix",
                        f"Invalid {texture_type} texture name:\n\n"
                        f"{texture_name}\n\n"
                        f"{texture_type} texture names must end with "
                        f"\"{required_suffix}\".\n\n"
                        f"Example:\n"
                        f"T_MyTexture{required_suffix}\n\n"
                        f"The {required_suffix} suffix cannot be "
                        f"removed or changed."
                    )
                    return

            if not material_name:
                messagebox.showwarning(
                    "Missing Material Name",
                    "PLEASE ENTER A MATERIAL NAME"
                )
                return

            if not material_path:
                messagebox.showwarning(
                    "Missing Material Path",
                    "PLEASE ENTER A PACKAGE PATH\n\n"
                    "for: Material Path"
                )
                return

            if not base_name:
                messagebox.showwarning(
                    "Missing Base Colour",
                    "PLEASE ENTER A BASE COLOUR TEXTURE NAME"
                )
                return

            if not base_package_path:
                messagebox.showwarning(
                    "Missing Base Colour Path",
                    "PLEASE ENTER A PACKAGE PATH\n\n"
                    "for: Base Colour Texture"
                )
                return

            if not normal_name:
                messagebox.showwarning(
                    "Missing Normal",
                    "PLEASE ENTER A NORMAL TEXTURE NAME"
                )
                return

            if not normal_package_path:
                messagebox.showwarning(
                    "Missing Normal Path",
                    "PLEASE ENTER A PACKAGE PATH\n\n"
                    "for: Normal Texture"
                )
                return

            if not packed_name:
                messagebox.showwarning(
                    "Missing Packed Texture",
                    "PLEASE ENTER A PACKED TEXTURE NAME"
                )
                return

            if not packed_package_path:
                messagebox.showwarning(
                    "Missing Packed Texture Path",
                    "PLEASE ENTER A PACKAGE PATH\n\n"
                    "for: Packed Texture"
                )
                return

            # Build the full Unreal paths

            material_full_path = (
                material_path.rstrip("/")
                + "/"
                + material_name
            )

            base_path = (
                base_package_path.rstrip("/")
                + "/"
                + base_name
            )

            normal_path = (
                normal_package_path.rstrip("/")
                + "/"
                + normal_name
            )

            packed_path = (
                packed_package_path.rstrip("/")
                + "/"
                + packed_name
            )

            materials.append({
                "name": material_name,
                "material_path": material_full_path,

                "base_name": base_name,
                "base_path": base_path,

                "normal_name": normal_name,
                "normal_path": normal_path,

                "packed_name": packed_name,
                "packed_path": packed_path
            })

        # Read the template
        try:
            with open(
                template_path,
                "r",
                encoding="utf-8"
            ) as f:
                template_data = json.load(f)

        except Exception as e:
            messagebox.showerror(
                "Template Error",
                f"Could not read the template material.\n\n{e}"
            )
            return

        # Output folder
        output_folder = output_folder_var.get().strip()

        if not output_folder:
            output_folder = DEFAULT_OUTPUT_FOLDER

        # ------------------------------------------------
        # Template values
        # ------------------------------------------------

        old_material_name = "MI_whee_treadA"

        old_base_path = (
            "/Game/ViceCity/Textures/Vehicle/"
            "T_Whee_Rubber_BC"
        )

        old_normal_path = (
            "/Game/ViceCity/Textures/Vehicle/"
            "T_Whee_Rubber_N"
        )

        old_packed_path = (
            "/Game/ViceCity/Textures/Vehicle/"
            "T_whee_treadA_P"
        )

        old_base_name = "T_Whee_Rubber_BC"
        old_normal_name = "T_Whee_Rubber_N"
        old_packed_name = "T_whee_treadA_P"

        old_material_path = (
            "/Game/ViceCity/Vehicles/"
            "MI_whee_treadA"
        )

        # ------------------------------------------------
        # Create each material
        # ------------------------------------------------

        created_count = 0

        for material in materials:

            material_name = material["name"]

            material_path = material["material_path"]

            base_name = material["base_name"]
            normal_name = material["normal_name"]
            packed_name = material["packed_name"]

            base_path = material["base_path"]

            normal_path = material["normal_path"]

            packed_path = material["packed_path"]

            # ------------------------------------------------
            # Build output folder for this material
            # ------------------------------------------------

            material_output_folder = output_folder

            if include_game_structure_var.get():

                game_path = material_path.strip()

                if game_path.startswith("/Game/"):

                    relative_game_path = game_path[
                        len("/Game/"):
                    ]

                    relative_game_directory = os.path.dirname(
                        relative_game_path
                    )

                    material_output_folder = os.path.join(
                        output_folder,
                        "Gameface",
                        "Content",
                        relative_game_directory
                    )

            try:
                os.makedirs(
                    material_output_folder,
                    exist_ok=True
                )

            except Exception as e:
                messagebox.showerror(
                    "Output Folder Error",
                    f"Could not create/access the output folder:\n\n"
                    f"{material_output_folder}\n\n"
                    f"{e}"
                )
                return

            # Make a completely independent copy
            material_data = copy.deepcopy(
                template_data
            )

            # ------------------------------------------------
            # Material NameMap
            # ------------------------------------------------

            new_name_map = []

            for name in material_data["NameMap"]:

                if name == old_material_name:
                    name = material_name

                elif name == old_material_path:
                    name = material_full_path

                # Base Colour
                elif name == old_base_path:
                    name = base_path

                elif name == old_base_name:
                    name = base_name

                # Normal
                elif name == old_normal_path:
                    name = normal_path

                elif name == old_normal_name:
                    name = normal_name

                # Packed
                elif name == old_packed_path:
                    name = packed_path

                elif name == old_packed_name:
                    name = packed_name

                new_name_map.append(name)

            material_data["NameMap"] = new_name_map

            # ------------------------------------------------
            # Export ObjectName
            # ------------------------------------------------

            for export in material_data.get(
                "Exports",
                []
            ):

                if export.get(
                    "ObjectName"
                ) == old_material_name:

                    export["ObjectName"] = (
                        material_name
                    )

            # ------------------------------------------------
            # Import Data
            # ------------------------------------------------

            for import_data in material_data.get(
                "Imports",
                []
            ):

                object_name = import_data.get(
                    "ObjectName"
                )

                object_path = import_data.get(
                    "ObjectPath"
                )

                # --------------------------------------------
                # Base Colour
                # --------------------------------------------

                if (
                    object_name == old_base_name
                    or object_path == old_base_path
                ):
                    import_data["ObjectName"] = base_name

                    if object_path == old_base_path:
                        import_data["ObjectPath"] = base_path

                # --------------------------------------------
                # Normal
                # --------------------------------------------

                elif (
                    object_name == old_normal_name
                    or object_path == old_normal_path
                ):
                    import_data["ObjectName"] = normal_name

                    if object_path == old_normal_path:
                        import_data["ObjectPath"] = normal_path

                # --------------------------------------------
                # Packed
                # --------------------------------------------

                elif (
                    object_name == old_packed_name
                    or object_path == old_packed_path
                ):
                    import_data["ObjectName"] = packed_name

                    if object_path == old_packed_path:
                        import_data["ObjectPath"] = packed_path

            # ------------------------------------------------
            # Replace Texture Paths Anywhere In Import Data
            # ------------------------------------------------

            def replace_texture_references(value):

                if isinstance(value, str):

                    if value == old_base_path:
                        return base_path

                    if value == old_normal_path:
                        return normal_path

                    if value == old_packed_path:
                        return packed_path

                    if value == old_base_name:
                        return base_name

                    if value == old_normal_name:
                        return normal_name

                    if value == old_packed_name:
                        return packed_name

                    return value

                if isinstance(value, list):
                    return [
                        replace_texture_references(item)
                        for item in value
                    ]

                if isinstance(value, dict):
                    return {
                        key: replace_texture_references(item)
                        for key, item in value.items()
                    }

                return value

            material_data["Imports"] = (
                replace_texture_references(
                    material_data.get("Imports", [])
                )
            )

            # ------------------------------------------------
            # Replace old material path anywhere in JSON data
            # ------------------------------------------------

            def replace_material_path(value):

                if isinstance(value, str):
                    return value.replace(
                        old_material_path,
                        material_full_path
                    )

                if isinstance(value, list):
                    return [
                        replace_material_path(item)
                        for item in value
                    ]

                if isinstance(value, dict):
                    return {
                        key: replace_material_path(item)
                        for key, item in value.items()
                    }

                return value

            material_data = replace_material_path(
                material_data
            )

            # ------------------------------------------------
            # Save JSON
            # ------------------------------------------------

            output_path = os.path.join(
                material_output_folder,
                f"{material_name}.json"
            )

            try:
                with open(
                    output_path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        material_data,
                        f,
                        indent=2
                    )

                print(
                    f"[LOG] Created temporary JSON: "
                    f"{output_path}"
                )

            except Exception as e:
                messagebox.showerror(
                    "Creation Error",
                    f"Could not create:\n\n"
                    f"{material_name}.json\n\n"
                    f"{e}"
                )
                return


            # ------------------------------------------------
            # Convert JSON to UAsset using UAssetGUI
            # ------------------------------------------------

            output_uasset_path = os.path.join(
                material_output_folder,
                f"{material_name}.uasset"
            )

            print(
                f"[LOG] Converting JSON to UAsset: "
                f"{output_uasset_path}"
            )

            try:
                result = subprocess.run(
                    [
                        UASSETGUI_PATH,
                        "fromjson",
                        output_path,
                        output_uasset_path
                    ],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            except Exception as e:
                messagebox.showerror(
                    "UAssetGUI Error",
                    f"Could not run UAssetGUI.\n\n"
                    f"{e}\n\n"
                    f"The JSON has been kept for debugging:\n"
                    f"{output_path}"
                )
                return


            # ------------------------------------------------
            # Check conversion result
            # ------------------------------------------------

            if result.returncode != 0 or not os.path.exists(
                output_uasset_path
            ):

                error_text = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Unknown UAssetGUI error."
                )

                messagebox.showerror(
                    "Material Conversion Error",
                    f"UAssetGUI could not convert:\n\n"
                    f"{material_name}.json\n\n"
                    f"{error_text}\n\n"
                    f"The JSON has been kept for debugging:\n"
                    f"{output_path}"
                )

                print(
                    f"[ERROR] UAssetGUI conversion failed for "
                    f"{material_name}"
                )

                return


            # ------------------------------------------------
            # Conversion successful - remove JSON
            # ------------------------------------------------

            try:
                os.remove(output_path)

                print(
                    f"[LOG] Removed temporary JSON: "
                    f"{output_path}"
                )

            except Exception as e:
                print(
                    f"[WARNING] Could not remove JSON: "
                    f"{output_path} - {e}"
                )

            created_count += 1

            print(
                f"[LOG] Created dummy material UAsset: "
                f"{output_uasset_path}"
            )

        messagebox.showinfo(
            "Materials Created",
            f"Successfully created {created_count} "
            f"dummy material"
            f"{'s' if created_count != 1 else ''}."
        )

        print(
            f"[LOG] Created {created_count} dummy material(s)."
            )


    # --------------------------------------------------------
    # Create Button
    # --------------------------------------------------------

    create_button = ttk.Button(
        dummy_window,
        text="Create Materials",
        width=30,
        command=create_materials,
        style="Main.TButton"
    )

    create_button.pack(
        pady=(15, 30),
        ipady=8
    )

    create_button.bind(
        "<Enter>",
        set_hand_cursor
    )
    create_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(cursor="")
    )

    # --------------------------------------------------------
    # Save Window Position When Closed
    # --------------------------------------------------------

    def close_dummy_window():

        save_child_window_position(
            dummy_window,
            DUMMY_POSITION_FILE
        )

        dummy_window.destroy()

    dummy_window.protocol(
        "WM_DELETE_WINDOW",
        close_dummy_window
    )

    dummy_window.update_idletasks()
    dummy_window.deiconify()

# --------------------------------------------------------
# Mesh Editor
# --------------------------------------------------------

def mesh_editor():

    # ----------------------------------------------------
    # Select source file first
    # ----------------------------------------------------

    source_path = filedialog.askopenfilename(
        parent=root,
        title="Open Mesh",
        filetypes=[
            ("Mesh Files (UAsset & JSON)", "*.uasset *.json"),
            ("UAsset Files", "*.uasset"),
            ("JSON Files", "*.json")
        ]
    )

    if not source_path:
        return

    source_extension = os.path.splitext(source_path)[1].lower()

    temporary_json = False

    # ----------------------------------------------------
    # Load / create JSON
    # ----------------------------------------------------

    if source_extension == ".uasset":

        json_path = os.path.splitext(source_path)[0] + ".json"

        try:

            result = subprocess.run(
                [
                    UASSETGUI_PATH,
                    "tojson",
                    source_path,
                    json_path,
                    "VER_UE4_26"
                ],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:

                error_output = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "No error output was returned."
                )

                messagebox.showerror(
                    "Mesh Conversion Failed",
                    (
                        "UAssetGUI failed to convert the mesh "
                        "to JSON.\n\n"
                        f"{error_output}"
                    )
                )

                return

            temporary_json = True

        except Exception as error:

            messagebox.showerror(
                "Mesh Conversion Failed",
                str(error)
            )

            return

    elif source_extension == ".json":

        json_path = source_path

    else:

        messagebox.showerror(
            "Invalid File",
            "Please select a .uasset or .json file."
        )

        return

    # ----------------------------------------------------
    # Read JSON
    # ----------------------------------------------------

    try:

        with open(
            json_path,
            "r",
            encoding="utf-8-sig"
        ) as file:

            parsed_data = json.load(
                file
            )

    except Exception as error:

        if temporary_json and os.path.exists(json_path):
            try:
                os.remove(json_path)
            except Exception:
                pass

        messagebox.showerror(
            "Mesh JSON Error",
            (
                "Could not read the mesh JSON.\n\n"
                f"{error}"
            )
        )

        return

    # ----------------------------------------------------
    # Find mesh export
    # ----------------------------------------------------

    exports = []

    if isinstance(
        parsed_data,
        dict
    ):

        exports = parsed_data.get(
            "Exports",
            []
        )

    elif isinstance(
        parsed_data,
        list
    ):

        exports = parsed_data

    mesh_export = None
    mesh_type = None

    for export in exports:

        if not isinstance(
            export,
            dict
        ):
            continue

        object_name = str(
            export.get(
                "ObjectName",
                ""
            )
        )

        object_name = object_name.split(
            " ",
            1
        )[0]

        if object_name.startswith(
            "SM_"
        ):

            mesh_export = export
            mesh_type = "Static Mesh"

            break

        if object_name.startswith(
            "SKR_"
        ):

            mesh_export = export
            mesh_type = "Skeletal Mesh"

            break

    if mesh_export is None:

        if temporary_json and os.path.exists(json_path):
            try:
                os.remove(json_path)
            except Exception:
                pass

        messagebox.showerror(
            "Mesh Not Found",
            (
                "Could not find a Static Mesh or "
                "Skeletal Mesh export.\n\n"
                "The mesh name must begin with SM_ or SKR_."
            )
        )

        return

    # ----------------------------------------------------
    # Get mesh name
    # ----------------------------------------------------

    mesh_name = str(
        mesh_export.get(
            "ObjectName",
            ""
        )
    )

    mesh_name = mesh_name.split(
        " ",
        1
    )[0]

    # ----------------------------------------------------
    # Find package path
    # ----------------------------------------------------

    package_path = ""

    mesh_full_path = ""

    name_map = []

    if isinstance(
        parsed_data,
        dict
    ):

        name_map = parsed_data.get(
            "NameMap",
            []
        )

    for name in name_map:

        if not isinstance(
            name,
            str
        ):
            continue

        if (
            name.startswith("/Game/")
            and
            name.endswith(
                "/" + mesh_name
            )
        ):

            mesh_full_path = name

            package_path = (
                name.rsplit(
                    "/",
                    1
                )[0]
                + "/"
            )

            break

    # Find Wheel Mesh
    wheel_mesh_name = ""
    wheel_mesh_path = ""

    if (
        isinstance(parsed_data, dict)
        and mesh_type == "Skeletal Mesh"
    ):

        exports = parsed_data.get(
            "Exports",
            []
        )

        imports = parsed_data.get(
            "Imports",
            []
        )

        # Find WheelMesh Property
        wheel_mesh_reference = None

        for export in exports:

            if not isinstance(
                export,
                dict
            ):

                continue

            for property_data in export.get(
                "Data",
                []
            ):

                if not isinstance(
                    property_data,
                    dict
                ):

                    continue

                if property_data.get(
                    "Name"
                ) == "WheelMesh":

                    wheel_mesh_reference = property_data.get(
                        "Value"
                    )

                    break

            if wheel_mesh_reference is not None:

                break

        # Resolve WheelMesh Reference
        if isinstance(
            wheel_mesh_reference,
            int
        ):

            if wheel_mesh_reference < 0:

                wheel_import_index = (
                    -wheel_mesh_reference
                ) - 1

                if (
                    0 <= wheel_import_index < len(imports)
                ):

                    wheel_import = imports[
                        wheel_import_index
                    ]

                    if isinstance(
                        wheel_import,
                        dict
                    ):

                        wheel_mesh_name = str(
                            wheel_import.get(
                                "ObjectName",
                                ""
                            )
                        )

                        wheel_mesh_name = wheel_mesh_name.split(
                            " ",
                            1
                        )[0]

                        # Find WheelMesh Path
                        for name in name_map:

                            if not isinstance(
                                name,
                                str
                            ):

                                continue

                            if name.endswith(
                                "/" + wheel_mesh_name
                            ):

                                wheel_mesh_path = (
                                    name.rsplit(
                                        "/",
                                        1
                                    )[0]
                                    + "/"
                                )

                                break

        wheel_mesh_reference = None

        for property_data in mesh_export.get(
            "Data",
            []
        ):

            if not isinstance(
                property_data,
                dict
            ):

                continue

            if property_data.get(
                "Name"
            ) == "WheelMesh":

                wheel_mesh_reference = property_data.get(
                    "Value"
                )

                break

        if isinstance(
            wheel_mesh_reference,
            int
        ):

            if wheel_mesh_reference < 0:

                wheel_import_index = (
                    -wheel_mesh_reference
                ) - 1

                imports = parsed_data.get(
                    "Imports",
                    []
                )

                if 0 <= wheel_import_index < len(
                    imports
                ):

                    wheel_import = imports[
                        wheel_import_index
                    ]

                    if isinstance(
                        wheel_import,
                        dict
                    ):

                        wheel_mesh_name = str(
                            wheel_import.get(
                                "ObjectName",
                                ""
                            )
                        )

                        for name in name_map:

                            if not isinstance(
                                name,
                                str
                            ):

                                continue

                            if name.endswith(
                                "/" + wheel_mesh_name
                            ):

                                wheel_mesh_path = (
                                    name.rsplit(
                                        "/",
                                        1
                                    )[0]
                                    + "/"
                                )

                                break

    # ----------------------------------------------------
    # Mesh Editor Window
    # ----------------------------------------------------

    editor_window = tk.Toplevel(
        root
    )

    editor_window.withdraw()

    # Prevent the window from being shown while it is being constructed
    editor_window.transient(root)

    try:
        editor_window.iconbitmap(
            os.path.join(
                get_script_directory(),
                "Files",
                "icon.ico"
            )
        )
    except Exception:
        pass

    editor_window.title(
        "Mesh Editor"
    )

    editor_window.geometry(
        "600x860"
    )

    if os.path.exists(
        ICON_PATH
    ):

        editor_window.iconbitmap(
            ICON_PATH
        )

    if os.path.isfile(
        MESH_EDITOR_POSITION_PATH
    ):

        try:

            with open(
                MESH_EDITOR_POSITION_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                position_data = file.read().strip()

            position_parts = position_data.split(
                ","
            )

            if len(position_parts) == 2:

                editor_window.geometry(
                    f"600x860+{int(position_parts[0])}+{int(position_parts[1])}"
                )

        except Exception:
            pass

    editor_window.resizable(
        False,
        False
    )

    editor_window.configure(
        bg="#1e1e1e" 
    )

    # ----------------------------------------------------
    # Output Folder
    # ----------------------------------------------------

    output_folder_var = tk.StringVar(
        value=load_output_folder()
    )

    output_frame = tk.Frame(
        editor_window,
        bg="#1e1e1e"
    )

    output_frame.pack(
        fill="x",
        padx=20,
        pady=(15, 5)
    )

    output_label = ttk.Label(
        output_frame,
        text="Output Folder:"
    )

    output_label.pack(
        anchor="w"
    )

    output_entry_frame = tk.Frame(
        output_frame,
        bg="#1e1e1e"
    )

    output_entry_frame.pack(
        fill="x",
        pady=(3, 0)
    )

    output_entry = ttk.Entry(
        output_entry_frame,
        textvariable=output_folder_var
    )

    output_entry.pack(
        side="left",
        fill="x",
        expand=True
    )

    setup_entry_undo(
        output_entry
    )

    def browse_output_folder():

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:

            output_folder_var.set(
                folder
            )

            save_output_folder(
                folder
            )

    browse_button = ttk.Button(
        output_entry_frame,
        text="Browse",
        command=browse_output_folder
    )

    browse_button.pack(
        side="left",
        padx=(8, 0)
    )

    browse_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    browse_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(
            cursor=""
        )
    )

    # ----------------------------------------------------
    # Game Folder Structure
    # ----------------------------------------------------

    include_game_structure_var = tk.BooleanVar(
        value=False
    )

    game_structure_check = ttk.Checkbutton(
        editor_window,
        text="Include game folder structure",
        variable=include_game_structure_var
    )

    game_structure_check.pack(
        anchor="w",
        padx=20,
        pady=(0, 10)
    )

    # ----------------------------------------------------
    # Title
    # ----------------------------------------------------

    title_label = tk.Label(
        editor_window,
        text="Mesh Editor",
        font=PRICEDOWN_FONT,
        bg="#1e1e1e",
        fg="white"
    )

    title_label.pack(
        pady=(15, 15)
    )

    # ========================================================
    # Mesh Information
    # ========================================================

    mesh_frame = ttk.LabelFrame(
        editor_window,
        text="Mesh"
    )

    mesh_frame.pack(
        fill="x",
        padx=20,
        pady=(5, 10)
    )

    mesh_frame.columnconfigure(
        1,
        weight=1
    )

    # --------------------------------------------------------
    # Mesh Type
    # --------------------------------------------------------

    mesh_type_label = ttk.Label(
        mesh_frame,
        text="Mesh Type:"
    )

    mesh_type_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    mesh_type_value = ttk.Label(
        mesh_frame,
        text=mesh_type,
        font=("Segoe UI", 10, "bold")
    )

    mesh_type_value.grid(
        row=0,
        column=1,
        sticky="w",
        padx=(0, 10),
        pady=8
    )

    # --------------------------------------------------------
    # Mesh Name
    # --------------------------------------------------------

    mesh_name_label = ttk.Label(
        mesh_frame,
        text="Mesh Name:"
    )

    mesh_name_label.grid(
        row=1,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    mesh_name_entry = ttk.Entry(
        mesh_frame
    )

    mesh_name_entry.insert(
        0,
        mesh_name
    )

    mesh_name_entry.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    setup_entry_undo(
        mesh_name_entry
    )

    # --------------------------------------------------------
    # Package Path
    # --------------------------------------------------------

    package_path_label = ttk.Label(
        mesh_frame,
        text="Package Path:"
    )

    package_path_label.grid(
        row=2,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    package_path_entry = ttk.Entry(
        mesh_frame
    )

    package_path_entry.insert(
        0,
        package_path
    )

    package_path_entry.grid(
        row=2,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    setup_entry_undo(
        package_path_entry
    )

    # ========================================================
    # Wheel Mesh
    # ========================================================

    if wheel_mesh_name:

        wheel_mesh_frame = ttk.LabelFrame(
            editor_window,
            text="Wheel Mesh"
        )

        wheel_mesh_frame.pack(
            fill="x",
            padx=20,
            pady=(5, 10)
        )

        wheel_mesh_frame.columnconfigure(
            1,
            weight=1
        )

        # --------------------------------------------------------
        # Wheel Mesh Type
        # --------------------------------------------------------

        wheel_mesh_type = ""

        if wheel_mesh_name.startswith(
            "SM_"
        ):

            wheel_mesh_type = "Static Mesh"

        elif wheel_mesh_name.startswith(
            "SKR_"
        ):

            wheel_mesh_type = "Skeletal Mesh"

        wheel_mesh_type_label = ttk.Label(
            wheel_mesh_frame,
            text="Mesh Type:"
        )

        wheel_mesh_type_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=8
        )

        wheel_mesh_type_value = ttk.Label(
            wheel_mesh_frame,
            text=wheel_mesh_type,
            font=("Segoe UI", 10, "bold")
        )

        wheel_mesh_type_value.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 10),
            pady=8
        )

        # --------------------------------------------------------
        # Wheel Mesh Name
        # --------------------------------------------------------

        wheel_mesh_name_label = ttk.Label(
            wheel_mesh_frame,
            text="Wheel Mesh Name:"
        )

        wheel_mesh_name_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=8
        )

        wheel_mesh_name_entry = ttk.Entry(
            wheel_mesh_frame
        )

        wheel_mesh_name_entry.insert(
            0,
            wheel_mesh_name
        )

        wheel_mesh_name_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=8
        )

        setup_entry_undo(
            wheel_mesh_name_entry
        )

        # --------------------------------------------------------
        # Wheel Mesh Package Path
        # --------------------------------------------------------

        wheel_mesh_path_label = ttk.Label(
            wheel_mesh_frame,
            text="Package Path:"
        )

        wheel_mesh_path_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=10,
            pady=8
        )

        wheel_mesh_path_entry = ttk.Entry(
            wheel_mesh_frame
        )

        if wheel_mesh_path:

            wheel_mesh_path_entry.insert(
                0,
                wheel_mesh_path
            )

        wheel_mesh_path_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=8
        )

        setup_entry_undo(
            wheel_mesh_path_entry
        )

    # ========================================================
    # Material References
    # ========================================================

    materials_frame = ttk.LabelFrame(
        editor_window,
        text="Material References"
    )

    materials_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    materials_canvas = tk.Canvas(
        materials_frame,
        bg="#2b2b2b",
        highlightthickness=0
    )

    materials_scrollbar = ttk.Scrollbar(
        materials_frame,
        orient="vertical",
        command=materials_canvas.yview
    )

    materials_inner = tk.Frame(
        materials_canvas,
        bg="#2b2b2b"
    )

    materials_inner.bind(
        "<Configure>",
        lambda event: materials_canvas.configure(
            scrollregion=materials_canvas.bbox("all")
        )
    )

    materials_canvas.create_window(
        (0, 0),
        window=materials_inner,
        anchor="nw"
    )

    materials_canvas.configure(
        yscrollcommand=materials_scrollbar.set
    )

    materials_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    materials_scrollbar.pack(
        side="right",
        fill="y"
    )

    # ----------------------------------------------------
    # Mouse Wheel Scrolling
    # ----------------------------------------------------

    def scroll_materials(event):

        # Only scroll when the mouse is inside
        # the Mesh Editor window
        try:

            widget = event.widget

            if (
                widget.winfo_toplevel()
                != editor_window
            ):

                return

        except Exception:

            return

        materials_canvas.yview_scroll(
            int(
                -1 * (
                    event.delta / 120
                )
            ),
            "units"
        )

        return "break"

    # ----------------------------------------------------
    # Bind Mouse Wheel Throughout Mesh Editor
    # ----------------------------------------------------

    editor_window.bind_all(
        "<MouseWheel>",
        scroll_materials,
        add="+"
    )

    # ----------------------------------------------------
    # Find Material References
    # ----------------------------------------------------

    material_references = []

    imports = []

    if isinstance(
        parsed_data,
        dict
    ):

        imports = parsed_data.get(
            "Imports",
            []
        )

    def find_material_package(
        material_import,
        material_name
    ):

        package_path = ""
        package_import_index = None

        outer_index = material_import.get(
            "OuterIndex"
        )

        # ------------------------------------------------
        # Resolve the Package Import through OuterIndex
        # ------------------------------------------------

        if (
            isinstance(
                outer_index,
                int
            )
            and
            outer_index < 0
        ):

            package_index = (
                -outer_index
            ) - 1

            if (
                0 <= package_index < len(
                    imports
                )
            ):

                package_import = imports[
                    package_index
                ]

                if isinstance(
                    package_import,
                    dict
                ):

                    package_name = str(
                        package_import.get(
                            "ObjectName",
                            ""
                        )
                    )

                    if (
                        package_name.startswith(
                            "/Game/"
                        )
                        and
                        package_name.endswith(
                            "/" + material_name
                        )
                    ):

                        package_path = (
                            package_name.rsplit(
                                "/",
                                1
                            )[0]
                            + "/"
                        )

                        package_import_index = (
                            package_index
                        )

        # ------------------------------------------------
        # Fallback - Search Package Imports
        # ------------------------------------------------

        if not package_path:

            for package_index, package_import in enumerate(
                imports
            ):

                if not isinstance(
                    package_import,
                    dict
                ):
                    continue

                if package_import.get(
                    "ClassName"
                ) != "Package":
                    continue

                package_name = str(
                    package_import.get(
                        "ObjectName",
                        ""
                    )
                )

                if not package_name.startswith(
                    "/Game/"
                ):
                    continue

                if package_name.endswith(
                    "/" + material_name
                ):

                    package_path = (
                        package_name.rsplit(
                            "/",
                            1
                        )[0]
                        + "/"
                    )

                    package_import_index = (
                        package_index
                    )

                    break

        # ------------------------------------------------
        # Final Fallback - NameMap
        # ------------------------------------------------

        if not package_path:

            for name in name_map:

                if not isinstance(
                    name,
                    str
                ):
                    continue

                if not name.startswith(
                    "/Game/"
                ):
                    continue

                if name.endswith(
                    "/" + material_name
                ):

                    package_path = (
                        name.rsplit(
                            "/",
                            1
                        )[0]
                        + "/"
                    )

                    break

        return (
            package_path,
            package_import_index
        )

    # ====================================================
    # Static Mesh Materials
    # ====================================================

    if mesh_type == "Static Mesh":

        static_materials = []

        for export in exports:

            if not isinstance(
                export,
                dict
            ):
                continue

            if export is not mesh_export:
                continue

            for property_data in export.get(
                "Data",
                []
            ):

                if not isinstance(
                    property_data,
                    dict
                ):
                    continue

                if property_data.get(
                    "Name"
                ) != "StaticMaterials":
                    continue

                values = property_data.get(
                    "Value",
                    []
                )

                if not isinstance(
                    values,
                    list
                ):
                    continue

                static_materials = values

                break

        for material_index, material_data in enumerate(
            static_materials
        ):

            if not isinstance(
                material_data,
                dict
            ):
                continue

            material_name = ""
            material_reference = None
            material_slot_name = ""

            for value in material_data.get(
                "Value",
                []
            ):

                if not isinstance(
                    value,
                    dict
                ):
                    continue

                property_name = value.get(
                    "Name"
                )

                if property_name == "MaterialInterface":

                    material_reference = value.get(
                        "Value"
                    )

                elif property_name == "MaterialSlotName":

                    material_slot_name = str(
                        value.get(
                            "Value",
                            ""
                        )
                    )

            if not isinstance(
                material_reference,
                int
            ):
                continue

            if material_reference >= 0:
                continue

            import_index = (
                -material_reference
            ) - 1

            if import_index < 0:
                continue

            if import_index >= len(
                imports
            ):
                continue

            material_import = imports[
                import_index
            ]

            if not isinstance(
                material_import,
                dict
            ):
                continue

            material_name = str(
                material_import.get(
                    "ObjectName",
                    ""
                )
            )

            (
                package_path,
                package_import_index
            ) = find_material_package(
                material_import,
                material_name
            )

            if not package_path:
                continue

            material_references.append(
                {
                    "name": material_name,
                    "path": package_path,
                    "slot": material_slot_name,
                    "import_index": import_index,
                    "package_import_index": package_import_index
                }
            )

    # ====================================================
    # Skeletal Mesh Materials
    # ====================================================

    elif mesh_type == "Skeletal Mesh":

        for import_index, material_import in enumerate(
            imports
        ):

            if not isinstance(
                material_import,
                dict
            ):
                continue

            if material_import.get(
                "ClassName"
            ) != "MaterialInstanceConstant":
                continue

            material_name = str(
                material_import.get(
                    "ObjectName",
                    ""
                )
            )

            (
                package_path,
                package_import_index
            ) = find_material_package(
                material_import,
                material_name
            )

            if not package_path:
                continue

            material_references.append(
                {
                    "name": material_name,
                    "path": package_path,
                    "slot": "",
                    "import_index": import_index,
                    "package_import_index": package_import_index
                }
            )

    # ----------------------------------------------------
    # Display Material References
    # ----------------------------------------------------

    material_name_entries = []
    material_path_entries = []

    for material_index, material in enumerate(
        material_references
    ):

        material_label = tk.Label(
            materials_inner,
            text=f"Material {material_index + 1}",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2b2b",
            fg="white"
        )

        material_label.pack(
            anchor="w",
            pady=(5, 3)
        )

        material_name_label = tk.Label(
            materials_inner,
            text="Material Name:",
            font=("Segoe UI", 9),
            bg="#2b2b2b",
            fg="white"
        )

        material_name_label.pack(
            anchor="w"
        )

        material_name_entry = ttk.Entry(
            materials_inner,
            width=70
        )

        material_name_entry.insert(
            0,
            material["name"]
        )

        material_name_entry.pack(
            fill="x",
            pady=(2, 5)
        )

        material_path_label = tk.Label(
            materials_inner,
            text="Package Path:",
            font=("Segoe UI", 9),
            bg="#2b2b2b",
            fg="white"
        )

        material_path_label.pack(
            anchor="w"
        )

        material_path_entry = ttk.Entry(
            materials_inner,
            width=70
        )

        material_path_entry.insert(
            0,
            material["path"]
        )

        material_path_entry.pack(
            fill="x",
            pady=(2, 15)
        )

        setup_entry_undo(
            material_name_entry
        )

        setup_entry_undo(
            material_path_entry
        )

        material_name_entries.append(
            material_name_entry
        )

        material_path_entries.append(
            material_path_entry
        )

    if not material_references:

        materials_info = tk.Label(
            materials_inner,
            text="No material references were found.",
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="#888888"
        )

        materials_info.pack(
            anchor="w",
            pady=(5, 10)
        )

    # ----------------------------------------------------
    # Save Mesh
    # ----------------------------------------------------

    def save_mesh():

        # ------------------------------------------------
        # Get Mesh Information
        # ------------------------------------------------

        new_mesh_name = mesh_name_entry.get().strip()
        new_mesh_package_path = package_path_entry.get().strip()

        # ------------------------------------------------
        # Validate Mesh Name
        # ------------------------------------------------

        if not new_mesh_name:

            messagebox.showwarning(
                "Missing Mesh Name",
                "PLEASE ENTER A MESH NAME"
            )

            return

        # ------------------------------------------------
        # Validate Mesh Prefix
        # ------------------------------------------------

        if not (
            new_mesh_name.startswith("SM_")
            or
            new_mesh_name.startswith("SKR_")
        ):

            messagebox.showerror(
                "Invalid Mesh Name",
                f"Invalid mesh name:\n\n"
                f"{new_mesh_name}\n\n"
                f"Mesh names must start with \"SM_\" "
                f"or \"SKR_\".\n\n"
                f"Examples:\n"
                f"SM_MyMesh\n"
                f"SKR_MyMesh"
            )

            return

        # ------------------------------------------------
        # Validate Mesh Package Path
        # ------------------------------------------------

        if not new_mesh_package_path:

            messagebox.showwarning(
                "Missing Mesh Path",
                "PLEASE ENTER A PACKAGE PATH\n\n"
                "for: Mesh"
            )

            return

        # ------------------------------------------------
        # Build New Mesh Full Path
        # ------------------------------------------------

        new_mesh_full_path = (
            new_mesh_package_path.rstrip("/")
            + "/"
            + new_mesh_name
        )

        # ------------------------------------------------
        # Original Mesh Full Path
        # ------------------------------------------------

        old_mesh_full_path = mesh_full_path

        if not old_mesh_full_path and package_path and mesh_name:

            old_mesh_full_path = (
                package_path.rstrip("/")
                + "/"
                + mesh_name
            )

        # ------------------------------------------------
        # Wheel Mesh Information
        # ------------------------------------------------

        new_wheel_mesh_name = ""
        new_wheel_mesh_package_path = ""
        new_wheel_mesh_full_path = ""

        old_wheel_mesh_full_path = ""

        if wheel_mesh_name:

            new_wheel_mesh_name = (
                wheel_mesh_name_entry.get().strip()
            )

            new_wheel_mesh_package_path = (
                wheel_mesh_path_entry.get().strip()
            )

            # ------------------------------------------------
            # Validate Wheel Mesh Name
            # ------------------------------------------------

            if not new_wheel_mesh_name:

                messagebox.showwarning(
                    "Missing Wheel Mesh Name",
                    "PLEASE ENTER A WHEEL MESH NAME"
                )

                return

            # ------------------------------------------------
            # Validate Wheel Mesh Prefix
            # ------------------------------------------------

            if not (
                new_wheel_mesh_name.startswith("SM_")
                or
                new_wheel_mesh_name.startswith("SKR_")
            ):

                messagebox.showerror(
                    "Invalid Wheel Mesh Name",
                    f"Invalid wheel mesh name:\n\n"
                    f"{new_wheel_mesh_name}\n\n"
                    f"Wheel mesh names must start with "
                    f"\"SM_\" or \"SKR_\".\n\n"
                    f"Examples:\n"
                    f"SM_MyWheel\n"
                    f"SKR_MyWheel"
                )

                return

            # ------------------------------------------------
            # Validate Wheel Mesh Package Path
            # ------------------------------------------------

            if not new_wheel_mesh_package_path:

                messagebox.showwarning(
                    "Missing Wheel Mesh Path",
                    "PLEASE ENTER A PACKAGE PATH\n\n"
                    "for: Wheel Mesh"
                )

                return

            # ------------------------------------------------
            # Build New Wheel Mesh Full Path
            # ------------------------------------------------

            new_wheel_mesh_full_path = (
                new_wheel_mesh_package_path.rstrip("/")
                + "/"
                + new_wheel_mesh_name
            )

            # ------------------------------------------------
            # Original Wheel Mesh Full Path
            # ------------------------------------------------

            if wheel_mesh_path and wheel_mesh_name:

                old_wheel_mesh_full_path = (
                    wheel_mesh_path.rstrip("/")
                    + "/"
                    + wheel_mesh_name
                )

        # ------------------------------------------------
        # Get Material Information
        # ------------------------------------------------

        material_changes = []

        for material_index, material in enumerate(
            material_references,
            start=1
        ):

            new_material_name = (
                material_name_entries[
                    material_index - 1
                ].get().strip()
            )

            new_material_package_path = (
                material_path_entries[
                    material_index - 1
                ].get().strip()
            )

            old_material_name = material.get(
                "name",
                ""
            )

            old_material_package_path = material.get(
                "path",
                ""
            )

            # ------------------------------------------------
            # Validate Material Name
            # ------------------------------------------------

            if not new_material_name:

                messagebox.showwarning(
                    "Missing Material Name",
                    f"PLEASE ENTER A MATERIAL NAME\n\n"
                    f"for: Material {material_index}"
                )

                return

            # ------------------------------------------------
            # Validate Material Prefix
            # ------------------------------------------------

            if not new_material_name.startswith(
                "MI_"
            ):

                messagebox.showerror(
                    "Invalid Material Name",
                    f"Invalid material name:\n\n"
                    f"{new_material_name}\n\n"
                    f"Material names must start with \"MI_\".\n\n"
                    f"Example:\n"
                    f"MI_MyMaterial"
                )

                return

            # ------------------------------------------------
            # Validate Material Package Path
            # ------------------------------------------------

            if not new_material_package_path:

                messagebox.showwarning(
                    "Missing Material Path",
                    f"PLEASE ENTER A PACKAGE PATH\n\n"
                    f"for: Material {material_index}"
                )

                return

            # ------------------------------------------------
            # Build Full Material Paths
            # ------------------------------------------------

            old_material_full_path = ""

            if (
                old_material_package_path
                and
                old_material_name
            ):

                old_material_full_path = (
                    old_material_package_path.rstrip("/")
                    + "/"
                    + old_material_name
                )

            new_material_full_path = (
                new_material_package_path.rstrip("/")
                + "/"
                + new_material_name
            )

            material_changes.append(
                {
                    "old_name": old_material_name,
                    "new_name": new_material_name,
                    "old_path": old_material_full_path,
                    "new_path": new_material_full_path,
                    "import_index": material.get(
                        "import_index"
                    ),
                    "package_import_index": material.get(
                        "package_import_index"
                    )
                }
            )

        # ------------------------------------------------
        # Output Folder
        # ------------------------------------------------

        output_folder = (
            output_folder_var.get().strip()
        )

        if not output_folder:

            output_folder = DEFAULT_OUTPUT_FOLDER

        save_output_folder(
            output_folder
        )

        # ------------------------------------------------
        # Determine Output Folder
        # ------------------------------------------------

        mesh_output_folder = output_folder

        if include_game_structure_var.get():

            game_path = new_mesh_full_path.strip()

            if game_path.startswith(
                "/Game/"
            ):

                relative_game_path = game_path[
                    len("/Game/"):
                ]

                relative_game_directory = os.path.dirname(
                    relative_game_path
                )

                mesh_output_folder = os.path.join(
                    output_folder,
                    "Gameface",
                    "Content",
                    relative_game_directory
                )

        # ------------------------------------------------
        # Create Output Folder
        # ------------------------------------------------

        try:

            os.makedirs(
                mesh_output_folder,
                exist_ok=True
            )

        except Exception as e:

            messagebox.showerror(
                "Output Folder Error",
                f"Could not create/access the output folder:\n\n"
                f"{mesh_output_folder}\n\n"
                f"{e}"
            )

            return

        # ------------------------------------------------
        # Create Independent JSON Copy
        # ------------------------------------------------

        edited_data = copy.deepcopy(
            parsed_data
        )

        # ------------------------------------------------
        # Build Replacement Pairs
        # ------------------------------------------------

        replacement_pairs = []

        # ------------------------------------------------
        # Mesh Name
        # ------------------------------------------------

        if mesh_name != new_mesh_name:

            replacement_pairs.append(
                (
                    mesh_name,
                    new_mesh_name
                )
            )

        # ------------------------------------------------
        # Mesh Full Path
        # ------------------------------------------------

        if old_mesh_full_path:

            replacement_pairs.append(
                (
                    old_mesh_full_path,
                    new_mesh_full_path
                )
            )

        # ------------------------------------------------
        # Wheel Mesh Name
        # ------------------------------------------------

        if (
            wheel_mesh_name
            and
            new_wheel_mesh_name
            and
            wheel_mesh_name != new_wheel_mesh_name
        ):

            replacement_pairs.append(
                (
                    wheel_mesh_name,
                    new_wheel_mesh_name
                )
            )

        # ------------------------------------------------
        # Wheel Mesh Full Path
        # ------------------------------------------------

        if (
            old_wheel_mesh_full_path
            and
            new_wheel_mesh_full_path
        ):

            replacement_pairs.append(
                (
                    old_wheel_mesh_full_path,
                    new_wheel_mesh_full_path
                )
            )

        # ------------------------------------------------
        # Update Actual Material Imports
        # ------------------------------------------------

        for material_change in material_changes:

            new_name = material_change[
                "new_name"
            ]

            new_path = material_change[
                "new_path"
            ]

            import_index = material_change.get(
                "import_index"
            )

            package_import_index = material_change.get(
                "package_import_index"
            )

            # ------------------------------------------------
            # Add Material Name Replacement Reference
            # ------------------------------------------------

            old_name = material_change.get(
                "old_name",
                ""
            )

            if (
                old_name
                and
                new_name
                and
                old_name != new_name
            ):

                replacement_pairs.append(
                    (
                        old_name,
                        new_name
                    )
                )

            # ------------------------------------------------
            # Update MaterialInstanceConstant Import
            # ------------------------------------------------

            if (
                isinstance(
                    import_index,
                    int
                )
                and
                0 <= import_index < len(
                    edited_data.get(
                        "Imports",
                        []
                    )
                )
            ):

                material_import = edited_data[
                    "Imports"
                ][
                    import_index
                ]

                if isinstance(
                    material_import,
                    dict
                ):

                    material_import[
                        "ObjectName"
                    ] = new_name

            # ------------------------------------------------
            # Update Package Import
            # ------------------------------------------------

            if (
                isinstance(
                    package_import_index,
                    int
                )
                and
                0 <= package_import_index < len(
                    edited_data.get(
                        "Imports",
                        []
                    )
                )
            ):

                package_import = edited_data[
                    "Imports"
                ][
                    package_import_index
                ]

                if isinstance(
                    package_import,
                    dict
                ):

                    package_import[
                        "ObjectName"
                    ] = new_path

        # ------------------------------------------------
        # Remove Duplicate Replacement Pairs
        # ------------------------------------------------

        unique_replacement_pairs = []

        for pair in replacement_pairs:

            if pair not in unique_replacement_pairs:

                unique_replacement_pairs.append(
                    pair
                )

        replacement_pairs = (
            unique_replacement_pairs
        )

        # ------------------------------------------------
        # Replace References Throughout JSON
        # ------------------------------------------------

        def replace_references(
            value
        ):

            if isinstance(
                value,
                str
            ):

                for (
                    old_value,
                    new_value
                ) in replacement_pairs:

                    if value == old_value:

                        return new_value

                return value

            if isinstance(
                value,
                list
            ):

                return [
                    replace_references(
                        item
                    )
                    for item in value
                ]

            if isinstance(
                value,
                dict
            ):

                return {
                    key: replace_references(
                        item
                    )
                    for key, item in value.items()
                }

            return value

        edited_data = replace_references(
            edited_data
        )

        # ------------------------------------------------
        # Update Mesh NameMap Path
        # ------------------------------------------------

        if old_mesh_full_path:

            for index, name in enumerate(
                edited_data.get(
                    "NameMap",
                    []
                )
            ):

                if not isinstance(
                    name,
                    str
                ):

                    continue

                if name == old_mesh_full_path:

                    edited_data[
                        "NameMap"
                    ][index] = (
                        new_mesh_full_path
                    )

        # ------------------------------------------------
        # Update Material NameMap Entries
        # ------------------------------------------------

        name_map = edited_data.setdefault(
            "NameMap",
            []
        )

        original_name_map = parsed_data.get(
            "NameMap",
            []
        )

        for material_change in material_changes:

            old_material_name = material_change[
                "old_name"
            ]

            new_material_name = material_change[
                "new_name"
            ]

            old_material_path = material_change[
                "old_path"
            ]

            new_material_path = material_change[
                "new_path"
            ]

            # ------------------------------------------------
            # Material Name
            # ------------------------------------------------

            name_found = False

            for index, name in enumerate(
                name_map
            ):

                if name == old_material_name:

                    name_map[index] = (
                        new_material_name
                    )

                    name_found = True

            if (
                not name_found
                and
                new_material_name
                and
                new_material_name not in name_map
            ):

                name_map.append(
                    new_material_name
                )

            # ------------------------------------------------
            # Material Path
            # ------------------------------------------------

            path_found = False

            for index, name in enumerate(
                name_map
            ):

                if name == old_material_path:

                    name_map[index] = (
                        new_material_path
                    )

                    path_found = True

            if (
                not path_found
                and
                new_material_path
                and
                new_material_path not in name_map
            ):

                name_map.append(
                    new_material_path
                )

        # ------------------------------------------------
        # Output JSON Filename
        # ------------------------------------------------

        output_json_path = os.path.join(
            mesh_output_folder,
            new_mesh_name + ".json"
        )

        output_uasset_path = os.path.join(
            mesh_output_folder,
            new_mesh_name + ".uasset"
        )

        # ------------------------------------------------
        # Save Edited JSON
        # ------------------------------------------------

        try:

            with open(
                output_json_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    edited_data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"[LOG] Created temporary mesh JSON: "
                f"{output_json_path}"
            )

        except Exception as e:

            messagebox.showerror(
                "Mesh Save Error",
                f"Could not create the temporary JSON:\n\n"
                f"{e}"
            )

            return

        # ------------------------------------------------
        # Check UAssetGUI
        # ------------------------------------------------

        if not os.path.exists(
            UASSETGUI_PATH
        ):

            try:

                if os.path.exists(
                    output_json_path
                ):

                    os.remove(
                        output_json_path
                    )

            except Exception:
                pass

            messagebox.showerror(
                "UAssetGUI Not Found",
                f"Could not find UAssetGUI.exe here:\n\n"
                f"{UASSETGUI_PATH}"
            )

            return

        # ------------------------------------------------
        # Convert JSON To UAsset
        # ------------------------------------------------

        try:

            result = subprocess.run(
                [
                    UASSETGUI_PATH,
                    "fromjson",
                    output_json_path,
                    output_uasset_path
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except Exception as e:

            # --------------------------------------------
            # Remove Temporary JSON After Failure
            # --------------------------------------------

            if os.path.exists(
                output_json_path
            ):

                try:

                    os.remove(
                        output_json_path
                    )

                except Exception:
                    pass

            messagebox.showerror(
                "UAssetGUI Error",
                f"Could not run UAssetGUI.\n\n"
                f"{e}"
            )

            return

        # ------------------------------------------------
        # Check Conversion Result
        # ------------------------------------------------

        if (
            result.returncode != 0
            or
            not os.path.exists(
                output_uasset_path
            )
        ):

            error_text = (
                result.stderr.strip()
                or
                result.stdout.strip()
                or
                "Unknown UAssetGUI error."
            )

            # --------------------------------------------
            # Remove Temporary JSON After Failure
            # --------------------------------------------

            if os.path.exists(
                output_json_path
            ):

                try:

                    os.remove(
                        output_json_path
                    )

                except Exception:
                    pass

            messagebox.showerror(
                "Mesh Conversion Failed",
                f"UAssetGUI could not create:\n\n"
                f"{new_mesh_name}.uasset\n\n"
                f"{error_text}"
            )

            print(
                f"[ERROR] UAssetGUI conversion failed for "
                f"{new_mesh_name}"
            )

            return

        # ------------------------------------------------
        # Conversion Successful - Remove JSON
        # ------------------------------------------------

        try:

            if os.path.exists(
                output_json_path
            ):

                os.remove(
                    output_json_path
                )

                print(
                    f"[LOG] Removed temporary mesh JSON: "
                    f"{output_json_path}"
                )

        except Exception as e:

            print(
                f"[WARNING] Could not remove temporary JSON: "
                f"{output_json_path} - {e}"
            )

        # ------------------------------------------------
        # Success
        # ------------------------------------------------

        messagebox.showinfo(
            "Mesh Saved",
            f"Mesh saved successfully.\n\n"
            f"{new_mesh_name}.uasset\n"
            f"{new_mesh_name}.uexp\n\n"
            f"Saved to:\n"
            f"{mesh_output_folder}"
        )

        print(
            f"[LOG] Saved edited mesh: "
            f"{output_uasset_path}"
        )

        close_editor()

    # ----------------------------------------------------
    # Save Button
    # ----------------------------------------------------

    save_button = ttk.Button(
        editor_window,
        text="Save Mesh",
        width=30,
        command=save_mesh,
        style="Main.TButton"
    )

    save_button.pack(
        pady=(35, 15),
        ipady=10
    )

    # ----------------------------------------------------
    # Hand Cursor
    # ----------------------------------------------------

    save_button.bind(
        "<Enter>",
        lambda event: event.widget.configure(
            cursor="hand2"
        )
    )

    save_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(
            cursor=""
        )
    )

    # ----------------------------------------------------
    # Cleanup
    # ----------------------------------------------------

    def close_editor():

        try:

            editor_window.unbind_all(
                "<MouseWheel>"
            )

            editor_window.update_idletasks()

            position_x = editor_window.winfo_x()
            position_y = editor_window.winfo_y()

            os.makedirs(
                os.path.dirname(
                    MESH_EDITOR_POSITION_PATH
                ),
                exist_ok=True
            )

            with open(
                MESH_EDITOR_POSITION_PATH,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    f"{position_x},{position_y}"
                )

        except Exception:
            pass

        if temporary_json and os.path.exists(
            json_path
        ):

            try:

                os.remove(
                    json_path
                )

            except Exception:
                pass

        editor_window.destroy()

    editor_window.protocol(
        "WM_DELETE_WINDOW",
        close_editor
    )

    editor_window.update_idletasks()
    editor_window.deiconify()

# --------------------------------------------------------
# Material Editor
# --------------------------------------------------------

def material_editor():

    # ----------------------------------------------------
    # Select source file first
    # ----------------------------------------------------

    source_path = filedialog.askopenfilename(
        title="Open Material",
        filetypes=[
            ("Material Files (UAsset & JSON)", "*.uasset *.json"),
            ("UAsset Files", "*.uasset"),
            ("JSON Files", "*.json")
        ]
    )

    if not source_path:
        return

    # ----------------------------------------------------
    # Validate Material File Name
    # ----------------------------------------------------

    source_filename = os.path.basename(
        source_path
    )

    source_name = os.path.splitext(
        source_filename
    )[0]

    if not (
        source_name.startswith("MI_")
        or
        source_name.startswith("M_")
    ):

        messagebox.showerror(
            "Invalid Material",
            (
                "The Material Editor can only open "
                "material files.\n\n"
                f"Selected file:\n"
                f"{source_filename}\n\n"
                "Material names must start with:\n"
                "MI_ or M_\n\n"
                "Examples:\n"
                "MI_MyMaterial\n"
                "M_MyMaterial"
            )
        )

        return

    source_extension = os.path.splitext(source_path)[1].lower()

    temporary_json = False

    # ----------------------------------------------------
    # Load / create JSON
    # ----------------------------------------------------

    if source_extension == ".uasset":

        if not os.path.exists(UASSETGUI_PATH):
            messagebox.showerror(
                "UAssetGUI Not Found",
                f"Could not find UAssetGUI.exe here:\n\n"
                f"{UASSETGUI_PATH}"
            )
            return

        output_folder = load_output_folder()

        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror(
                "Output Folder Error",
                f"Could not create the output folder:\n\n{e}"
            )
            return

        json_filename = os.path.splitext(
            os.path.basename(source_path)
        )[0] + ".json"

        json_path = os.path.join(
            output_folder,
            json_filename
        )

        try:

            result = subprocess.run(
                [
                    UASSETGUI_PATH,
                    "tojson",
                    source_path,
                    json_path,
                    "VER_UE4_26"
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except Exception as e:

            messagebox.showerror(
                "UAssetGUI Error",
                f"Could not run UAssetGUI:\n\n{e}"
            )
            return

        if result.returncode != 0 or not os.path.exists(json_path):
            error_text = result.stderr.strip()
            if not error_text:
                error_text = result.stdout.strip()
            messagebox.showerror(
                "JSON Conversion Failed",
                "UAssetGUI could not convert the UAsset to JSON.\n\n"
                f"{error_text}"
            )
            return

        # Mark the generated JSON as temporary so it is
        # automatically deleted if the editor is closed
        # without saving.
        temporary_json = True

    elif source_extension == ".json":

        output_folder = load_output_folder()

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ------------------------------------------------
        # Create a working copy of the JSON
        # ------------------------------------------------

        original_json_path = source_path

        original_json_name = os.path.basename(
            source_path
        )

        json_path = os.path.join(
            output_folder,
            original_json_name
        )

        try:

            shutil.copy2(
                original_json_path,
                json_path
            )

        except Exception as e:

            messagebox.showerror(
                "JSON Copy Error",
                f"Could not create a working copy of the JSON:\n\n{e}"
            )
            return

        temporary_json = True

    else:

        messagebox.showerror(
            "Invalid File",
            "Please select either a .uasset or .json file."
        )
        return

    # ----------------------------------------------------
    # Read JSON
    # ----------------------------------------------------

    try:

        with open(
            json_path,
            "r",
            encoding="utf-8"
        ) as f:

            material_data = json.load(f)

    except Exception as e:

        messagebox.showerror(
            "JSON Error",
            f"Could not read the JSON file:\n\n{e}"
        )
        return

    # ----------------------------------------------------
    # Extract material information
    # ----------------------------------------------------

    material_name = ""
    material_path = ""

    base_name = ""
    base_path = ""

    normal_name = ""
    normal_path = ""

    packed_name = ""
    packed_path = ""

    # ----------------------------------------------------
    # Material name
    # ----------------------------------------------------

    exports = material_data.get("Exports", [])

    for export in exports:

        if not export.get(
            "bIsAsset",
            False
        ):

            continue

        object_name = export.get(
            "ObjectName",
            ""
        )

        if object_name:

            material_name = object_name

            if isinstance(
                material_name,
                str
            ):

                material_name = material_name.split(
                    "'"
                )[0]

            break

    # ----------------------------------------------------
    # Find material path from NameMap
    # ----------------------------------------------------

    name_map = material_data.get("NameMap", [])

    if material_name:

        for name in name_map:

            if not isinstance(name, str):
                continue

            if name.endswith("/" + material_name):
                material_path = name.rsplit("/", 1)[0] + "/"
                break

    # ----------------------------------------------------
    # Find texture references
    # ----------------------------------------------------

    texture_imports = []

    for import_entry in material_data.get("Imports", []):

        object_name = import_entry.get("ObjectName", "")
        class_name = import_entry.get("ClassName", "")

        if class_name != "Texture2D":
            continue

        if not object_name:
            continue

        if not object_name.startswith("T_"):
            continue

        texture_imports.append(
            object_name
        )

    # ----------------------------------------------------
    # Find full texture paths from NameMap
    # ----------------------------------------------------

    texture_paths = {}

    for name in material_data.get("NameMap", []):

        if not isinstance(name, str):
            continue

        if not name.startswith("/Game/"):
            continue

        for texture_name in texture_imports:

            if name.endswith("/" + texture_name):
                texture_paths[texture_name] = (
                    name.rsplit("/", 1)[0] + "/"
                )

    # ----------------------------------------------------
    # Identify textures by suffix
    # ----------------------------------------------------

    base_name = ""
    base_path = ""

    normal_name = ""
    normal_path = ""

    packed_name = ""
    packed_path = ""

    metallic_name = ""
    metallic_path = ""

    roughness_name = ""
    roughness_path = ""

    emissive_name = ""
    emissive_path = ""

    for texture_name in texture_imports:

        texture_upper = texture_name.upper()

        if texture_upper.endswith("_BC"):

            base_name = texture_name
            base_path = texture_paths.get(
                texture_name,
                ""
            )

        elif texture_upper.endswith("_N"):

            normal_name = texture_name
            normal_path = texture_paths.get(
                texture_name,
                ""
            )

        elif texture_upper.endswith("_P"):

            packed_name = texture_name
            packed_path = texture_paths.get(
                texture_name,
                ""
            )

        elif texture_upper.endswith("_MT"):

            metallic_name = texture_name
            metallic_path = texture_paths.get(
                texture_name,
                ""
            )

        elif texture_upper.endswith("_R"):

            roughness_name = texture_name
            roughness_path = texture_paths.get(
                texture_name,
                ""
            )

        elif texture_upper.endswith("_E"):

            emissive_name = texture_name
            emissive_path = texture_paths.get(
                texture_name,
                ""
            )

    # ----------------------------------------------------
    # Rebuild original full texture paths
    # ----------------------------------------------------

    old_base_full_path = ""

    if base_path and base_name:
        old_base_full_path = (
            base_path.rstrip("/")
            + "/"
            + base_name
        )

    old_normal_full_path = ""

    if normal_path and normal_name:
        old_normal_full_path = (
            normal_path.rstrip("/")
            + "/"
            + normal_name
        )

    old_packed_full_path = ""

    if packed_path and packed_name:
        old_packed_full_path = (
            packed_path.rstrip("/")
            + "/"
            + packed_name
        )

    old_metallic_full_path = ""

    if metallic_path and metallic_name:
        old_metallic_full_path = (
            metallic_path.rstrip("/")
            + "/"
            + metallic_name
        )

    old_roughness_full_path = ""

    if roughness_path and roughness_name:
        old_roughness_full_path = (
            roughness_path.rstrip("/")
            + "/"
            + roughness_name
        )

    old_emissive_full_path = ""

    if emissive_path and emissive_name:
        old_emissive_full_path = (
            emissive_path.rstrip("/")
            + "/"
            + emissive_name
        )

    # ----------------------------------------------------
    # Material Editor Window
    # ----------------------------------------------------

    editor_window = tk.Toplevel(root)

    editor_window.withdraw()
    editor_window.transient(root)
    editor_window.overrideredirect(True)

    editor_window.title("Material Editor")
    editor_window.geometry("600x700")
    editor_window.resizable(False, False)
    editor_window.configure(bg="#1e1e1e")

    load_child_window_position(
        editor_window,
        EDITOR_POSITION_FILE
    )

    if os.path.exists(ICON_PATH):
        editor_window.iconbitmap(ICON_PATH)

    # ----------------------------------------------------
    # Output Folder
    # ----------------------------------------------------

    output_folder_var = tk.StringVar(
        value=load_output_folder()
    )

    include_game_structure_var = tk.BooleanVar(
        value=False
    )

    output_frame = ttk.Frame(editor_window)
    output_frame.pack(
        fill="x",
        padx=20,
        pady=(20, 10)
    )

    output_label = ttk.Label(
        output_frame,
        text="Output Folder"
    )
    output_label.pack(anchor="w")

    output_entry_frame = ttk.Frame(output_frame)
    output_entry_frame.pack(
        fill="x",
        pady=(3, 0)
    )

    output_entry = ttk.Entry(
        output_entry_frame,
        textvariable=output_folder_var
    )
    output_entry.pack(
        side="left",
        fill="x",
        expand=True
    )

    def browse_output_folder():

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:

            output_folder_var.set(folder)
            save_output_folder(folder)

    browse_button = ttk.Button(
        output_entry_frame,
        text="Browse",
        command=browse_output_folder
    )
    browse_button.pack(
        side="left",
        padx=(8, 0)
    )

    browse_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    browse_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(cursor="")
    )

    # ----------------------------------------------------
    # Game Folder Structure
    # ----------------------------------------------------

    game_structure_check = ttk.Checkbutton(
        output_frame,
        text="Include game folder structure",
        variable=include_game_structure_var
    )

    game_structure_check.pack(
        anchor="w",
        pady=(6, 0)
    )

    # ----------------------------------------------------
    # Title
    # ----------------------------------------------------

    title_label = ttk.Label(
        editor_window,
        text="Material Editor",
        font=PRICEDOWN_FONT
    )
    title_label.pack(
        pady=(5, 15)
    )

    # ========================================================
    # Material Information
    # ========================================================

    material_frame = ttk.LabelFrame(
        editor_window,
        text="Material"
    )

    material_frame.pack(
        fill="x",
        padx=20,
        pady=(5, 10)
    )

    material_frame.columnconfigure(
        1,
        weight=1
    )

    # --------------------------------------------------------
    # Material Name
    # --------------------------------------------------------

    material_name_label = ttk.Label(
        material_frame,
        text="Material Name:"
    )

    material_name_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    material_name_entry = ttk.Entry(
        material_frame,
        state=(
            "normal"
            if material_name and material_path
            else "disabled"
        )
    )

    if material_name:

        material_name_entry.insert(
            0,
            material_name
        )

    material_name_entry.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    # --------------------------------------------------------
    # Material Package Path
    # --------------------------------------------------------

    material_path_label = ttk.Label(
        material_frame,
        text="Package Path:"
    )

    material_path_label.grid(
        row=1,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    material_path_entry = ttk.Entry(
        material_frame,
        state=(
            "normal"
            if material_name and material_path
            else "disabled"
        )
    )

    if material_path:

        material_path_entry.insert(
            0,
            material_path
        )

    material_path_entry.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    setup_entry_undo(
        material_name_entry
    )

    setup_entry_undo(
        material_path_entry
    )

    # ========================================================
    # Textures
    # ========================================================

    texture_outer_frame = ttk.LabelFrame(
        editor_window,
        text="Textures"
    )

    texture_outer_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    # --------------------------------------------------------
    # Scrollable Texture Area
    # --------------------------------------------------------

    texture_container = ttk.Frame(
        texture_outer_frame
    )

    texture_container.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    texture_canvas = tk.Canvas(
        texture_container,
        bg="#1e1e1e",
        highlightthickness=0
    )

    texture_scrollbar = ttk.Scrollbar(
        texture_container,
        orient="vertical",
        command=texture_canvas.yview
    )

    texture_frame = ttk.Frame(
        texture_canvas
    )

    texture_window = texture_canvas.create_window(
        (0, 0),
        window=texture_frame,
        anchor="nw"
    )

    texture_canvas.configure(
        yscrollcommand=texture_scrollbar.set
    )

    texture_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    texture_scrollbar.pack(
        side="right",
        fill="y"
    )

    def update_texture_scroll_region(
        event=None
    ):

        texture_canvas.configure(
            scrollregion=texture_canvas.bbox(
                "all"
            )
        )

    texture_frame.bind(
        "<Configure>",
        update_texture_scroll_region
    )

    def resize_texture_frame(
        event
    ):

        texture_canvas.itemconfigure(
            texture_window,
            width=event.width
        )

    texture_canvas.bind(
        "<Configure>",
        resize_texture_frame
    )

    # --------------------------------------------------------
    # Mouse Wheel
    # --------------------------------------------------------

    def on_texture_mousewheel(
        event
    ):

        texture_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    texture_canvas.bind(
        "<Enter>",
        lambda event: texture_canvas.bind_all(
            "<MouseWheel>",
            on_texture_mousewheel
        )
    )

    texture_canvas.bind(
        "<Leave>",
        lambda event: texture_canvas.unbind_all(
            "<MouseWheel>"
        )
    )

    # ========================================================
    # Helper for Creating Texture Boxes
    # ========================================================

    def create_texture_box(
        title,
        name_value,
        path_value
    ):

        texture_box = ttk.LabelFrame(
            texture_frame,
            text=title
        )

        texture_box.pack(
            fill="x",
            padx=5,
            pady=5
        )

        texture_box.columnconfigure(
            1,
            weight=1
        )

        if name_value and path_value:

            entry_state = "normal"

        else:

            entry_state = "disabled"

        # ----------------------------------------------------
        # Texture Name
        # ----------------------------------------------------

        name_label = ttk.Label(
            texture_box,
            text="Texture Name:"
        )

        name_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        name_entry = ttk.Entry(
            texture_box,
            state=entry_state
        )

        if name_value:

            name_entry.insert(
                0,
                name_value
            )

        name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=6
        )

        # ----------------------------------------------------
        # Package Path
        # ----------------------------------------------------

        path_label = ttk.Label(
            texture_box,
            text="Package Path:"
        )

        path_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=10,
            pady=6
        )

        path_entry = ttk.Entry(
            texture_box,
            state=entry_state
        )

        if path_value:

            path_entry.insert(
                0,
                path_value
            )

        path_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 10),
            pady=6
        )

        setup_entry_undo(
            name_entry
        )

        setup_entry_undo(
            path_entry
        )

        return (
            name_entry,
            path_entry
        )

    # ========================================================
    # Base Colour
    # ========================================================

    base_name_entry, base_path_entry = create_texture_box(
        "Base Color (_BC)",
        base_name,
        base_path
    )

    # ========================================================
    # Normal
    # ========================================================

    normal_name_entry, normal_path_entry = create_texture_box(
        "Normal (_N)",
        normal_name,
        normal_path
    )

    # ========================================================
    # Packed
    # ========================================================

    packed_name_entry, packed_path_entry = create_texture_box(
        "Packed (_P)",
        packed_name,
        packed_path
    )

    # ========================================================
    # Metallic
    # ========================================================

    metallic_name_entry, metallic_path_entry = create_texture_box(
        "Metallic (_MT)",
        metallic_name,
        metallic_path
    )

    # ========================================================
    # Roughness
    # ========================================================

    roughness_name_entry, roughness_path_entry = create_texture_box(
        "Roughness (_R)",
        roughness_name,
        roughness_path
    )

    # ========================================================
    # Emissive
    # ========================================================

    emissive_name_entry, emissive_path_entry = create_texture_box(
        "Emissive (_E)",
        emissive_name,
        emissive_path
    )
    
    # ----------------------------------------------------
    # Save Button
    # ----------------------------------------------------

    working_json_path = json_path

    def save_material():

        # ------------------------------------------------
        # Get values from the editor
        # ------------------------------------------------

        new_material_name = material_name_entry.get().strip()
        new_material_path = material_path_entry.get().strip()

        new_base_name = base_name_entry.get().strip()
        new_base_path = base_path_entry.get().strip()

        new_normal_name = normal_name_entry.get().strip()
        new_normal_path = normal_path_entry.get().strip()

        new_packed_name = packed_name_entry.get().strip()
        new_packed_path = packed_path_entry.get().strip()

        new_metallic_name = metallic_name_entry.get().strip()
        new_metallic_path = metallic_path_entry.get().strip()

        new_roughness_name = roughness_name_entry.get().strip()
        new_roughness_path = roughness_path_entry.get().strip()

        new_emissive_name = emissive_name_entry.get().strip()
        new_emissive_path = emissive_path_entry.get().strip()

        # ------------------------------------------------
        # Build full Unreal paths from Name + package Path
        # ------------------------------------------------

        if new_material_path:
            new_material_path = (
                new_material_path.rstrip("/")
                + "/"
                + new_material_name
            )

        if new_base_path and new_base_name:
            new_base_path = (
                new_base_path.rstrip("/")
                + "/"
                + new_base_name
            )

        if new_normal_path and new_normal_name:
            new_normal_path = (
                new_normal_path.rstrip("/")
                + "/"
                + new_normal_name
            )

        if new_packed_path and new_packed_name:
            new_packed_path = (
                new_packed_path.rstrip("/")
                + "/"
                + new_packed_name
            )

        if new_metallic_path and new_metallic_name:
            new_metallic_path = (
                new_metallic_path.rstrip("/")
                + "/"
                + new_metallic_name
            )

        if new_roughness_path and new_roughness_name:
            new_roughness_path = (
                new_roughness_path.rstrip("/")
                + "/"
                + new_roughness_name
            )

        if new_emissive_path and new_emissive_name:
            new_emissive_path = (
                new_emissive_path.rstrip("/")
                + "/"
                + new_emissive_name
            )


        # ------------------------------------------------
        # Basic validation
        # ------------------------------------------------

        if not new_material_name:
            messagebox.showerror(
                "Invalid Material",
                "Please enter a material name."
            )
            return

        if not new_material_name.startswith("MI_"):
            messagebox.showerror(
                "Invalid Material Name",
                "Material Name must start with \"MI_\".\n\n"
                "Example:\n"
                "MI_MyMaterial"
            )
            return

        if not new_material_path:
            messagebox.showerror(
                "Invalid Material Path",
                "Please enter a package path for the material.\n\n"
                "Example:\n"
                "/Game/ViceCity/Vehicles/"
            )
            return


        # ------------------------------------------------
        # Texture name validation
        # ------------------------------------------------

        texture_names = [
            ("Base", new_base_name, new_base_path),
            ("Normal", new_normal_name, new_normal_path),
            ("Packed", new_packed_name, new_packed_path),
            ("Metallic", new_metallic_name, new_metallic_path),
            ("Roughness", new_roughness_name, new_roughness_path),
            ("Emissive", new_emissive_name, new_emissive_path)
        ]

        for texture_type, texture_name, texture_path in texture_names:

            # ------------------------------------------------
            # Required texture suffix
            # ------------------------------------------------

            required_suffixes = {
                "Base": "_BC",
                "Normal": "_N",
                "Packed": "_P",
                "Metallic": "_MT",
                "Roughness": "_R",
                "Emissive": "_E"
            }

            required_suffix = required_suffixes.get(texture_type)

            # ------------------------------------------------
        # Texture name validation
        # ------------------------------------------------

        texture_names = [
            ("Base", new_base_name, new_base_path),
            ("Normal", new_normal_name, new_normal_path),
            ("Packed", new_packed_name, new_packed_path),
            ("Metallic", new_metallic_name, new_metallic_path),
            ("Roughness", new_roughness_name, new_roughness_path),
            ("Emissive", new_emissive_name, new_emissive_path)
        ]

        for texture_type, texture_name, texture_path in texture_names:

            # ------------------------------------------------
            # Required texture suffix
            # ------------------------------------------------

            required_suffixes = {
                "Base": "_BC",
                "Normal": "_N",
                "Packed": "_P",
                "Metallic": "_MT",
                "Roughness": "_R",
                "Emissive": "_E"
            }

            required_suffix = required_suffixes.get(texture_type)

            # ------------------------------------------------
            # Texture does not exist in this material
            # ------------------------------------------------

            if not texture_name and not texture_path:
                continue

            # ------------------------------------------------
            # Texture name validation
            # ------------------------------------------------

            if not texture_name:

                messagebox.showwarning(
                    "Missing Texture Name",
                    f"PLEASE ENTER A {texture_type.upper()} TEXTURE\n\n"
                    f"for: {required_suffix.lstrip('_')} texture"
                )
                return

            if not texture_name.startswith("T_"):

                messagebox.showerror(
                    "Invalid Texture Name",
                    f"{texture_type} texture name must start with \"T_\".\n\n"
                    "Example:\n"
                    "T_MyTexture"
                )
                return

            if required_suffix and not texture_name.upper().endswith(
                required_suffix
            ):

                messagebox.showerror(
                    "Invalid Texture Suffix",
                    f"{texture_type} texture name must end with "
                    f"\"{required_suffix}\".\n\n"
                    f"Example:\n"
                    f"T_MyTexture{required_suffix}\n\n"
                    f"The {required_suffix} suffix cannot be removed or changed."
                )
                return

            # ------------------------------------------------
            # Texture path validation
            # ------------------------------------------------

            if not texture_path:

                messagebox.showwarning(
                    "Missing Texture Path",
                    f"PLEASE ENTER A PACKAGE PATH\n\n"
                    f"for: {required_suffix.lstrip('_')} texture"
                )
                return

            texture_path_name = (
                texture_path.rstrip("/").split("/")[-1]
            )

            if not texture_path_name.startswith("T_"):

                messagebox.showerror(
                    "Invalid Texture Path",
                    f"{texture_type} texture path must end with "
                    f"a texture name starting with \"T_\".\n\n"
                    "Example:\n"
                    "/Game/ViceCity/Textures/Vehicle/T_MyTexture"
                )
                return

            if required_suffix and not texture_path_name.upper().endswith(
                required_suffix
            ):

                messagebox.showerror(
                    "Invalid Texture Path Suffix",
                    f"{texture_type} texture path must end with "
                    f"\"{required_suffix}\".\n\n"
                    f"Example:\n"
                    f"/Game/ViceCity/Textures/Vehicle/T_MyTexture{required_suffix}\n\n"
                    f"The {required_suffix} suffix cannot be removed or changed."
                )
                return

        # ------------------------------------------------
        # Update Material NameMap
        # ------------------------------------------------

        old_material_name = material_name

        for index, name in enumerate(
            material_data.get("NameMap", [])
        ):

            if not isinstance(name, str):
                continue

            # --------------------------------------------
            # Material name
            # --------------------------------------------

            if name == old_material_name:

                material_data["NameMap"][index] = (
                    new_material_name
                )

            # --------------------------------------------
            # Full material path
            # --------------------------------------------

            elif old_material_name and name.endswith(
                "/" + old_material_name
            ):

                if new_material_path:

                    material_data["NameMap"][index] = (
                        new_material_path.rstrip("/")
                    )

        # ------------------------------------------------
        # Update Material ObjectName
        # ------------------------------------------------

        for export in material_data.get("Exports", []):

            if export.get("ObjectName") == old_material_name:

                export["ObjectName"] = new_material_name

        # ------------------------------------------------
        # Rebuild original full texture paths
        # ------------------------------------------------

        old_base_full_path = ""
        old_normal_full_path = ""
        old_packed_full_path = ""
        old_metallic_full_path = ""
        old_roughness_full_path = ""
        old_emissive_full_path = ""

        if base_path and base_name:
            old_base_full_path = (
                base_path.rstrip("/")
                + "/"
                + base_name
            )

        if normal_path and normal_name:
            old_normal_full_path = (
                normal_path.rstrip("/")
                + "/"
                + normal_name
            )

        if packed_path and packed_name:
            old_packed_full_path = (
                packed_path.rstrip("/")
                + "/"
                + packed_name
            )

        if metallic_path and metallic_name:
            old_metallic_full_path = (
                metallic_path.rstrip("/")
                + "/"
                + metallic_name
            )

        if roughness_path and roughness_name:
            old_roughness_full_path = (
                roughness_path.rstrip("/")
                + "/"
                + roughness_name
            )

        if emissive_path and emissive_name:
            old_emissive_full_path = (
                emissive_path.rstrip("/")
                + "/"
                + emissive_name
            )

        # ------------------------------------------------
        # Update texture names and paths
        # ------------------------------------------------

        texture_changes = [
            (
                base_name,
                new_base_name,
                old_base_full_path,
                new_base_path
            ),
            (
                normal_name,
                new_normal_name,
                old_normal_full_path,
                new_normal_path
            ),
            (
                packed_name,
                new_packed_name,
                old_packed_full_path,
                new_packed_path
            ),
            (
                metallic_name,
                new_metallic_name,
                old_metallic_full_path,
                new_metallic_path
            ),
            (
                roughness_name,
                new_roughness_name,
                old_roughness_full_path,
                new_roughness_path
            ),
            (
                emissive_name,
                new_emissive_name,
                old_emissive_full_path,
                new_emissive_path
            )
        ]


        # ------------------------------------------------
        # Replace texture references throughout JSON
        # ------------------------------------------------

        def replace_texture_references(value):

            if isinstance(value, str):

                for (
                    old_name,
                    new_name,
                    old_path,
                    new_path
                ) in texture_changes:

                    # Full Unreal texture path
                    if old_path and value == old_path:

                        return new_path.rstrip("/")

                    # Texture object name
                    if old_name and value == old_name:

                        return new_name

                return value


            if isinstance(value, list):

                return [
                    replace_texture_references(item)
                    for item in value
                ]


            if isinstance(value, dict):

                return {
                    key: replace_texture_references(item)
                    for key, item in value.items()
                }


            return value


        updated_material_data = replace_texture_references(
            material_data
        )

        material_data.clear()
        material_data.update(
            updated_material_data
        )

        # ------------------------------------------------
        # Set output JSON filename from Material Name
        # ------------------------------------------------

        output_folder = output_folder_var.get().strip()

        if not output_folder:
            output_folder = DEFAULT_OUTPUT_FOLDER

        material_output_folder = output_folder

        if include_game_structure_var.get():

            game_path = new_material_path.strip()

            if game_path.startswith("/Game/"):

                relative_game_path = game_path[
                    len("/Game/"):
                ]

                relative_game_directory = os.path.dirname(
                    relative_game_path
                )

                material_output_folder = os.path.join(
                    output_folder,
                    "Gameface",
                    "Content",
                    relative_game_directory
                )

        try:
            os.makedirs(
                material_output_folder,
                exist_ok=True
            )

        except Exception as e:
            messagebox.showerror(
                "Output Folder Error",
                f"Could not create/access the output folder:\n\n"
                f"{material_output_folder}\n\n"
                f"{e}"
            )
            return

        new_json_path = os.path.join(
            material_output_folder,
            new_material_name + ".json"
        )

        old_json_path = working_json_path

        # ------------------------------------------------
        # Save edited JSON
        # ------------------------------------------------

        try:

            with open(
                new_json_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    material_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            # --------------------------------------------
            # Remove the old working JSON
            # --------------------------------------------

            if old_json_path != new_json_path:

                if os.path.exists(old_json_path):

                    try:
                        os.remove(old_json_path)
                    except Exception:
                        pass

        except Exception as e:

            messagebox.showerror(
                "Save Error",
                f"Could not save the JSON file:\n\n{e}"
            )
            return
        
        if not os.path.exists(UASSETGUI_PATH):

            messagebox.showerror(
                "UAssetGUI Not Found",
                f"Could not find UAssetGUI.exe here:\n\n"
                f"{UASSETGUI_PATH}"
            )
            return

        # ------------------------------------------------
        # Convert JSON back to UAsset
        # ------------------------------------------------

        output_uasset_path = os.path.join(
            material_output_folder,
            new_material_name + ".uasset"
        )

        try:

            result = subprocess.run(
                [
                    UASSETGUI_PATH,
                    "fromjson",
                    new_json_path,
                    output_uasset_path
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                if os.path.exists(new_json_path):
                    try:
                        os.remove(new_json_path)
                    except Exception as e:
                        messagebox.showwarning(
                            "Warning",
                            f"Material was created, but the temporary JSON could not be removed:\n\n{e}"
                        )

        except Exception as e:

            messagebox.showerror(
                "UAssetGUI Error",
                f"Could not run UAssetGUI:\n\n{e}"
            )
            return

        # ------------------------------------------------
        # Check conversion result
        # ------------------------------------------------

        if result.returncode != 0:

            error_text = result.stderr.strip()

            if not error_text:
                error_text = result.stdout.strip()

            messagebox.showerror(
                "UAsset Creation Failed",
                "UAssetGUI could not create the UAsset.\n\n"
                f"{error_text}"
            )
            return

        # ------------------------------------------------
        # Successful save
        # ------------------------------------------------

        messagebox.showinfo(
            "Material Saved",
            "Material saved successfully."
        )

        editor_window.destroy()

    # ----------------------------------------------------
    # Save Button/material
    # ----------------------------------------------------

    save_button = ttk.Button(
        editor_window,
        text="Save Material",
        command=save_material,
        style="Main.TButton"
    )

    save_button.pack(
        side="bottom",
        pady=(10, 20),
        ipadx=20,
        ipady=8
    )

    save_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    save_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(cursor="")
    )

    # ----------------------------------------------------
    # Handle Window Close
    # ----------------------------------------------------

    def close_editor():

        if temporary_json and os.path.exists(
            json_path
        ):

            try:

                os.remove(
                    json_path
                )

            except Exception:

                pass

        save_child_window_position(
            editor_window,
            EDITOR_POSITION_FILE
        )

        editor_window.destroy()

    editor_window.protocol(
        "WM_DELETE_WINDOW",
        close_editor
    )

    editor_window.update_idletasks()

    editor_window.overrideredirect(False)

    editor_window.deiconify()
    editor_window.lift()
    editor_window.focus_force()

def game_material():

    template_root = os.path.join(
        get_script_directory(),
        "Files",
        ".MaterialCreation",
        ".TemplateMats"
    )

    if not os.path.exists(template_root):

        messagebox.showerror(
            "Template Folder Not Found",
            f"Could not find the material template folder:\n\n"
            f"{template_root}"
        )

        return

    game_window = tk.Toplevel(root)
    game_window.withdraw()

    icon_path = os.path.join(
        get_script_directory(),
        "Files",
        ".Resources",
        "ICON.ico"
    )

    if os.path.exists(icon_path):

        game_window.iconbitmap(
            icon_path
        )

    game_window.title(
        "Create Game Material"
    )

    game_window.geometry(
        "650x800"
    )

    load_child_window_position(
        game_window,
        GAME_POSITION_FILE
    )

    game_window.resizable(
        False,
        False
    )

    game_window.configure(
        bg="#1e1e1e"
    )

    # ========================================================
    # Variables
    # ========================================================

    selected_template_data = {
        "data": None,
        "path": None
    }

    texture_data_from_template = {}

    texture_entries = {}

    texture_entries = {}

    material_name_var = tk.StringVar()
    material_path_var = tk.StringVar()
    template_var = tk.StringVar()

    include_game_structure_var = tk.BooleanVar(
        value=False
    )

    material_preview_data = {
        "image": None
    }

    # ========================================================
    # Output Folder
    # ========================================================

    output_frame = ttk.Frame(
        game_window
    )

    output_frame.pack(
        fill="x",
        padx=20,
        pady=(15, 0)
    )

    output_label = ttk.Label(
        output_frame,
        text="Output Folder:"
    )

    output_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 10)
    )

    output_var = tk.StringVar(
        value=load_output_folder()
    )

    output_entry = ttk.Entry(
        output_frame,
        textvariable=output_var
    )

    output_entry.grid(
        row=0,
        column=1,
        sticky="ew"
    )

    def browse_output_folder():

        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )

        if folder:

            output_var.set(
                folder
            )

            save_output_folder(
                folder
            )

    browse_button = ttk.Button(
        output_frame,
        text="Browse",
        command=browse_output_folder
    )

    browse_button.grid(
        row=0,
        column=2,
        padx=(10, 0)
    )

    output_frame.columnconfigure(
        1,
        weight=1
    )

    output_entry.bind(
        "<FocusOut>",
        lambda event: save_output_folder(
            output_var.get()
        )
    )

    browse_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    browse_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(
            cursor=""
        )
    )

    # --------------------------------------------------------
    # Game Folder Structure
    # --------------------------------------------------------

    game_structure_check = ttk.Checkbutton(
        output_frame,
        text="Include game folder structure",
        variable=include_game_structure_var
    )

    game_structure_check.grid(
        row=1,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(6, 0)
    )    

    # ========================================================
    # Title
    # ========================================================

    title_label = ttk.Label(
        game_window,
        text="Create Game Material",
        font=PRICEDOWN_FONT
    )

    title_label.pack(
        pady=(20, 10)
    )

    description_label = ttk.Label(
        game_window,
        text="Select a material type to load it's template.",
        font=("Segoe Script", 12)
    )

    description_label.pack(
        pady=(0, 15)
    )

    # ========================================================
    # Template Selection
    # ========================================================

    template_frame = ttk.Frame(
        game_window
    )

    template_frame.pack(
        fill="x",
        padx=20
    )

    template_label = ttk.Label(
        template_frame,
        text="Material Type:"
    )

    template_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 10)
    )

    template_combo = ttk.Combobox(
        template_frame,
        textvariable=template_var,
        state="readonly",
        width=35
    )

    template_combo.grid(
        row=0,
        column=1,
        sticky="ew"
    )

    template_preview_label = ttk.Label(
        template_frame,
        anchor="center"
    )

    template_preview_label.grid(
        row=0,
        column=2,
        sticky="e",
        padx=(10, 0)
    )

    template_frame.columnconfigure(
        1,
        weight=1
    )

    # ========================================================
    # Material Information
    # ========================================================

    material_frame = ttk.LabelFrame(
        game_window,
        text="Material"
    )

    material_frame.pack(
        fill="x",
        padx=20,
        pady=(15, 10)
    )

    material_name_label = ttk.Label(
        material_frame,
        text="Material Name:"
    )

    material_name_label.grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    material_name_entry = ttk.Entry(
        material_frame,
        textvariable=material_name_var,
        width=55
    )

    material_name_entry.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    setup_entry_undo(
        material_name_entry
    )

    material_path_label = ttk.Label(
        material_frame,
        text="Package Path:"
    )

    material_path_label.grid(
        row=1,
        column=0,
        sticky="w",
        padx=10,
        pady=8
    )

    material_path_entry = ttk.Entry(
        material_frame,
        textvariable=material_path_var,
        width=55
    )

    material_path_entry.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(0, 10),
        pady=8
    )

    setup_entry_undo(
        material_path_entry
    )

    material_frame.columnconfigure(
        1,
        weight=1
    )

    # ========================================================
    # Texture Area
    # ========================================================

    texture_outer_frame = ttk.LabelFrame(
        game_window,
        text="Textures"
    )

    texture_outer_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(10, 0)
    )

    texture_canvas = tk.Canvas(
        texture_outer_frame,
        bg="#1e1e1e",
        highlightthickness=0
    )

    texture_scrollbar = ttk.Scrollbar(
        texture_outer_frame,
        orient="vertical",
        command=texture_canvas.yview
    )

    texture_frame = ttk.Frame(
        texture_canvas
    )

    texture_window = texture_canvas.create_window(
        (0, 0),
        window=texture_frame,
        anchor="nw"
    )

    texture_canvas.configure(
        yscrollcommand=texture_scrollbar.set
    )

    texture_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    texture_scrollbar.pack(
        side="right",
        fill="y"
    )

    def update_texture_scroll_region(event=None):

        texture_canvas.configure(
            scrollregion=texture_canvas.bbox("all")
        )

    texture_frame.bind(
        "<Configure>",
        update_texture_scroll_region
    )

    def resize_texture_frame(event):

        texture_canvas.itemconfigure(
            texture_window,
            width=event.width
        )

    texture_canvas.bind(
        "<Configure>",
        resize_texture_frame
    )

    # ========================================================
    # Mouse Wheel Scrolling
    # ========================================================

    def scroll_texture_canvas(event):

        try:

            # Only scroll when the mouse is inside
            # the Create Game Material window
            if event.widget.winfo_toplevel() != game_window:
                return

        except Exception:

            return

        texture_canvas.yview_scroll(
            int(
                -1 * (
                    event.delta / 120
                )
            ),
            "units"
        )

        return "break"

    # Allow mouse wheel scrolling anywhere
    # inside the Create Game Material window
    game_window.bind_all(
        "<MouseWheel>",
        scroll_texture_canvas,
        add="+"
    )

    # ========================================================
    # Texture Type Names
    # ========================================================

    texture_type_names = {
        "_BC": "Base Color (_BC)",
        "_N": "Normal (_N)",
        "_P": "Packed (_P)",
        "_MT": "Metallic (_MT)",
        "_R": "Roughness (_R)",
        "_E": "Emissive (_E)"
    }

    # ========================================================
    # Clear Texture Fields
    # ========================================================

    def clear_texture_fields():

        for widget in texture_frame.winfo_children():

            widget.destroy()

        texture_entries.clear()

    # ========================================================
    # Populate Texture Fields
    # ========================================================

    def populate_texture_fields(texture_data):

        clear_texture_fields()

        if not texture_data:

            no_texture_label = ttk.Label(
                texture_frame,
                text="No textures found in this material template."
            )

            no_texture_label.pack(
                pady=20
            )

            return

        row = 0

        for suffix in [
            "_BC",
            "_N",
            "_P",
            "_MT",
            "_R",
            "_E"
        ]:

            if suffix not in texture_data:
                continue

            texture_info = texture_data[suffix]

            name_var = tk.StringVar(
                value=texture_info.get(
                    "name",
                    ""
                )
            )

            path_var = tk.StringVar(
                value=texture_info.get(
                    "path",
                    ""
                )
            )

            type_frame = ttk.LabelFrame(
                texture_frame,
                text=texture_type_names[suffix]
            )

            type_frame.grid(
                row=row,
                column=0,
                sticky="ew",
                padx=5,
                pady=5
            )

            type_frame.columnconfigure(
                1,
                weight=1
            )

            name_label = ttk.Label(
                type_frame,
                text="Texture Name:"
            )

            name_label.grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=6
            )

            name_entry = ttk.Entry(
                type_frame,
                textvariable=name_var
            )

            name_entry.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=(0, 10),
                pady=6
            )

            path_label = ttk.Label(
                type_frame,
                text="Package Path:"
            )

            path_label.grid(
                row=1,
                column=0,
                sticky="w",
                padx=10,
                pady=6
            )

            path_entry = ttk.Entry(
                type_frame,
                textvariable=path_var
            )

            path_entry.grid(
                row=1,
                column=1,
                sticky="ew",
                padx=(0, 10),
                pady=6
            )

            texture_entries[suffix] = {
                "name_var": name_var,
                "path_var": path_var,
                "name_entry": name_entry,
                "path_entry": path_entry
            }

            setup_entry_undo(
                name_entry
            )

            setup_entry_undo(
                path_entry
            )

            row += 1

    # ========================================================
    # Material Preview
    # ========================================================

    material_preview_map = {
        "MI_Mirror": "MI_Mirror_VC",
        "MI_Chrome": "MI_Chrome",
        "MI_neo1Blue": "MI_neonblue",
        "MI_neo1Pink": "MI_neonpink",
        "MI_neo1": "MI_neonwhite",
        "MI_LanternLights_On_Itsm0ver": "MI_Lights_texture",
        "MI_dt_cops_US_new1": "MI_Wind"
    }

    material_preview_names = [
        "MI_Chrome",
        "MI_Lights_texture",
        "MI_Mirror_VC",
        "MI_neonblue",
        "MI_neonpink",
        "MI_neonwhite",
        "MI_Wind"
    ]

    def update_material_preview(material_name):

        resources_folder = os.path.join(
            get_script_directory(),
            "Files",
            ".Resources"
        )

        if not material_name:

            template_preview_label.configure(
                image=""
            )

            material_preview_data["image"] = None

            return

        preview_material_name = material_preview_map.get(
            material_name,
            material_name
        )

        material_name_normalized = (
            preview_material_name
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        preview_path = None

        # ----------------------------------------------------
        # Exact Match
        # ----------------------------------------------------

        for preview_name in material_preview_names:

            for extension in [
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".bmp"
            ]:

                possible_path = os.path.join(
                    resources_folder,
                    preview_name + extension
                )

                if (
                    os.path.exists(
                        possible_path
                    )
                    and
                    preview_name
                    .lower()
                    .replace("_", "")
                    .replace("-", "")
                    .replace(" ", "")
                    ==
                    material_name_normalized
                ):

                    preview_path = possible_path

                    break

            if preview_path:
                break

        # ----------------------------------------------------
        # Fuzzy Match
        # ----------------------------------------------------

        if not preview_path:

            best_match = None
            best_score = 0

            for preview_name in material_preview_names:

                preview_normalized = (
                    preview_name
                    .lower()
                    .replace("_", "")
                    .replace("-", "")
                    .replace(" ", "")
                )

                score = 0

                if (
                    preview_normalized
                    in material_name_normalized
                    or
                    material_name_normalized
                    in preview_normalized
                ):

                    score = min(
                        len(material_name_normalized),
                        len(preview_normalized)
                    )

                if score > best_score:

                    best_score = score
                    best_match = preview_name

            if best_match:

                for extension in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                    ".bmp"
                ]:

                    possible_path = os.path.join(
                        resources_folder,
                        best_match + extension
                    )

                    if os.path.exists(
                        possible_path
                    ):

                        preview_path = possible_path

                        break

        # ----------------------------------------------------
        # Display Preview
        # ----------------------------------------------------

        if preview_path:

            try:

                preview_image = Image.open(
                    preview_path
                )

                preview_image.thumbnail(
                    (200, 130),
                    Image.LANCZOS
                )

                preview_photo = ImageTk.PhotoImage(
                    preview_image
                )

                material_preview_data["image"] = (
                    preview_photo
                )

                template_preview_label.configure(
                    image=preview_photo
                )

            except Exception as e:

                print(
                    f"[WARNING] Could not load material preview: "
                    f"{preview_path} - {e}"
                )

                template_preview_label.configure(
                    image=""
                )

                material_preview_data["image"] = None

        else:

            template_preview_label.configure(
                image=""
            )

            material_preview_data["image"] = None

    # ========================================================
    # Read Template
    # ========================================================

    def load_template(event=None):

        selected_name = template_var.get()

        if not selected_name:

            return

        template_folder = os.path.join(
            template_root,
            selected_name
        )

        json_files = []

        for root_folder, directories, files in os.walk(
            template_folder
        ):

            for filename in files:

                if filename.lower().endswith(
                    ".json"
                ):

                    json_files.append(
                        os.path.join(
                            root_folder,
                            filename
                        )
                    )

        if not json_files:

            selected_template_data["data"] = None
            selected_template_data["path"] = None

            material_name_var.set("")
            material_path_var.set("")

            clear_texture_fields()

            messagebox.showwarning(
                "Template JSON Not Found",
                f"No JSON template was found in:\n\n"
                f"{template_folder}"
            )

            return

        json_files.sort()

        template_path = json_files[0]

        try:

            with open(
                template_path,
                "r",
                encoding="utf-8"
            ) as f:

                material_data = json.load(f)

        except Exception as e:

            messagebox.showerror(
                "Template Error",
                f"Could not read the material template:\n\n{e}"
            )

            return

        selected_template_data["data"] = material_data
        selected_template_data["path"] = template_path

        # ----------------------------------------------------
        # Material Name
        # ----------------------------------------------------

        material_name = ""

        exports = material_data.get(
            "Exports",
            []
        )

        for export in exports:

            if not export.get(
                "bIsAsset",
                False
            ):

                continue

            object_name = export.get(
                "ObjectName",
                ""
            )

            if object_name:

                material_name = object_name

                if isinstance(
                    material_name,
                    str
                ):

                    material_name = material_name.split(
                        "'"
                    )[0]

                break

        # ----------------------------------------------------
        # Material Path
        # ----------------------------------------------------

        material_path = ""

        name_map = material_data.get(
            "NameMap",
            []
        )

        if material_name:

            for name in name_map:

                if not isinstance(
                    name,
                    str
                ):

                    continue

                if name.endswith(
                    "/" + material_name
                ):

                    material_path = (
                        name.rsplit(
                            "/",
                            1
                        )[0]
                        + "/"
                    )

                    break

        material_name_var.set(
            material_name
        )

        material_path_var.set(
            material_path
        )

        update_material_preview(
            material_name
        )

        # ----------------------------------------------------
        # Find Texture Imports
        # ----------------------------------------------------

        texture_imports = []

        for import_entry in material_data.get(
            "Imports",
            []
        ):

            object_name = import_entry.get(
                "ObjectName",
                ""
            )

            class_name = import_entry.get(
                "ClassName",
                ""
            )

            if class_name != "Texture2D":

                continue

            if not object_name:

                continue

            if not object_name.startswith(
                "T_"
            ):

                continue

            texture_imports.append(
                object_name
            )

        # ----------------------------------------------------
        # Find Texture Paths
        # ----------------------------------------------------

        texture_paths = {}

        for name in name_map:

            if not isinstance(
                name,
                str
            ):

                continue

            if not name.startswith(
                "/Game/"
            ):

                continue

            for texture_name in texture_imports:

                if name.endswith(
                    "/" + texture_name
                ):

                    texture_paths[texture_name] = (
                        name.rsplit(
                            "/",
                            1
                        )[0]
                        + "/"
                    )

        # ----------------------------------------------------
        # Classify Textures
        # ----------------------------------------------------

        texture_data = {}

        texture_data_from_template.clear()

        for texture_name in texture_imports:

            texture_upper = texture_name.upper()

            suffix = None

            if texture_upper.endswith("_BC"):

                suffix = "_BC"

            elif texture_upper.endswith("_N"):

                suffix = "_N"

            elif texture_upper.endswith("_P"):

                suffix = "_P"

            elif texture_upper.endswith("_MT"):

                suffix = "_MT"

            elif texture_upper.endswith("_R"):

                suffix = "_R"

            elif texture_upper.endswith("_E"):

                suffix = "_E"

            if suffix is None:

                continue

            texture_data[suffix] = {
                "name": texture_name,
                "path": texture_paths.get(
                    texture_name,
                    ""
                )
            }

        populate_texture_fields(
            texture_data
        )

        texture_data_from_template.update(
            texture_data
        )

    # ========================================================
    # Find Available Material Templates
    # ========================================================

    template_names = []

    for item in sorted(
        os.listdir(template_root)
    ):

        item_path = os.path.join(
            template_root,
            item
        )

        if os.path.isdir(
            item_path
        ):

            template_names.append(
                item
            )

    template_combo["values"] = (
        template_names
    )

    template_combo.bind(
        "<<ComboboxSelected>>",
        load_template
    )

    # ========================================================
    # Initial Empty State
    # ========================================================

    material_name_var.set("")
    material_path_var.set("")

    empty_label = ttk.Label(
        texture_frame,
        text="Select a material type above to load its textures."
    )

    empty_label.pack(
        pady=20
    )

    # ========================================================
    # Create Material
    # ========================================================

    def create_game_material():

        # ----------------------------------------------------
        # Check that a template has been selected
        # ----------------------------------------------------

        template_data = selected_template_data.get(
            "data"
        )

        template_path = selected_template_data.get(
            "path"
        )

        if template_data is None or not template_path:

            messagebox.showwarning(
                "No Material Selected",
                "Please select a material type before creating a material."
            )

            return

        # ----------------------------------------------------
        # Get Material Information
        # ----------------------------------------------------

        new_material_name = (
            material_name_var.get()
            .strip()
        )

        new_material_package_path = (
            material_path_var.get()
            .strip()
        )

        # ----------------------------------------------------
        # Validate Material Name
        # ----------------------------------------------------

        if not new_material_name:

            messagebox.showwarning(
                "Missing Material Name",
                "PLEASE ENTER A MATERIAL NAME"
            )

            return

        if not new_material_name.startswith(
            "MI_"
        ):

            messagebox.showerror(
                "Invalid Material Name",
                f"Invalid material name:\n\n"
                f"{new_material_name}\n\n"
                f"Material names must start with \"MI_\".\n\n"
                f"Example:\n"
                f"MI_MyMaterial"
            )

            return

        # ----------------------------------------------------
        # Validate Material Package Path
        # ----------------------------------------------------

        if not new_material_package_path:

            messagebox.showwarning(
                "Missing Material Path",
                "PLEASE ENTER A PACKAGE PATH\n\n"
                "for: Material"
            )

            return

        # ----------------------------------------------------
        # Build New Material Full Path
        # ----------------------------------------------------

        new_material_full_path = (
            new_material_package_path.rstrip("/")
            + "/"
            + new_material_name
        )

        # ----------------------------------------------------
        # Find Original Material Name
        # ----------------------------------------------------

        old_material_name = ""

        for export in template_data.get(
            "Exports",
            []
        ):

            if not export.get(
                "bIsAsset",
                False
            ):

                continue

            object_name = export.get(
                "ObjectName",
                ""
            )

            if object_name:

                old_material_name = object_name

                if isinstance(
                    old_material_name,
                    str
                ):

                    old_material_name = (
                        old_material_name.split(
                            "'"
                        )[0]
                    )

                break

        if not old_material_name:

            messagebox.showerror(
                "Template Error",
                "Could not determine the material name from the selected template."
            )

            return

        # ----------------------------------------------------
        # Find Original Material Full Path
        # ----------------------------------------------------

        old_material_full_path = ""

        for name in template_data.get(
            "NameMap",
            []
        ):

            if not isinstance(
                name,
                str
            ):

                continue

            if name.endswith(
                "/" + old_material_name
            ):

                old_material_full_path = name

                break

        # ----------------------------------------------------
        # Build Texture Changes
        # ----------------------------------------------------

        texture_changes = []

        for suffix, entry_data in texture_entries.items():

            new_texture_name = (
                entry_data["name_var"].get()
                .strip()
            )

            new_texture_package_path = (
                entry_data["path_var"].get()
                .strip()
            )

            # ------------------------------------------------
            # Validate Texture Name
            # ------------------------------------------------

            texture_type = texture_type_names.get(
                suffix,
                suffix
            )

            if not new_texture_name:

                messagebox.showwarning(
                    "Missing Texture Name",
                    f"PLEASE ENTER A TEXTURE NAME\n\n"
                    f"for: {texture_type}"
                )

                return

            if not new_texture_name.startswith(
                "T_"
            ):

                messagebox.showerror(
                    "Invalid Texture Name",
                    f"Invalid texture name:\n\n"
                    f"{new_texture_name}\n\n"
                    f"Texture names must start with \"T_\".\n\n"
                    f"Example:\n"
                    f"T_MyTexture{suffix}"
                )

                return

            # ------------------------------------------------
            # Validate Texture Suffix
            # ------------------------------------------------

            if not new_texture_name.upper().endswith(
                suffix
            ):

                messagebox.showerror(
                    "Invalid Texture Suffix",
                    f"Invalid texture name:\n\n"
                    f"{new_texture_name}\n\n"
                    f"This texture must end with:\n"
                    f"{suffix}\n\n"
                    f"The {suffix} suffix cannot be removed or changed."
                )

                return

            # ------------------------------------------------
            # Validate Texture Package Path
            # ------------------------------------------------

            if not new_texture_package_path:

                messagebox.showwarning(
                    "Missing Texture Path",
                    f"PLEASE ENTER A PACKAGE PATH\n\n"
                    f"for: {texture_type}"
                )

                return

            # ------------------------------------------------
            # Original Texture Information
            # ------------------------------------------------

            original_texture_name = (
                texture_data_from_template.get(
                    suffix,
                    {}
                ).get(
                    "name",
                    ""
                )
            )

            original_texture_package_path = (
                texture_data_from_template.get(
                    suffix,
                    {}
                ).get(
                    "path",
                    ""
                )
            )

            if not original_texture_name:

                continue

            original_texture_full_path = (
                original_texture_package_path.rstrip("/")
                + "/"
                + original_texture_name
            )

            new_texture_full_path = (
                new_texture_package_path.rstrip("/")
                + "/"
                + new_texture_name
            )

            texture_changes.append({
                "old_name": original_texture_name,
                "new_name": new_texture_name,
                "old_path": original_texture_full_path,
                "new_path": new_texture_full_path
            })

        # ----------------------------------------------------
        # Output Folder
        # ----------------------------------------------------

        output_folder = (
            output_var.get()
            .strip()
        )

        if not output_folder:

            output_folder = DEFAULT_OUTPUT_FOLDER

        material_output_folder = output_folder

        # ----------------------------------------------------
        # Include Game Folder Structure
        # ----------------------------------------------------

        if include_game_structure_var.get():

            game_path = new_material_full_path.strip()

            if game_path.startswith("/Game/"):

                relative_game_path = game_path[
                    len("/Game/"):
                ]

                relative_game_directory = os.path.dirname(
                    relative_game_path
                )

                material_output_folder = os.path.join(
                    output_folder,
                    "Gameface",
                    "Content",
                    relative_game_directory
                )

            # ------------------------------------------------
            # Copy Template Gameface Files
            # ------------------------------------------------

            template_material_folder = os.path.dirname(
                template_path
            )

            while (
                os.path.basename(
                    template_material_folder
                ) != template_var.get()
                and template_material_folder != os.path.dirname(
                    template_material_folder
                )
            ):

                template_material_folder = os.path.dirname(
                    template_material_folder
                )

            template_gameface_folder = os.path.join(
                template_material_folder,
                "Gameface"
            )

            output_gameface_folder = os.path.join(
                output_folder,
                "Gameface"
            )

            if os.path.exists(
                template_gameface_folder
            ):

                try:

                    for root_folder, directories, files in os.walk(
                        template_gameface_folder
                    ):

                        relative_folder = os.path.relpath(
                            root_folder,
                            template_gameface_folder
                        )

                        if relative_folder == ".":
                            destination_folder = (
                                output_gameface_folder
                            )
                        else:
                            destination_folder = os.path.join(
                                output_gameface_folder,
                                relative_folder
                            )

                        os.makedirs(
                            destination_folder,
                            exist_ok=True
                        )

                        for filename in files:

                            source_file = os.path.join(
                                root_folder,
                                filename
                            )

                            # Do not copy the template JSON
                            if os.path.abspath(
                                source_file
                            ) == os.path.abspath(
                                template_path
                            ):
                                continue

                            destination_file = os.path.join(
                                destination_folder,
                                filename
                            )

                            shutil.copy2(
                                source_file,
                                destination_file
                            )

                except Exception as e:

                    messagebox.showerror(
                        "Game Structure Copy Error",
                        f"Could not copy the template game folder structure:\n\n"
                        f"{template_gameface_folder}\n\n"
                        f"{e}"
                    )

                    return

            else:

                print(
                    f"[WARNING] Template Gameface folder not found:\n"
                    f"{template_gameface_folder}"
                )

        try:

            os.makedirs(
                material_output_folder,
                exist_ok=True
            )

            save_output_folder(
                output_folder
            )

        except Exception as e:

            messagebox.showerror(
                "Output Folder Error",
                f"Could not create/access the output folder:\n\n"
                f"{material_output_folder}\n\n"
                f"{e}"
            )

            return

        # ----------------------------------------------------
        # Create Independent Template Copy
        # ----------------------------------------------------

        material_data = copy.deepcopy(
            template_data
        )

        # ----------------------------------------------------
        # Build All Replacement Pairs
        # ----------------------------------------------------

        replacement_pairs = []

        # Material name
        if old_material_name != new_material_name:

            replacement_pairs.append(
                (
                    old_material_name,
                    new_material_name
                )
            )

        # Textures
        for texture_change in texture_changes:

            old_name = texture_change[
                "old_name"
            ]

            new_name = texture_change[
                "new_name"
            ]

            old_path = texture_change[
                "old_path"
            ]

            new_path = texture_change[
                "new_path"
            ]

            if old_path:

                replacement_pairs.append(
                    (
                        old_path,
                        new_path
                    )
                )

            if old_name:

                replacement_pairs.append(
                    (
                        old_name,
                        new_name
                    )
                )

        # ----------------------------------------------------
        # Replace References Throughout JSON
        # ----------------------------------------------------

        def replace_references(value):

            if isinstance(
                value,
                str
            ):

                for (
                    old_value,
                    new_value
                ) in replacement_pairs:

                    if value == old_value:
                        return new_value

                return value

            if isinstance(
                value,
                list
            ):

                return [
                    replace_references(item)
                    for item in value
                ]

            if isinstance(
                value,
                dict
            ):

                return {
                    key: replace_references(item)
                    for key, item in value.items()
                }

            return value

        material_data = replace_references(
            material_data
        )

        # ----------------------------------------------------
        # Update Material Path In NameMap
        # ----------------------------------------------------

        if old_material_full_path:

            for index, name in enumerate(
                material_data.get(
                    "NameMap",
                    []
                )
            ):

                if not isinstance(
                    name,
                    str
                ):
                    continue

                if name == old_material_full_path:

                    material_data["NameMap"][index] = (
                        new_material_full_path
                    )

        # ----------------------------------------------------
        # Save JSON
        # ----------------------------------------------------

        output_json_path = os.path.join(
            material_output_folder,
            new_material_name + ".json"
        )

        try:

            with open(
                output_json_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    material_data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception as e:

            messagebox.showerror(
                "Creation Error",
                f"Could not create the temporary JSON:\n\n"
                f"{e}"
            )

            return

        # ----------------------------------------------------
        # Check UAssetGUI
        # ----------------------------------------------------

        if not os.path.exists(
            UASSETGUI_PATH
        ):

            messagebox.showerror(
                "UAssetGUI Not Found",
                f"Could not find UAssetGUI.exe here:\n\n"
                f"{UASSETGUI_PATH}"
            )

            return

        # ----------------------------------------------------
        # Output UAsset
        # ----------------------------------------------------

        output_uasset_path = os.path.join(
            material_output_folder,
            new_material_name + ".uasset"
        )

        # ----------------------------------------------------
        # Convert JSON to UAsset
        # ----------------------------------------------------

        try:

            result = subprocess.run(
                [
                    UASSETGUI_PATH,
                    "fromjson",
                    output_json_path,
                    output_uasset_path
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except Exception as e:

            messagebox.showerror(
                "UAssetGUI Error",
                f"Could not run UAssetGUI.\n\n"
                f"{e}\n\n"
                f"The JSON has been kept for debugging:\n"
                f"{output_json_path}"
            )

            return

        # ----------------------------------------------------
        # Check Conversion
        # ----------------------------------------------------

        if (
            result.returncode != 0
            or not os.path.exists(
                output_uasset_path
            )
        ):

            error_text = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Unknown UAssetGUI error."
            )

            messagebox.showerror(
                "Material Conversion Error",
                f"UAssetGUI could not create the material:\n\n"
                f"{new_material_name}.uasset\n\n"
                f"{error_text}\n\n"
                f"The JSON has been kept for debugging:\n"
                f"{output_json_path}"
            )

            return

        # ----------------------------------------------------
        # Remove Temporary JSON
        # ----------------------------------------------------

        try:

            os.remove(
                output_json_path
            )

        except Exception as e:

            print(
                f"[WARNING] Could not remove temporary JSON: "
                f"{output_json_path} - {e}"
            )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        messagebox.showinfo(
            "Material Created",
            f"Material created successfully.\n\n"
            f"{new_material_name}.uasset\n"
            f"{new_material_name}.uexp\n\n"
            f"Saved to:\n"
            f"{material_output_folder}"
        )

        print(
            f"[LOG] Created game material: "
            f"{output_uasset_path}"
        )

        close_game_window()

    # ========================================================
    # Create Material Button
    # ========================================================

    create_button = ttk.Button(
        game_window,
        text="Create Material",
        command=create_game_material,
        width=30,
        style="Main.TButton"
    )

    create_button.pack(
        side="bottom",
        pady=(10, 20),
        ipady=8
    )

    create_button.bind(
        "<Enter>",
        set_hand_cursor
    )

    create_button.bind(
        "<Leave>",
        lambda event: event.widget.configure(
            cursor=""
        )
    )

    # --------------------------------------------------------
    # Save Window Position When Closed
    # --------------------------------------------------------

    def close_game_window():

        save_child_window_position(
            game_window,
            GAME_POSITION_FILE
        )

        game_window.unbind_all(
            "<MouseWheel>"
        )

        game_window.destroy()

    game_window.protocol(
        "WM_DELETE_WINDOW",
        close_game_window
    )

    game_window.update_idletasks()
    game_window.deiconify()

# ============================================================
# Entry Undo / Redo
# ============================================================

entry_history = {}
entry_history_index = {}


def setup_entry_undo(entry):
    entry_history[entry] = [entry.get()]
    entry_history_index[entry] = 0

    def record_change(event=None):
        current_value = entry.get()

        history = entry_history[entry]
        index = entry_history_index[entry]

        if history[index] == current_value:
            return

        history[:] = history[:index + 1]
        history.append(current_value)

        if len(history) > 100:
            history.pop(0)

        entry_history_index[entry] = len(history) - 1

    def shortcut(event=None):
        if not event:
            return

        key = event.keysym.lower()

        if key == "z":
            if event.state & 0x0001:
                history = entry_history[entry]
                index = entry_history_index[entry]

                if index < len(history) - 1:
                    index += 1

                    entry_history_index[entry] = index

                    entry.delete(
                        0,
                        tk.END
                    )

                    entry.insert(
                        0,
                        history[index]
                    )

                return "break"

            history = entry_history[entry]
            index = entry_history_index[entry]

            if index > 0:
                index -= 1

                entry_history_index[entry] = index

                entry.delete(
                    0,
                    tk.END
                )

                entry.insert(
                    0,
                    history[index]
                )

            return "break"

        if key == "y":
            history = entry_history[entry]
            index = entry_history_index[entry]

            if index < len(history) - 1:
                index += 1

                entry_history_index[entry] = index

                entry.delete(
                    0,
                    tk.END
                )

                entry.insert(
                    0,
                    history[index]
                )

            return "break"

    entry.bind(
        "<Control-KeyPress>",
        shortcut
    )

    entry.bind(
        "<KeyRelease>",
        record_change
    )


# ============================================================
# HELP WINDOWS
# ============================================================

def show_help():
    help_window = tk.Toplevel(root)
    help_window.withdraw()
    
    help_window.title("How To Use")

    screen_width = help_window.winfo_screenwidth()
    screen_height = help_window.winfo_screenheight()

    window_width = 650
    window_height = 500

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    help_window.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )
    
    help_window.resizable(False, False)

    help_window.iconbitmap(ICON_PATH)

    help_window.configure(bg="#2b2b2b")

    title = tk.Label(
        help_window,
        text="How To Use",
        font=PRICEDOWN_FONT,
        bg="#2b2b2b",
        fg="white"
    )
    title.pack(pady=(20, 15))

    text_frame = tk.Frame(
        help_window,
        bg="#2b2b2b"
    )
    text_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 20)
    )

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(
        side="right",
        fill="y"
    )

    text = tk.Text(
        text_frame,
        wrap="word",
        bg="#202020",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=("Segoe UI", 10),
        padx=15,
        pady=15,
        yscrollcommand=scrollbar.set
    )

    text.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.config(
        command=text.yview
    )

    help_text = """Asset Manager
GTA Trilogy Definitive Edition


IMPORTANT — NAMING CONVENTIONS

The correct naming convention must be used for materials and textures.
Incorrect naming can cause materials or textures to not work correctly.

MATERIALS

Material instances must begin with:

MI_

Example:
MI_Vehicle_Body


Base materials must begin with:

M_

Example:
M_Vehicle_Body


TEXTURES

All textures must begin with:

T_

Texture names must also use the correct texture type suffix:

_BC — Base Color
_N  — Normal
_P  — Packed / Mask texture
_MT — Metallic
_R  — Roughness
_E  — Emissive

Examples:

T_Vehicle_Body_BC
T_Vehicle_Body_N
T_Vehicle_Body_P
T_Vehicle_Body_MT
T_Vehicle_Body_R
T_Vehicle_Body_E


MESHES

Static meshes must begin with:

SM_

Example:
SM_Vehicle_Body


Skeletal meshes must begin with:

SKR_

Example:
SKR_Vehicle_Body

----------------------------------


HOW TO USE


NEW DUMMY MATERIAL

New Dummy Material is used to quickly create new material
instances using the names and paths you provide.

Use this option when you want to create basic material instances
and have the tool generate the required material files for you.

To use it:

1. Click "New Dummy Material" from the main window.
2. Select and edit the required material names and package paths.
3. Add or remove material entries as required.
4. Enter the required texture names and package paths.
5. Make sure your materials use the correct MI_ naming convention.
6. Make sure your textures use the correct T_ naming convention
   and appropriate texture type suffix.
7. Make sure all required fields are completed.
8. Click "Create Materials".
9. The generated material files can then be used with your
   GTA Trilogy Definitive Edition mod.


CREATE GAME MATERIALS

Create Game Materials is used to create unique materials specifically
for use with the GTA Trilogy Definitive Edition games.

Use this option when you want to create a material with specific
characteristics provided by the available material templates.

To use it:

1. Click "Create Game Materials" from the main window.
2. Select the material type you would like to create.
3. Enter the material name using the required MI_ naming convention.
4. Select and edit the required material and texture names and paths.
5. Make sure every texture uses the correct T_ naming convention
   and appropriate texture suffix.
6. Make sure all required fields are completed.
7. Create the material.
8. The generated material can then be used with your
   GTA Trilogy Definitive Edition mod.


MATERIAL EDITOR

Material Editor is used to edit existing Unreal Engine material
assets and their internal names and package paths.

The Material Editor can open both Material Instances (MI_) and
Base Materials (M_) only.

Mesh assets such as SM_ Static Meshes and SKR_ Skeletal Meshes
cannot be opened with the Material Editor.

To use it:

1. Click "Material Editor" from the main window.
2. Select an existing MI_ or M_ material UAsset or JSON file.
3. Edit the Material Name and Package Path as required.
4. Edit the texture references and their package paths as required.
5. Make sure any renamed materials use the correct naming convention.
6. Make sure any renamed textures use the correct T_ naming convention
   and appropriate texture suffix.
7. Use Ctrl+Z to undo text changes in the editable fields.
8. Use Ctrl+Y to redo text changes.
9. Click "Save Material" when finished.
10. The edited material can then be used with your
    GTA Trilogy Definitive Edition mod.


MESH EDITOR

Mesh Editor is used to edit existing Unreal Engine Static Mesh
and Skeletal Mesh assets.

It can be used to edit mesh names, package paths, material references,
and, for supported Skeletal Meshes, Wheel Mesh references.

The Mesh Editor can open:

SM_ — Static Meshes
SKR_ — Skeletal Meshes

To use it:

1. Click "Mesh Editor" from the main window.
2. Select an existing SM_ Static Mesh or SKR_ Skeletal Mesh
   UAsset or JSON file.
3. Edit the Mesh Name and Package Path as required.
4. For Skeletal Meshes with a Wheel Mesh reference, edit the
   Wheel Mesh Name and Package Path as required.
5. Edit the Material References as required.
6. Each material reference contains a Material Name and Package Path.
7. Make sure renamed materials use the correct material naming convention.
8. Select "Include game folder structure" if you want the output
    to recreate the appropriate game folder structure.
9. Click "Save Mesh" when finished.
10. The edited mesh can then be used with your
    GTA Trilogy Definitive Edition mod.

----------------------------------


MESH MATERIAL REFERENCES

When editing a mesh, the Material References section displays
the materials assigned to that mesh.

Each material reference contains:

Material Name
Package Path

Changing a material name updates the corresponding material
references throughout the mesh.

Changing a material package path updates the material import
information used by the mesh.

The Material Interface reference itself should remain unchanged
when only the material name or package path is being edited.


SKELETAL MESHES

Skeletal Meshes can contain a Wheel Mesh reference.

When a supported Skeletal Mesh contains a Wheel Mesh reference,
the Mesh Editor will display:

Wheel Mesh Name
Wheel Mesh Package Path

These fields can be edited in the same way as the main mesh
name and package path.


OUTPUT

The editors can save the resulting UAsset files to the selected
output folder.

When "Include game folder structure" is enabled, the tool recreates
the appropriate Gameface/Content folder structure based on the
package path of the asset.

This can make it easier to place the generated files directly
into the correct location for GTA Trilogy Definitive Edition mods.

----------------------------------

IMPORTANT

Before saving or creating assets, always check that your names
and package paths are correct.

Material Instances must use the MI_ prefix.

Base Materials must use the M_ prefix.

Static Meshes must use the SM_ prefix.

Skeletal Meshes must use the SKR_ prefix.

Textures must use the T_ prefix and the appropriate texture
type suffix.

Using the correct names and package paths is especially important
when working with Unreal Engine assets intended for the
GTA Trilogy Definitive Edition.
"""

    text.insert("1.0", help_text)
    text.config(state="disabled")

    help_window.update_idletasks()
    help_window.deiconify()

def show_credits():
    credits_window = tk.Toplevel(root)
    credits_window.withdraw()
    credits_window.title("Credits")

    screen_width = credits_window.winfo_screenwidth()
    screen_height = credits_window.winfo_screenheight()

    window_width = 500
    window_height = 400

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    credits_window.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )
    
    credits_window.resizable(False, False)

    credits_window.iconbitmap(ICON_PATH)

    credits_window.configure(bg="#2b2b2b")

    title = tk.Label(
        credits_window,
        text="Credits",
        font=PRICEDOWN_FONT,
        bg="#2b2b2b",
        fg="white"
    )
    title.pack(pady=(30, 25))

    credits_text = """Asset Manager


Created by

ITSM0VER


UAssetGUI

Required by this application for
Unreal Engine UAsset conversion
and material editing.
"""

    text = tk.Label(
        credits_window,
        text=credits_text,
        justify="center",
        font=("Segoe UI", 11),
        bg="#2b2b2b",
        fg="white"
    )

    text.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=10
    )

    credits_window.update_idletasks()
    credits_window.deiconify()

# ============================================================
# HELP MENU
# ============================================================

menu_frame = tk.Frame(
    root,
    bg="#3a3a3a",
    height=25
)

menu_frame.pack(
    side="top",
    fill="x"
)


help_button = tk.Menubutton(
    menu_frame,
    text="Help",
    bg="#3a3a3a",
    fg="white",
    activebackground="#444444",
    activeforeground="white",
    relief="flat",
    font=("Segoe Script Bold", 10),
    cursor="hand2"
)


help_menu = tk.Menu(
    help_button,
    tearoff=0,
    bg="#2b2b2b",
    fg="white",
    activebackground="#444444",
    activeforeground="white"
)

help_menu.add_command(
    label="How to Use",
    command=show_help
)

help_menu.add_separator()

help_menu.add_command(
    label="Credits",
    command=show_credits
)

help_button.config(
    menu=help_menu
)

help_button.pack(
    side="left",
    padx=5
)


# ============================================================
# UI
# ============================================================

title_label = ttk.Label(
    root,
    text="Asset Manager",
    font=PRICEDOWN_FONT
)

title_label.pack(pady=(40, 30))


description_label = ttk.Label(
    root,
    text="What type of material would you like to create or edit?",
    font=("Segoe Script", 12)
)

description_label.pack(pady=(0, 25))


button_frame = ttk.Frame(root)
button_frame.pack()


dummy_button = ttk.Button(
    button_frame,
    text="New Dummy Material",
    command=new_dummy_material,
    width=30,
    style="Main.TButton"
)

dummy_button.grid(
    row=0,
    column=0,
    padx=15,
    pady=(0, 15),
    ipady=10
)


game_button = ttk.Button(
    button_frame,
    text="Create Game Materials",
    command=game_material,
    width=30,
    style="Main.TButton"
)

game_button.grid(
    row=0,
    column=1,
    padx=15,
    pady=(0, 15),
    ipady=10
)


editor_button = ttk.Button(
    button_frame,
    text="Material Editor",
    command=material_editor,
    width=30,
    style="Main.TButton"
)

editor_button.grid(
    row=1,
    column=0,
    padx=15,
    pady=(15, 0),
    ipady=10
)

mesh_editor_button = ttk.Button(
    button_frame,
    text="Mesh Editor",
    command=mesh_editor,
    width=30,
    style="Main.TButton"
)

mesh_editor_button.grid(
    row=1,
    column=1,
    padx=15,
    pady=(15, 0),
    ipady=10
)

watermark = tk.Label(
    root,
    text="Made by ITSM0VER",
    font=("Segoe UI", 9),
    bg="#2b2b2b",
    fg="#666666"
)

watermark.pack(
    side="bottom",
    pady=(0, 8)
)

# Hand cursor when hovering over buttons
def set_hand_cursor(event):
    event.widget.configure(cursor="hand2")

dummy_button.bind("<Enter>", set_hand_cursor)
dummy_button.bind("<Leave>", lambda event: event.widget.configure(cursor=""))

game_button.bind("<Enter>", set_hand_cursor)
game_button.bind("<Leave>", lambda event: event.widget.configure(cursor=""))

editor_button.bind("<Enter>", set_hand_cursor)
editor_button.bind("<Leave>", lambda event: event.widget.configure(cursor=""))

mesh_editor_button.bind("<Enter>", set_hand_cursor)
mesh_editor_button.bind("<Leave>", lambda event: event.widget.configure(cursor=""))


# ============================================================
# Start
# ============================================================

root.deiconify()
root.mainloop()
