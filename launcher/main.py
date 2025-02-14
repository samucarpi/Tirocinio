from launcher.launcher import Launcher
from analyst.main import main as aMain
from utils.loader import Loader

def main(debug):
    l=Launcher(debug)
    l.initialization()
    loader = Loader()
    l.launch(loader)
    if not debug:
        loader.stop()
    aMain(l.getLauncherParameters(),debug)
