import threading
import os
import signal
import json
import time
import logging
import logging.handlers
from AttendanceGUI import Window
from datetime import datetime
from configapi import get_config_info as configs
from dateutil import parser
from dateutil import tz


class App(threading.Thread):
    myToken = ''
    myTitle = ''
    prevState = 'NEW'
    prevToken = 'NEW'
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, tk_root):
        self.logger = logging.getLogger('Main App')
        self.logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.handlers.RotatingFileHandler(
            self.dir_path + '/log/app.log',
            mode='a',
            maxBytes=10 * 1024 * 1024,
            backupCount=3
        )
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(handler)

        self.root = tk_root
        conf = configs()
        self.is_projector = conf.get('projector', False) == 'True'
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        while True:
            current_time = datetime.now(tz=tz.gettz('America/New_York'))
            self.myTitle = 'Date: ' + current_time.strftime('%Y-%m-%d')
            with open(self.dir_path + '/json/session.json') as confApiJson:
                json_dict = json.load(confApiJson)
                isActiveSession = False
                self.myTitle += '\n\n' + json_dict.get('name')
                for session in json_dict['sessions']:
                    notBefore = parser.parse(session.get('notBefore')).astimezone(tz=tz.gettz('America/New_York'))
                    notAfter = parser.parse(session.get('notAfter')).astimezone(tz=tz.gettz('America/New_York'))
                    isActiveSession = (notBefore <= current_time <= notAfter)
                    if isActiveSession:
                        self.logger.info('Active session, current time is ' + current_time.strftime('%Y-%m-%d %H:%M'))
                        self.myToken = session.get('token', '')
                        startTime = session.get('stringStartTime', '')
                        endTime = session.get('stringEndTime', '')
                        self.myTitle += '\n' + session['courses'][0].get('subject') + ' ' + \
                                        session['courses'][0].get('subjectCode') + ': ' + session['courses'][0].get(
                            'className')
                        self.myTitle += '\n' + startTime + ' - ' + endTime
                        instructors = session.get('instructors', False)
                        if instructors:
                            instructor = filter(lambda inst: inst['primary'], instructors).__next__()
                            self.myTitle += '\n\nInstructor: ' + instructor['displayName']
                        break

            if self.prevState == 'NEW':
                self.root.createMyView(self.myToken, self.myTitle, projector_view=self.is_projector)
            elif self.prevToken != self.myToken:
                self.logger.info('Destroying the view, the previous state was ' + self.prevState)
                for widget in self.root.winfo_children():
                    widget.destroy()
                self.root.createMyView(self.myToken, self.myTitle, projector_view=self.is_projector)

            self.prevToken = self.myToken
            self.myToken = ''
            self.myTitle = ''
            if isActiveSession:
                self.prevState = 'ACTIVE'
            else:
                self.prevState = 'INACTIVE'
            self.logger.info('Previous Token: ' + self.prevToken)
            time.sleep(60)

    @staticmethod
    def killme():
        os.kill(os.getpid(), signal.SIGKILL)


if __name__ == "__main__":
    with open(App.dir_path + '/pid.txt', 'w') as pidfile:
        pidfile.write(str(os.getpid()))
    window = Window()
    APP = App(window)
    window.protocol("WM_DELETE_WINDOW", APP.killme)
    window.mainloop()
