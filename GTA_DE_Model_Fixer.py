import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox, filedialog, colorchooser, Toplevel, Label
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import io
import subprocess
import sys
import webbrowser
from PIL import Image, ImageTk, ImageFont
import ctypes
import ctypes.wintypes
from win32com.client import Dispatch
import gdown
import requests
import zipfile
import io
import shutil
import threading
import ctypes
import json
import queue
import time
from ctypes import windll
import pyperclip
from concurrent.futures import ThreadPoolExecutor, as_completed

# Make sure the application never uses the Files folder as its working directory
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_script_directory():
    if getattr(sys, 'frozen', False):
        # The script is bundled into an executable
        return os.path.abspath(os.path.dirname(sys.executable))
    else:
        # The script is run directly
        return os.path.abspath(os.path.dirname(__file__))

def check_disk_space():
    base_dir = get_script_directory()

    total, used, free = shutil.disk_usage(base_dir)

    # Minimum free space required: 500 MB
    minimum_free_space = 500 * 1024 * 1024

    free_gb = free / (1024 ** 3)

    if free < minimum_free_space:
        raise OSError(
            28,
            f"Not enough free disk space.\n\n"
            f"Location checked:\n"
            f"{base_dir}\n\n"
            f"Free space: {free_gb:.2f} GB\n"
            f"Required: 0.50 GB"
        )

def ensure_app_icon():
    files_folder = os.path.join(get_script_directory(), "Files")
    resources_folder = os.path.join(files_folder, ".Resources")
    icon_path = os.path.join(resources_folder, "ICON.ico")

    # Icon already exists
    if os.path.exists(icon_path):
        return

    print("[LOG] Application icon not found. Downloading...")

    url = "https://drive.google.com/uc?id=1gywK4OTaLNEjHxTOMUsNHiw3l4mPdP6n"

    zip_path = os.path.join(
        get_script_directory(),
        "app_icon.zip"
    )

    temp_extract = os.path.join(
        get_script_directory(),
        "temp_app_icon"
    )

    try:
        # Make sure destination folder exists
        os.makedirs(resources_folder, exist_ok=True)

        # Download ZIP
        gdown.download(
            url,
            zip_path,
            quiet=True
        )

        # Extract ZIP to temporary location
        os.makedirs(temp_extract, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract)

        # Locate ICON.ico inside:
        # Files/.Resources/ICON.ico
        source_icon = os.path.join(
            temp_extract,
            "Files",
            ".Resources",
            "ICON.ico"
        )

        if not os.path.exists(source_icon):
            print("[ERROR] ICON.ico was not found inside the downloaded ZIP.")
            return

        # Copy icon to the correct location
        shutil.copy2(
            source_icon,
            icon_path
        )

        print("[LOG] Application icon installed successfully!")

    except Exception as e:
        print(f"[ERROR] Failed to install application icon: {e}")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_extract):
            try:
                shutil.rmtree(temp_extract)
            except Exception:
                pass

        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception:
                pass

# Make sure the application icon exists first
ensure_app_icon()

# Make a temporary copy of the application icon outside the Files folder.
# This prevents Tkinter from keeping ICON.ico locked inside Files.
ICON_SOURCE = os.path.join(
    get_script_directory(),
    "Files",
    ".Resources",
    "ICON.ico"
)

ICON_PATH = os.path.join(
    get_script_directory(),
    "ModelFixer_temp.ico"
)

try:
    shutil.copy2(ICON_SOURCE, ICON_PATH)
except Exception as e:
    print(f"[WARNING] Could not create temporary icon: {e}")

# --- Startup UI ---
root = TkinterDnD.Tk()

# Keep the root completely hidden during startup.
# It will only be shown if the resource installation splash is required.
root.withdraw()

root.title("DE Modding Utility by ITSM0VER")
root.geometry("400x150")
root.configure(bg="#2b2b2b")
root.resizable(False, False)

# Center window
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 400) // 2
y = (screen_height - 150) // 2
root.geometry(f"400x150+{x}+{y}")

splash_title = tk.Label(
    root,
    text="Installing Resources",
    font=("Segoe UI", 16, "bold"),
    fg="white",
    bg="#2b2b2b"
)
splash_title.pack(pady=(35, 5))

splash_message = tk.Label(
    root,
    text="Please wait...",
    font=("Segoe UI", 10),
    fg="#cccccc",
    bg="#2b2b2b"
)
splash_message.pack()

# Icon
if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

# Force the window to appear before downloading starts
root.update()

def ensure_files_exist():
    files_folder = os.path.join(get_script_directory(), "Files")
    unrealpak427_folder = os.path.join(files_folder, "UnrealPak427")
    references_folder = os.path.join(files_folder, ".References")

    if not os.path.exists(files_folder) or not os.path.exists(unrealpak427_folder):
        download_unrealpak427()
        download_and_extract_v1_3_files()

    references_folder = os.path.join(
        files_folder,
        ".References"
    )

    material_creation_folder = os.path.join(
        files_folder,
        ".MaterialCreation"
    )

    if (
        not os.path.exists(references_folder)
        or
        not os.path.exists(material_creation_folder)
    ):
        download_and_extract_v1_4_files()

def download_unrealpak427():
    print("[LOG] Downloading UnrealPak427 files…")

    url = "https://drive.google.com/uc?id=1asiecgtQKvtaY9jJuKMd0Y2PalWRAmue"  # new zip only for UnrealPak427
    zip_path = os.path.join(get_script_directory(), "unrealpak427.zip")
    files_folder = os.path.join(get_script_directory(), "Files")
    target_folder = os.path.join(files_folder, "UnrealPak427")

    os.makedirs(files_folder, exist_ok=True)

    # download
    gdown.download(url, zip_path, quiet=True)

    # extract
    temp_extract = os.path.join(get_script_directory(), "temp_427")
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_extract)

    # move contents into Files/
    inner_folder = os.path.join(temp_extract, "UnrealPak427")

    if os.path.exists(inner_folder):
        shutil.move(inner_folder, target_folder)

    # cleanup
    shutil.rmtree(temp_extract)
    os.remove(zip_path)

    print("[LOG] UnrealPak427 installed successfully!")

def download_and_extract_v1_3_files():
    import os, gdown, zipfile, shutil

    print("[LOG] 'Files/Batches' not found. Downloading…")

    url = "https://drive.google.com/uc?id=1Stcn7DIL5Fgy5cry-Q6bQUlJNGxMmbMc"
    zip_path = os.path.join(get_script_directory(), "v1.3Files.zip")
    files_folder = os.path.join(get_script_directory(), "Files")
    batches_folder = os.path.join(files_folder)

    # Ensure base folder exists
    os.makedirs(files_folder, exist_ok=True)
    os.makedirs(batches_folder, exist_ok=True)

    # Download the zip
    gdown.download(url, zip_path, quiet=True)

    # Extract to temp folder
    temp_extract = os.path.join(get_script_directory(), "temp_files")
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_extract)

    # TARGET INSIDE ZIP: Files/Batches
    inner_batches = os.path.join(temp_extract, "Files")

    if os.path.exists(inner_batches):
        print("[LOG] Installing BAT files...")

        for item in os.listdir(inner_batches):
            src = os.path.join(inner_batches, item)
            dst = os.path.join(batches_folder, item)

            if os.path.isdir(src):
                shutil.move(src, dst)
            else:
                shutil.move(src, dst)
    else:
        print("[ERROR] Batches folder not found in ZIP structure!")

    # Clean up
    shutil.rmtree(temp_extract)
    os.remove(zip_path)

    print("[LOG] Download and extraction complete!")

