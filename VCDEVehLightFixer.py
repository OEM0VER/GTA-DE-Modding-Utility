import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, filedialog, messagebox
from ctypes import windll


# ============================================================
# PATHS
# ============================================================

def get_script_directory():
    if getattr(sys, "frozen", False):
        # Compiled EXE is inside Files/.Resources
        return os.path.dirname(
            os.path.dirname(
                os.path.dirname(sys.executable)
            )
        )

    # Running directly as a Python script
    return os.path.dirname(
        os.path.abspath(__file__)
    )


SCRIPT_DIR = get_script_directory()

PRICEDOWN_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "pricedown bl.otf"
)

UASSETGUI_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "UAssetGUI.exe"
)

ICON_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "ICON.ico"
)

REFERENCES_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".References"
)

CUE4PARSE_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "cue4parse.exe"
)

UNREALPAK_BAT_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    "UnrealPak-Without-Compression.bat"
)

UASSET2JSON_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "UAsset2JsonConverter.py"
)

UASSET2JSON_EXE_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "UAsset2JsonConverter.exe"
)

POSITION_FILE = os.path.join(
    SCRIPT_DIR,
    "Files",
    "veh_light_window_position.txt"
)

MATERIAL_VIEWER_POSITION_FILE = os.path.join(
    SCRIPT_DIR,
    "Files",
    "material_viewer_window_position.txt"
)

ENGINE_VERSION = "VER_UE4_26"

CUE4PARSE_GAME_VERSION = "GAME_UE4_26"


# ============================================================
# VEHICLE USER DATA PROPERTIES WE TRANSFER
# ============================================================

TRANSFER_PROPERTIES = {
    "WheelMesh",
    "bHasVertexAO",
    "VertexAOStrength",
    "LightOnMIC",
    "LightOnTailLightsMIC",
    "LightOffMIC",
    "LeftSirenIndex",
    "RightSirenIndex",
}


LIGHT_INDEX_PROPERTIES = {
    "LightIndex_LF",
    "LightIndex_RF",
    "LightIndex_LR",
    "LightIndex_RR",
}


# ============================================================
# APPLICATION
# ============================================================

