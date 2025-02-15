from launcher.launcher import Launcher, Loader
from analyst.main import main as aMain

def main(debug):
    l=Launcher(debug)
    l.initialization()
    loader = Loader()
    l.launch(loader)
    if not debug:
        loader.stop()
    aMain(l.getLauncherParameters(),debug)