def download_and_extract_v1_4_files():
    print("[LOG] v1.4 files not found. Downloading…")

    url = "https://drive.google.com/uc?id=1tN4oMlgA-zKNNC8gC7FTkljPWu3GF0my"

    zip_path = os.path.join(get_script_directory(), "v1.4Files.zip")
    files_folder = os.path.join(get_script_directory(), "Files")

    os.makedirs(files_folder, exist_ok=True)

    # Download the ZIP
    gdown.download(url, zip_path, quiet=True)

    # Extract to temporary folder
    temp_extract = os.path.join(get_script_directory(), "temp_v1_4")
    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_extract)

    # -----------------------------------------
    # INSTALL .References
    # -----------------------------------------

    inner_references = os.path.join(
        temp_extract,
        "Files",
        ".References"
    )

    references_folder = os.path.join(
        files_folder,
        ".References"
    )

    if os.path.exists(inner_references):
        print("[LOG] Installing .References files...")

        if os.path.exists(references_folder):
            shutil.rmtree(references_folder)

        shutil.move(
            inner_references,
            references_folder
        )
    else:
        print("[ERROR] .References folder not found in ZIP structure!")


    # -----------------------------------------
    # INSTALL .MaterialCreation
    # -----------------------------------------

    inner_material_creation = os.path.join(
        temp_extract,
        "Files",
        ".MaterialCreation"
    )

    material_creation_folder = os.path.join(
        files_folder,
        ".MaterialCreation"
    )

    if os.path.exists(inner_material_creation):
        print("[LOG] Installing .MaterialCreation files...")

        if os.path.exists(material_creation_folder):
            shutil.rmtree(material_creation_folder)

        shutil.move(
            inner_material_creation,
            material_creation_folder
        )
    else:
        print("[ERROR] .MaterialCreation folder not found in ZIP structure!")

    # -----------------------------------------
    # INSTALL .Resources
    # -----------------------------------------

    inner_resources = os.path.join(
        temp_extract,
        "Files",
        ".Resources"
    )

    resources_folder = os.path.join(
        files_folder,
        ".Resources"
    )

    if os.path.exists(inner_resources):
        print("[LOG] Installing .Resources files...")

        os.makedirs(resources_folder, exist_ok=True)

        for item in os.listdir(inner_resources):
            src = os.path.join(inner_resources, item)
            dst = os.path.join(resources_folder, item)

            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)

            shutil.move(src, dst)

    else:
        print("[ERROR] .Resources folder not found in ZIP structure!")

    # -----------------------------------------
    # INSTALL UnrealPak427
    # -----------------------------------------

    inner_unrealpak427 = os.path.join(
        temp_extract,
        "Files",
        "UnrealPak427"
    )

    unrealpak427_folder = os.path.join(
        files_folder,
        "UnrealPak427"
    )

    if os.path.exists(inner_unrealpak427):
        print("[LOG] Installing UnrealPak427 files...")

        # Make sure the original UnrealPak427 folder exists
        os.makedirs(unrealpak427_folder, exist_ok=True)

        # The v1.4 ZIP contains the updated BAT file
        bat_file = "UnrealUnpak427M0VER.bat"

        src = os.path.join(
            inner_unrealpak427,
            bat_file
        )

        dst = os.path.join(
            unrealpak427_folder,
            bat_file
        )

        if os.path.exists(src):
            # Replace ONLY the BAT file.
            # All existing UnrealPak427 files remain untouched.
            shutil.copy2(src, dst)
            print(f"[LOG] Updated {bat_file}")
        else:
            print(f"[ERROR] {bat_file} not found in v1.4 ZIP!")

    else:
        print("[ERROR] UnrealPak427 folder not found in ZIP structure!")

    # -----------------------------------------
    # INSTALL BAT FILES
    # -----------------------------------------

    bat_files = [
        "UnrealPak-With-Compression.bat",
        "UnrealPak-Without-Compression.bat",
        "UnrealUnpakM0VER.bat"
    ]

    for bat_file in bat_files:
        src = os.path.join(
            temp_extract,
            "Files",
            bat_file
        )

        dst = os.path.join(
            files_folder,
            bat_file
        )

        if os.path.exists(src):
            print(f"[LOG] Installing {bat_file}...")

            if os.path.exists(dst):
                os.remove(dst)

            shutil.move(src, dst)
        else:
            print(f"[ERROR] {bat_file} not found in ZIP structure!")

    # -----------------------------------------
    # CLEAN UP
    # -----------------------------------------

    shutil.rmtree(temp_extract)
    os.remove(zip_path)

    print("[LOG] v1.4 download and extraction complete!")

def download_and_extract_files():
    print("[LOG] 'Files' folder not found. Downloading…")
    
    url = "https://drive.google.com/uc?id=1VFpiBVSSNVsjB0H6tFAmkJiJMtWf4oBg"
    zip_path = os.path.join(get_script_directory(), "files.zip")
    files_folder = os.path.join(get_script_directory(), "Files")
    
    # Ensure base folder exists
    os.makedirs(files_folder, exist_ok=True)

    # Download the ZIP
    gdown.download(url, zip_path, quiet=True)

    # Extract to temp folder
    temp_extract = os.path.join(get_script_directory(), "temp_files")

    if os.path.exists(temp_extract):
        shutil.rmtree(temp_extract)

    os.makedirs(temp_extract, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_extract)

    # Inner Files folder from the ZIP
    inner_folder = os.path.join(temp_extract, "Files")

    if os.path.exists(inner_folder):

        for item in os.listdir(inner_folder):

            src = os.path.join(inner_folder, item)
            dst = os.path.join(files_folder, item)

            # -------------------------------------------------
            # Folder already exists -> MERGE contents
            # -------------------------------------------------
            if os.path.isdir(src):

                os.makedirs(dst, exist_ok=True)

                for root_dir, dirs, files in os.walk(src):

                    # Work out the corresponding destination folder
                    relative_path = os.path.relpath(root_dir, src)
                    destination_dir = (
                        dst if relative_path == "."
                        else os.path.join(dst, relative_path)
                    )

                    os.makedirs(destination_dir, exist_ok=True)

                    # Copy files
                    for file in files:
                        source_file = os.path.join(root_dir, file)
                        destination_file = os.path.join(
                            destination_dir,
                            file
                        )

                        shutil.copy2(
                            source_file,
                            destination_file
                        )

                # Remove temporary source folder
                shutil.rmtree(src)

            # -------------------------------------------------
            # Normal file -> copy directly into Files
            # -------------------------------------------------
            else:

                shutil.copy2(src, dst)

    # Clean up temporary files
    shutil.rmtree(temp_extract)
    os.remove(zip_path)

    print("[LOG] Download and extraction complete!")

def cleanup_failed_install():
    print("[LOG] Cleaning up failed installation...")

    base_dir = get_script_directory()

    cleanup_items = [
        os.path.join(base_dir, "Files"),

        # Downloaded ZIP files
        os.path.join(base_dir, "files.zip"),
        os.path.join(base_dir, "v1.3Files.zip"),
        os.path.join(base_dir, "v1.4Files.zip"),
        os.path.join(base_dir, "unrealpak427.zip"),
        os.path.join(base_dir, "app_icon.zip"),

        # Temporary extraction folders
        os.path.join(base_dir, "temp_files"),
        os.path.join(base_dir, "temp_v1_4"),
        os.path.join(base_dir, "temp_427"),
        os.path.join(base_dir, "temp_app_icon"),

        # Temporary application icon
        os.path.join(base_dir, "ModelFixer_temp.ico"),
    ]

    for item in cleanup_items:
        try:
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
                print(f"[LOG] Removed folder: {item}")

            elif os.path.isfile(item):
                os.remove(item)
                print(f"[LOG] Removed file: {item}")

        except Exception as e:
            print(f"[WARNING] Could not remove {item}: {e}")

    print("[LOG] Failed installation cleanup complete!")

def install_all_resources():

    try:

        # ------------------------------------------------
        # Check free disk space before starting installation
        # ------------------------------------------------

        check_disk_space()

        # ------------------------------------------------
        # Install/check every resource package
        # ------------------------------------------------

        ensure_files_folder()
        ensure_files_exist()

        return True, None

    except OSError as e:

        # ------------------------------------------------
        # Disk space error
        # ------------------------------------------------

        if getattr(e, "errno", None) == 28:

            error_message = (
                "Not enough free disk space.\n\n"
                "Please free up at least 500 MB of disk space "
                "and try again."
            )

            print(
                "[ERROR] Not enough free disk space!"
            )

        else:

            error_message = (
                "A system error occurred while installing "
                "the required resources.\n\n"
                f"{e}"
            )

            print(
                f"[ERROR] Resource installation failed: {e}"
            )

        cleanup_failed_install()

        return False, error_message

    except Exception as e:

        # ------------------------------------------------
        # General installation error
        # ------------------------------------------------

        error_message = (
            "Resource installation failed.\n\n"
            f"{e}"
        )

        print(
            f"[ERROR] Resource installation failed: {e}"
        )

        cleanup_failed_install()

        return False, error_message

def ensure_files_folder():
    files_folder = os.path.join(get_script_directory(), "Files")

    # Crucial files/folders that must exist
    required_items = [
        "MeshAibRemover.exe",
        "UnrealPak.exe",
        "UnrealPak-With-Compression.bat",
        "UnrealPak-Without-Compression.bat",
        "UnrealUnpakM0VER.bat",
        ".Resources",
        ".Resources\\bk.png",
        ".Resources\\pricedown bl.otf",
        ".Resources\\ICON.ico",
        ".Resources\\M0VER.png",
    ]

    missing_items = []

    for item in required_items:
        item_path = os.path.join(files_folder, item)

        if not os.path.exists(item_path):
            missing_items.append(item)

    # Everything is present
    if not missing_items:
        #print("[LOG] 'Files' folder and all crucial files are present.")
        return

    # Files folder exists but something is missing
    if os.path.exists(files_folder):
        print("[LOG] 'Files' folder exists, but crucial files are missing:")

        for item in missing_items:
            print(f"[LOG] - {item}")
    else:
        print("[LOG] 'Files' folder not found.")

    print("[LOG] Downloading required files...")

    download_and_extract_files()  # blocking, console download

