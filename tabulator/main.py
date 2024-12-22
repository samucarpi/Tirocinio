
from tabulator.tabulator import Tabulator

def main(debug):
    t = Tabulator(debug)
    t.initialize()
    t.writeFile()