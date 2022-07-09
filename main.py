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