def run_fix_model():
    file_paths = filedialog.askopenfilenames(
        title="Select UAsset files",
        filetypes=[("UAsset Files", "*.uasset")]
    )

    if not file_paths:
        return

    exe_path = os.path.join(get_script_directory(), "Files", "MeshAibRemover.exe")
    if not os.path.exists(exe_path):
        messagebox.showerror("Error", f"MeshAibRemover.exe not found:\n{exe_path}")
        return

    def run_file(file_path):
        try:
            subprocess.run(
                [exe_path, file_path],
                check=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print(f"✅ Fixed {file_path}")
        except Exception as e:
            print(f"❌ Failed {file_path} ({e})")

    # Run files in background threads
    def background_task():
        max_workers = 5
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_file, fp) for fp in file_paths]
            # Wait for all futures to complete
            for future in as_completed(futures):
                pass

        # Notify user when done
        messagebox.showinfo("Model Fixer", f"Finished processing {len(file_paths)} file(s). Check console for details.")

    threading.Thread(target=background_task, daemon=True).start()

def create_desktop_shortcut(shortcut_name="Model Fixer"):
    """
    Create a shortcut for the application on the desktop.
    """
    try:
        script_dir = get_script_directory()
        target_path = os.path.join(script_dir, "GTA_DE_Model_Fixer.exe")  # adjust if your exe name is different

        # Get the desktop folder path
        desktop_path = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetSpecialFolderPathW(None, desktop_path, 0x00, False)

        # Shortcut path
        shortcut_path = os.path.join(desktop_path.value, f"{shortcut_name}.lnk")

        # Create the shortcut
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = script_dir
        shortcut.IconLocation = target_path
        shortcut.Save()

        messagebox.showinfo("Success", f"Desktop shortcut '{shortcut_name}' created!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create shortcut:\n{e}")

def open_dotnet_download():
    webbrowser.open("https://dotnet.microsoft.com/en-us/download/dotnet/8.0/runtime")

def get_screen_resolution():
    return root.winfo_screenwidth(), root.winfo_screenheight()

def setup_drag_and_drop():
    def drop(event, action):
        dropped_items = root.tk.splitlist(event.data)

        base_dir = os.path.join(get_script_directory(), "Files")

        if action == "create_pak":
            if compression_mode == "Compressed":
                bat_path = os.path.join(base_dir, "UnrealPak-With-Compression.bat")
            else:
                bat_path = os.path.join(base_dir, "UnrealPak-Without-Compression.bat")

        elif action == "unpack_pak":
            if unrealpak_version == "UE4.27":
                bat_path = os.path.join(
                    base_dir,
                    "UnrealPak427",
                    "UnrealUnpak427M0VER.bat"
                )
            else:
                bat_path = os.path.join(base_dir, "UnrealUnpakM0VER.bat")

        if os.path.exists(bat_path):

            for item in dropped_items:
                dropped_item = os.path.abspath(item)

                subprocess.Popen(
                    [bat_path, dropped_item],
                    shell=True
                )

        else:
            messagebox.showerror("Error", f"{bat_path} not found")

    def create_drop_widget(frame, text, action, width=35, height=3, fg="#fc98de", bg="#198246"):
        screen_width, screen_height = get_screen_resolution()
        font_size = 10 if screen_width >= 1920 else 8
        dnd_widget = tk.Label(frame, text=text, width=width, height=height, relief="solid",
                              padx=10, pady=10, anchor="center",
                              font=("Segoe Script Bold", font_size),
                              fg=fg, bg=bg)
        dnd_widget.pack(pady=2)
        dnd_widget.drop_target_register(DND_FILES)
        dnd_widget.dnd_bind('<<Drop>>', lambda event: drop(event, action))

    # Parent frame under the Fix Model button
    pak_frame = tk.Frame(root, bg="#198246")
    pak_frame.place(relx=0.5, rely=0.78, anchor="n")  # position under button

    # Create folder drop frame
    create_frame = tk.Frame(pak_frame, bg="#198246")
    create_frame.pack(side=tk.LEFT, padx=8)
    create_drop_widget(create_frame, "Drop folder to make .PAK", "create_pak")

    # Create unpack drop frame
    unpack_frame = tk.Frame(pak_frame, bg="#198246")
    unpack_frame.pack(side=tk.RIGHT, padx=8)
    create_drop_widget(unpack_frame, "Drop .PAK file to unpack", "unpack_pak")

POSITION_FILE = os.path.join(get_script_directory(), "Files", "window_position.txt")

def save_window_position():
    x = root.winfo_x()
    y = root.winfo_y()
    with open(POSITION_FILE, "w") as f:
        f.write(f"{x},{y}")

def load_window_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as f:
            pos = f.read().strip().split(",")
            if len(pos) == 2 and pos[0].isdigit() and pos[1].isdigit():
                return int(pos[0]), int(pos[1])
    return None

def reset_all_window_positions():
    files_folder = os.path.join(
        get_script_directory(),
        "Files"
    )

    deleted_files = []

    if not os.path.exists(files_folder):
        messagebox.showerror(
            "Reset Window Positions",
            "The Files folder could not be found."
        )
        return

    # Search through Files and all subfolders
    for root_dir, dirs, files in os.walk(files_folder):
        for filename in files:

            # Case-insensitive check for *position*.txt
            if (
                "position" in filename.lower()
                and filename.lower().endswith(".txt")
            ):
                file_path = os.path.join(
                    root_dir,
                    filename
                )

                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    print(f"[LOG] Deleted window position file: {file_path}")

                except Exception as e:
                    print(
                        f"[ERROR] Could not delete "
                        f"{file_path}: {e}"
                    )

    if deleted_files:
        messagebox.showinfo(
            "Reset Window Positions",
            "All saved window positions have been reset.\n\n"
            f"Deleted {len(deleted_files)} position file(s).\n\n"
            "The windows will use their default positions "
            "the next time they are opened."
        )
    else:
        messagebox.showinfo(
            "Reset Window Positions",
            "No saved window position files were found."
        )

def show_credits():
    credits_win = tk.Toplevel(root)
    credits_win.title("Credits")
    credits_win.geometry("550x300")  # slightly taller for links
    credits_win.configure(bg="#2b2b2b")
    credits_win.resizable(False, False)

    # Set the app icon for this Toplevel window
    credits_win.iconbitmap(ICON_PATH)

    # Center the window
    credits_win.update_idletasks()
    w = 550
    h = 300
    screen_w = credits_win.winfo_screenwidth()
    screen_h = credits_win.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    credits_win.geometry(f"{w}x{h}+{x}+{y}")

    # Title
    title = tk.Label(
        credits_win,
        text="Credits",
        font=("Segoe UI", 14, "bold"),
        fg="white",
        bg="#2b2b2b"
    )
    title.pack(pady=(10,5))

    # Frame for credits text and links
    content_frame = tk.Frame(credits_win, bg="#2b2b2b")
    content_frame.pack(expand=True, fill="both", padx=10, pady=5)

    # Credit text
    credits_text = tk.Text(
        credits_win,
        wrap="word",
        font=("Segoe UI", 10),
        fg="white",
        bg="#2b2b2b",
        borderwidth=0,
        highlightthickness=0
    )
    credits_text.insert("1.0",
        "Special thanks to:\n"
        "- ITSM0VER: Made UI for this tool & helped with research.\n"
        "- hypermodule: For making this all possible, wrote the script to make models work again!\n"
        "- RoRoGothic: Helped in many ways!\n\n"
        "Thanks to everyone who helped create, test and support this tool!"
    )
    credits_text.config(state="disabled")
    credits_text.pack(expand=False, fill="x")  # leave space below

