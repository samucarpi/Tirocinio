from analyst.analyst import Analyst

def main(parameters,debug):
    a=Analyst(parameters,debug)
    rows=a.getData()
    a.writeFile(rows)