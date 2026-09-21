import json
import os
import sys
import subprocess
import threading
import ctypes
from ctypes import windll
import tkinter.font as tkFont
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


APP_TITLE = "UAsset → JSON Converter"
DEFAULT_ENGINE = "VER_UE4_26"


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


SCRIPT_DIR = get_script_directory()

POSITION_FILE = os.path.join(
    SCRIPT_DIR,
    "Files",
    "uasset_json_converter_window_position.txt"
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

# ---------------------------------------------------------
# Pricedown font
# ---------------------------------------------------------

PRICEDOWN_PATH = os.path.join(
    SCRIPT_DIR,
    "Files",
    ".Resources",
    "pricedown bl.otf"
)

class UAssetJSONConverter:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("660x735")

        last_position = self.load_window_position()

        if last_position:

            self.root.geometry(
                f"+{last_position[0]}+{last_position[1]}"
            )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_closing
        )

        self.input_uasset = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.engine_version = tk.StringVar(value=DEFAULT_ENGINE)

        self.skip_existing = tk.BooleanVar(value=True)
        self.recursive = tk.BooleanVar(value=False)

        self.running = False
        self.processed = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0

        self.build_ui()

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


    def on_closing(self):

        self.save_window_position()

        # Remove Pricedown font from Windows
        if PRICEDOWN_LOADED:
            windll.gdi32.RemoveFontResourceW(PRICEDOWN_PATH)

        self.root.destroy()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="UAsset → JSON Converter",
            font=PRICEDOWN_FONT
        ).pack(anchor="w")

        ttk.Label(
            main,
            text="Batch-convert Unreal Engine .uasset files to .JSON using the included UAssetGUI.",
            font=("Segoe Script", 10)
        ).pack(anchor="w", pady=(2, 10))

        ttk.Label(
            main,
            text="UAssetGUI: Files\\.Resources\\UAssetGUI.exe",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 8))

        # Input UAsset
        self.add_path_row(
            main,
            "Input UAsset:",
            self.input_uasset,
            self.browse_uasset
        )

        # Input folder
        self.add_path_row(
            main,
            "Input folder:",
            self.input_folder,
            self.browse_input
        )

        # Output
        self.add_path_row(
            main,
            "Output folder:",
            self.output_folder,
            self.browse_output
        )

        options = ttk.LabelFrame(main, text="Options", padding=12)
        options.pack(fill="x", pady=(16, 12))

        ttk.Label(
            options,
            text="Engine version:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10)
        )

        ttk.Label(
            options,
            text="UE 4.26"
        ).grid(
            row=0,
            column=1,
            sticky="w"
        )

        ttk.Checkbutton(
            options,
            text="Skip JSON files that already exist",
            variable=self.skip_existing,
            cursor="hand2"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(10, 0)
        )

        ttk.Checkbutton(
            options,
            text="Search subfolders recursively",
            variable=self.recursive,
            cursor="hand2"
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(6, 0)
        )

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(4, 10))

        self.start_button = ttk.Button(
            buttons,
            text="Export All .JSON Files",
            command=self.start_conversion,
            cursor="hand2"
        )
        self.start_button.pack(side="left")

        self.clear_button = ttk.Button(
            buttons,
            text="Clear Log",
            command=self.clear_log,
            cursor="hand2"
        )
        self.clear_button.pack(
            side="left",
            padx=(8, 0)
        )

        self.progress = ttk.Progressbar(
            main,
            mode="determinate"
        )
        self.progress.pack(
            fill="x",
            pady=(2, 4)
        )

        self.status_label = ttk.Label(
            main,
            text="Ready."
        )
        self.status_label.pack(anchor="w")

        log_frame = ttk.LabelFrame(
            main,
            text="Conversion Log",
            padding=6
        )
        log_frame.pack(
            fill="both",
            expand=True,
            pady=(10, 0)
        )

        self.log_text = tk.Text(
            log_frame,
            wrap="none",
            height=14,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            state="disabled"
        )

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_text.yview
        )

        self.log_text.configure(
            yscrollcommand=scrollbar.set
        )

        self.log_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Watermark label
        watermark = tk.Label(
            main,
            text="UI Made by ITSM0VER",
            font=("Segoe UI", 8, "italic"),
            fg="#AAAAAA",
            bg="#2b2b2b"
        )

        watermark.pack(
            side="bottom",
            pady=(8, 0)
        )

    def add_path_row(self, parent, label, variable, command):
        row = ttk.Frame(parent)
        row.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            row,
            text=label,
            width=16
        ).pack(side="left")

        entry = ttk.Entry(
            row,
            textvariable=variable
        )
        entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        ttk.Button(
            row,
            text="Browse...",
            command=command,
            cursor="hand2"
        ).pack(
            side="left",
            padx=(8, 0)
        )

    def browse_uasset(self):
        path = filedialog.askopenfilename(
            title="Select UAsset file",
            filetypes=[
                (
                    "Unreal Asset",
                    "*.uasset"
                )
            ]
        )

        if path:
            self.input_uasset.set(path)

            # Automatically use the same folder as the UAsset
            # for the JSON output if no output folder is selected.
            if not self.output_folder.get():
                self.output_folder.set(
                    str(Path(path).parent / "JSON")
                )

        if path:
            self.input_uasset.set(path)

            # Automatically use the same folder as the UAsset
            # for the JSON output if no output folder is selected.
            if not self.output_folder.get():
                self.output_folder.set(
                    str(Path(path).parent / "JSON")
                )

    def browse_input(self):
        path = filedialog.askdirectory(
            title="Select folder containing .uasset files"
        )

        if path:
            self.input_folder.set(path)

            # Convenient default:
            # create a JSON folder beside the input folder.
            if not self.output_folder.get():
                self.output_folder.set(
                    str(Path(path) / "JSON")
                )

    def browse_output(self):
        path = filedialog.askdirectory(
            title="Select output folder for JSON files"
        )

        if path:
            self.output_folder.set(path)

    def log(self, message):
        def write():
            self.log_text.configure(
                state="normal"
            )

            self.log_text.insert(
                "end",
                message + "\n"
            )

            self.log_text.see("end")

            self.log_text.configure(
                state="disabled"
            )

        self.root.after(
            0,
            write
        )

    def clear_log(self):
        self.log_text.configure(
            state="normal"
        )

        self.log_text.delete(
            "1.0",
            "end"
        )

        self.log_text.configure(
            state="disabled"
        )

    def start_conversion(self):
        if self.running:
            return

        # UAssetGUI is automatically located relative
        # to the script / executable.
        uassetgui = Path(UASSETGUI_PATH)

        # Get the user's selections
        input_uasset_text = self.input_uasset.get().strip('" ')
        input_folder_text = self.input_folder.get().strip('" ')
        output_folder_text = self.output_folder.get().strip('" ')

        # ---------------------------------------------------------
        # Check UAssetGUI
        # ---------------------------------------------------------

        if not uassetgui.is_file():
            messagebox.showerror(
                "UAssetGUI not found",
                "UAssetGUI.exe could not be found here:\n\n"
                f"{uassetgui}\n\n"
                "Make sure it is located in:\n"
                "Files\\.Resources\\UAssetGUI.exe"
            )
            return

        # ---------------------------------------------------------
        # Determine input mode
        # ---------------------------------------------------------

        # SINGLE UASSET MODE
        if input_uasset_text:

            uasset_file = Path(input_uasset_text)

            if not uasset_file.is_file():
                messagebox.showerror(
                    "UAsset not found",
                    "The selected UAsset could not be found:\n\n"
                    f"{uasset_file}"
                )
                return

            if uasset_file.suffix.lower() != ".uasset":
                messagebox.showerror(
                    "Invalid file",
                    "The selected file is not a .uasset file."
                )
                return

            # One-file conversion
            files = [uasset_file]

            # Used to calculate the output path
            input_folder = uasset_file.parent

        # BATCH FOLDER MODE
        elif input_folder_text:

            input_folder = Path(input_folder_text)

            if not input_folder.is_dir():
                messagebox.showerror(
                    "Input folder not found",
                    "Please select a valid folder containing .uasset files."
                )
                return

            # Find UAssets
            if self.recursive.get():
                files = sorted(
                    input_folder.rglob("*.uasset")
                )
            else:
                files = sorted(
                    input_folder.glob("*.uasset")
                )

        # NOTHING SELECTED
        else:

            messagebox.showerror(
                "No input selected",
                "Please select either an individual .uasset file "
                "or an input folder."
            )
            return

        # ---------------------------------------------------------
        # Output folder
        # ---------------------------------------------------------

        if output_folder_text:
            output_folder = Path(output_folder_text)

        else:
            # Automatically create/use a JSON folder beside
            # the selected UAsset or input folder.
            output_folder = input_folder / "JSON"

            self.output_folder.set(
                str(output_folder)
            )

        try:
            output_folder.mkdir(
                parents=True,
                exist_ok=True
            )

        except Exception as exc:

            messagebox.showerror(
                "Output folder error",
                f"Could not create the output folder:\n\n{exc}"
            )

            return

        # ---------------------------------------------------------
        # Check for files
        # ---------------------------------------------------------

        if not files:

            messagebox.showinfo(
                "No UAssets found",
                "No .uasset files were found in the selected input folder."
            )

            return

        # ---------------------------------------------------------
        # Start conversion
        # ---------------------------------------------------------

        self.running = True

        self.start_button.configure(
            state="disabled"
        )

        self.processed = 0
        self.success = 0
        self.failed = 0
        self.skipped = 0

        self.progress.configure(
            maximum=len(files),
            value=0
        )

        if len(files) == 1:
            self.status_label.configure(
                text="Found 1 .uasset file."
            )
        else:
            self.status_label.configure(
                text=f"Found {len(files)} .uasset files."
            )

        thread = threading.Thread(
            target=self.convert_files,
            args=(
                uassetgui,
                input_folder,
                output_folder,
                files
            ),
            daemon=True
        )

        thread.start()

    def convert_files(
        self,
        uassetgui,
        input_folder,
        output_folder,
        files
    ):
        for uasset in files:

            relative = uasset.relative_to(
                input_folder
            )

            # Preserve subfolder structure when
            # recursive mode is enabled.
            json_file = (
                output_folder /
                relative.with_suffix(".json")
            )

            json_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            self.log(
                f"[{self.processed + 1}/{len(files)}] {relative}"
            )

            if (
                self.skip_existing.get()
                and json_file.exists()
            ):
                self.skipped += 1
                self.processed += 1

                self.log(
                    f"    SKIPPED - already exists: "
                    f"{json_file.name}"
                )

                self.update_progress(
                    len(files)
                )

                continue

            command = [
                str(uassetgui),
                "tojson",
                str(uasset),
                str(json_file),
                self.engine_version.get()
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=str(SCRIPT_DIR)
                )

                if (
                    result.returncode == 0
                    and json_file.exists()
                ):
                    self.success += 1

                    self.log(
                        f"    OK -> {json_file}"
                    )

                else:
                    self.failed += 1

                    self.log(
                        f"    FAILED "
                        f"(exit code {result.returncode})"
                    )

                    if result.stdout.strip():
                        self.log(
                            f"    stdout: "
                            f"{result.stdout.strip()}"
                        )

                    if result.stderr.strip():
                        self.log(
                            f"    stderr: "
                            f"{result.stderr.strip()}"
                        )

            except Exception as exc:
                self.failed += 1

                self.log(
                    f"    ERROR: {exc}"
                )

            self.processed += 1

            self.update_progress(
                len(files)
            )

        self.root.after(
            0,
            self.conversion_finished
        )

    def update_progress(self, total):
        self.root.after(
            0,
            lambda: (
                self.progress.configure(
                    value=self.processed
                ),
                self.status_label.configure(
                    text=(
                        f"Processed {self.processed}/{total}  |  "
                        f"Success: {self.success}  |  "
                        f"Skipped: {self.skipped}  |  "
                        f"Failed: {self.failed}"
                    )
                )
            )
        )

    def conversion_finished(self):
        self.running = False

        self.start_button.configure(
            state="normal"
        )

        self.status_label.configure(
            text=(
                f"Finished — "
                f"{self.success} converted, "
                f"{self.skipped} skipped, "
                f"{self.failed} failed."
            )
        )

        # Clear the input fields so the next conversion
        # starts with a clean slate.
        self.input_uasset.set("")
        self.input_folder.set("")

        messagebox.showinfo(
            "Conversion Complete",
            f"Conversion finished.\n\n"
            f"Converted: {self.success}\n"
            f"Skipped: {self.skipped}\n"
            f"Failed: {self.failed}"
        )

