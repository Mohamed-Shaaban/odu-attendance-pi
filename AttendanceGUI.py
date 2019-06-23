import json
import time
import pyqrcode
import requests
import logging
import logging.handlers
import os
from tkinter import *
from configapi import get_config_info as configs
from PIL import ImageTk, Image
from AnimatedGIF import AnimatedGIF


class Window(Tk):
    cardCode = ''
    theToken = ''
    cancel_after_id = ''
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        Tk.__init__(self)
        self.confs = configs()
        self.logger = logging.getLogger('Attendace GUI')
        self.logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.handlers.RotatingFileHandler(
            self.dir_path + '/log/attendance_gui.log',
            mode='a',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(handler)
        self.title("Old Dominion Attendance Application")
        self.state = True
        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)

    def createMyView(self, token, title, projector_view=False):
        self.theToken = token
        if token:
            if projector_view:
                self.geometry('{}x{}'.format(1820, 980))
                self.createProjectorView(token, title)
            else:
                self.geometry('{}x{}'.format(800, 500))
                self.createReaderView(token, title)
        else:
            self.geometry('{}x{}'.format(1820, 980)) if projector_view else self.geometry('{}x{}'.format(800, 500))
            self.createNotActiveSesstionView()

    def createProjectorView(self, token, title):
        # Generate the Code based on the session token
        Window.createQRCode(token)
        qr_code_frame = Frame(
            self, bg='white',
            highlightbackground="green",
            highlightcolor="red",
            highlightthickness=0,
            bd=0
        )
        label_frame = Frame(
            self, bg='white',
            highlightbackground="gray",
            highlightcolor="red",
            highlightthickness=1,
            bd=0
        )

        qr_code_frame.pack(anchor=N, fill=BOTH, expand=True, side=LEFT)
        label_frame.pack(anchor=S, fill=BOTH, expand=True, side=LEFT)

        Qrimage = self.createImage('/img/code.png', (1000, 1000))
        qr_panel = Label(qr_code_frame, image=Qrimage, borderwidth=0)
        qr_panel.pack(side=LEFT)
        # panel.grid(row=0, column=1, sticky="nw")
        qr_panel.image = Qrimage

        title_label = Label(label_frame, text=title)
        title_label.place(x=160, y=60, anchor="center")
        title_label.config(width=600, font=("Arial", 18), bg="white", pady=25)
        title_label.pack(side=TOP)

    def createReaderView(self, token, title):
        # Generate the Code based on the session token
        Window.createQRCode(token)
        # Main containers
        left = Frame(self, bg='white', highlightthickness=0)
        top_right = Frame(self, bg='white', highlightthickness=0)
        btm_right = Frame(self, bg='white', highlightthickness=0)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # old frame setting
        for r in range(6):
            self.grid_rowconfigure(r, weight=1)
        for c in range(6):
            self.grid_columnconfigure(c, weight=1)

        left.grid(row=0, column=0, rowspan=6, columnspan=3, sticky=W + E + N + S)
        top_right.grid(row=0, column=3, rowspan=2, columnspan=3, padx=0, sticky=W + E + N + S)
        btm_right.grid(row=2, column=3, rowspan=4, columnspan=3, sticky=W + E + N + S)

        self.label1 = Label(top_right, text=title)
        self.label1.place(x=200, y=65, anchor="center")
        self.label1.config(width=800, font=("Arial", 12), bg="white", padx=35)

        # reading the card
        self.label = Label(btm_right, text="Please Swipe your Card")
        self.label.place(x=200, y=165, anchor="center")
        self.label.config(width=400, font=("Arial", 12), bg="white", padx=0)

        self.canvas = Canvas(btm_right, width=250, height=210, highlightthickn=0)
        self.canvas.configure(background='white')
        self.canvas.place(x=165, y=45, anchor="center")

        self.present_img = self.createImage('/img/present.png', size=(150, 150))
        self.absent_img = self.createImage('/img/absent.png', size=(130, 130))
        self.invalid_img = self.createImage('/img/invalid.png', size=(150, 150))
        self.late_img = self.createImage('/img/late.png', size=(150, 150))
        # self.loading_gif = AnimatedGIF(self.canvas, self.dir_path + '/img/loading.gif')

        self.status_item = self.canvas.create_image(155, 125, image=self.present_img, state=HIDDEN)
        # self.loading = self.canvas.create_window(155, 125, window=self.loading_gif, state=HIDDEN)

        self.bind('<Key>', self.get_key)

        # insert QR code
        qr_img = self.createImage('/img/code.png', size=(450, 450))
        panel = Label(left, image=qr_img, borderwidth=0)
        panel.place(x=200, y=200, anchor="center")
        panel.image = qr_img

        odu_logo = self.createImage(file_path='/img/odu-logo.gif', size=(150, 75))
        panel = Label(btm_right, image=odu_logo, borderwidth=0)
        panel.place(x=200, y=245, anchor="center")
        panel.config(highlightthickness=0)
        panel.image = odu_logo

        top_right.grid_rowconfigure(0, weight=1)
        top_right.grid_columnconfigure(1, weight=1)

    def createImage(self, file_path, size):
        image = Image.open(self.dir_path + file_path)
        image = image.resize(size, Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        return image

    def createNotActiveSesstionView(self):
        main = Frame(
            self, bg='white',
            highlightbackground="green",
            highlightcolor="green",
            highlightthickness=2,
            bd=0
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main.pack(anchor=N, fill=BOTH, expand=True, side=LEFT)
        oduLogo = Image.open(self.dir_path + '/img/odu.jpg')
        basewidth = 400
        wpercent = (basewidth / float(oduLogo.size[0]))
        hsize = int((float(oduLogo.size[1]) * float(wpercent)))
        oduLogo = oduLogo.resize((basewidth, hsize), Image.ANTIALIAS)
        oduLogo = ImageTk.PhotoImage(oduLogo)
        panel = Label(main, image=oduLogo, borderwidth=0)
        panel.image = oduLogo
        panel.pack(anchor=CENTER)

        label = Label(main, text="No Active Session", borderwidth=1, relief="solid")
        label.config(width=100, font=("Arial", 60), bg="white")
        label.pack(anchor=CENTER)

    def get_key(self, event):
        if not self.theToken:
            return None

        if event.char in '0123456789;=':
            self.cardCode += event.char
        elif event.char == '?':
            self.cardCode += event.char
            headers = {'Authorization': self.confs['OAuthToken'], 'Content-type': 'application/json'}
            # if the card code is not proper format
            if len(self.cardCode) != 16:
                if len(self.cardCode) > 16:
                    codes = set(self.cardCode.split(";"))
                    for code in codes:
                        if len(code) != 15:
                            continue
                        code = ";" + code
                        self.submit_code(code, headers)
                    return None
                else:
                    self.logger.error('Error reading card: ' + self.cardCode)
                    self.label.after_cancel(self.cancel_after_id)
                    self.clear_label()
                    self.label['text'] = "Error, Please try again!"
                    self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.invalid_img)
                    self.cancel_after_id = self.label.after(1000, self.clear_label)
                    return None

            self.submit_code(self.cardCode, headers)
            return None

    def submit_code(self, code, headers):
        self.label.after_cancel(self.cancel_after_id)
        # self.loading_gif.start_animation()
        # self.canvas.itemconfigure(self.loading, state=NORMAL)
        current_time = int(round(time.time() * 1000))
        postData = {
            "timestamp": current_time,
            "token": self.theToken,
            "identifier": {
                "type": "SWIPE",
                "identifier": code
            }
        }
        jsonData = json.dumps(postData)
        try:
            response = requests.post(self.confs['submitAttendanceAPI'], data=jsonData, headers=headers)
        except Exception as e:
            self.logger.error("Error, was not able to post the request to ESB! ")
            self.clear_label()
            self.label['text'] = "Error Submitting, Please try again!"
            self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.invalid_img)
            self.cancel_after_id = self.label.after(1000, self.clear_label)
            return

        after_scan = int(round(time.time() * 1000))
        if response.status_code == 200:
            result = json.loads(response.content.decode('utf-8'))
            response_code = result.get('response', 'unknown')
            self.logger.info('Attendance was submitted successfully for card number: ' + code
                             + ' -- submission time: ' + str(after_scan - current_time) + ' (ms) '
                             + ' -- result code: ' + str(response_code))
            self.clear_label()
            if response_code == 1:
                self.label['text'] = "Marked Present"
                self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.present_img)
            elif response_code == 2:
                self.label['text'] = "Marked Absent"
                self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.absent_img)
            elif response_code == 3:
                self.label['text'] = "Marked Tardy"
                self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.late_img)
            elif response_code == 99:
                self.label['text'] = "Invalid, Please try again later"
                self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.invalid_img)
            else:
                self.label['text'] = "Invalid, Unknown Error!"
                self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.invalid_img)
            self.cancel_after_id = self.label.after(1000, self.clear_label)
        else:
            self.logger.error('Error submitting card info: ' + code
                              + ' -- Error code: ' + str(response.status_code)
                              + ' -- submission time: ' + str(after_scan - current_time) + ' (ms) ')

            self.clear_label()
            self.label['text'] = "Error Submitting, Please try again!"
            self.canvas.itemconfigure(self.status_item, state=NORMAL, image=self.invalid_img)
            self.cancel_after_id = self.label.after(1000, self.clear_label)
            # raise Exception

    def clear_label(self):
        # self.canvas.itemconfigure(self.loading, state=HIDDEN)
        # self.loading_gif.stop_animation()
        self.label['text'] = "Please Swipe your Card"
        self.cardCode = ""
        self.canvas.itemconfigure(self.status_item, state=HIDDEN)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.attributes("-fullscreen", False)
        return "break"

    @staticmethod
    def createQRCode(qr_token):
        qrCode = pyqrcode.create(qr_token, error='L')
        qrCode.png(Window.dir_path + '/img/code.png', scale=6, module_color=(0, 0, 0, 128),
                   background=(0xff, 0xff, 0xff))
