from mutator.mutator import Mutator

def main(debug):
    m=Mutator(debug)
    m.initialization()
    m.mutate()
    m.writeOutputFiles()