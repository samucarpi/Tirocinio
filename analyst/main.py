from analyst.analyst import Analyst

def main(parameters,debug,kauffman):
    a=Analyst(parameters,debug,kauffman)
    rows=a.getData()
    a.writeFile(rows)