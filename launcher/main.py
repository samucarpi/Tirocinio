from launcher.launcher import Launcher
from analyst.main import main as aMain

def main(debug, kauffman):
    l=Launcher(debug, kauffman)
    l.initialization()
    l.launch()
    aMain(l.getLauncherParameters(),debug,kauffman)
