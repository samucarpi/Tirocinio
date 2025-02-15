from launcher.launcher import Launcher
from analyst.main import main as aMain

def main(debug):
    l=Launcher(debug)
    l.initialization()
    l.launch()
    aMain(l.getLauncherParameters(),debug)
