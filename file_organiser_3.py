import os
import shutil
import logging
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
config = configparser.ConfigParser()
config.read('file_organizer_config.ini')

# Conversion factors
BYTE = 1
KILOBYTE = 1024 * BYTE
MEGABYTE = 1024 * KILOBYTE
GIGABYTE = 1024 * MEGABYTE


def convert_size(size, unit):
    if unit == "Bytes":
        return size * BYTE
    elif unit == "Kilobytes":
        return size * KILOBYTE
    elif unit == "Megabytes":
        return size * MEGABYTE
    elif unit == "Gigabytes":
        return size * GIGABYTE
    else:
        return size  # Default to bytes if unit is not recognized


def should_process_file(file_path, min_size, max_size, size_unit):
    # Convert size limits to bytes
    min_size_bytes = convert_size(min_size, size_unit)
    max_size_bytes = convert_size(max_size, size_unit)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Filter by size
    if (min_size != 0 and file_size < min_size_bytes) or (max_size != 0 and file_size > max_size_bytes):
        return False

    return True


def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}({counter}){extension}"
        counter += 1

    return new_filename


def organize_files(directory, delete_originals, dry_run, min_size, max_size, size_unit):
    file_extension_dict = {}

    # Loop over each file in the selected directory
    for fileName in os.listdir(directory):
        # Get the full path of the file
        file_path = os.path.join(directory, fileName)

        # Skip if it is a directory or a hidden/system file
        if os.path.isdir(file_path) or fileName.startswith('.'):
            continue

        # Check if file should be processed
        if not should_process_file(file_path, min_size, max_size, size_unit):
            continue

        # Split the file name into name and extension
        name, fileExtension = os.path.splitext(fileName)

        # Remove the leading dot from the extension
        fileExtension = fileExtension[1:] if fileExtension else 'no_extension'

        # Append the file to the corresponding extension list
        if fileExtension not in file_extension_dict:
            file_extension_dict[fileExtension] = []
        file_extension_dict[fileExtension].append(fileName)

    # Create directories for each file extension, copy the files, then delete them
    for extension, files in file_extension_dict.items():
        # Create directory for the extension if it does not exist
        extension_dir = os.path.join(directory, extension)
        if not os.path.exists(extension_dir):
            if not dry_run:
                os.mkdir(extension_dir)
            logging.info(f"Created directory: {extension_dir}")

        # Copy files into the corresponding directory and delete them from original path
        for file in files:
            src_file_path = os.path.join(directory, file)
            unique_dest_file = get_unique_filename(extension_dir, file)
            dest_file_path = os.path.join(extension_dir, unique_dest_file)
            try:
                if dry_run:
                    logging.info(f"Would copy {src_file_path} to {dest_file_path}")
                else:
                    shutil.copy(src_file_path, dest_file_path)
                    logging.info(f"Copied {src_file_path} to {dest_file_path}")
                    if delete_originals:
                        os.remove(src_file_path)
                        logging.info(f"Deleted {src_file_path}")
            except PermissionError as e:
                logging.error(f"PermissionError: {e} - {src_file_path}")
            except Exception as e:
                logging.error(f"Error: {e} - {src_file_path}")

    # Print the result
    result_message = ""
    for extension, files in file_extension_dict.items():
        result_message += f"Files with .{extension} extension:\n"
        for file in files:
            result_message += f"  - {file}\n"

    return result_message


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        delete_originals = delete_var.get()
        dry_run = dry_run_var.get()

        min_size = 0 if min_size_var.get() == '' else float(min_size_var.get())
        max_size = 0 if max_size_var.get() == '' else float(max_size_var.get())
        size_unit = unit_var.get()

        result_message = organize_files(directory, delete_originals, dry_run, min_size, max_size, size_unit)
        messagebox.showinfo("Operation Completed", result_message)


# Create the main application window
root = ctk.CTk()
root.title("File Organizer")

# Set the window size
root.geometry("500x600")
root.resizable(False, False)

# Create and place UI elements
ctk.CTkLabel(root, text="Size Unit:").pack(padx=20, pady=10)
unit_var = tk.StringVar()
unit_var.set("Bytes")  # Default selection
units = ["Bytes", "Kilobytes", "Megabytes", "Gigabytes"]
for unit in units:
    ctk.CTkRadioButton(root, text=unit, variable=unit_var, value=unit).pack(padx=20, pady=10)

ctk.CTkLabel(root, text="Minimum File Size:").pack(padx=20, pady=10)
min_size_var = tk.StringVar()
ctk.CTkEntry(root, textvariable=min_size_var).pack(padx=20, pady=10)

ctk.CTkLabel(root, text="Maximum File Size:").pack(padx=20, pady=10)
max_size_var = tk.StringVar()
ctk.CTkEntry(root, textvariable=max_size_var).pack(padx=20, pady=10)


delete_var = ctk.BooleanVar()
ctk.CTkCheckBox(root, text="Delete original files", variable=delete_var).pack(padx=20, pady=10)

dry_run_var = ctk.BooleanVar()
ctk.CTkCheckBox(root, text="Dry run (simulate operations)", variable=dry_run_var).pack(padx=20, pady=10)

select_button = ctk.CTkButton(root, text="Select Directory and Organize Files", command=select_directory)
select_button.pack(expand=True)

ctk.CTkLabel(root, text='Author: Yousef (Joey) Sedik©\nFile Organiser V1.3 11/7/2024').pack(padx=20, pady=10)

# Run the application
root.mainloop()
