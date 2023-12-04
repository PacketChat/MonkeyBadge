"""Cleans all files from a board"""
import os

def clean_flags(d):
    files = os.listdir(d)
    for file in files:
        if file.startswith('ho') and len(file) == 3 and file[2].isdigit():
            print(f'removing flag identifier file: {file}')
            os.unlink(file)

if __name__ == '__main__':
    clean_flags('')