def main():
    global PRICEDOWN_FONT, PRICEDOWN_LOADED

    root = tk.Tk()

    root.withdraw()

    # Load Pricedown font
    PRICEDOWN_LOADED = False

    if os.path.isfile(PRICEDOWN_PATH):
        if windll.gdi32.AddFontResourceW(PRICEDOWN_PATH):
            PRICEDOWN_LOADED = True

    PRICEDOWN_FAMILY = None

    for family in tkFont.families(root):
        if "Pricedown" in family:
            PRICEDOWN_FAMILY = family
            break

    if PRICEDOWN_FAMILY:
        PRICEDOWN_FONT = (PRICEDOWN_FAMILY, 30)
    else:
        PRICEDOWN_FONT = ("Segoe UI", 18, "bold")

    root.resizable(False, False)

    # Dark background
    root.configure(
        bg="#2b2b2b"
    )

    # Set application icon
    if os.path.isfile(ICON_PATH):
        root.iconbitmap(ICON_PATH)

    # Dark theme
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Main background
    style.configure(
        "TFrame",
        background="#2b2b2b"
    )

    # Labels
    style.configure(
        "TLabel",
        background="#2b2b2b",
        foreground="#FFFFFF"
    )

    # LabelFrame
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

    # Entry boxes
    style.configure(
        "TEntry",
        fieldbackground="#3a3a3a",
        foreground="#FFFFFF"
    )

    # Buttons
    style.configure(
        "TButton",
        background="#3a3a3a",
        foreground="#FFFFFF"
    )

    style.map(
        "TButton",
        background=[
            ("active", "#FF69B4")
        ],
        foreground=[
        ("active", "#FFFFFF")
        ]
    )

    # Checkbuttons
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

    # Progress bar
    style.configure(
        "TProgressbar",
        background="#5a5a5a",
        troughcolor="#1e1e1e"
    )

    UAssetJSONConverter(root)

    root.update_idletasks()
    root.deiconify()

    root.mainloop()


if __name__ == "__main__":
    main()
