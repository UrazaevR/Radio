import os, datetime

def log(s: str) -> None:
    if not os.path.exists('logging.txt'):
        mode = 'w'
    else: mode = 'a'
    with open('logging.txt', mode) as file:
        file.write(f'{datetime.datetime.now()} - {s}\n')