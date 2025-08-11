import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import json
import subprocess
from time import sleep
import os
import sys
from PIL import Image, ImageTk

ico_path = None
output_name = None
icon_preview = None


def write_token(user_token):
    with open("config.json", "r") as config:
        data = json.load(config)
        data["token"] = user_token
        with open('config.json', 'w') as f:
            json.dump(data, f, indent=4)
    messagebox.showinfo("Success", "Token Saved Successfully in config.json!")

def take_token():
    with open("config.json", "r") as token:
        data = json.load(token)
        return data["token"]

def write_to_hater(token):
    with open("HaterCollecter.py", "rb") as hater_content:
        hater_data = hater_content.read()
    if f'token = "{token}"'.encode("utf-8") in hater_data and "bot.run(token)".encode("utf-8") in hater_data:
        messagebox.showerror("Error", "Already Saved in HaterCollecter.py")
    else:
        with open("HaterCollecter.py", "a") as hater:
            hater.write(f'\ntoken = "{token}"\nbot.run(token)')
            messagebox.showinfo("Success", "Saved in HaterCollecter.py")



def build_file(ico_file, name):
    status_label.configure(text="Building...")
    progress_bar.start()
    app.update_idletasks()
    cmd = [
        'pyinstaller',
        '--onefile',
        'HaterCollecter.py',
        '--windowed',
        f'--icon={ico_file}',
        f'--name={name}',
    ]
    subprocess.run(cmd, check=True)
    os.system("clear || cls")
    sleep(0.5)
    progress_bar.stop()
    progress_bar.set(1)
    messagebox.showinfo("Success", f"Created {name}.exe in /dist")
    dist_path = os.path.join(os.getcwd(), "dist")
    try:
        if sys.platform.startswith('win'):
            os.startfile(dist_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', dist_path])
        else:
            subprocess.Popen(['xdg-open', dist_path])
    except Exception:
        pass
    app.after(3000, clear_status)

def clear_status():
    status_label.configure(text="")
    progress_bar.set(0)

def change_theme(mode):
    ctk.set_appearance_mode(mode.lower())

def save_token():
    user_token = token_entry.get()
    if user_token == "":
        messagebox.showerror("Error","Enter Token.")
        return False
    else:
        write_token(user_token=user_token)
        write_to_hater(token=user_token)

def browse_icon():
    file_path = filedialog.askopenfilename(
        title="Select Icon File", filetypes=(("ICO Files", "*.ico"),),
    )
    if file_path:
        ico_path.set(file_path)
        try:
            img = Image.open(file_path).resize((32, 32), Image.LANCZOS)
            icon = ImageTk.PhotoImage(img)
            icon_preview.configure(image=icon, text="")
            icon_preview.image = icon
        except Exception:
            icon_preview.configure(text="No preview")



def create_exe():
    if save_token() is False:
        return
    if not ico_path.get():
        messagebox.showerror("Error", "Please select an ICO file.")
        return
    name = output_name.get().strip() or "HaterCollecter"
    build_file(ico_file=ico_path.get(), name=name)

app = tk.Tk()
app.iconbitmap("fav.ico")
app.title("HaterCollecter Builder")
app.geometry("600x500")
app.resizable(False, False)
ico_path = tk.StringVar()
output_name = tk.StringVar(value="HaterCollecter")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app.configure(bg="#060606")

frame = ctk.CTkFrame(master=app, corner_radius=15, fg_color="#121212")
frame.pack(pady=20, padx=20, fill="both", expand=True)

theme_menu = ctk.CTkOptionMenu(master=frame, values=["Dark", "Light"], command=change_theme, width=120)
theme_menu.set("Dark")
theme_menu.place(relx=1, x=-20, y=20, anchor="ne")

title_label = ctk.CTkLabel(master=frame, text="HaterCollecter Builder", font=("Arial", 24, "bold"))
title_label.pack(pady=(30, 10))

desc_label = ctk.CTkLabel(master=frame, text="Generate an executable for your Discord bot", font=("Arial", 14))
desc_label.pack(pady=(0, 20))

token_label = ctk.CTkLabel(master=frame, text="Bot Token", font=("Arial", 14, "bold"))
token_label.pack(pady=(0, 6))

token_entry = ctk.CTkEntry(master=frame, width=260, height=32,
                           font=("Arial", 12), placeholder_text="Enter token...")
token_entry.pack(pady=6, padx=10)

# Pre-fill the entry with the token from config.json if available
try:
    token_entry.insert(0, take_token())
except Exception:
    pass

icon_label = ctk.CTkLabel(master=frame, text="Icon File", font=("Arial", 14, "bold"))
icon_label.pack(pady=(10, 6))

icon_frame = ctk.CTkFrame(master=frame, fg_color="transparent")
icon_frame.pack(pady=(0, 6))
icon_entry = ctk.CTkEntry(
    master=icon_frame,
    width=200,
    height=32,
    font=("Arial", 12),
    textvariable=ico_path,
    placeholder_text="Select icon...",
)
icon_entry.pack(side="left", padx=(0, 6))
browse_button = ctk.CTkButton(
    master=icon_frame,
    text="Browse",
    command=browse_icon,
    width=70,
    height=32,
    font=("Arial", 12),
)
browse_button.pack(side="left")

icon_preview = ctk.CTkLabel(master=icon_frame, text="", width=32, height=32)
icon_preview.pack(side="left", padx=(6, 0))

name_label = ctk.CTkLabel(master=frame, text="Output Name", font=("Arial", 14, "bold"))
name_label.pack(pady=(10, 6))

name_entry = ctk.CTkEntry(
    master=frame,
    width=260,
    height=32,
    font=("Arial", 12),
    textvariable=output_name,
    placeholder_text="HaterCollecter",
)
name_entry.pack(pady=6, padx=10)

build_button = ctk.CTkButton(master=frame, text="Build EXE", command=create_exe, width=200, height=40, font=("Arial", 12, "bold"), fg_color="#1e90ff", hover_color="#1c7ed6")
build_button.pack(pady=18, padx=10)

progress_bar = ctk.CTkProgressBar(master=frame, width=260)
progress_bar.pack(pady=(0, 12))
progress_bar.set(0)

status_label = ctk.CTkLabel(master=frame, text="", font=("Arial", 12, "italic"))
status_label.pack(pady=(0, 10))

window_width = 600
window_height = 500

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

app.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

app.mainloop()
