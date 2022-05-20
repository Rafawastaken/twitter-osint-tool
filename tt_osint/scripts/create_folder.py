from email.mime import base
import os

def create_folder(username, BASEDIR):
    try:
        if not os.path.exists(f'{BASEDIR}\data\{username}'):
            os.mkdir(f'{BASEDIR}\data\{username}')
        if not os.path.exists(f'{BASEDIR}\data\{username}\media'):
            os.mkdir(f'{BASEDIR}\data\{username}\media')
        return True
    except:
        return False