class VehicleLightingTool:

    # ========================================================
    # WINDOW POSITION
    # ========================================================

    def save_window_position(self):

        try:

            x = self.root.winfo_x()
            y = self.root.winfo_y()

            os.makedirs(
                os.path.dirname(POSITION_FILE),
                exist_ok=True
            )

            with open(
                POSITION_FILE,
                "w"
            ) as file:

                file.write(
                    f"{x},{y}"
                )

        except Exception:
            pass


    def load_window_position(self):

        try:

            if os.path.exists(
                POSITION_FILE
            ):

                with open(
                    POSITION_FILE,
                    "r"
                ) as file:

                    pos = file.read().strip().split(",")

                if (
                    len(pos) == 2
                    and pos[0].lstrip("-").isdigit()
                    and pos[1].lstrip("-").isdigit()
                ):

                    return (
                        int(pos[0]),
                        int(pos[1])
                    )

        except Exception:
            pass

        return None

    def save_material_viewer_position(self, viewer):

        try:

            x = viewer.winfo_x()
            y = viewer.winfo_y()

            os.makedirs(
                os.path.dirname(
                    MATERIAL_VIEWER_POSITION_FILE
                ),
                exist_ok=True
            )

            with open(
                MATERIAL_VIEWER_POSITION_FILE,
                "w"
            ) as file:

                file.write(
                    f"{x},{y}"
                )

        except Exception:
            pass


    def load_material_viewer_position(self):

        try:

            if os.path.exists(
                MATERIAL_VIEWER_POSITION_FILE
            ):

                with open(
                    MATERIAL_VIEWER_POSITION_FILE,
                    "r"
                ) as file:

                    pos = file.read().strip().split(",")

                if (
                    len(pos) == 2
                    and pos[0].lstrip("-").isdigit()
                    and pos[1].lstrip("-").isdigit()
                ):

                    return (
                        int(pos[0]),
                        int(pos[1])
                    )

        except Exception:
            pass

        return None

    def on_closing(self):

        self.save_window_position()


        # ----------------------------------------------------
        # REMOVE TEMPORARY INPUT JSON
        # ----------------------------------------------------

        if self.temporary_input_json:

            try:

                temporary_folder = os.path.dirname(
                    self.temporary_input_json
                )


                if os.path.isfile(
                    self.temporary_input_json
                ):

                    os.remove(
                        self.temporary_input_json
                    )


                if (
                    os.path.basename(
                        temporary_folder
                    ).lower() == "temp"
                    and os.path.isdir(
                        temporary_folder
                    )
                    and not os.listdir(
                        temporary_folder
                    )
                ):

                    os.rmdir(
                        temporary_folder
                    )


            except OSError:

                pass

            self.temporary_input_json = None


        if PRICEDOWN_LOADED:

            windll.gdi32.RemoveFontResourceW(
                PRICEDOWN_PATH
            )

        self.root.destroy()

    def __init__(self, root):

        self.root = root

        self.root.title(
            "GTA DE Vehicle Lighting Tool"
        )

        self.root.geometry(
            "720x840"
        )

        self.root.resizable(
            False,
            False
        )

        self.root.configure(
            bg="#2b2b2b"
        )

        if os.path.isfile(ICON_PATH):
            try:
                self.root.iconbitmap(
                    ICON_PATH
                )
            except tk.TclError:
                pass

        self.setup_style()

        self.setup_pricedown_font()

        self.create_menu()


        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.input_json = tk.StringVar()

        self.output_uasset = tk.StringVar()

        self.keep_modified_json = tk.BooleanVar(
            value=False
        )

        self.install_converted_asset = tk.BooleanVar(
            value=False
        )

        self.light_entries = {}

        self.wheel_mesh_entry = None

        self.siren_entries = {}

        self.reference_data = None

        self.reference_path = None

        self.temporary_input_json = None
    

        # ----------------------------------------------------
        # BUILD UI
        # ----------------------------------------------------

        self.create_ui()

        last_position = self.load_window_position()

        if last_position:

            self.root.geometry(
                f"+{last_position[0]}+{last_position[1]}"
            )


        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )

    # ========================================================
    # PRICEDOWN FONT
    # ========================================================

    def setup_pricedown_font(self):

        global PRICEDOWN_FONT
        global PRICEDOWN_LOADED

        PRICEDOWN_LOADED = False

        if os.path.isfile(
            PRICEDOWN_PATH
        ):

            if windll.gdi32.AddFontResourceW(
                PRICEDOWN_PATH
            ):

                PRICEDOWN_LOADED = True

        pricedown_family = None

        for family in tkFont.families(
            self.root
        ):

            if "Pricedown" in family:

                pricedown_family = family
                break

        if pricedown_family:

            PRICEDOWN_FONT = (
                pricedown_family,
                26
            )

        else:

            PRICEDOWN_FONT = (
                "Segoe UI",
                18,
                "bold"
            )
    

    # ========================================================
    # MENU
    # ========================================================

    def create_menu(self):

        # ----------------------------------------------------
        # CUSTOM DARK MENU BAR
        # ----------------------------------------------------

        menu_frame = tk.Frame(
            self.root,
            bg="#3a3a3a",
            height=25
        )

        menu_frame.pack(
            side="top",
            fill="x"
        )


        # ----------------------------------------------------
        # HELPER FUNCTION
        # ----------------------------------------------------

        def create_dark_menubutton(
            parent,
            text,
            menu_items,
            font_size=10
        ):

            btn = tk.Menubutton(
                parent,
                text=text,
                bg="#3a3a3a",
                fg="white",
                activebackground="#444444",
                activeforeground="white",
                relief="flat",
                font=("Segoe Script Bold", font_size),
                cursor="hand2"
            )


            menu = tk.Menu(
                btn,
                tearoff=0,
                bg="#2b2b2b",
                fg="white",
                activebackground="#444444",
                activeforeground="white"
            )


            for item in menu_items:

                if item == "separator":

                    menu.add_separator()

                else:

                    label, command = item

                    menu.add_command(
                        label=label,
                        command=command
                    )


            btn.config(
                menu=menu
            )


            btn.pack(
                side="left",
                padx=5
            )


            return btn


        # ----------------------------------------------------
        # FILE MENU
        # ----------------------------------------------------

        file_items = [
            (
                "Convert UAsset to JSON",
                self.open_uasset_converter
            ),
            "separator",
            (
                "Exit",
                self.on_closing
            )
        ]


        # ----------------------------------------------------
        # HELP MENU
        # ----------------------------------------------------

        help_items = [
            (
                "How To Use",
                self.show_help
            ),
            (
                "Credits",
                self.show_credits
            ),
            "separator",
            (
                "About",
                self.show_about
            )
        ]


        # ----------------------------------------------------
        # CREATE MENU BUTTONS
        # ----------------------------------------------------

        file_btn = create_dark_menubutton(
            menu_frame,
            "File",
            file_items
        )


        help_btn = create_dark_menubutton(
            menu_frame,
            "Help",
            help_items
        )


    def open_uasset_converter(self):

        # ----------------------------------------------------
        # COMPILED VERSION - EXE
        # ----------------------------------------------------

        if os.path.isfile(
            UASSET2JSON_EXE_PATH
        ):

            try:

                subprocess.Popen(
                    [
                        UASSET2JSON_EXE_PATH
                    ],
                    cwd=SCRIPT_DIR
                )

                return

            except Exception as error:

                messagebox.showerror(
                    "Could Not Open Converter",
                    (
                        "The UAsset → JSON Converter could not be opened.\n\n"
                        f"{error}"
                    )
                )

                return


        # ----------------------------------------------------
        # DEVELOPMENT VERSION - PYTHON
        # ----------------------------------------------------

        if os.path.isfile(
            UASSET2JSON_PATH
        ):

            try:

                subprocess.Popen(
                    [
                        sys.executable,
                        UASSET2JSON_PATH
                    ],
                    cwd=SCRIPT_DIR
                )

                return

            except Exception as error:

                messagebox.showerror(
                    "Could Not Open Converter",
                    (
                        "The UAsset → JSON Converter could not be opened.\n\n"
                        f"{error}"
                    )
                )

                return


        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        messagebox.showerror(
            "Converter Not Found",
            (
                "The UAsset → JSON Converter could not be found.\n\n"
                "Expected either:\n\n"
                f"{UASSET2JSON_EXE_PATH}\n"
                f"{UASSET2JSON_PATH}"
            )
        )

    def show_help(self):

        help_window = tk.Toplevel(
            self.root
        )

        help_window.withdraw()

        help_window.attributes(
            "-alpha",
            0.0
        )

        help_window.configure(
            bg="#2b2b2b"
        )

        help_window.title(
            "How To Use"
        )

        window_width = 650
        window_height = 650

        screen_width = help_window.winfo_screenwidth()
        screen_height = help_window.winfo_screenheight()

        position_x = (
            screen_width - window_width
        ) // 2

        position_y = (
            screen_height - window_height
        ) // 2

        help_window.geometry(
            f"{window_width}x{window_height}+{position_x}+{position_y}"
        )

        help_window.resizable(
            False,
            False
        )

        if os.path.isfile(
            ICON_PATH
        ):
            try:
                help_window.iconbitmap(
                    ICON_PATH
                )
            except tk.TclError:
                pass


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            help_window,
            text="How To Use - GTA DE Vehicle Lighting Tool",
            font=PRICEDOWN_FONT,
            fg="#FFFFFF",
            bg="#2b2b2b"
        )

        title.pack(
            pady=(18, 4)
        )


        subtitle = tk.Label(
            help_window,
            text="Follow these steps to transfer vehicle lighting data.",
            font=("Segoe Script", 11),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        subtitle.pack(
            pady=(0, 15)
        )


        # ----------------------------------------------------
        # HELP TEXT
        # ----------------------------------------------------

        text_frame = tk.Frame(
            help_window,
            bg="#2b2b2b"
        )

        text_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )


        scrollbar = tk.Scrollbar(
            text_frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        help_text = tk.Text(
            text_frame,
            bg="#1e1e1e",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
            wrap="word",
            font=("Segoe UI", 10),
            padx=15,
            pady=15,
            yscrollcommand=scrollbar.set
        )

        help_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=help_text.yview
        )


        instructions = (
            "STEP 1 — SELECT YOUR CUSTOM VEHICLE JSON\n\n"
            "Click Browse... and select the JSON file for "
            "your custom vehicle model.\n\n"
            "The tool uses this JSON to detect the vehicle "
            "and determine which original VCDE vehicle "
            "reference should be used.\n\n\n"

            "STEP 2 — CHECK THE DETECTED VEHICLE\n\n"
            "Once the JSON is selected, the tool will display "
            "the detected vehicle and the original reference "
            "vehicle being used.\n\n"
            "Make sure the detected vehicle is correct before "
            "continuing.\n\n\n"

            "STEP 3 — ENTER YOUR LIGHT MATERIAL SLOTS\n\n"
            "Enter the material-slot number used by each light "
            "on your custom model:\n\n"
            "LF = Left Front\n"
            "RF = Right Front\n"
            "LR = Left Rear\n"
            "RR = Right Rear\n\n"
            "These numbers tell the tool which material slot "
            "on your new model should receive the lighting "
            "data.\n\n\n"

            "STEP 4 — ENTER SIREN SLOTS (IF REQUIRED)\n\n"
            "Some vehicles use siren material slots.\n\n"
            "If the original reference vehicle contains siren "
            "data, an additional Siren Material Slot section "
            "will appear.\n\n"
            "Enter the corresponding material-slot numbers "
            "from your custom model.\n\n\n"

            "STEP 5 — CHOOSE THE OUTPUT LOCATION\n\n"
            "The tool automatically creates an output UAsset "
            "path based on your selected JSON.\n\n"
            "You can change this location if required.\n\n\n"

            "STEP 6 — TRANSFER & CONVERT\n\n"
            "Click TRANSFER & CONVERT to transfer the required "
            "vehicle lighting properties from the original "
            "VCDE vehicle reference to your custom vehicle.\n\n"
            "The modified JSON is then converted back into a "
            ".uasset using UAssetGUI.\n\n\n"

            "STEP 7 — USE YOUR NEW UASSET\n\n"
            "Once conversion is complete, the finished UAsset "
            "will be available at the selected output location.\n\n"
            "Use the resulting asset in your GTA Trilogy "
            "Definitive Edition vehicle mod.\n\n\n"

            "VIEW MATERIAL SLOTS\n\n"
            "The VIEW MATERIAL SLOTS button allows you to "
            "inspect the material slots and sections of an "
            "existing UAsset.\n\n"
            "This can be useful when determining the correct "
            "LF, RF, LR and RR material-slot numbers for your "
            "custom model.\n\n\n"

            "IMPORTANT\n\n"
            "The four light positions normally use the same "
            "light material. You are entering the material "
            "slot numbers used by each light section on your "
            "custom model — not creating four different "
            "light materials."
        )


        help_text.insert(
            "1.0",
            instructions
        )

        help_text.config(
            state="disabled"
        )


        close_button = tk.Button(
            help_window,
            text="CLOSE",
            command=help_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#ff69b4",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            height=1
        )

        close_button.pack(
            pady=(0, 15)
        )


        help_window.transient(
            self.root
        )

        help_window.grab_set()

        help_window.update_idletasks()

        help_window.deiconify()

        help_window.update()

        help_window.attributes(
            "-alpha",
            1.0
        )


    def show_about(self):

        messagebox.showinfo(
            "About",
            (
                "GTA DE Vehicle Lighting Tool\n\n"
                "Transfer VCDE vehicle lighting data "
                "to custom models.\n\n"
                "Made by ITSM0VER"
            )
        )

    def show_credits(self):

        credits_window = tk.Toplevel(
            self.root
        )

        credits_window.title(
            "Credits"
        )

        window_width = 500
        window_height = 430

        screen_width = credits_window.winfo_screenwidth()
        screen_height = credits_window.winfo_screenheight()

        position_x = (
            screen_width - window_width
        ) // 2

        position_y = (
            screen_height - window_height
        ) // 2

        credits_window.geometry(
            f"{window_width}x{window_height}+{position_x}+{position_y}"
        )

        credits_window.resizable(
            False,
            False
        )

        credits_window.configure(
            bg="#2b2b2b"
        )

        if os.path.isfile(
            ICON_PATH
        ):
            try:
                credits_window.iconbitmap(
                    ICON_PATH
                )
            except tk.TclError:
                pass


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            credits_window,
            text="Credits",
            font=PRICEDOWN_FONT,
            fg="#FFFFFF",
            bg="#2b2b2b"
        )

        title.pack(
            pady=(25, 5)
        )


        subtitle = tk.Label(
            credits_window,
            text="GTA DE Vehicle Lighting Tool",
            font=PRICEDOWN_FONT,
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        subtitle.pack(
            pady=(0, 25)
        )


        # ----------------------------------------------------
        # CREDITS
        # ----------------------------------------------------

        credits_frame = tk.Frame(
            credits_window,
            bg="#1e1e1e"
        )

        credits_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 20)
        )


        credits = (
            "UAssetGUI\n"
            "Asset conversion\n\n"

            "CUE4Parse\n"
            "Asset parsing\n\n"

            "ITSM0VER\n"
            "Creation & development\n\n"

            "RoRoGothic\n"
            "Help & advice"
        )


        credits_label = tk.Label(
            credits_frame,
            text=credits,
            font=("Segoe UI", 11),
            fg="#FFFFFF",
            bg="#1e1e1e",
            justify="center"
        )

        credits_label.pack(
            expand=True
        )


        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        footer = tk.Label(
            credits_window,
            text="Thank you to everyone who helped make this tool possible.",
            font=("Segoe UI", 8, "italic"),
            fg="#666666",
            bg="#2b2b2b"
        )

        footer.pack(
            pady=(0, 10)
        )


        close_button = tk.Button(
            credits_window,
            text="CLOSE",
            command=credits_window.destroy,
            font=("Segoe UI", 10, "bold"),
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#ff69b4",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            height=1
        )

        close_button.pack(
            pady=(0, 15)
        )


        credits_window.transient(
            self.root
        )

        credits_window.grab_set()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style(
            self.root
        )

        try:
            style.theme_use(
                "clam"
            )
        except tk.TclError:
            pass

        style.configure(
            "TFrame",
            background="#2b2b2b"
        )

        style.configure(
            "TLabel",
            background="#2b2b2b",
            foreground="#FFFFFF"
        )

        style.configure(
            "TLabelframe",
            background="#2b2b2b",
            foreground="#FFFFFF"
        )

        style.configure(
            "TLabelframe.Label",
            background="#2b2b2b",
            foreground="#FFFFFF"
        )

        style.configure(
            "TEntry",
            fieldbackground="#3a3a3a",
            foreground="#FFFFFF"
        )

        style.configure(
            "TButton",
            background="#3a3a3a",
            foreground="#FFFFFF"
        )

        style.map(
            "TButton",
            background=[
                ("active", "#4a4a4a")
            ],
            foreground=[
                ("active", "#FFFFFF")
            ]
        )

        style.configure(
            "TCombobox",
            fieldbackground="#3a3a3a",
            foreground="#FFFFFF"
        )

        style.configure(
            "TCheckbutton",
            background="#2b2b2b",
            foreground="#FFFFFF"
        )

        style.map(
            "TCheckbutton",
            background=[
                ("active", "#2b2b2b")
            ],
            foreground=[
                ("active", "#FFFFFF")
            ]
        )


    # ========================================================
    # UI
    # ========================================================

    def create_ui(self):

        # ========================================================
        # SCROLLABLE MAIN AREA
        # ========================================================

        scroll_container = tk.Frame(
            self.root,
            bg="#2b2b2b"
        )

        scroll_container.pack(
            fill="both",
            expand=True
        )


        canvas = tk.Canvas(
            scroll_container,
            bg="#2b2b2b",
            highlightthickness=0,
            bd=0
        )

        scrollbar = ttk.Scrollbar(
            scroll_container,
            orient="vertical",
            command=canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        main = tk.Frame(
            canvas,
            bg="#2b2b2b"
        )

        canvas_window = canvas.create_window(
            (20, 20),
            window=main,
            anchor="nw"
        )


        def update_scroll_region(event=None):

            bbox = canvas.bbox("all")

            if bbox:

                canvas.configure(
                    scrollregion=(
                        0,
                        0,
                        bbox[2] + 20,
                        bbox[3] + 20
                    )
                )


        def resize_canvas_window(event):

            canvas.itemconfigure(
                canvas_window,
                width=event.width - 40
            )


        main.bind(
            "<Configure>",
            update_scroll_region
        )

        canvas.bind(
            "<Configure>",
            resize_canvas_window
        )


        canvas.pack(
            fill="both",
            expand=True
        )


        def on_mousewheel(event):

            try:

                if event.widget.winfo_toplevel() != self.root:
                    return

                canvas.yview_scroll(
                    int(-1 * (event.delta / 120)),
                    "units"
                )

            except tk.TclError:
                pass


        self.root.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            main,
            text="GTA DE Vehicle Lighting Tool",
            font=PRICEDOWN_FONT,
            fg="#FFFFFF",
            bg="#2b2b2b"
        )

        title.pack(
            pady=(0, 4)
        )


        subtitle = tk.Label(
            main,
            text="Transfer VCDE vehicle lighting data to custom models",
            font=("Segoe Script", 10),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        subtitle.pack(
            pady=(0, 18)
        )


        # ----------------------------------------------------
        # CUSTOM JSON
        # ----------------------------------------------------

        input_frame = ttk.LabelFrame(
            main,
            text="Custom Vehicle UAsset/JSON"
        )

        input_frame.pack(
            fill="x",
            pady=(0, 12)
        )


        input_row = tk.Frame(
            input_frame,
            bg="#2b2b2b"
        )

        input_row.pack(
            fill="x",
            padx=10,
            pady=10
        )


        self.input_entry = tk.Entry(
            input_row,
            textvariable=self.input_json,
            bg="#3a3a3a",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat"
        )

        self.input_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5
        )


        browse_input = tk.Button(
            input_row,
            text="Browse...",
            command=self.browse_json,
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#4a4a4a",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )

        browse_input.pack(
            side="left",
            padx=(8, 0)
        )

        # ----------------------------------------------------
        # DETECTED VEHICLE
        # ----------------------------------------------------

        detected_frame = ttk.LabelFrame(
            main,
            text="Detected Vehicle"
        )

        detected_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        detected_row = tk.Frame(
            detected_frame,
            bg="#2b2b2b"
        )

        detected_row.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.detected_vehicle_label = tk.Label(
            detected_row,
            text="Select a custom JSON...",
            font=("Segoe UI", 10, "bold"),
            fg="#FFFFFF",
            bg="#2b2b2b",
            anchor="w"
        )

        self.detected_vehicle_label.pack(
            fill="x"
        )

        self.detected_reference_label = tk.Label(
            detected_row,
            text="",
            font=("Segoe UI", 9),
            fg="#AAAAAA",
            bg="#2b2b2b",
            anchor="w"
        )

        self.detected_reference_label.pack(
            fill="x",
            pady=(3, 0)
        )


        # ----------------------------------------------------
        # WHEEL MESH
        # ----------------------------------------------------

        wheel_mesh_frame = ttk.LabelFrame(
            main,
            text="Wheel Mesh"
        )

        wheel_mesh_frame.pack(
            fill="x",
            pady=(0, 12)
        )


        explanation = tk.Label(
            wheel_mesh_frame,
            text=(
                "Enter the Unreal asset path used by the wheel mesh "
                "on your new model."
            ),
            font=("Segoe Script", 10),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        explanation.pack(
            pady=(10, 5)
        )


        wheel_mesh_container = tk.Frame(
            wheel_mesh_frame,
            bg="#2b2b2b"
        )

        wheel_mesh_container.pack(
            fill="x",
            padx=15,
            pady=(5, 12)
        )


        self.wheel_mesh_entry = tk.Entry(
            wheel_mesh_container,
            justify="left",
            bg="#3a3a3a",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
            font=("Consolas", 11)
        )

        self.wheel_mesh_entry.pack(
            fill="x",
            ipady=4
        )

        # ----------------------------------------------------
        # LIGHT INDICES
        # ----------------------------------------------------

        light_frame = ttk.LabelFrame(
            main,
            text="New Model Material Slot Numbers"
        )

        light_frame.pack(
            fill="x",
            pady=(0, 12)
        )


        explanation = tk.Label(
            light_frame,
            text=(
                "Enter the material-slot number used by each light "
                "on your new model."
            ),
            font=("Segoe Script", 10),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        explanation.pack(
            pady=(10, 5)
        )


        light_grid = tk.Frame(
            light_frame,
            bg="#2b2b2b"
        )

        light_grid.pack(
            pady=(5, 12)
        )


        for column, light_name in enumerate(
            ["LF", "RF", "LR", "RR"]
        ):

            container = tk.Frame(
                light_grid,
                bg="#2b2b2b"
            )

            container.grid(
                row=0,
                column=column,
                padx=15
            )


            tk.Label(
                container,
                text=light_name,
                font=("Segoe UI", 10, "bold"),
                fg="#FFFFFF",
                bg="#2b2b2b"
            ).pack()


            entry = tk.Entry(
                container,
                width=8,
                justify="center",
                bg="#3a3a3a",
                fg="#FFFFFF",
                insertbackground="#FFFFFF",
                relief="flat",
                font=("Consolas", 11)
            )

            entry.pack(
                pady=(5, 0),
                ipady=4
            )


            self.light_entries[
                light_name
            ] = entry


        # ----------------------------------------------------
        # SIREN INDICES
        # ----------------------------------------------------

        self.siren_frame = ttk.LabelFrame(
            main,
            text="New Model Siren Material Slot Numbers"
        )


        siren_grid = tk.Frame(
            self.siren_frame,
            bg="#2b2b2b"
        )

        siren_grid.pack(
            pady=12
        )


        for column, siren_name in enumerate(
            ["Left", "Right"]
        ):

            container = tk.Frame(
                siren_grid,
                bg="#2b2b2b"
            )

            container.grid(
                row=0,
                column=column,
                padx=25
            )


            tk.Label(
                container,
                text=siren_name,
                font=("Segoe UI", 10, "bold"),
                fg="#FFFFFF",
                bg="#2b2b2b"
            ).pack()


            entry = tk.Entry(
                container,
                width=8,
                justify="center",
                bg="#3a3a3a",
                fg="#FFFFFF",
                insertbackground="#FFFFFF",
                relief="flat",
                font=("Consolas", 11)
            )

            entry.pack(
                pady=(5, 0),
                ipady=4
            )


            self.siren_entries[
                siren_name
            ] = entry


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output_frame = ttk.LabelFrame(
            main,
            text="Output UAsset/UEXP"
        )

        output_frame.pack(
            fill="x",
            pady=(0, 10)
        )


        output_row = tk.Frame(
            output_frame,
            bg="#2b2b2b"
        )

        output_row.pack(
            fill="x",
            padx=10,
            pady=10
        )


        self.output_entry = tk.Entry(
            output_row,
            textvariable=self.output_uasset,
            bg="#3a3a3a",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat"
        )

        self.output_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5
        )


        browse_output = tk.Button(
            output_row,
            text="Browse...",
            command=self.browse_output,
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#4a4a4a",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )

        browse_output.pack(
            side="left",
            padx=(8, 0)
        )


        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        options_frame = tk.Frame(
            main,
            bg="#2b2b2b"
        )

        options_frame.pack(
            fill="x",
            pady=(0, 8)
        )


        keep_json = tk.Checkbutton(
            options_frame,
            text="Keep modified JSON",
            variable=self.keep_modified_json,
            bg="#2b2b2b",
            fg="#FFFFFF",
            activebackground="#2b2b2b",
            activeforeground="#FFFFFF",
            selectcolor="#3a3a3a",
            cursor="hand2"
        )

        keep_json.pack(
            side="left"
        )

        install_asset = tk.Checkbutton(
            options_frame,
            text="Include game folder structure",
            variable=self.install_converted_asset,
            bg="#2b2b2b",
            fg="#FFFFFF",
            activebackground="#2b2b2b",
            activeforeground="#FFFFFF",
            selectcolor="#3a3a3a",
            cursor="hand2"
        )

        install_asset.pack(
            side="left",
            padx=(20, 0)
        )


        # ----------------------------------------------------
        # CONVERT BUTTON
        # ----------------------------------------------------

        self.convert_button = tk.Button(
            main,
            text="TRANSFER & CONVERT",
            command=self.convert_vehicle,
            font=("Segoe UI", 11, "bold"),
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#ff69b4",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            height=1
        )

        self.convert_button.pack(
            fill="x",
            pady=(3, 12)
        )

        # ----------------------------------------------------
        # MATERIAL SLOT VIEWER
        # ----------------------------------------------------

        self.material_slots_button = tk.Button(
            main,
            text="VIEW MATERIAL SLOTS",
            command=self.view_material_slots,
            font=("Segoe UI", 11, "bold"),
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#ff69b4",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            height=1
        )

        self.material_slots_button.pack(
            fill="x",
            pady=(0, 12)
        )


        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        log_frame = ttk.LabelFrame(
            main,
            text="Log"
        )

        log_frame.pack(
            fill="both",
            expand=True
        )


        self.log_text = tk.Text(
            log_frame,
            wrap="none",
            height=11,
            font=("Consolas", 9),
            state="disabled",
            bg="#1e1e1e",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            selectbackground="#555555",
            selectforeground="#FFFFFF",
            relief="flat",
            borderwidth=0
        )

        self.log_text.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )


        # ----------------------------------------------------
        # CLEAR LOG
        # ----------------------------------------------------

        clear_button = tk.Button(
            main,
            text="Clear Log",
            command=self.clear_log,
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#4a4a4a",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )

        clear_button.pack(
            pady=(8, 8)
        )

        # ----------------------------------------------------
        # WATERMARK
        # ----------------------------------------------------

        watermark_frame = tk.Frame(
            self.root,
            bg="#1f1f1f"
        )

        watermark_frame.pack(
            side="bottom",
            pady=5
        )

        watermark = tk.Label(
            watermark_frame,
            text="Made by ITSM0VER",
            font=("Segoe UI", 8, "italic"),
            fg="#AAAAAA",
            bg="#1f1f1f"
        )

        watermark.pack(
            padx=5,
            pady=2
        )


    def find_reference_for_vehicle(
        self,
        custom_data
    ):

        exports = custom_data.get(
            "Exports",
            []
        )

        if not exports:
            return None, None

        # The main vehicle SkeletalMesh is normally
        # the export named after the vehicle.
        vehicle_name = None

        for export in exports:

            object_name = str(
                export.get(
                    "ObjectName",
                    ""
                )
            )

            if object_name.startswith(
                "GTAVehicleUserData"
            ):
                continue

            if object_name:
                vehicle_name = object_name
                break

        if not vehicle_name:
            return None, None


        # --------------------------------------------------------
        # Exact reference filename
        # --------------------------------------------------------

        exact_path = os.path.join(
            REFERENCES_PATH,
            vehicle_name + ".json"
        )

        if os.path.isfile(
            exact_path
        ):

            return vehicle_name, exact_path


        # --------------------------------------------------------
        # Search recursively
        # --------------------------------------------------------

        for root_dir, dirs, files in os.walk(
            REFERENCES_PATH
        ):

            for filename in files:

                if not filename.lower().endswith(
                    ".json"
                ):
                    continue

                if os.path.splitext(
                    filename
                )[0].lower() == vehicle_name.lower():

                    return (
                        vehicle_name,
                        os.path.join(
                            root_dir,
                            filename
                        )
                    )


        return vehicle_name, None

    # ========================================================
    # SIREN VISIBILITY
    # ========================================================

    def update_siren_visibility(
        self,
        reference_data
    ):

        user_data = self.find_vehicle_user_data(
            reference_data
        )

        has_sirens = False

        if user_data:

            for prop in user_data.get(
                "Data",
                []
            ):

                if prop.get("Name") in (
                    "LeftSirenIndex",
                    "RightSirenIndex"
                ):

                    has_sirens = True
                    break


        if has_sirens:

            if not self.siren_frame.winfo_ismapped():

                self.siren_frame.pack(
                    fill="x",
                    pady=(0, 12),
                    before=self.output_entry.master.master
                )

        else:

            self.siren_frame.pack_forget()

            for entry in self.siren_entries.values():

                entry.delete(
                    0,
                    "end"
                )


    # ========================================================
    # FIND GTAVEHICLEUSERDATA
    # ========================================================

    def find_vehicle_user_data(
        self,
        data
    ):

        for export in data.get(
            "Exports",
            []
        ):

            object_name = str(
                export.get(
                    "ObjectName",
                    ""
                )
            )

            if object_name.startswith(
                "GTAVehicleUserData"
            ):
                return export

        return None


    # ========================================================
    # WHEEL MESH HELPERS
    # ========================================================

    def get_wheel_mesh_path(
        self,
        data
    ):

        user_data = (
            self.find_vehicle_user_data(
                data
            )
        )


        if user_data is None:
            return ""


        property_data = self.find_property(
            user_data.get(
                "Data",
                []
            ),
            "WheelMesh"
        )


        if property_data is None:
            return ""


        wheel_mesh_index = (
            property_data.get(
                "Value"
            )
        )


        if not isinstance(
            wheel_mesh_index,
            int
        ) or wheel_mesh_index >= 0:

            return ""


        wheel_mesh_import = self.get_import(
            data,
            wheel_mesh_index
        )


        if wheel_mesh_import is None:
            return ""


        package_index = (
            wheel_mesh_import.get(
                "OuterIndex",
                0
            )
        )


        package_import = self.get_import(
            data,
            package_index
        )


        if package_import is None:
            return ""


        return str(
            package_import.get(
                "ObjectName",
                ""
            )
        )


    def parse_wheel_mesh_path(
        self,
        wheel_mesh_path
    ):

        wheel_mesh_path = (
            wheel_mesh_path
            .strip()
            .replace("\\", "/")
        )


        if not wheel_mesh_path:

            raise ValueError(
                "Wheel Mesh Path cannot be empty."
            )


        if not wheel_mesh_path.startswith(
            "/Game/"
        ):

            raise ValueError(
                "Wheel Mesh Path must start with /Game/."
            )


        wheel_mesh_path = (
            wheel_mesh_path.rstrip("/")
        )


        last_slash = (
            wheel_mesh_path.rfind("/")
        )

        last_dot = (
            wheel_mesh_path.rfind(".")
        )


        # ----------------------------------------------------
        # Support:
        #
        # /Game/Vehicles/SM_Wheel
        #
        # and:
        #
        # /Game/Vehicles/SM_Wheel.SM_Wheel
        # ----------------------------------------------------

        if last_dot > last_slash:

            package_path = (
                wheel_mesh_path[
                    :last_dot
                ]
            )

            mesh_name = (
                wheel_mesh_path[
                    last_dot + 1:
                ]
            )

        else:

            package_path = (
                wheel_mesh_path
            )

            mesh_name = (
                wheel_mesh_path[
                    last_slash + 1:
                ]
            )


        if not package_path:

            raise ValueError(
                "Invalid Wheel Mesh Path."
            )


        if not mesh_name:

            raise ValueError(
                "Could not determine the Wheel Mesh name."
            )


        return (
            package_path,
            mesh_name
        )


    def set_wheel_mesh_reference(
        self,
        custom_data,
        properties,
        wheel_mesh_path
    ):

        # ----------------------------------------------------
        # Parse the user-entered Wheel Mesh path.
        #
        # Example:
        #
        # /Game/ViceCity/Vehicles/SM_Wheel_Custom
        #
        # becomes:
        #
        # Package Path = /Game/ViceCity/Vehicles/SM_Wheel_Custom
        # Mesh Name    = SM_Wheel_Custom
        # ----------------------------------------------------

        package_path, mesh_name = (
            self.parse_wheel_mesh_path(
                wheel_mesh_path
            )
        )


        # ----------------------------------------------------
        # Find the WheelMesh property.
        # ----------------------------------------------------

        wheel_mesh_property = (
            self.find_property(
                properties,
                "WheelMesh"
            )
        )


        if wheel_mesh_property is None:

            raise RuntimeError(
                "The vehicle does not contain "
                "a WheelMesh property."
            )


        # ----------------------------------------------------
        # Get the EXISTING WheelMesh import index.
        #
        # Example:
        #
        # Value = -40
        # ----------------------------------------------------

        wheel_mesh_index = (
            wheel_mesh_property.get(
                "Value"
            )
        )


        if not isinstance(
            wheel_mesh_index,
            int
        ) or wheel_mesh_index >= 0:

            raise RuntimeError(
                "WheelMesh does not contain "
                "a valid import reference."
            )


        # ----------------------------------------------------
        # Get the EXISTING StaticMesh import.
        #
        # We are editing this import directly.
        # ----------------------------------------------------

        wheel_mesh_import = (
            self.get_import(
                custom_data,
                wheel_mesh_index
            )
        )


        if wheel_mesh_import is None:

            raise RuntimeError(
                "Could not find the existing "
                "WheelMesh StaticMesh import."
            )


        # ----------------------------------------------------
        # The StaticMesh import's OuterIndex points to
        # the EXISTING Package import.
        # ----------------------------------------------------

        package_index = (
            wheel_mesh_import.get(
                "OuterIndex"
            )
        )


        if not isinstance(
            package_index,
            int
        ) or package_index >= 0:

            raise RuntimeError(
                "Could not find the existing "
                "WheelMesh Package import."
            )


        wheel_mesh_package = (
            self.get_import(
                custom_data,
                package_index
            )
        )


        if wheel_mesh_package is None:

            raise RuntimeError(
                "Could not find the existing "
                "WheelMesh Package import."
            )


        # ----------------------------------------------------
        # Verify that the existing imports are the expected
        # Unreal types.
        # ----------------------------------------------------

        if (
            wheel_mesh_import.get(
                "ClassName"
            )
            != "StaticMesh"
        ):

            raise RuntimeError(
                "WheelMesh reference does not "
                "point to a StaticMesh import."
            )


        if (
            wheel_mesh_package.get(
                "ClassName"
            )
            != "Package"
        ):

            raise RuntimeError(
                "WheelMesh OuterIndex does not "
                "point to a Package import."
            )


        # ----------------------------------------------------
        # EDIT THE EXISTING PACKAGE IMPORT IN-PLACE.
        #
        # OLD:
        # /Game/ViceCity/Vehicles/SM_Wheel_Sport
        #
        # NEW:
        # /Game/ViceCity/Vehicles/SM_Wheel_Custom
        # ----------------------------------------------------

        wheel_mesh_package[
            "ObjectName"
        ] = package_path


        # ----------------------------------------------------
        # EDIT THE EXISTING STATICMESH IMPORT IN-PLACE.
        #
        # OLD:
        # SM_Wheel_Sport
        #
        # NEW:
        # SM_Wheel_Custom
        # ----------------------------------------------------

        wheel_mesh_import[
            "ObjectName"
        ] = mesh_name


        # ----------------------------------------------------
        # KEEP THE EXISTING OuterIndex.
        #
        # DO NOT create another Package import.
        # DO NOT create another StaticMesh import.
        # ----------------------------------------------------

        wheel_mesh_import[
            "OuterIndex"
        ] = package_index


        # ----------------------------------------------------
        # WheelMesh.Value already points to this EXISTING
        # StaticMesh import.
        #
        # DO NOT change it.
        # ----------------------------------------------------


        # ----------------------------------------------------
        # Make sure the new Package and StaticMesh names
        # exist in the NameMap.
        # ----------------------------------------------------

        self.ensure_names_from_object(
            custom_data,
            wheel_mesh_package
        )


        self.ensure_names_from_object(
            custom_data,
            wheel_mesh_import
        )


        return wheel_mesh_index

    # ========================================================
    # FIND SKELETAL MESH EXPORT
    # ========================================================

    def find_skeletal_mesh_export(
        self,
        data
    ):

        imports = data.get(
            "Imports",
            []
        )

        for index, export in enumerate(
            data.get(
                "Exports",
                []
            ),
            start=1
        ):

            class_index = export.get(
                "ClassIndex"
            )

            if not isinstance(
                class_index,
                int
            ):
                continue

            if class_index >= 0:
                continue

            import_number = (
                -class_index
            )

            if not (
                1 <= import_number <= len(imports)
            ):
                continue

            class_import = imports[
                import_number - 1
            ]

            if class_import.get(
                "ObjectName"
            ) == "SkeletalMesh":

                return index, export

        return None, None


    # ========================================================
    # IMPORT HELPERS
    # ========================================================

    def get_import(
        self,
        data,
        package_index
    ):

        if not isinstance(
            package_index,
            int
        ):
            return None

        if package_index >= 0:
            return None

        number = -package_index

        imports = data.get(
            "Imports",
            []
        )

        if not (
            1 <= number <= len(imports)
        ):
            return None

        return imports[
            number - 1
        ]


    def import_full_path(
        self,
        data,
        package_index,
        cache=None
    ):

        if cache is None:
            cache = {}

        if package_index in cache:
            return cache[
                package_index
            ]

        imp = self.get_import(
            data,
            package_index
        )

        if imp is None:
            return None

        object_name = str(
            imp.get(
                "ObjectName",
                ""
            )
        )

        outer_index = imp.get(
            "OuterIndex",
            0
        )

        if outer_index == 0:

            result = object_name

        elif outer_index < 0:

            outer_path = self.import_full_path(
                data,
                outer_index,
                cache
            )

            if outer_path:
                result = (
                    outer_path
                    + "."
                    + object_name
                )

            else:
                result = object_name

        else:

            result = object_name


        cache[
            package_index
        ] = result

        return result


    def import_identity(
        self,
        data,
        package_index
    ):

        imp = self.get_import(
            data,
            package_index
        )

        if imp is None:
            return None

        outer_index = imp.get(
            "OuterIndex",
            0
        )

        class_index = imp.get(
            "ClassIndex",
            0
        )

        template_index = imp.get(
            "TemplateIndex",
            0
        )

        return (
            self.import_full_path(
                data,
                package_index
            ),
            self.import_full_path(
                data,
                class_index
            ),
            self.import_full_path(
                data,
                template_index
            )
        )


    # ========================================================
    # FIND MATCHING IMPORT
    # ========================================================

    def find_matching_import(
        self,
        custom_data,
        reference_data,
        reference_index
    ):

        reference_identity = (
            self.import_identity(
                reference_data,
                reference_index
            )
        )

        if reference_identity is None:
            return None

        imports = custom_data.get(
            "Imports",
            []
        )

        for number in range(
            1,
            len(imports) + 1
        ):

            custom_index = -number

            custom_identity = (
                self.import_identity(
                    custom_data,
                    custom_index
                )
            )

            if (
                custom_identity
                == reference_identity
            ):

                return custom_index

        return None


        # ========================================================
        # ENSURE NAME MAP ENTRY
        # ========================================================

        def ensure_name_map_entry(
            self,
            custom_data,
            name
        ):

            if name is None:
                return

            name = str(name)

            if not name:
                return

            name_map = custom_data.setdefault(
                "NameMap",
                []
            )

            if name not in name_map:

                name_map.append(
                    name
                )

    # ========================================================
    # ENSURE NAMEMAP ENTRIES
    # ========================================================

    def ensure_name_map_entry(
        self,
        custom_data,
        name
    ):

        if name is None:
            return

        name = str(name)

        if not name:
            return

        name_map = custom_data.setdefault(
            "NameMap",
            []
        )

        if name not in name_map:

            name_map.append(
                name
            )


    def ensure_names_from_object(
        self,
        custom_data,
        obj
    ):
        """
        Scan a copied UAsset JSON object and make sure every
        field that represents an FName/name reference exists
        in the custom asset's NameMap.
        """

        if isinstance(obj, dict):

            for key, value in obj.items():

                # These fields contain FName-style references
                # that need to exist in the NameMap.
                if key in {
                    "ObjectName",
                    "Name",
                    "StructType",
                    "EnumType",
                    "EnumValue",
                    "ByteType",
                    "ClassPackage",
                    "ClassName",
                }:

                    if isinstance(value, str):

                        self.ensure_name_map_entry(
                            custom_data,
                            value
                        )

                # Continue recursively through nested
                # properties / structures.
                else:

                    self.ensure_names_from_object(
                        custom_data,
                        value
                    )

        elif isinstance(obj, list):

            for item in obj:

                self.ensure_names_from_object(
                    custom_data,
                    item
                )

    # ========================================================
    # ADD / REMAP IMPORT
    # ========================================================

    def copy_import(
        self,
        custom_data,
        reference_data,
        reference_index,
        import_cache
    ):

        if reference_index == 0:

            return 0


        if reference_index >= 0:

            raise ValueError(
                "copy_import expected an import FPackageIndex."
            )


        # ----------------------------------------------------
        # Already copied during this operation
        # ----------------------------------------------------

        if reference_index in import_cache:

            return import_cache[
                reference_index
            ]


        # ----------------------------------------------------
        # Does custom already contain it?
        # ----------------------------------------------------

        existing = self.find_matching_import(
            custom_data,
            reference_data,
            reference_index
        )

        if existing is not None:

            import_cache[
                reference_index
            ] = existing

            return existing


        # ----------------------------------------------------
        # Get reference import
        # ----------------------------------------------------

        reference_import = self.get_import(
            reference_data,
            reference_index
        )

        if reference_import is None:

            raise ValueError(
                (
                    "Reference import "
                    f"{reference_index} could not be resolved."
                )
            )


        # ----------------------------------------------------
        # CREATE IMPORT IMMEDIATELY
        #
        # This is important.
        #
        # The import must be appended BEFORE recursively
        # processing its dependencies so that its negative
        # package index is permanently correct.
        # ----------------------------------------------------

        custom_imports = (
            custom_data["Imports"]
        )


        new_import = copy.deepcopy(
            reference_import
        )

        # Make sure every name used by this imported
        # object exists in the custom asset NameMap.
        self.ensure_names_from_object(
            custom_data,
            new_import
        )

        custom_imports.append(
            new_import
        )


        new_index = -len(
            custom_imports
        )


        # Cache the REAL index immediately.
        #
        # This also protects against recursive references
        # back to this same import.
        #

        import_cache[
            reference_index
        ] = new_index


        # ----------------------------------------------------
        # Remap OuterIndex
        # ----------------------------------------------------

        outer_index = new_import.get(
            "OuterIndex",
            0
        )

        if (
            isinstance(
                outer_index,
                int
            )
            and outer_index < 0
        ):

            new_import[
                "OuterIndex"
            ] = self.copy_import(
                custom_data,
                reference_data,
                outer_index,
                import_cache
            )


        # ----------------------------------------------------
        # Remap ClassIndex
        # ----------------------------------------------------

        class_index = new_import.get(
            "ClassIndex",
            0
        )

        if (
            isinstance(
                class_index,
                int
            )
            and class_index < 0
        ):

            new_import[
                "ClassIndex"
            ] = self.copy_import(
                custom_data,
                reference_data,
                class_index,
                import_cache
            )


        # ----------------------------------------------------
        # Remap TemplateIndex
        # ----------------------------------------------------

        template_index = new_import.get(
            "TemplateIndex",
            0
        )

        if (
            isinstance(
                template_index,
                int
            )
            and template_index < 0
        ):

            new_import[
                "TemplateIndex"
            ] = self.copy_import(
                custom_data,
                reference_data,
                template_index,
                import_cache
            )


        # ----------------------------------------------------
        # Return the actual index of this import
        # ----------------------------------------------------

        return new_index


    # ========================================================
    # REMAP PROPERTY OBJECT REFERENCES
    # ========================================================

    def remap_property_references(
        self,
        properties,
        custom_data,
        reference_data,
        import_cache
    ):

        for prop in properties:

            if not isinstance(
                prop,
                dict
            ):
                continue


            # ObjectPropertyData
            if (
                prop.get("$type", "")
                .find("ObjectPropertyData")
                != -1
            ):

                value = prop.get(
                    "Value"
                )

                if (
                    isinstance(value, int)
                    and value < 0
                ):

                    prop[
                        "Value"
                    ] = self.copy_import(
                        custom_data,
                        reference_data,
                        value,
                        import_cache
                    )


            # Array / Struct / nested properties
            value = prop.get(
                "Value"
            )

            if isinstance(
                value,
                list
            ):

                self.remap_nested_values(
                    value,
                    custom_data,
                    reference_data,
                    import_cache
                )


    def remap_nested_values(
        self,
        value,
        custom_data,
        reference_data,
        import_cache
    ):

        if isinstance(
            value,
            list
        ):

            for item in value:

                if isinstance(
                    item,
                    dict
                ):

                    if (
                        item.get("$type", "")
                        .find("ObjectPropertyData")
                        != -1
                    ):

                        item_value = item.get(
                            "Value"
                        )

                        if (
                            isinstance(item_value, int)
                            and item_value < 0
                        ):

                            item[
                                "Value"
                            ] = self.copy_import(
                                custom_data,
                                reference_data,
                                item_value,
                                import_cache
                            )

                    self.remap_nested_values(
                        item.get(
                            "Value"
                        ),
                        custom_data,
                        reference_data,
                        import_cache
                    )


    # ========================================================
    # FIND PROPERTY
    # ========================================================

    def find_property(
        self,
        properties,
        property_name
    ):

        for prop in properties:

            if (
                isinstance(prop, dict)
                and prop.get("Name")
                == property_name
            ):

                return prop

        return None


    # ========================================================
    # REPLACE / ADD PROPERTY
    # ========================================================

    def replace_or_add_property(
        self,
        properties,
        new_property
    ):

        property_name = new_property.get(
            "Name"
        )

        for index, existing in enumerate(
            properties
        ):

            if (
                isinstance(existing, dict)
                and existing.get("Name")
                == property_name
            ):

                properties[
                    index
                ] = new_property

                return


        properties.append(
            new_property
        )


    # ========================================================
    # CREATE ASSET USER DATA PROPERTY
    # ========================================================

    def create_asset_user_data_property(
        self,
        export_index
    ):

        return {
            "$type": (
                "UAssetAPI.PropertyTypes.Objects."
                "ArrayPropertyData, UAssetAPI"
            ),
            "ArrayType": "ObjectProperty",
            "Name": "AssetUserData",
            "ArrayIndex": 0,
            "PropertyGuid": None,
            "IsZero": False,
            "PropertyTagFlags": "None",
            "PropertyTypeName": None,
            "PropertyTagExtensions": "NoExtension",
            "Value": [
                {
                    "$type": (
                        "UAssetAPI.PropertyTypes.Objects."
                        "ObjectPropertyData, UAssetAPI"
                    ),
                    "Name": "0",
                    "ArrayIndex": 0,
                    "PropertyGuid": None,
                    "IsZero": False,
                    "PropertyTagFlags": "None",
                    "PropertyTypeName": None,
                    "PropertyTagExtensions": "NoExtension",
                    "Value": export_index
                }
            ]
        }


    # ========================================================
    # GET UNIQUE EXPORT NAME
    # ========================================================

    def get_unique_export_name(
        self,
        custom_data,
        reference_export
    ):

        base_name = str(
            reference_export.get(
                "ObjectName",
                "GTAVehicleUserData"
            )
        )

        existing_names = {
            str(
                export.get(
                    "ObjectName",
                    ""
                )
            )
            for export in custom_data.get(
                "Exports",
                []
            )
        }


        if base_name not in existing_names:

            return base_name


        number = 1

        while True:

            candidate = (
                f"{base_name}_{number}"
            )

            if candidate not in existing_names:

                return candidate

            number += 1


    # ========================================================
    # BUILD GTAVEHICLEUSERDATA
    # ========================================================

    def build_vehicle_user_data(
        self,
        custom_data,
        reference_data,
        reference_export,
        custom_skeletal_export_index,
        new_light_indices,
        new_siren_indices,
        wheel_mesh_path
    ):

        import_cache = {}


        # ----------------------------------------------------
        # Copy the reference export as our starting structure.
        # ----------------------------------------------------

        new_export = copy.deepcopy(
            reference_export
        )


        # ----------------------------------------------------
        # The copied GTAVehicleUserData export can contain
        # many FName references which may not exist in the
        # custom asset's NameMap.
        # ----------------------------------------------------

        self.ensure_names_from_object(
            custom_data,
            new_export
        )


        new_export[
            "ObjectName"
        ] = self.get_unique_export_name(
            custom_data,
            reference_export
        )


        # ----------------------------------------------------
        # This export will be appended to the custom package.
        # Its OuterIndex must point to the custom SkeletalMesh.
        # ----------------------------------------------------

        new_export[
            "OuterIndex"
        ] = custom_skeletal_export_index


        # ----------------------------------------------------
        # Remap the class import.
        # ----------------------------------------------------

        reference_class = reference_export.get(
            "ClassIndex",
            0
        )

        if reference_class < 0:

            new_export[
                "ClassIndex"
            ] = self.copy_import(
                custom_data,
                reference_data,
                reference_class,
                import_cache
            )


        # ----------------------------------------------------
        # Remap TemplateIndex.
        # ----------------------------------------------------

        reference_template = reference_export.get(
            "TemplateIndex",
            0
        )

        if reference_template < 0:

            new_export[
                "TemplateIndex"
            ] = self.copy_import(
                custom_data,
                reference_data,
                reference_template,
                import_cache
            )


        # ----------------------------------------------------
        # Copy only the relevant vehicle data.
        # ----------------------------------------------------

        reference_properties = (
            reference_export.get(
                "Data",
                []
            )
        )


        new_properties = []


        for reference_property in (
            reference_properties
        ):

            property_name = (
                reference_property.get(
                    "Name"
                )
            )


            if property_name in (
                TRANSFER_PROPERTIES
                | LIGHT_INDEX_PROPERTIES
            ):

                new_properties.append(
                    copy.deepcopy(
                        reference_property
                    )
                )


        # ----------------------------------------------------
        # Remap object references inside copied properties.
        # ----------------------------------------------------

        self.remap_property_references(
            new_properties,
            custom_data,
            reference_data,
            import_cache
        )


        # ----------------------------------------------------
        # Replace the WheelMesh with the USER value.
        # ----------------------------------------------------

        self.set_wheel_mesh_reference(
            custom_data,
            new_properties,
            wheel_mesh_path
        )


        # ----------------------------------------------------
        # Replace the light indices with USER values.
        # ----------------------------------------------------

        for property_name in (
            LIGHT_INDEX_PROPERTIES
        ):

            if property_name not in new_light_indices:
                continue

            property_data = self.find_property(
                new_properties,
                property_name
            )

            if property_data is None:

                # Create a basic IntPropertyData.
                property_data = {
                    "$type": (
                        "UAssetAPI.PropertyTypes.Objects."
                        "IntPropertyData, UAssetAPI"
                    ),
                    "Name": property_name,
                    "ArrayIndex": 0,
                    "PropertyGuid": None,
                    "IsZero": False,
                    "PropertyTagFlags": "None",
                    "PropertyTypeName": None,
                    "PropertyTagExtensions": "NoExtension",
                    "Value": new_light_indices[
                        property_name
                    ]
                }

                new_properties.append(
                    property_data
                )

            else:

                property_data[
                    "Value"
                ] = new_light_indices[
                    property_name
                ]


        # ----------------------------------------------------
        # Replace siren indices when applicable.
        # ----------------------------------------------------

        siren_mapping = {
            "LeftSirenIndex": "Left",
            "RightSirenIndex": "Right"
        }


        for property_name, field_name in (
            siren_mapping.items()
        ):

            if field_name not in new_siren_indices:
                continue

            property_data = self.find_property(
                new_properties,
                property_name
            )

            if property_data is not None:

                property_data[
                    "Value"
                ] = new_siren_indices[
                    field_name
                ]


        new_export[
            "Data"
        ] = new_properties


        # ----------------------------------------------------
        # Rebuild export dependency indices.
        # ----------------------------------------------------

        for dependency_key in (
            "SerializationBeforeSerializationDependencies",
            "CreateBeforeSerializationDependencies",
            "SerializationBeforeCreateDependencies",
            "CreateBeforeCreateDependencies"
        ):

            dependencies = reference_export.get(
                dependency_key,
                []
            )

            remapped_dependencies = []


            for dependency in dependencies:

                if not isinstance(
                    dependency,
                    int
                ):

                    continue


                if dependency < 0:

                    remapped = self.copy_import(
                        custom_data,
                        reference_data,
                        dependency,
                        import_cache
                    )

                    remapped_dependencies.append(
                        remapped
                    )

                elif dependency > 0:

                    # Positive package indices are exports.
                    #
                    # The GTAVehicleUserData reference normally
                    # depends on its owning SkeletalMesh.
                    #
                    # Since our new user-data export is being
                    # attached to the custom SkeletalMesh,
                    # references to the original owner become
                    # references to the custom owner.
                    remapped_dependencies.append(
                        custom_skeletal_export_index
                    )

                else:

                    remapped_dependencies.append(
                        dependency
                    )


            new_export[
                dependency_key
            ] = remapped_dependencies


        # ----------------------------------------------------
        # Append export.
        # ----------------------------------------------------

        custom_data[
            "Exports"
        ].append(
            new_export
        )


        new_export_index = len(
            custom_data[
                "Exports"
            ]
        )


        return (
            new_export,
            new_export_index,
            import_cache
        )


    # ========================================================
    # ADD ASSET USER DATA
    # ========================================================

    def add_asset_user_data(
        self,
        custom_data,
        skeletal_export,
        vehicle_user_data_export_index
    ):

        properties = skeletal_export.setdefault(
            "Data",
            []
        )


        # ----------------------------------------------------
        # Ensure AssetUserData exists in the NameMap.
        # ----------------------------------------------------

        self.ensure_name_map_entry(
            custom_data,
            "AssetUserData"
        )


        asset_user_data = self.find_property(
            properties,
            "AssetUserData"
        )


        if asset_user_data is None:

            properties.append(
                self.create_asset_user_data_property(
                    vehicle_user_data_export_index
                )
            )

            return


        # ----------------------------------------------------
        # Existing AssetUserData array.
        # ----------------------------------------------------

        values = asset_user_data.setdefault(
            "Value",
            []
        )


        # Check whether the object is already there.
        for item in values:

            if (
                isinstance(item, dict)
                and item.get("Value")
                == vehicle_user_data_export_index
            ):

                return


        values.append(
            {
                "$type": (
                    "UAssetAPI.PropertyTypes.Objects."
                    "ObjectPropertyData, UAssetAPI"
                ),
                "Name": str(
                    len(values)
                ),
                "ArrayIndex": len(values),
                "PropertyGuid": None,
                "IsZero": False,
                "PropertyTagFlags": "None",
                "PropertyTypeName": None,
                "PropertyTagExtensions": "NoExtension",
                "Value": vehicle_user_data_export_index
            }
        )


    # ========================================================
    # PROCESS VEHICLE
    # ========================================================

    def process_vehicle(
        self,
        custom_data,
        reference_data,
        new_light_indices,
        new_siren_indices,
        wheel_mesh_path
    ):

        # ----------------------------------------------------
        # Find custom SkeletalMesh.
        # ----------------------------------------------------

        skeletal_index, skeletal_export = (
            self.find_skeletal_mesh_export(
                custom_data
            )
        )


        if skeletal_export is None:

            raise RuntimeError(
                "Could not find the SkeletalMesh export "
                "in the custom JSON."
            )


        self.log(
            f"Custom SkeletalMesh export: {skeletal_index}"
        )


        # ----------------------------------------------------
        # Find OG vehicle user data.
        # ----------------------------------------------------

        reference_user_data = (
            self.find_vehicle_user_data(
                reference_data
            )
        )


        if reference_user_data is None:

            raise RuntimeError(
                "The selected reference JSON does not "
                "contain GTAVehicleUserData."
            )


        self.log(
            (
                "Reference vehicle data found: "
                f"{reference_user_data['ObjectName']}"
            )
        )


        # ----------------------------------------------------
        # Make sure custom package has required top-level
        # collections.
        # ----------------------------------------------------

        custom_data.setdefault(
            "Imports",
            []
        )

        custom_data.setdefault(
            "Exports",
            []
        )

        custom_data.setdefault(
            "DependsMap",
            []
        )


        # ----------------------------------------------------
        # Build new GTAVehicleUserData.
        # ----------------------------------------------------

        (
            new_user_data,
            new_user_data_index,
            import_cache
        ) = self.build_vehicle_user_data(
            custom_data,
            reference_data,
            reference_user_data,
            skeletal_index,
            new_light_indices,
            new_siren_indices,
            wheel_mesh_path
        )


        self.log(
            (
                "Added "
                f"{new_user_data['ObjectName']} "
                f"as export {new_user_data_index}"
            )
        )


        # ----------------------------------------------------
        # Add AssetUserData to SkeletalMesh.
        # ----------------------------------------------------

        self.add_asset_user_data(
            custom_data,
            skeletal_export,
            new_user_data_index
        )


        self.log(
            (
                "Added GTAVehicleUserData reference "
                "to SkeletalMesh AssetUserData."
            )
        )


        # ----------------------------------------------------
        # Add DependsMap entry for the new export.
        # ----------------------------------------------------

        depends_map = custom_data[
            "DependsMap"
        ]


        while len(depends_map) < new_user_data_index:

            depends_map.append(
                []
            )


        # The reference DependsMap is normally empty for
        # these assets, but preserve its structure if present.
        reference_export_index = (
            reference_data[
                "Exports"
            ].index(
                reference_user_data
            )
            + 1
        )


        reference_depends = []

        if (
            reference_export_index - 1
            < len(
                reference_data.get(
                    "DependsMap",
                    []
                )
            )
        ):

            reference_depends = copy.deepcopy(
                reference_data[
                    "DependsMap"
                ][
                    reference_export_index - 1
                ]
            )


        remapped_depends = []


        for dependency in reference_depends:

            if (
                isinstance(dependency, int)
                and dependency < 0
            ):

                remapped_depends.append(
                    import_cache.get(
                        dependency,
                        dependency
                    )
                )

            elif (
                isinstance(dependency, int)
                and dependency > 0
            ):

                remapped_depends.append(
                    skeletal_index
                )

            else:

                remapped_depends.append(
                    dependency
                )


        depends_map[
            new_user_data_index - 1
        ] = remapped_depends


        return custom_data


    # ========================================================
    # VALIDATE INTEGER
    # ========================================================

    def read_integer_entry(
        self,
        entry,
        field_name
    ):

        value = entry.get().strip()

        if not value:

            raise ValueError(
                f"{field_name} cannot be empty."
            )

        try:

            number = int(
                value
            )

        except ValueError:

            raise ValueError(
                f"{field_name} must be a whole number."
            )


        if number < 0:

            raise ValueError(
                f"{field_name} cannot be negative."
            )


        return number


    # ========================================================
    # BROWSE JSON
    # ========================================================

    def browse_json(self):

        filename = filedialog.askopenfilename(
            title="Select Custom Vehicle JSON or UAsset",
            filetypes=[
                (
                    "UAsset files",
                    "*.uasset"
                ),
                (
                    "JSON files",
                    "*.json"
                )
            ]
        )

        if not filename:
            return


        # ----------------------------------------------------
        # REMOVE PREVIOUS TEMPORARY JSON
        # ----------------------------------------------------

        if self.temporary_input_json:

            try:

                if os.path.isfile(
                    self.temporary_input_json
                ):

                    os.remove(
                        self.temporary_input_json
                    )

                temporary_folder = os.path.dirname(
                    self.temporary_input_json
                )

                if (
                    os.path.basename(
                        temporary_folder
                    ).lower() == "temp"
                    and os.path.isdir(
                        temporary_folder
                    )
                    and not os.listdir(
                        temporary_folder
                    )
                ):

                    os.rmdir(
                        temporary_folder
                    )

            except OSError:

                pass

            self.temporary_input_json = None


        source_filename = filename

        source_extension = (
            os.path.splitext(
                filename
            )[1]
            .lower()
        )


        # ----------------------------------------------------
        # CONVERT UASSET TO TEMPORARY JSON
        # ----------------------------------------------------

        if source_extension == ".uasset":

            if not os.path.isfile(
                UASSETGUI_PATH
            ):

                messagebox.showerror(
                    "UAssetGUI Not Found",
                    (
                        "UAssetGUI.exe could not be found.\n\n"
                        "Expected:\n"
                        f"{UASSETGUI_PATH}"
                    )
                )

                return


            self.log(
                f"UAsset selected: {filename}"
            )

            self.log(
                "Converting UAsset to temporary JSON..."
            )


            temporary_json = None


            try:

                input_directory = os.path.dirname(
                    filename
                )

                temporary_folder = os.path.join(
                    input_directory,
                    "TEMP"
                )


                os.makedirs(
                    temporary_folder,
                    exist_ok=True
                )


                base_name = os.path.splitext(
                    os.path.basename(
                        filename
                    )
                )[0]


                temporary_json = os.path.join(
                    temporary_folder,
                    base_name + ".json"
                )

                counter = 2

                while os.path.exists(
                    temporary_json
                ):

                    temporary_json = os.path.join(
                        temporary_folder,
                        f"{base_name}_{counter}.json"
                    )

                    counter += 1


                result = subprocess.run(
                    [
                        UASSETGUI_PATH,
                        "tojson",
                        filename,
                        temporary_json,
                        "VER_UE4_26"
                    ],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )


            except Exception as error:

                try:

                    if (
                        temporary_json
                        and os.path.isfile(
                            temporary_json
                        )
                    ):

                        os.remove(
                            temporary_json
                        )

                    if (
                        "temporary_folder" in locals()
                        and os.path.isdir(
                            temporary_folder
                        )
                        and not os.listdir(
                            temporary_folder
                        )
                    ):

                        os.rmdir(
                            temporary_folder
                        )

                except OSError:

                    pass


                messagebox.showerror(
                    "UAssetGUI Error",
                    (
                        "Could not convert the UAsset to JSON.\n\n"
                        f"{error}"
                    )
                )

                return


            if (
                result.returncode != 0
                or not os.path.isfile(
                    temporary_json
                )
            ):

                error_text = (
                    result.stderr.strip()
                )

                if not error_text:

                    error_text = (
                        result.stdout.strip()
                    )

                if not error_text:

                    error_text = (
                        "Unknown UAssetGUI error."
                    )


                try:

                    if os.path.isfile(
                        temporary_json
                    ):

                        os.remove(
                            temporary_json
                        )

                    if (
                        os.path.isdir(
                            temporary_folder
                        )
                        and not os.listdir(
                            temporary_folder
                        )
                    ):

                        os.rmdir(
                            temporary_folder
                        )

                except OSError:

                    pass


                messagebox.showerror(
                    "JSON Conversion Failed",
                    (
                        "UAssetGUI could not convert "
                        "the UAsset to JSON.\n\n"
                        f"{error_text}"
                    )
                )

                return


            self.temporary_input_json = (
                temporary_json
            )

            filename = temporary_json


            self.log(
                (
                    "Temporary JSON created: "
                    f"{temporary_json}"
                )
            )


        elif source_extension != ".json":

            messagebox.showerror(
                "Invalid File",
                "Please select a .json or .uasset file."
            )

            return


        # ----------------------------------------------------
        # SET INPUT JSON
        # ----------------------------------------------------

        self.input_json.set(
            filename
        )


        # ----------------------------------------------------
        # CREATE OUTPUT PATH FROM ORIGINAL FILE
        # ----------------------------------------------------

        base_name = os.path.splitext(
            os.path.basename(
                source_filename
            )
        )[0]

        # Remove duplicate/custom suffixes such as "(2)"
        import re

        base_name = re.sub(
            r"\s*\(\d+\)$",
            "",
            base_name
        )

        output_directory = os.path.join(
            os.path.dirname(
                source_filename
            ),
            "Converted Vehicles"
        )

        output_name = (
            base_name
            + ".uasset"
        )

        output_path = os.path.join(
            output_directory,
            output_name
        )

        self.output_uasset.set(
            output_path
        )


        if source_extension == ".uasset":

            self.log(
                (
                    "Using temporary JSON for vehicle "
                    "detection and editing."
                )
            )

        else:

            self.log(
                f"Custom JSON selected: {source_filename}"
            )


        # ----------------------------------------------------
        # LOAD CUSTOM JSON
        # ----------------------------------------------------

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                custom_data = json.load(
                    file
                )

            # ------------------------------------------------
            # CHECK FOR EXISTING GTAVehicleUserData
            # ------------------------------------------------

            existing_user_data = self.find_vehicle_user_data(
                custom_data
            )

            if existing_user_data is not None:

                messagebox.showwarning(
                    "GTAVehicleUserData Already Exists",
                    (
                        "This vehicle JSON already contains "
                        "a GTAVehicleUserData export.\n\n"
                        "The vehicle lighting data has already been "
                        "added to this JSON.\n\n"
                        "The process has been cancelled."
                    )
                )

                self.input_json.set("")
                self.output_uasset.set("")

                self.reference_data = None
                self.reference_path = None

                self.detected_vehicle_label.config(
                    text="Select a custom JSON..."
                )

                self.detected_reference_label.config(
                    text=""
                )

                return


            # ------------------------------------------------
            # AUTOMATICALLY FIND OG REFERENCE
            # ------------------------------------------------

            vehicle_name, reference_path = (
                self.find_reference_for_vehicle(
                    custom_data
                )
            )


            if not vehicle_name:

                self.reference_data = None
                self.reference_path = None

                self.wheel_mesh_entry.delete(
                    0,
                    "end"
                )

                self.detected_vehicle_label.config(
                    text="Could not detect vehicle"
                )

                self.detected_reference_label.config(
                    text="",
                    fg="#AAAAAA"
                )

                return


            self.detected_vehicle_label.config(
                text=vehicle_name
            )


            if reference_path:

                self.reference_path = (
                    reference_path
                )


                with open(
                    reference_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    self.reference_data = json.load(
                        file
                    )


                self.detected_reference_label.config(
                    text=(
                        "Reference found: "
                        + os.path.basename(
                            reference_path
                        )
                    ),
                    fg="#AAAAAA"
                )


                self.update_siren_visibility(
                    self.reference_data
                )


                # ------------------------------------------------
                # LOAD CURRENT WHEEL MESH
                # ------------------------------------------------

                current_wheel_mesh = (
                    self.get_wheel_mesh_path(
                        self.reference_data
                    )
                )


                self.wheel_mesh_entry.delete(
                    0,
                    "end"
                )


                if current_wheel_mesh:

                    self.wheel_mesh_entry.insert(
                        0,
                        current_wheel_mesh
                    )


                self.log(
                    (
                        "Automatically matched reference: "
                        + os.path.basename(
                            reference_path
                        )
                    )
                )


            else:

                self.reference_data = None
                self.reference_path = None

                self.wheel_mesh_entry.delete(
                    0,
                    "end"
                )

                self.detected_reference_label.config(
                    text=(
                        "Reference not found in "
                        "Files\\.References"
                    ),
                    fg="#FF8080"
                )


                self.log(
                    (
                        "WARNING: No reference JSON found "
                        f"for {vehicle_name}"
                    )
                )


                # ------------------------------------------------
                # REMOVE TEMPORARY JSON IF NO REFERENCE EXISTS
                # ------------------------------------------------

                if self.temporary_input_json:

                    try:

                        temporary_folder = os.path.dirname(
                            self.temporary_input_json
                        )


                        if os.path.isfile(
                            self.temporary_input_json
                        ):

                            os.remove(
                                self.temporary_input_json
                            )

                            self.log(
                                "Temporary JSON removed."
                            )


                        if (
                            os.path.basename(
                                temporary_folder
                            ).lower() == "temp"
                            and os.path.isdir(
                                temporary_folder
                            )
                            and not os.listdir(
                                temporary_folder
                            )
                        ):

                            os.rmdir(
                                temporary_folder
                            )

                            self.log(
                                "Temporary folder removed."
                            )


                        self.temporary_input_json = None


                    except OSError as error:

                        self.log(
                            (
                                "[WARNING] Could not remove "
                                f"temporary files: {error}"
                            )
                        )


                self.input_json.set("")
                self.output_uasset.set("")

                self.detected_vehicle_label.config(
                    text="Select a custom JSON..."
                )

                return


        except Exception as error:

            self.reference_data = None
            self.reference_path = None

            self.wheel_mesh_entry.delete(
                0,
                "end"
            )

            self.detected_vehicle_label.config(
                text="Error reading JSON"
            )

            self.detected_reference_label.config(
                text=str(error),
                fg="#FF8080"
            )

            self.log(
                f"[ERROR] Could not detect vehicle: {error}"
            )


    # ========================================================
    # BROWSE OUTPUT
    # ========================================================

    def browse_output(self):

        filename = filedialog.asksaveasfilename(
            title="Save Converted UAsset",
            defaultextension=".uasset",
            filetypes=[
                (
                    "Unreal Asset",
                    "*.uasset"
                ),
                (
                    "All Files",
                    "*.*"
                )
            ]
        )

        if not filename:
            return


        self.output_uasset.set(
            filename
        )


    # ========================================================
    # LOG
    # ========================================================

    def log(
        self,
        message
    ):

        self.log_text.config(
            state="normal"
        )

        self.log_text.insert(
            "end",
            message + "\n"
        )

        self.log_text.see(
            "end"
        )

        self.log_text.config(
            state="disabled"
        )


    def clear_log(self):

        self.log_text.config(
            state="normal"
        )

        self.log_text.delete(
            "1.0",
            "end"
        )

        self.log_text.config(
            state="disabled"
        )


    # ========================================================
    # CONVERT
    # ========================================================

    def convert_vehicle(self):

        input_json = (
            self.input_json.get()
            .strip()
        )


        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not input_json:

            messagebox.showerror(
                "Missing JSON",
                "Please select the custom vehicle JSON."
            )

            return


        if not os.path.isfile(
            input_json
        ):

            messagebox.showerror(
                "File Not Found",
                "The selected custom JSON does not exist."
            )

            return


        # ----------------------------------------------------
        # READ WHEEL MESH
        # ----------------------------------------------------

        try:

            wheel_mesh_path = (
                self.wheel_mesh_entry.get()
                .strip()
            )


            self.parse_wheel_mesh_path(
                wheel_mesh_path
            )


            # ------------------------------------------------
            # READ LIGHT INDICES
            # ------------------------------------------------

            new_light_indices = {
                "LightIndex_LF":
                    self.read_integer_entry(
                        self.light_entries["LF"],
                        "LF"
                    ),

                "LightIndex_RF":
                    self.read_integer_entry(
                        self.light_entries["RF"],
                        "RF"
                    ),

                "LightIndex_LR":
                    self.read_integer_entry(
                        self.light_entries["LR"],
                        "LR"
                    ),

                "LightIndex_RR":
                    self.read_integer_entry(
                        self.light_entries["RR"],
                        "RR"
                    )
            }


            new_siren_indices = {}


            if self.siren_frame.winfo_ismapped():

                new_siren_indices = {
                    "Left":
                        self.read_integer_entry(
                            self.siren_entries["Left"],
                            "Siren Left"
                        ),

                    "Right":
                        self.read_integer_entry(
                            self.siren_entries["Right"],
                            "Siren Right"
                        )
                }


        except ValueError as error:

            messagebox.showerror(
                "Invalid Wheel Mesh / Material Slot",
                str(error)
            )

            return


        # ----------------------------------------------------
        # DISABLE BUTTON
        # ----------------------------------------------------

        self.convert_button.config(
            state="disabled"
        )


        try:

            self.log("")

            self.log(
                "========================================"
            )

            self.log(
                "Starting vehicle lighting transfer..."
            )

            self.log(
                f"Custom JSON: {input_json}"
            )


            # ------------------------------------------------
            # LOAD CUSTOM JSON
            # ------------------------------------------------

            with open(
                input_json,
                "r",
                encoding="utf-8"
            ) as file:

                custom_data = json.load(
                    file
                )


            self.log(
                (
                    "Custom package: "
                    f"{len(custom_data.get('Imports', []))} imports / "
                    f"{len(custom_data.get('Exports', []))} exports"
                )
            )


            # ------------------------------------------------
            # AUTO-DETECT REFERENCE
            # ------------------------------------------------

            self.log(
                "Detecting vehicle reference..."
            )


            vehicle_name, reference_path = (
                self.find_reference_for_vehicle(
                    custom_data
                )
            )


            if not vehicle_name:

                raise RuntimeError(
                    (
                        "Could not determine the vehicle name "
                        "from the custom JSON."
                    )
                )


            if not reference_path:

                raise RuntimeError(
                    (
                        "Could not find the OG VCDE reference JSON "
                        f"for '{vehicle_name}' in:\n"
                        f"{REFERENCES_PATH}"
                    )
                )


            self.reference_path = (
                reference_path
            )


            self.log(
                f"Detected vehicle: {vehicle_name}"
            )

            self.log(
                (
                    "Reference: "
                    f"{os.path.basename(reference_path)}"
                )
            )


            # ------------------------------------------------
            # LOAD REFERENCE JSON
            # ------------------------------------------------

            with open(
                reference_path,
                "r",
                encoding="utf-8"
            ) as file:

                reference_data = json.load(
                    file
                )


            self.reference_data = (
                reference_data
            )


            self.log(
                (
                    "Reference package: "
                    f"{len(reference_data.get('Imports', []))} imports / "
                    f"{len(reference_data.get('Exports', []))} exports"
                )
            )


            # ------------------------------------------------
            # PROCESS
            # ------------------------------------------------

            self.log(
                "Transferring vehicle lighting data..."
            )


            self.process_vehicle(
                custom_data,
                reference_data,
                new_light_indices,
                new_siren_indices,
                wheel_mesh_path
            )


            self.log(
                "Vehicle lighting data transferred."
            )


            # ------------------------------------------------
            # LOG VALUES
            # ------------------------------------------------

            self.log(
                f"Wheel Mesh: {wheel_mesh_path}"
            )

            self.log(
                (
                    "Light slots: "
                    f"LF={new_light_indices['LightIndex_LF']} "
                    f"RF={new_light_indices['LightIndex_RF']} "
                    f"LR={new_light_indices['LightIndex_LR']} "
                    f"RR={new_light_indices['LightIndex_RR']}"
                )
            )


            if new_siren_indices:

                self.log(
                    (
                        "Siren slots: "
                        f"Left={new_siren_indices['Left']} "
                        f"Right={new_siren_indices['Right']}"
                    )
                )


            # ------------------------------------------------
            # SAVE MODIFIED JSON
            # ------------------------------------------------

            output_json = (
                os.path.splitext(
                    input_json
                )[0]
                + "_modified.json"
            )


            self.log(
                "Writing modified JSON..."
            )


            with open(
                output_json,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    custom_data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )


            self.log(
                "Modified JSON saved successfully."
            )

            self.log(
                output_json
            )


            # ------------------------------------------------
            # CONVERT MODIFIED JSON TO UASSET
            # ------------------------------------------------

            output_uasset = (
                self.output_uasset.get()
                .strip()
            )

            if not output_uasset:

                raise RuntimeError(
                    "No output UAsset path has been selected."
                )

            # ------------------------------------------------
            # OPTIONAL GAME FOLDER STRUCTURE
            # ------------------------------------------------

            if self.install_converted_asset.get():

                # Find the vehicle asset path in the JSON NameMap.
                # Example:
                # /Game/ViceCity/Vehicles/SKR_Cheetah

                asset_path = None

                for name in custom_data.get("NameMap", []):

                    if (
                        isinstance(name, str)
                        and name.startswith("/Game/")
                        and name.endswith(
                            f"/{vehicle_name}"
                        )
                    ):

                        asset_path = name
                        break

                if not asset_path:

                    raise RuntimeError(
                        "Could not find the vehicle's "
                        "/Game/ asset path in the JSON NameMap."
                    )

                asset_parts = (
                    asset_path
                    .strip("/")
                    .split("/")
                )

                # Example:
                # Game/ViceCity/Vehicles/SKR_Cheetah
                #
                # Becomes:
                # ViceCity/Vehicles

                asset_directories = asset_parts[1:-1]

                output_directory = os.path.join(
                    os.path.dirname(output_uasset),
                    "Gameface",
                    "Content",
                    *asset_directories
                )

                os.makedirs(
                    output_directory,
                    exist_ok=True
                )

                output_uasset = os.path.join(
                    output_directory,
                    asset_parts[-1] + ".uasset"
                )

                self.log(
                    "Game folder structure enabled."
                )

                self.log(
                    f"Asset path: {asset_path}"
                )

                self.log(
                    f"Structured output: {output_uasset}"
                )

            else:

                output_directory = os.path.dirname(
                    output_uasset
                )

                if output_directory:

                    os.makedirs(
                        output_directory,
                        exist_ok=True
                    )

            self.log(
                "Converting modified JSON to UAsset..."
            )

            self.log(
                f"Output UAsset: {output_uasset}"
            )


            if not os.path.isfile(
                UASSETGUI_PATH
            ):

                raise RuntimeError(
                    "UAssetGUI.exe was not found:\n"
                    + UASSETGUI_PATH
                )


            command = [
                UASSETGUI_PATH,
                "fromjson",
                output_json,
                output_uasset
            ]


            self.log(
                "Running UAssetGUI..."
            )


            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(
                    UASSETGUI_PATH
                )
            )


            if result.stdout.strip():

                self.log(
                    result.stdout.strip()
                )


            if result.stderr.strip():

                self.log(
                    result.stderr.strip()
                )


            if result.returncode != 0:

                raise RuntimeError(
                    "UAssetGUI failed to convert "
                    "the modified JSON."
                )


            if not os.path.isfile(
                output_uasset
            ):

                raise RuntimeError(
                    "UAssetGUI completed without "
                    "creating the output UAsset."
                )


            self.log(
                "UAsset created successfully."
            )


            # ------------------------------------------------
            # REMOVE MODIFIED JSON IF NOT REQUESTED
            # ------------------------------------------------

            if not self.keep_modified_json.get():

                try:

                    os.remove(
                        output_json
                    )

                    self.log(
                        "Modified JSON removed."
                    )

                except OSError as error:

                    self.log(
                        (
                            "[WARNING] Could not remove "
                            f"modified JSON: {error}"
                        )
                    )


            # ------------------------------------------------
            # REMOVE TEMPORARY UASSET JSON
            # ------------------------------------------------

            if self.temporary_input_json:

                try:

                    temporary_folder = os.path.dirname(
                        self.temporary_input_json
                    )


                    if os.path.isfile(
                        self.temporary_input_json
                    ):

                        os.remove(
                            self.temporary_input_json
                        )

                        self.log(
                            "Temporary input JSON removed."
                        )


                    if (
                        os.path.basename(
                            temporary_folder
                        ).lower() == "temp"
                        and os.path.isdir(
                            temporary_folder
                        )
                        and not os.listdir(
                            temporary_folder
                        )
                    ):

                        os.rmdir(
                            temporary_folder
                        )

                        self.log(
                            "Temporary folder removed."
                        )


                    self.temporary_input_json = None


                except OSError as error:

                    self.log(
                        (
                            "[WARNING] Could not remove "
                            f"temporary files: {error}"
                        )
                    )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            messagebox.showinfo(
                "Transfer Complete",
                (
                    "Vehicle lighting data was transferred "
                    "successfully.\n\n"
                    f"UAsset:\n{output_uasset}"
                )
            )


        except Exception as error:

            self.log(
                f"[ERROR] {error}"
            )


            messagebox.showerror(
                "Transfer Failed",
                str(error)
            )


        finally:

            if self.temporary_input_json:

                try:

                    temporary_folder = os.path.dirname(
                        self.temporary_input_json
                    )


                    if os.path.isfile(
                        self.temporary_input_json
                    ):

                        os.remove(
                            self.temporary_input_json
                        )

                        self.log(
                            "Temporary input JSON removed."
                        )


                    if (
                        os.path.basename(
                            temporary_folder
                        ).lower() == "temp"
                        and os.path.isdir(
                            temporary_folder
                        )
                        and not os.listdir(
                            temporary_folder
                        )
                    ):

                        os.rmdir(
                            temporary_folder
                        )

                        self.log(
                            "Temporary folder removed."
                        )


                    self.temporary_input_json = None


                except OSError as error:

                    self.log(
                        (
                            "[WARNING] Could not remove "
                            f"temporary files: {error}"
                        )
                    )


            self.convert_button.config(
                state="normal"
            )


    # ========================================================
    # MATERIAL SLOT VIEWER
    # ========================================================

    def view_material_slots(self):

        filename = filedialog.askopenfilename(
            title="Select Vehicle UAsset",
            filetypes=[
                (
                    "Unreal Asset",
                    "*.uasset"
                )
            ]
        )

        if not filename:
            return

        if not filename.lower().endswith(
            ".uasset"
        ):
            messagebox.showerror(
                "Invalid File",
                "Please select a .uasset file."
            )
            return

        uexp_path = os.path.splitext(
            filename
        )[0] + ".uexp"

        if not os.path.isfile(
            uexp_path
        ):
            messagebox.showerror(
                "Missing UEXP",
                (
                    "The matching .uexp file could not "
                    "be found.\n\n"
                    f"Expected:\n{uexp_path}"
                )
            )
            return

        if not os.path.isfile(
            UNREALPAK_BAT_PATH
        ):
            messagebox.showerror(
                "UnrealPak BAT Not Found",
                (
                    "UnrealPak-Without-Compression.bat "
                    "could not be found.\n\n"
                    f"Expected:\n{UNREALPAK_BAT_PATH}"
                )
            )
            return

        if not os.path.isfile(
            CUE4PARSE_PATH
        ):
            messagebox.showerror(
                "CUE4Parse Not Found",
                (
                    "cue4parse.exe could not be found.\n\n"
                    f"Expected:\n{CUE4PARSE_PATH}"
                )
            )
            return

        viewer = tk.Toplevel(
            self.root
        )

        viewer.configure(
            bg="#2b2b2b"
        )

        viewer.attributes(
            "-topmost",
            True
        )

        viewer.title(
            "Material Slot Viewer"
        )

        viewer.geometry(
            "720x680"
        )

        last_position = self.load_material_viewer_position()

        if last_position:

            viewer.geometry(
                f"+{last_position[0]}+{last_position[1]}"
            )

        viewer.resizable(
            False,
            False
        )

        viewer.configure(
            bg="#2b2b2b"
        )

        if os.path.isfile(
            ICON_PATH
        ):
            try:
                viewer.iconbitmap(
                    ICON_PATH
                )
            except tk.TclError:
                pass

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            viewer,
            text="Material Slot Viewer",
            font=("Segoe UI", 18, "bold"),
            fg="#FFFFFF",
            bg="#2b2b2b"
        )

        title.pack(
            pady=(18, 4)
        )

        subtitle = tk.Label(
            viewer,
            text=(
                "Read material slot numbers from a GTA DE UAsset"
            ),
            font=("Segoe UI", 9),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        subtitle.pack(
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # SELECTED UASSET
        # ----------------------------------------------------

        file_frame = ttk.LabelFrame(
            viewer,
            text="Selected UAsset"
        )

        file_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        file_label = tk.Label(
            file_frame,
            text=filename,
            font=("Segoe UI", 9),
            fg="#FFFFFF",
            bg="#2b2b2b",
            anchor="w",
            justify="left"
        )

        file_label.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        results_frame = ttk.LabelFrame(
            viewer,
            text="Material Slots"
        )

        results_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        results_text = tk.Text(
            results_frame,
            wrap="none",
            font=("Consolas", 10),
            state="disabled",
            bg="#1e1e1e",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            selectbackground="#555555",
            selectforeground="#FFFFFF",
            relief="flat",
            borderwidth=0
        )

        results_text.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status_label = tk.Label(
            viewer,
            text="Ready.",
            font=("Segoe UI", 9),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        status_label.pack(
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        close_button = tk.Button(
            viewer,
            text="Close",
            command=lambda: (
                self.save_material_viewer_position(viewer),
                viewer.destroy()
            ),
            bg="#3a3a3a",
            fg="#FFFFFF",
            activebackground="#4a4a4a",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2"
        )

        close_button.pack(
            pady=(0, 15)
        )

        viewer.protocol(
            "WM_DELETE_WINDOW",
            lambda: (
                self.save_material_viewer_position(viewer),
                viewer.destroy()
            )
        )

        watermark_label = tk.Label(
            viewer,
            text="Made by ITSM0VER",
            font=("Segoe UI", 9),
            bg="#2b2b2b",
            fg="#666666"
        )

        watermark_label.pack(
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # PROCESS
        # ----------------------------------------------------

        try:

            status_label.config(
                text="Creating temporary package..."
            )

            viewer.update_idletasks()

            viewer.update()

            # ------------------------------------------------
            # CREATE UNIQUE MATERIAL VIEWER TEMP FOLDER
            # ------------------------------------------------

            temp_parent = os.path.dirname(
                filename
            )

            temp_root = os.path.join(
                temp_parent,
                "TEMP_MaterialViewer"
            )

            counter = 2

            while os.path.exists(
                temp_root
            ) :

                temp_root = os.path.join(
                    temp_parent,
                    f"TEMP_MaterialViewer_{counter}"
                )

                counter += 1

            temp_vehicle_directory = os.path.join(
                temp_root,
                "Gameface",
                "Content",
                "Vehicle"
            )

            temp_pak = (
                temp_root
                + ".pak"
            )

            # ------------------------------------------------
            # CLEAN PREVIOUS TEMP DATA
            # ------------------------------------------------

            if os.path.isdir(
                temp_root
            ):
                shutil.rmtree(
                    temp_root
                )

            if os.path.isfile(
                temp_pak
            ):
                os.remove(
                    temp_pak
                )

            os.makedirs(
                temp_vehicle_directory,
                exist_ok=True
            )

            # ------------------------------------------------
            # COPY UASSET
            # ------------------------------------------------

            shutil.copy2(
                filename,
                os.path.join(
                    temp_vehicle_directory,
                    os.path.basename(filename)
                )
            )

            # ------------------------------------------------
            # COPY UEXP
            # ------------------------------------------------

            shutil.copy2(
                uexp_path,
                os.path.join(
                    temp_vehicle_directory,
                    os.path.basename(uexp_path)
                )
            )

            # ------------------------------------------------
            # COPY UBULK IF PRESENT
            # ------------------------------------------------

            ubulk_path = (
                os.path.splitext(
                    filename
                )[0]
                + ".ubulk"
            )

            if os.path.isfile(
                ubulk_path
            ):
                shutil.copy2(
                    ubulk_path,
                    os.path.join(
                        temp_vehicle_directory,
                        os.path.basename(
                            ubulk_path
                        )
                    )
                )

            self.log(
                "Material Slot Viewer:"
            )

            self.log(
                f"UAsset: {filename}"
            )

            self.log(
                f"Temporary directory: {temp_root}"
            )

            # ------------------------------------------------
            # RUN EXISTING UNREALPAK BAT
            # ------------------------------------------------

            viewer.update_idletasks()

            startup_info = subprocess.STARTUPINFO()

            startup_info.dwFlags |= (
                subprocess.STARTF_USESHOWWINDOW
            )

            startup_info.wShowWindow = 6

            pak_command = [
                "cmd",
                "/c",
                UNREALPAK_BAT_PATH,
                temp_root
            ]

            pak_result = subprocess.run(
                pak_command,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                cwd=os.path.dirname(
                    UNREALPAK_BAT_PATH
                ),
                startupinfo=startup_info
            )

            if pak_result.stdout.strip():
                self.log(
                    pak_result.stdout.strip()
                )

            if pak_result.stderr.strip():
                self.log(
                    pak_result.stderr.strip()
                )

            if pak_result.returncode != 0:
                raise RuntimeError(
                    "UnrealPak failed to create TEMP.pak."
                )

            if not os.path.isfile(
                temp_pak
            ):
                raise RuntimeError(
                    (
                        "UnrealPak completed but "
                        "TEMP.pak was not created."
                    )
                )

            self.log(
                f"Created temporary PAK: {temp_pak}"
            )

            # ------------------------------------------------
            # RUN CUE4PARSE
            # ------------------------------------------------

            status_label.config(
                text="Reading UAsset with CUE4Parse..."
            )

            viewer.update_idletasks()

            asset_name = os.path.basename(
                filename
            )

            package_path = (
                "Gameface/Content/Vehicle/"
                + asset_name
            )

            cue_command = [
                CUE4PARSE_PATH,
                "--pak",
                temp_pak,
                "-p",
                package_path,
                "-g",
                CUE4PARSE_GAME_VERSION,
                "-f",
                "json",
                "-o",
                temp_root
            ]

            cue_result = subprocess.run(
                cue_command,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(
                    CUE4PARSE_PATH
                ),
                startupinfo=startup_info
            )

            if cue_result.stderr.strip():
                self.log(
                    cue_result.stderr.strip()
                )

            if cue_result.returncode != 0:

                error_output = (
                    cue_result.stderr.strip()
                    or cue_result.stdout.strip()
                    or "No error output was returned."
                )

                raise RuntimeError(
                    (
                        "CUE4Parse failed.\n\n"
                        f"Return code: {cue_result.returncode}\n\n"
                        f"{error_output}"
                    )
                )

            self.log(
                "CUE4Parse completed successfully."
            )

            # ------------------------------------------------
            # FIND EXTRACTED JSON
            # ------------------------------------------------

            status_label.config(
                text="Finding extracted JSON..."
            )

            viewer.update_idletasks()

            json_file = None

            for root_dir, directories, files in os.walk(
                temp_root
            ):

                for file_name in files:

                    if file_name.lower().endswith(
                        ".json"
                    ):

                        json_file = os.path.join(
                            root_dir,
                            file_name
                        )

                        break

                if json_file:
                    break

            if not json_file:

                raise RuntimeError(
                    (
                        "CUE4Parse completed successfully, "
                        "but no JSON file was found inside "
                        "the temporary folder.\n\n"
                        f"Expected output folder:\n{temp_root}"
                    )
                )

            self.log(
                f"CUE4Parse JSON found: {json_file}"
            )

            # ------------------------------------------------
            # READ JSON
            # ------------------------------------------------

            status_label.config(
                text="Reading material slot data..."
            )

            viewer.update_idletasks()

            with open(
                json_file,
                "r",
                encoding="utf-8-sig"
            ) as file:

                parsed_data = json.load(
                    file
                )

            self.log(
                "CUE4Parse JSON loaded successfully."
            )

            # ------------------------------------------------
            # READ MATERIAL SLOTS
            # ------------------------------------------------

            skeletal_mesh = None

            if isinstance(
                parsed_data,
                list
            ):

                for export in parsed_data:

                    if (
                        isinstance(
                            export,
                            dict
                        )
                        and export.get(
                            "Type"
                        ) == "SkeletalMesh"
                    ):

                        skeletal_mesh = export
                        break

            elif (
                isinstance(
                    parsed_data,
                    dict
                )
                and parsed_data.get(
                    "Type"
                ) == "SkeletalMesh"
            ):

                skeletal_mesh = parsed_data

            if skeletal_mesh is None:

                raise RuntimeError(
                    (
                        "Could not find a SkeletalMesh "
                        "export in the CUE4Parse JSON."
                    )
                )

            skeletal_materials = skeletal_mesh.get(
                "SkeletalMaterials",
                []
            )

            lod_models = skeletal_mesh.get(
                "LODModels",
                []
            )

            if not skeletal_materials:

                raise RuntimeError(
                    "The SkeletalMesh contains no SkeletalMaterials."
                )

            if not lod_models:

                raise RuntimeError(
                    "The SkeletalMesh contains no LODModels."
                )

            # ------------------------------------------------
            # BUILD MATERIAL SLOT INFORMATION
            # ------------------------------------------------

            slot_usage = {}

            for material_index in range(
                len(skeletal_materials)
            ):

                slot_usage[
                    material_index
                ] = []

            # ------------------------------------------------
            # READ SECTION MATERIAL INDICES
            # ------------------------------------------------

            sections = lod_models[0].get(
                "Sections",
                []
            )

            for section_index, section in enumerate(
                sections
            ):

                material_index = section.get(
                    "MaterialIndex"
                )

                if material_index is None:
                    continue

                if material_index not in slot_usage:

                    slot_usage[
                        material_index
                    ] = []

                slot_usage[
                    material_index
                ].append(
                    section_index
                )

            # ------------------------------------------------
            # BUILD MATERIAL SLOT DISPLAY
            # ------------------------------------------------

            display_lines = []

            display_lines.append(
                "MATERIAL SLOTS"
            )

            display_lines.append(
                "=============="
            )

            display_lines.append(
                ""
            )

            display_lines.append(
                f"{'SLOT':<8}"
                f"{'MATERIAL':<50}"
                #f"SECTION(S)"
            )

            display_lines.append(
                f"{'-' * 8}"
                f"{'-' * 50}"
                #f"{'-' * 20}"
            )

            for material_index, material in enumerate(
                skeletal_materials
            ):

                material_name = material.get(
                    "MaterialSlotName",
                    ""
                )

                sections_used = slot_usage.get(
                    material_index,
                    []
                )

                if sections_used:

                    section_text = ", ".join(
                        str(section_index)
                        for section_index in sections_used
                    )

                else:

                    section_text = "-"

                display_lines.append(
                    f"{material_index:<8}"
                    f"{material_name:<50}"
                    #f"{section_text}"
                )

            # ------------------------------------------------
            # DISPLAY MATERIAL SLOTS
            # ------------------------------------------------

            results_text.config(
                state="normal"
            )

            results_text.delete(
                "1.0",
                "end"
            )

            results_text.insert(
                "end",
                "\n".join(
                    display_lines
                )
            )

            results_text.config(
                state="disabled"
            )

            status_label.config(
                text=(
                    f"Found {len(skeletal_materials)} "
                    "material slots."
                )
            )

            self.log(
                (
                    "Material Slot Viewer loaded "
                    f"{len(skeletal_materials)} material slots."
                )
            )

        except Exception as error:

            status_label.config(
                text="Failed."
            )

            self.log(
                f"[ERROR] Material Slot Viewer: {error}"
            )

            messagebox.showerror(
                "Material Slot Viewer",
                str(error),
                parent=viewer
            )

        finally:

            # ------------------------------------------------
            # CLEAN TEMPORARY DATA
            # ------------------------------------------------

            try:

                if os.path.isdir(
                    temp_root
                ):
                    shutil.rmtree(
                        temp_root
                    )

                if os.path.isfile(
                    temp_pak
                ):
                    os.remove(
                        temp_pak
                    )

                self.log(
                    "Temporary Material Slot Viewer files removed."
                )

            except Exception as cleanup_error:

                self.log(
                    (
                        "[WARNING] Could not fully clean "
                        f"temporary files: {cleanup_error}"
                    )
                )


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()
    root.withdraw()

    VehicleLightingTool(
        root
    )

    root.deiconify()

    root.mainloop()


if __name__ == "__main__":
    main()