def show_info():
    info_win = tk.Toplevel(root)
    info_win.title("Info")
    info_win.geometry("550x300")
    info_win.configure(bg="#2b2b2b")
    info_win.resizable(False, False)

    # Set the app icon for this Toplevel window
    info_win.iconbitmap(ICON_PATH)

    # Center the window
    info_win.update_idletasks()
    w = 550
    h = 300
    screen_w = info_win.winfo_screenwidth()
    screen_h = info_win.winfo_screenheight()
    x = (screen_w // 2) - (w // 2)
    y = (screen_h // 2) - (h // 2)
    info_win.geometry(f"{w}x{h}+{x}+{y}")

    # Title
    title = tk.Label(
        info_win,
        text="Info",
        font=("Segoe UI", 14, "bold"),
        fg="white",
        bg="#2b2b2b"
    )
    title.pack(pady=(10,5))

    # Frame for info text and links
    content_frame = tk.Frame(info_win, bg="#2b2b2b")
    content_frame.pack(expand=True, fill="both", padx=10, pady=(0,5))

    # Text content
    info_text = tk.Text(
        info_win,
        wrap="word",
        font=("Segoe UI", 10),
        fg="white",
        bg="#2b2b2b",
        borderwidth=0,
        highlightthickness=0
    )
    info_text.insert("1.0",
    "Welcome to the DE modding utility!\n\n"

    "How to use model fixer:\n"
    "- Click 'Fix Model' to repair a model with serialisation error.\n"
    "- Choose the uasset file (with uexp in the same folder).\n\n"

    "Convert UAsset to JSON:\n"
    "- Go to File -> Convert UAsset to JSON to open the UAsset to JSON Converter.\n"
    "- Select a .uasset file and convert it into a JSON file for editing or further use.\n\n"

    "How to use Fix Vehicle Lights:\n"
    "- Click 'Fix Vehicle Lights' to open the GTA DE Vehicle Lighting Tool.\n"
    "- You will need to convert the uasset&uexp for your custom VCDE car first!.\n"
    "- This tool is used to repair vehicle lighting data for GTA Definitive Edition vehicles.\n\n"

    "How to use Asset Manager:\n"
    "- Click 'Asset Manager' to open the GTA DE Asset Manager.\n"
    "- The Asset Manager is used to manage and work with GTA Definitive Edition assets.\n"
    "- Use the available asset tools to select and work with the required game files.\n\n"

    "How to use packaging:\n"
    "- Drag a folder onto the first box to create an uncompressed .PAK.\n"
    "- Drag a .PAK file onto the second box to unpack it.\n\n"

    "Changing UnrealPak version:\n"
    "- You may need or want to change the version if a pak file doesnt unpack correctly.\n"
    "- The latest version v4.27 has been added.\n"
    "- Simply click on File -> Change UnrealPak Version at the top.\n\n"

    "Make sure .NET 8.0 Runtime is installed and files are in the correct folders."
)
    info_text.config(state="disabled")
    info_text.pack(expand=True, fill="both", padx=10, pady=5)

    # Function to open URLs
    def open_url(url):
        webbrowser.open(url)

    # Mesh Remover Link
    aib_label = tk.Label(
        content_frame,
        text="GTA DE MeshAibRemover GitHub",
        font=("Segoe UI", 9, "underline"),
        fg="#4a90e2",
        bg="#2b2b2b",
        cursor="hand2"
    )
    aib_label.pack(pady=(2,0))
    aib_label.bind("<Button-1>", lambda e: open_url("https://github.com/hypermodule/MeshAibRemover"))

    # Links directly under the thank-you message
    cue4_label = tk.Label(
        content_frame,
        text="CUE4Parse GitHub",
        font=("Segoe UI", 9, "underline"),
        fg="#4a90e2",
        bg="#2b2b2b",
        cursor="hand2"
    )
    cue4_label.pack(pady=(2,0))
    cue4_label.bind("<Button-1>", lambda e: open_url("https://github.com/FabianFG/CUE4Parse"))

    # UnrealPak GitHub link
    unrealpak_label = tk.Label(
        content_frame,
        text="UnrealPak GitHub",
        font=("Segoe UI", 9, "underline"),
        fg="#4a90e2",
        bg="#2b2b2b",
        cursor="hand2"
    )
    unrealpak_label.pack(pady=(2,0))
    unrealpak_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/xamarth/unrealpak"))

    # UAssetGUI GitHub link
    uassetgui_label = tk.Label(
        content_frame,
        text="UAssetGUI GitHub",
        font=("Segoe UI", 9, "underline"),
        fg="#4a90e2",
        bg="#2b2b2b",
        cursor="hand2"
    )
    uassetgui_label.pack(pady=(2,0))
    uassetgui_label.bind(
        "<Button-1>",
        lambda e: open_url("https://github.com/atenfyr/UAssetGUI")
    )

def open_link():
    webbrowser.open("https://next.nexusmods.com/profile/ITSM0VER/mods")  # URL Link

def on_closing():

    # Make absolutely sure the process is not inside the Files folder
    try:
        os.chdir(get_script_directory())
    except:
        pass

    save_window_position()
    save_unrealpak_settings()
    save_compression_settings()

    # Close the Pillow font object
    try:
        font.close()
    except:
        pass

    # Unload the privately loaded Pricedown font
    font_path = os.path.join(
        get_script_directory(),
        "Files",
        ".Resources",
        "pricedown bl.otf"
    )

    if os.path.exists(font_path):
        try:
            windll.gdi32.RemoveFontResourceExW(
                font_path,
                0x10 | 0x20,
                0
            )
        except Exception:
            pass

    # Destroy all Tkinter windows/resources
    try:
        root.quit()
    except Exception:
        pass

    try:
        root.destroy()
    except Exception:
        pass

    # Remove temporary icon outside the Files folder
    try:
        if os.path.exists(ICON_PATH):
            os.remove(ICON_PATH)
    except Exception:
        pass  

# ---------------------------------------------------------
# Check whether resource installation is actually required
# BEFORE showing the installation window.
# ---------------------------------------------------------

def resources_are_missing():
    files_folder = os.path.join(get_script_directory(), "Files")

    # Files/folders required by the main application
    required_items = [
        "MeshAibRemover.exe",
        "UnrealPak.exe",
        "UnrealPak-With-Compression.bat",
        "UnrealPak-Without-Compression.bat",
        "UnrealUnpakM0VER.bat",
        ".Resources",
        ".Resources\\bk.png",
        ".Resources\\pricedown bl.otf",
        ".Resources\\ICON.ico",
        ".Resources\\M0VER.png",
        "UnrealPak427",
        ".References",
        ".MaterialCreation",
    ]

    for item in required_items:
        item_path = os.path.join(files_folder, item)

        if not os.path.exists(item_path):
            return True

    return False


# ---------------------------------------------------------
# Only show "Installing Resources" if something is missing
# ---------------------------------------------------------

if resources_are_missing():

    # Resources are missing, so show the installation window
    root.deiconify()

    # Force the installation window to appear
    root.update()

    install_result = [False, None]

    def run_install():
        install_result[0], install_result[1] = install_all_resources()

    install_thread = threading.Thread(
        target=run_install,
        daemon=True
    )

    install_thread.start()

    while install_thread.is_alive():
        root.update()
        time.sleep(0.05)

    install_thread.join()

    if not install_result[0]:

        messagebox.showerror(
            "Installation Failed",
            install_result[1]
        )

        root.destroy()
        sys.exit(1)

    # Remove splash screen widgets
    splash_title.destroy()
    splash_message.destroy()


# ---------------------------------------------------------
# Hide the root while the main UI is being constructed
# ---------------------------------------------------------

root.withdraw()

def open_image_picker_window(parent=None):
    def open_image():
        nonlocal original_image, scale_ratio, img_pos_x, img_pos_y, photo

        picker_window.attributes("-topmost", False)
        picker_window.update()

        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            with Image.open(file_path) as source_image:
                original_image = source_image.copy()

            # Reset zoom & position
            scale_ratio = min(canvas_width / original_image.width, canvas_height / original_image.height, 1)
            new_w, new_h = int(original_image.width * scale_ratio), int(original_image.height * scale_ratio)
            img_pos_x = (canvas_width - new_w) // 2
            img_pos_y = (canvas_height - new_h) // 2
            update_image()

            picker_window.attributes("-topmost", True)
            picker_window.update()

    def display_image(img, x, y):
        canvas.delete("all")
        canvas.config(width=canvas_width, height=canvas_height)
        canvas.create_image(x, y, anchor=tk.NW, image=img)
        canvas.image = img

    def get_pixel_color(event):
        if original_image is not None:
            img_x = event.x - img_pos_x
            img_y = event.y - img_pos_y
            if 0 <= img_x < original_image.width * scale_ratio and 0 <= img_y < original_image.height * scale_ratio:
                orig_x = int(img_x / scale_ratio)
                orig_y = int(img_y / scale_ratio)
                pixel_color_rgb = original_image.getpixel((orig_x, orig_y))
                pixel_color_hex = f"#{pixel_color_rgb[0]:02x}{pixel_color_rgb[1]:02x}{pixel_color_rgb[2]:02x}"
                rgb_label.config(text=f"RGBA: {pixel_color_rgb}")
                hex_label.config(text=f"HEX: {pixel_color_hex}")

    def copy_color_hex():
        hex_value = hex_label.cget("text").split(": ")[1]
        pyperclip.copy(hex_value)

    def update_image(center_x=None, center_y=None):
        nonlocal photo, img_pos_x, img_pos_y
        if original_image is None:
            return

        scale_ratio_clamped = max(0.1, min(scale_ratio, 5.0))
        new_width = int(original_image.width * scale_ratio_clamped)
        new_height = int(original_image.height * scale_ratio_clamped)
        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)

        # Keep zoom centered on given point or canvas center
        if center_x is None or center_y is None:
            center_x, center_y = canvas_width // 2, canvas_height // 2
        # Current image coords relative to zoom point
        rel_x = (center_x - img_pos_x) / (original_image.width * scale_ratio)
        rel_y = (center_y - img_pos_y) / (original_image.height * scale_ratio)
        # New top-left
        img_pos_x = int(center_x - rel_x * new_width)
        img_pos_y = int(center_y - rel_y * new_height)

        display_image(photo, img_pos_x, img_pos_y)

    def zoom(event):
        nonlocal scale_ratio
        factor = 1.1 if event.delta > 0 else 0.9
        scale_ratio *= factor
        update_image(event.x, event.y)

    def start_pan(event):
        nonlocal pan_start_x, pan_start_y
        pan_start_x = event.x
        pan_start_y = event.y

    def do_pan(event):
        nonlocal img_pos_x, img_pos_y, pan_start_x, pan_start_y
        dx = event.x - pan_start_x
        dy = event.y - pan_start_y
        img_pos_x += dx
        img_pos_y += dy
        pan_start_x = event.x
        pan_start_y = event.y
        display_image(photo, img_pos_x, img_pos_y)

    # Create Toplevel
    picker_window = tk.Toplevel(parent)
    picker_window.title("Image Color Picker")
    picker_window.configure(bg="#2b2b2b")
    picker_window.attributes("-topmost", True)
    window_width, window_height = 650, 700
    picker_window.geometry(f"{window_width}x{window_height}")
    picker_window.resizable(False, False)
    picker_window.iconbitmap(ICON_PATH)

    # Center window
    screen_width = picker_window.winfo_screenwidth()
    screen_height = picker_window.winfo_screenheight()
    pos_x = (screen_width - window_width) // 2
    pos_y = (screen_height - window_height) // 2
    picker_window.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

    # Canvas
    canvas_width, canvas_height = 600, 500
    canvas = tk.Canvas(picker_window, width=canvas_width, height=canvas_height, bg="#1f1f1f", cursor="pencil")
    canvas.pack(pady=10)

    # Labels
    rgb_label = tk.Label(picker_window, text="RGBA: ", font=("Segoe UI", 10), fg="white", bg="#2b2b2b")
    rgb_label.pack(pady=2)
    hex_label = tk.Label(picker_window, text="HEX: ", font=("Segoe UI", 10), fg="white", bg="#2b2b2b")
    hex_label.pack(pady=2)

    # Buttons
    button_frame = ttk.Frame(picker_window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    open_button = ttk.Button(button_frame, text="Open Image", command=open_image, cursor="hand2")
    open_button.pack(side=tk.LEFT, padx=5, pady=5)

    copy_button = ttk.Button(button_frame, text="Copy Color #", command=copy_color_hex, cursor="hand2")
    copy_button.pack(side=tk.LEFT, padx=5, pady=5)

    #zoom_in_button = ttk.Button(button_frame, text="+", command=lambda: [scale_ratio:=scale_ratio*1.1, update_image()], width=3, cursor="hand2")
    #zoom_in_button.pack(side=tk.LEFT, padx=5, pady=5)

    #zoom_out_button = ttk.Button(button_frame, text="-", command=lambda: [scale_ratio:=scale_ratio/1.1, update_image()], width=3, cursor="hand2")
    #zoom_out_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Variables
    photo = None
    original_image = None
    scale_ratio = 1.0
    img_pos_x = 0
    img_pos_y = 0
    pan_start_x = 0
    pan_start_y = 0

    # Left-click: pick color
    canvas.bind("<Button-1>", get_pixel_color)

    # Right-click: start panning
    canvas.bind("<ButtonPress-3>", start_pan)
    canvas.bind("<B3-Motion>", do_pan)

    # Zoom with mouse wheel
    canvas.bind("<MouseWheel>", zoom)  # Windows
    canvas.bind("<Button-4>", lambda e: [scale_ratio:=scale_ratio*1.1, update_image()])  # Linux scroll up
    canvas.bind("<Button-5>", lambda e: [scale_ratio:=scale_ratio/1.1, update_image()])  # Linux scroll down

    picker_window.wait_window()

def show_links():
    links = [
        ("Tutorials Index", "https://gtaforums.com/topic/982746-gta-definitive-trilogy-tutorials-index/"),
        ("LC.net Tutorial", "https://libertycity.net/gta-the-trilogy/articles/5194-how-to-create-mods-for-gta-the-trilogy.html"),
        ("Modding the NSwitch Version ARCHIVED", "https://web.archive.org/web/20211118210532/https://www.reddit.com/r/GTATrilogyMods/comments/qwzkcc/modding_for_the_nintendo_switch_version/"),
        ("Modding the NSwitch Version", "https://www.reddit.com/r/GTATrilogyMods/comments/qwzkcc/modding_for_the_nintendo_switch_version/"),
        ("Texture Modding Guide", "https://gtaforums.com/topic/977439-gtasade-texture-modding-guide/"),
        ("Sound Modding Guide", "https://gtaforums.com/topic/910487-gta-sa-guide-for-making-car-sound-mods/"),
        ("Localization Modding Guide", "https://gtaforums.com/topic/977646-gtasade-localization-modding-guide/"),
        ("Vehicle Modding Guide", "https://video.wixstatic.com/video/4db758_7b8a302870994003b449e45b1de60f06/1080p/mp4/file.mp4")
    ]

    links_window = tk.Toplevel(root)
    links_window.title("Helpful Links")
    links_window.resizable(False, False)
    links_window.configure(bg="#2b2b2b")
    links_window.wm_attributes("-topmost", 1)

    # Set the app icon for this Toplevel window
    links_window.iconbitmap(ICON_PATH)

    # Fixed size & center
    window_width, window_height = 700, 320
    screen_width = links_window.winfo_screenwidth()
    screen_height = links_window.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    links_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Title label
    title_label = tk.Label(
        links_window,
        text="Helpful GTA DE Modding Links",
        font=("Segoe UI", 14, "bold"),
        bg="#2b2b2b",
        fg="white"
    )
    title_label.pack(pady=(10, 5))

    # Frame for text + scrollbar
    frame = tk.Frame(links_window, bg="#2b2b2b")
    frame.pack(expand=1, fill="both", padx=10, pady=(0,10))

    # Text widget
    text_widget = tk.Text(
        frame,
        wrap="word",
        bg="#2b2b2b",
        fg="white",
        font=("Segoe UI", 10),
        borderwidth=0,
        highlightthickness=0
    )
    text_widget.pack(side="left", expand=1, fill="both")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.insert(tk.END, "Helpful Links:\n\n")

    for description, url in links:
        text_widget.insert(tk.END, f"{description}\n", "desc")
        start = text_widget.index(tk.INSERT)
        text_widget.insert(tk.END, f"{url}\n\n", "link")
        end = text_widget.index(tk.INSERT)
        text_widget.tag_add("link", start, end)

    # Styling
    text_widget.tag_configure("link", foreground="#4a90e2", underline=True)
    text_widget.tag_configure("desc", foreground="white", font=("Segoe UI", 10, "bold"))

    # Link behavior
    def open_url(event):
        start, end = text_widget.tag_prevrange("link", text_widget.index(tk.CURRENT))
        url = text_widget.get(start, end)
        webbrowser.open_new(url)

    text_widget.tag_bind("link", "<Button-1>", open_url)
    text_widget.tag_bind("link", "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind("link", "<Leave>", lambda e: text_widget.config(cursor=""))

    text_widget.config(state=tk.DISABLED)

def update_color():
    r = red_scale.get()
    g = green_scale.get()
    b = blue_scale.get()
    hex_color = f'#{r:02x}{g:02x}{b:02x}'.upper()
    # Update color display (tk.Label)
    color_display.config(bg=hex_color)
    color_code.set(f'RGB({r}, {g}, {b}) / {hex_color}')
    hex_entry_var.set(hex_color)

def choose_color():
    global color_display, red_scale, green_scale, blue_scale, color_code, color_picker_window
    
    # Hide color_picker_window
    color_picker_window.withdraw()
    
    # Open color chooser dialog
    chosen_color = colorchooser.askcolor(title="Choose color", initialcolor="#000000")
    
    if chosen_color[1] is not None:  # Check if a color was actually chosen
        rgb_values = chosen_color[0]  # RGB values are in chosen_color[0]
        red_scale.set(int(rgb_values[0]))
        green_scale.set(int(rgb_values[1]))
        blue_scale.set(int(rgb_values[2]))
        update_color()
        
    # Bring the color picker window back
    color_picker_window.deiconify()
    color_picker_window.lift()
    color_picker_window.focus_force()

def copy_color_decimal():
    # Get the current hex color code from color_code
    hex_code = color_code.get().split(' / ')[-1]
    
    # Copy the hex code to clipboard
    color_picker_window.clipboard_clear()
    color_picker_window.clipboard_append(hex_code)
    color_picker_window.update()  # Manually update clipboard

def update_from_hex(event=None):
    hex_color = hex_entry_var.get()
    if len(hex_color) == 7 and hex_color[0] == '#':
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            red_scale.set(r)
            green_scale.set(g)
            blue_scale.set(b)
            update_color()
        except ValueError:
            pass

def open_color_picker_window(parent=None):
    global color_display, red_scale, green_scale, blue_scale, color_code, color_picker_window, hex_entry_var

    # Create the window
    color_picker_window = tk.Toplevel(parent)
    color_picker_window.title("Color Codes")
    color_picker_window.configure(bg="#2b2b2b")  # Dark background
    color_picker_window.attributes('-topmost', True)
    window_width, window_height = 320, 280
    color_picker_window.geometry(f"{window_width}x{window_height}")
    color_picker_window.resizable(False, False)

    # Set the app icon for this Toplevel window
    color_picker_window.iconbitmap(ICON_PATH)

    # Center the window
    screen_width = color_picker_window.winfo_screenwidth()
    screen_height = color_picker_window.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    color_picker_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Color display
    color_display = tk.Label(
        color_picker_window,
        text="Color Display",
        width=20,
        height=5,
        bg="#1f1f1f",
        fg="white",
        relief="sunken",
        bd=2
    )
    color_display.grid(row=0, column=0, columnspan=3, pady=10)

    # RGB sliders
    slider_bg = "#2b2b2b"
    slider_fg = "#ff5fc0"
    red_scale = tk.Scale(color_picker_window, from_=0, to=255, orient=tk.HORIZONTAL, label="Red",
                         command=lambda x: update_color(), bg=slider_bg, fg=slider_fg, highlightbackground=slider_bg)
    red_scale.grid(row=1, column=0)
    green_scale = tk.Scale(color_picker_window, from_=0, to=255, orient=tk.HORIZONTAL, label="Green",
                           command=lambda x: update_color(), bg=slider_bg, fg=slider_fg, highlightbackground=slider_bg)
    green_scale.grid(row=1, column=1)
    blue_scale = tk.Scale(color_picker_window, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue",
                          command=lambda x: update_color(), bg=slider_bg, fg=slider_fg, highlightbackground=slider_bg)
    blue_scale.grid(row=1, column=2)

    # Current color code display
    color_code = tk.StringVar()
    color_code.set("RGB(0, 0, 0) / #000000")
    color_code_label = tk.Label(
        color_picker_window,
        textvariable=color_code,
        bg="#2b2b2b",
        fg="white"
    )
    color_code_label.grid(row=2, column=0, columnspan=3, pady=5)

    # HEX entry
    hex_entry_var = tk.StringVar()
    hex_entry_var.set("")
    hex_entry = ttk.Entry(color_picker_window, textvariable=hex_entry_var, width=12)
    hex_entry.grid(row=3, column=0, columnspan=3, pady=5)
    hex_entry.bind("<Return>", update_from_hex)

    # Buttons
    choose_color_button = tk.Button(
        color_picker_window,
        text="Choose Color",
        command=choose_color,
        bg="#ff5fc0",
        fg="white",
        activebackground="#ff79d1",
        cursor="hand2"
    )
    choose_color_button.grid(row=4, column=0, pady=10, padx=5)

    # Spacer
    spacer = tk.Label(color_picker_window, width=5, bg="#2b2b2b")
    spacer.grid(row=4, column=1)

    copy_color_button = tk.Button(
        color_picker_window,
        text="Copy Color #",
        command=copy_color_decimal,
        bg="#ff5fc0",
        fg="white",
        activebackground="#ff79d1",
        cursor="hand2"
    )
    copy_color_button.grid(row=4, column=2, pady=10, padx=5)

def rgb_hex_to_float(color):
    if color.startswith('#'):
        color = color[1:]  # Remove the '#' if present
    
    if len(color) == 6:
        r = round(int(color[0:2], 16) / 255.0, 3)
        g = round(int(color[2:4], 16) / 255.0, 3)
        b = round(int(color[4:6], 16) / 255.0, 3)
        return (r, g, b, 1.0)  # Alpha is 1.0 for fully opaque
    elif len(color) == 3:
        r = round(int(color[0], 16) / 15.0, 3)
        g = round(int(color[1], 16) / 15.0, 3)
        b = round(int(color[2], 16) / 15.0, 3)
        return (r, g, b, 1.0)
    elif ',' in color:
        r, g, b = map(float, color.split(','))
        r = round(r / 255.0, 3)
        g = round(g / 255.0, 3)
        b = round(b / 255.0, 3)
        return (r, g, b, 1.0)  # Alpha is 1.0 for fully opaque
    else:
        raise ValueError("Invalid input format")

def open_converter(parent=None):
    def convert_color():
        input_color = entry.get().strip()
        try:
            result = rgb_hex_to_float(input_color)
            result_label.config(text=f"Converted result: {result}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def copy_to_clipboard():
        result = result_label.cget("text")
        if result.startswith("Converted result: "):
            result = result[len("Converted result: "):]
            result = result.strip("()")
            converter_window.clipboard_clear()
            converter_window.clipboard_append(result)

    # Create the converter window
    converter_window = tk.Toplevel(parent)
    converter_window.title("Converter")
    converter_window.resizable(False, False)
    converter_window.configure(bg="#2b2b2b")  # Dark theme
    converter_window.attributes("-topmost", True)
    window_width, window_height = 320, 180

    # Set the app icon for this Toplevel window
    converter_window.iconbitmap(ICON_PATH)

    # Center the window
    screen_width = converter_window.winfo_screenwidth()
    screen_height = converter_window.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    converter_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    # Label
    label = tk.Label(converter_window, text="Enter RGB(0, 0, 0) / HEX(#000000) value:",
                     bg="#2b2b2b", fg="white")
    label.pack(pady=10)

    # Entry
    entry = ttk.Entry(converter_window, width=30)
    entry.pack()

    # Result frame
    result_frame = tk.Frame(converter_window, bg="#2b2b2b")
    result_frame.pack(pady=10)

    result_label = tk.Label(result_frame, text="Converted result will appear here",
                            bg="#2b2b2b", fg="white")
    result_label.pack(side=tk.LEFT)

    copy_button = tk.Button(result_frame, text="Copy", command=copy_to_clipboard,
                            bg="#ff5fc0", fg="white", activebackground="#ff79d1", cursor="hand2")
    copy_button.pack(side=tk.LEFT, padx=5)

    # Convert button
    convert_button = tk.Button(converter_window, text="Convert", command=convert_color,
                               bg="#ff5fc0", fg="white", activebackground="#ff79d1", cursor="hand2")
    convert_button.pack(pady=10)

UNREALPAK_CONFIG_FILE = os.path.join(get_script_directory(), "Files", "config.json")

unrealpak_version = "Default"

def load_unrealpak_settings():
    global unrealpak_version

    if os.path.exists(UNREALPAK_CONFIG_FILE):
        try:
            with open(UNREALPAK_CONFIG_FILE, "r") as f:
                data = json.load(f)
                unrealpak_version = data.get("unrealpak_version", "Default")
        except:
            unrealpak_version = "Default"

def save_unrealpak_settings():
    os.makedirs(os.path.dirname(UNREALPAK_CONFIG_FILE), exist_ok=True)

    with open(UNREALPAK_CONFIG_FILE, "w") as f:
        json.dump({
            "unrealpak_version": unrealpak_version
        }, f)

COMPRESSION_CONFIG_FILE = os.path.join(get_script_directory(), "Files", "config2.json")

compression_mode = "No Compression"

def load_compression_settings():
    global compression_mode

    if os.path.exists(COMPRESSION_CONFIG_FILE):
        try:
            with open(COMPRESSION_CONFIG_FILE, "r") as f:
                data = json.load(f)
                compression_mode = data.get("compression_mode", "No Compression")
        except:
            compression_mode = "No Compression"

def save_compression_settings():
    os.makedirs(os.path.dirname(COMPRESSION_CONFIG_FILE), exist_ok=True)

    with open(COMPRESSION_CONFIG_FILE, "w") as f:
        json.dump({
            "compression_mode": compression_mode
        }, f)

def get_unrealpak_bat():
    base_dir = os.path.join(get_script_directory(), "Files")

    if compression_mode == "Compressed":
        return os.path.join(base_dir, "UnrealPak-With-Compression.bat")
    else:
        return os.path.join(base_dir, "UnrealPak-Without-Compression.bat")

def Compression_Changer():
    global compression_mode

    window = tk.Toplevel(root)
    window.title("Select Compression Mode")
    window.configure(bg="#2b2b2b")
    window.resizable(False, False)

    # Center window
    win_width = 300
    win_height = 160
    x = (root.winfo_screenwidth() // 2) - (win_width // 2)
    y = (root.winfo_screenheight() // 2) - (win_height // 2)
    window.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Icon
    window.iconbitmap(ICON_PATH)

    # Title label
    tk.Label(
        window,
        text=f"Current Mode:\n{compression_mode}",
        bg="#2b2b2b",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        justify="center"
    ).pack(pady=10)

    # Button style
    btn_style = {
        "bg": "#444444",
        "fg": "white",
        "activebackground": "#555555",
        "activeforeground": "white",
        "relief": "flat",
        "width": 18,
        "font": ("Segoe UI", 10),
        "cursor": "hand2"
    }

    def set_compressed():
        global compression_mode
        compression_mode = "Compressed"
        save_compression_settings()
        window.destroy()

    def set_uncompressed():
        global compression_mode
        compression_mode = "No Compression"
        save_compression_settings()
        window.destroy()

    tk.Button(window, text="Compressed", command=set_compressed, **btn_style).pack(pady=5)
    tk.Button(window, text="No Compression", command=set_uncompressed, **btn_style).pack(pady=5)

def Unreal_Pak_Changer():
    global unrealpak_version

    window = tk.Toplevel(root)
    window.title("Select UnrealPak Version")
    window.configure(bg="#2b2b2b")
    window.resizable(False, False)

    # Center window
    win_width = 300
    win_height = 160
    x = (root.winfo_screenwidth() // 2) - (win_width // 2)
    y = (root.winfo_screenheight() // 2) - (win_height // 2)
    window.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Icon
    window.iconbitmap(ICON_PATH)

    # Title label
    tk.Label(
        window,
        text=f"Current Version:\n{unrealpak_version}",
        bg="#2b2b2b",
        fg="white",
        font=("Segoe UI", 11, "bold"),
        justify="center"
    ).pack(pady=10)

    # Button style (NOW includes hand cursor)
    btn_style = {
        "bg": "#444444",
        "fg": "white",
        "activebackground": "#555555",
        "activeforeground": "white",
        "relief": "flat",
        "width": 18,
        "font": ("Segoe UI", 10),
        "cursor": "hand2"
    }

    def set_default():
        global unrealpak_version
        unrealpak_version = "Default"
        save_unrealpak_settings()
        window.destroy()

    def set_427():
        global unrealpak_version
        unrealpak_version = "UE4.27"
        save_unrealpak_settings()
        window.destroy()

    tk.Button(window, text="Default UnrealPak", command=set_default, **btn_style).pack(pady=5)
    tk.Button(window, text="UnrealPak 4.27", command=set_427, **btn_style).pack(pady=5)

def run_converter_clicked():
    converter_exe = os.path.join(
        get_script_directory(),
        "Files",
        ".Resources",
        "UAsset2JsonConverter.exe"
    )

    if os.path.exists(converter_exe):
        subprocess.Popen([converter_exe])
    else:
        messagebox.showerror(
            "Converter Not Found",
            "UAsset2JsonConverter.exe could not be found in Files\\.Resources."
        )

# --- Main UI setup ---
root.title("DE Modding Utility by ITSM0VER")
root.geometry("750x510")
root.configure(bg="#2b2b2b")
root.resizable(False, False)

def load_pricedown_font(font_path):
    FR_PRIVATE = 0x10
    FR_NOT_ENUM = 0x20
    if os.path.exists(font_path):
        windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE | FR_NOT_ENUM, 0)
        return "Pricedown Bl"  # Internal font name from the font file
    return "Arial"  # fallback

pricedown_font_family = load_pricedown_font(
    os.path.join(get_script_directory(), "Files", ".Resources", "pricedown bl.otf")
)

# Path to font file
font_path = os.path.join(get_script_directory(), "Files", ".Resources", "pricedown bl.otf")

# Load the font into memory so Pillow never keeps the OTF file open
with open(font_path, "rb") as f:
    font_data = f.read()

font = ImageFont.truetype(io.BytesIO(font_data), 22)

bg_path = os.path.join(get_script_directory(), "Files", ".Resources", "bk.png")

# Load image completely into memory so Pillow does not keep the PNG file open
with Image.open(bg_path) as source_image:
    bg_image = source_image.copy()

# Resize background to exactly match the application window
window_width = 750
window_height = 530

bg_image = bg_image.resize(
    (window_width, window_height),
    Image.Resampling.LANCZOS
)

# Convert to Tkinter image
bg_photo = ImageTk.PhotoImage(bg_image)

# Place in a label
bg_label = tk.Label(root, image=bg_photo, bg="#2b2b2b")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def get_background_crop(x, y, width, height):
    crop = bg_image.crop(
        (
            x,
            y,
            x + width,
            y + height
        )
    )

    return ImageTk.PhotoImage(crop)

# Icon
if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

def show_about():
    about_win = tk.Toplevel(root)
    about_win.title("About")
    about_win.configure(bg="#2b2b2b")
    about_win.resizable(False, False)

    # Center the window
    win_width = 300
    win_height = 150
    x = (root.winfo_screenwidth() // 2) - (win_width // 2)
    y = (root.winfo_screenheight() // 2) - (win_height // 2)
    about_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Set the app icon for this Toplevel window
    about_win.iconbitmap(ICON_PATH)

    # About text
    tk.Label(
        about_win,
        text="DE Modding Utility v1.4\nby ITSM0VER",
        bg="#2b2b2b",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        justify="center"
    ).pack(expand=True)

    # OK button
    tk.Button(
        about_win,
        text="OK",
        command=about_win.destroy,
        bg="#444444",
        fg="white",
        activebackground="#555555",
        activeforeground="white",
        relief="flat",
        width=10
    ).pack(pady=10)

# --- Custom dark menu bar ---
menu_frame = tk.Frame(
    root,
    bg="#2b2b2b",
    height=25,
    bd=0,
    highlightthickness=0
)

# Pin the menu bar directly to the top-left of the client area.
menu_frame.place(
    x=0,
    y=0,
    relwidth=1.0,
    height=25
)

# Helper function to create dark Menubuttons
def create_dark_menubutton(parent, text, menu_items, font_size=10):
    btn = tk.Menubutton(
        parent,
        text=text,
        bg="#2b2b2b",
        fg="white",
        activebackground="#444444",
        activeforeground="white",
        relief="flat",
        font=("Segoe Script Bold", font_size),
        cursor="hand2"
    )
    menu = tk.Menu(btn, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#444444", activeforeground="white")
    for item in menu_items:
        if item == "separator":
            menu.add_separator()
        else:
            label, command = item
            menu.add_command(label=label, command=command)
    btn.config(menu=menu)
    btn.pack(side="left", padx=5, pady=0)
    return btn

# File menu items
file_items = [
    ("Convert UAsset to JSON", run_converter_clicked),
    "separator",
    ("Change UnrealPak Version", Unreal_Pak_Changer),
    ("Change UnrealPak Compression", Compression_Changer),
    "separator",
    ("Create Desktop Shortcut", create_desktop_shortcut),
    ("Reset All Window Positions", reset_all_window_positions),
    "separator",
    ("Exit", on_closing)
]

# Tools menu items
tools_items = [
    ("Image Color Picker", open_image_picker_window),
    ("RGB Color Codes", open_color_picker_window),
    ("RGB&HEX to float32 Converter", open_converter)
]

# Help menu items
help_items = [
    ("Info", show_info),
    "separator",
    ("Tutorial Links", show_links),
    "separator",
    ("Credits", show_credits),
    (".NET 8.0 Download", open_dotnet_download),
    ("About", show_about)
]

# Create the buttons
file_btn = create_dark_menubutton(menu_frame, "File", file_items)
tools_btn = create_dark_menubutton(menu_frame, "Tools", tools_items)
help_btn = create_dark_menubutton(menu_frame, "Help", help_items)

# Restore last position
last_pos = load_window_position()
if last_pos:
    root.geometry(f"+{last_pos[0]}+{last_pos[1]}")  # only position, keep current size

# Save position on close
root.protocol("WM_DELETE_WINDOW", on_closing)

# ttk styling
style = ttk.Style()
style.theme_use("clam")  # modern base theme

# Style for normal button
style.configure(
    "Fix.TButton",
    font=("Segoe UI", 12, "bold"),
    foreground="white",
    background="#4a90e2",
    padding=10,
    borderwidth=0
)

# Hover effect
style.map(
    "Fix.TButton",
    background=[("active", "#357ABD")],  # darker blue on hover
    foreground=[("active", "white")]
)

# Display photo at the top
img_path = os.path.join(get_script_directory(), "Files", ".Resources", "M0VER.png")

with Image.open(img_path) as source_image:
    img = source_image.copy()

img = img.resize((120, 120), Image.Resampling.LANCZOS)
photo = ImageTk.PhotoImage(img)
img_label = tk.Label(root, image=photo, bg="#2b2b2b", cursor="hand2")  # hand cursor
img_label.image = photo
img_label.place(relx=0.5, rely=0.25, anchor="center")

# Make it clickable
img_label.bind("<Button-1>", lambda e: open_link())

# Place Fix Model button below the image
def on_enter(e):
    btn_canvas.itemconfig(polygon, fill="#2ecc71")  # brighter green

def on_leave(e):
    btn_canvas.itemconfig(polygon, fill="#27ae60")  # normal green

def run_fix_model_clicked():
    run_fix_model() #Fix that thang PACHOW xD

def run_vehicle_lights_clicked():
    vehicle_lights_exe = os.path.join(
        get_script_directory(),
        "Files",
        ".Resources",
        "VCDEVehLightFixer.exe"
    )

    if os.path.exists(vehicle_lights_exe):
        subprocess.Popen([vehicle_lights_exe])
    else:
        messagebox.showerror(
            "Vehicle Lights Fixer Not Found",
            "VCDEVehLightFixer.exe could not be found in Files\\.Resources."
        )

def run_asset_manager_clicked():

    asset_editor_exe = os.path.join(
        get_script_directory(),
        "Files",
        ".Resources",
        "AssetEditor.exe"
    )

    if os.path.exists(asset_editor_exe):
        os.startfile(asset_editor_exe)
    else:
        messagebox.showerror(
            "Asset Manager Not Found",
            "AssetEditor.exe could not be found in Files\\.Resources."
        )

# Place button canvas, but no bg color
btn_canvas = tk.Canvas(root, width=230, height=60, highlightthickness=0, bd=0)
btn_canvas.place(relx=0.5, rely=0.47, anchor="center")

# Fix Model Button background
button_width = 230
button_height = 60

# Position of the button on the main window
button_x = int((750 - button_width) / 2)
button_y = int(530 * 0.47 - button_height / 2)

# Get the exact background underneath the button
bg_subimage = get_background_crop(
    button_x,
    button_y,
    button_width,
    button_height
)

# Draw on canvas
btn_canvas.create_image(
    0,
    0,
    image=bg_subimage,
    anchor="nw"
)

# Keep reference
btn_canvas.bg_ref = bg_subimage

# Draw on canvas
btn_canvas.create_image(0, 0, image=bg_subimage, anchor="nw")

# Keep a reference to stop garbage collection
btn_canvas.bg_ref = bg_subimage

# Amount to shift everything right
x_offset = 15  # increase to move further right

# Polygon (shifted)
polygon = btn_canvas.create_polygon(
    15 + x_offset, 0, 185 + x_offset, 0, 170 + x_offset, 50, 0 + x_offset, 50,
    fill="", outline="", width=2
)

# Shadow text (shifted)
shadow = btn_canvas.create_text(
    95 + x_offset, 25,
    text="Fix Model",
    fill="black",
    font=("Pricedown bl", 22, "bold")
)

# Main text (shifted)
text = btn_canvas.create_text(
    93 + x_offset, 23,
    text="Fix Model",
    fill="#ff5fc0",
    font=("Pricedown bl", 22, "bold")
)


# Hover effect functions
def on_enter(e):
    btn_canvas.itemconfig(polygon, fill="#27ae60", outline="#000000")  # green fill with black border
    btn_canvas.itemconfig(shadow, fill="black")

def on_leave(e):
    btn_canvas.itemconfig(polygon, fill="", outline="")  # fully invisible again
    btn_canvas.itemconfig(text, fill="#ff5fc0")
    btn_canvas.itemconfig(shadow, fill="black")

for item in (text, shadow, polygon):
    btn_canvas.tag_bind(item, "<Enter>", lambda e: [on_enter(e), btn_canvas.config(cursor="hand2")])
    btn_canvas.tag_bind(item, "<Leave>", lambda e: [on_leave(e), btn_canvas.config(cursor="")])
    btn_canvas.tag_bind(item, "<Button-1>", lambda e: run_fix_model_clicked())

# -----------------------------------------
# Vehicle Lights button
# -----------------------------------------

vehlights_btn_canvas = tk.Canvas(
    root,
    width=230,
    height=60,
    highlightthickness=0,
    bd=0
)

vehlights_btn_canvas.place(
    relx=0.5,
    rely=0.6,
    anchor="center"
)

# Vehicle Lights button background
vehlights_width = 230
vehlights_height = 60

# Position of the button on the main window
vehlights_x = int((750 - vehlights_width) / 2)
vehlights_y = int(525 * 0.60 - vehlights_height / 2)

# Get the exact background underneath the button
vehlights_bg_subimage = get_background_crop(
    vehlights_x,
    vehlights_y,
    vehlights_width,
    vehlights_height
)

vehlights_btn_canvas.create_image(
    0,
    0,
    image=vehlights_bg_subimage,
    anchor="nw"
)

vehlights_btn_canvas.bg_ref = vehlights_bg_subimage

vehlights_polygon = vehlights_btn_canvas.create_polygon(
    5 + x_offset, 0,
    210 + x_offset, 0,
    195 + x_offset, 50,
    -10 + x_offset, 50,
    fill="",
    outline="",
    width=2
)

# Shadow text
vehlights_shadow = vehlights_btn_canvas.create_text(
    101 + x_offset,
    25,
    text="Fix Vehicle Lights",
    fill="black",
    font=("Pricedown bl", 19, "bold")
)

# Main text
vehlights_text = vehlights_btn_canvas.create_text(
    99 + x_offset,
    23,
    text="Fix Vehicle Lights",
    fill="#ff5fc0",
    font=("Pricedown bl", 19, "bold")
)

# Hover effect
def vehlights_on_enter(e):
    vehlights_btn_canvas.itemconfig(
        vehlights_polygon,
        fill="#27ae60",
        outline="#000000"
    )
    vehlights_btn_canvas.itemconfig(
        vehlights_shadow,
        fill="black"
    )

def vehlights_on_leave(e):
    vehlights_btn_canvas.itemconfig(
        vehlights_polygon,
        fill="",
        outline=""
    )
    vehlights_btn_canvas.itemconfig(
        vehlights_text,
        fill="#ff5fc0"
    )
    vehlights_btn_canvas.itemconfig(
        vehlights_shadow,
        fill="black"
    )

# Hover and click bindings
for item in (
    vehlights_text,
    vehlights_shadow,
    vehlights_polygon
):
    vehlights_btn_canvas.tag_bind(
        item,
        "<Enter>",
        lambda e: [
            vehlights_on_enter(e),
            vehlights_btn_canvas.config(cursor="hand2")
        ]
    )

    vehlights_btn_canvas.tag_bind(
        item,
        "<Leave>",
        lambda e: [
            vehlights_on_leave(e),
            vehlights_btn_canvas.config(cursor="")
        ]
    )

    vehlights_btn_canvas.tag_bind(
        item,
        "<Button-1>",
        lambda e: run_vehicle_lights_clicked()
    )

# -----------------------------------------
# Asset Manager button
# -----------------------------------------

asset_btn_canvas = tk.Canvas(
    root,
    width=230,
    height=60,
    highlightthickness=0,
    bd=0
)

asset_btn_canvas.place(
    relx=0.5,
    rely=0.73,
    anchor="center"
)

# Asset Manager button background
asset_width = 230
asset_height = 60

# Position of the button on the main window
asset_x = int((750 - asset_width) / 2)
asset_y = int(530 * 0.73 - asset_height / 2)

# Get the exact background underneath the button
asset_bg_subimage = get_background_crop(
    asset_x,
    asset_y,
    asset_width,
    asset_height
)

asset_btn_canvas.create_image(
    0,
    0,
    image=asset_bg_subimage,
    anchor="nw"
)

asset_btn_canvas.bg_ref = asset_bg_subimage

# Polygon
asset_polygon = asset_btn_canvas.create_polygon(
    5 + x_offset, 0,
    210 + x_offset, 0,
    195 + x_offset, 50,
    -10 + x_offset, 50,
    fill="",
    outline="",
    width=2
)

# Shadow text
asset_shadow = asset_btn_canvas.create_text(
    101 + x_offset,
    25,
    text="Asset Manager",
    fill="black",
    font=("Pricedown bl", 21, "bold")
)

# Main text
asset_text = asset_btn_canvas.create_text(
    99 + x_offset,
    23,
    text="Asset Manager",
    fill="#ff5fc0",
    font=("Pricedown bl", 21, "bold")
)


# Hover effect
def asset_on_enter(e):

    asset_btn_canvas.itemconfig(
        asset_polygon,
        fill="#27ae60",
        outline="#000000"
    )

    asset_btn_canvas.itemconfig(
        asset_shadow,
        fill="black"
    )


def asset_on_leave(e):

    asset_btn_canvas.itemconfig(
        asset_polygon,
        fill="",
        outline=""
    )

    asset_btn_canvas.itemconfig(
        asset_text,
        fill="#ff5fc0"
    )

    asset_btn_canvas.itemconfig(
        asset_shadow,
        fill="black"
    )


# Hover and click bindings
for item in (
    asset_text,
    asset_shadow,
    asset_polygon
):

    asset_btn_canvas.tag_bind(
        item,
        "<Enter>",
        lambda e: [
            asset_on_enter(e),
            asset_btn_canvas.config(cursor="hand2")
        ]
    )

    asset_btn_canvas.tag_bind(
        item,
        "<Leave>",
        lambda e: [
            asset_on_leave(e),
            asset_btn_canvas.config(cursor="")
        ]
    )

    asset_btn_canvas.tag_bind(
        item,
        "<Button-1>",
        lambda e: run_asset_manager_clicked()
    )

# Watermark label
watermark = tk.Label(
    root,
    text="Made by ITSM0VER",
    font=("Segoe UI", 8, "italic"),
    fg="#AAAAAA",        # light gray text
    bg="#2b2b2b"         # match window background
)
watermark.pack(side="bottom", pady=0)

load_unrealpak_settings()

load_compression_settings()

setup_drag_and_drop()

# Re-apply the temporary application icon
if os.path.exists(ICON_PATH):
    try:
        root.iconbitmap(ICON_PATH)
    except Exception as e:
        print(f"[WARNING] Could not set application icon: {e}")

# Make sure all widgets have their correct geometry before showing
root.update_idletasks()

# Show the fully constructed main application
root.deiconify()

root.mainloop()
