import sys,time,threading
from termcolor import colored

class Loader:
    def __init__(self):
        self.stopLoad=True
        self.thread=None

    def start(self,string):
        interval=0.5
        def load():
            points = 0
            while not self.stopLoad:
                str=f"{string} {'.'*points}{' '*(3 - points)}"
                out=colored(f"\r{str}", color="yellow", attrs=["bold"])
                sys.stdout.write(out)
                sys.stdout.flush()
                time.sleep(interval)
                points=(points+1)%4
        self.stopLoad=False
        self.thread=threading.Thread(target=load, daemon=True)
        self.thread.start()

    def stop(self):
        self.stopLoad=True
        if self.thread is not None:
            self.thread.join()
            sys.stdout.write('\r\033[K')