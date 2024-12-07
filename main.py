
from generator.generator import Generator
import time

def main():
    start = time.time()
    g=Generator()
    g.initialization()
    g.reaction()
    g.output()
    tempo = time.time() - start
    print("TEMPO DI ESECUZIONE: "+str(tempo))

if __name__=="__main__":
    main()