from mutator.mutator import Mutator

def main(debug, seed):
    m=Mutator(debug,seed)
    m.initialization()
    m.mutate()
    m.writeOutputFiles()