"""
    Copyright (C) 2022  Mohamed Mongi Saidane
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    Author contact: saidanemongi@gmail.com
"""

import requests, json
from bs4 import BeautifulSoup
from exceptions import BadLogin, FileNotFoundException, UnableToGetActionToken, UploadFileException
from logger import Logger
from utils import SHA256sum
from os import path


class MediaFireBot:
    def __init__(self, email: str, password: str, logger : Logger = None, debug : bool = False) -> None:
        self.email = email
        self.password = password
        self.session = requests.session()
        self.logger = logger
        self.USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'

        if debug:
            # BurpSuite Proxy
            self.session.proxies = {
                'http': 'http://127.0.0.1:8080',
                'https': 'http://127.0.0.1:8080',
            }
    

    def login(self):
        resp = self.session.get(
            "https://www.mediafire.com/login",
            headers={
                'User-Agent': self.USER_AGENT
            }
        )
        soup = BeautifulSoup(resp.content, 'html.parser')
        form = soup.find(id='widgetCaptchaForm')
        security = form.find('input', {'type': 'hidden', 'name': 'security'})

        assert security is not None, "Couldn't retrieve security token."
        self.security = security.get('value')

        self.logAction('Security Token:', self.security, caller='login')

        resp = self.session.post(
            'https://www.mediafire.com/dynamic/client_login/mediafire.php',
            {
                'security': self.security,
                'login_email': self.email,
                'login_pass': self.password,
                'login_remember': 'true'
            },
            headers={
                'Referer': 'https://www.mediafire.com/login/',
                'Origin': 'https://www.mediafire.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': self.USER_AGENT
            }
        )
        
        resp_json = json.loads(resp.content)
        self.logAction('Login Response:', resp_json, caller='login')

        if resp_json['action'] == 10:
            raise BadLogin("Invalid login creds")
        
        if resp_json['action'] == 15:
            self.session_cookie = resp.cookies.get('session')
            self.logAction('Session Cookie:', self.session_cookie, caller='login')
            return
    

    def uploadFile(self, file_path : str):
        if not path.exists(file_path):
            raise FileNotFoundException("Unable to find file: " + file_path)
        
        self.session_token = self.getSessionToken()
        self.logAction('Session token:', self.session_token, caller='uploadFile')

        self.action_token = self.getActionToken()
        self.logAction('Action token:', self.action_token, caller='uploadFile')

        with open(file_path, 'rb') as f:
            resp = self.session.post(
                'https://ul.mediafireuserupload.com/api/upload/resumable.php?folder_key=myfiles&response_format=json&session_token='+self.action_token,
                headers={
                    'User-Agent': self.USER_AGENT,
                    'Content-Type': 'application/octet-stream',
                    'X-Filename': path.split(file_path)[1],
                    'X-Filetype': '',
                    'X-Unit-Hash': SHA256sum(file_path),
                    'X-Filesize': str(path.getsize(file_path)),
                    'X-Unit-Size': str(path.getsize(file_path)),
                    'X-Unit-Id': '0'
                },
                data=f.read()
            )
            resp_json = resp.content
            self.logAction('Upload file json response:', resp_json, caller='uploadFile')

            if resp_json['response']['result'] == 'Success':
                return True
            
            raise UploadFileException("Unable to upload file, check logs.")


    def getSessionToken(self) -> str:
        resp = self.session.post('https://www.mediafire.com/application/get_session_token.php')
        resp_json = json.loads(resp.content)
        self.logAction('Session Token Response:', resp_json, caller='getSessionToken')
        return resp_json['response']['session_token']


    def getActionToken(self) -> str:
        BODY = [
            '------WebKitFormBoundary2cKWpQ6aR72sPqIW',
            'Content-Disposition: form-data; name="type"',
            '',
            'upload',
            '------WebKitFormBoundary2cKWpQ6aR72sPqIW',
            'Content-Disposition: form-data; name="lifespan"',
            '',
            '1440',
            '------WebKitFormBoundary2cKWpQ6aR72sPqIW',
            'Content-Disposition: form-data; name="response_format"',
            '',
            'json',
            '------WebKitFormBoundary2cKWpQ6aR72sPqIW',
            'Content-Disposition: form-data; name="session_token"',
            '',
            self.session_token,
            '------WebKitFormBoundary2cKWpQ6aR72sPqIW--',
            ''
        ]
        BODY = '\n'.join(BODY)

        resp = self.session.post(
            'http://www.mediafire.com/api/1.5/user/get_action_token.php',
            data=BODY,
            headers={
                'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary2cKWpQ6aR72sPqIW',
                'User-Agent': self.USER_AGENT
            },
        )
        resp_json = json.loads(resp.content)
        self.logAction('Action Token Response:', resp_json, caller='getActionToken')
        if resp_json['response']['result'] == 'Error':
            raise UnableToGetActionToken("Couldn't get action token, check logs.")

        return resp_json['response']['action_token']


    def logAction(self, *args, **argd):
        if self.logger:
            if 'caller' in argd:
                caller = argd['caller']
            else:
                caller = 'UNKNOWN'
            
            self.logger("[{0}] {1}".format(caller, ' '.join([str(x) for x in args])))
