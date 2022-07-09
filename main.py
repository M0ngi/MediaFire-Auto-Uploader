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

import json
from Bot import MediaFireBot
from exceptions import ConfigFileNotFound
from logger import Logger
from os.path import exists

def loadCreds():
    if not exists('config.json'):
        raise ConfigFileNotFound('Config file config.json not found.')
    
    with open('config.json', 'r') as f:
        return json.load(f)


if __name__ == '__main__':
    creds = loadCreds()
    log = Logger()

    assert 'email' in creds, 'No email found in config.json'
    assert 'password' in creds, 'No password found in config.json'

    bot = MediaFireBot(creds['email'], creds['password'], logger=log)
    bot.login()
    bot.uploadFile('testupload')


