"""Cleans all files from a board"""
import os

def clean_dir(d):
    files = os.listdir(d)
    for file in files:
        fullpath = '{}/{}'.format(d, file) if d else file
        try:
            print('unlinking {}'.format(fullpath))
            os.unlink(fullpath)
        except OSError as err:
            if err.args == (39,):
                clean_dir(fullpath)
                print('rmdir {}'.format(fullpath))
                os.rmdir(fullpath)

if __name__ == '__main__':
    clean_dir('')
