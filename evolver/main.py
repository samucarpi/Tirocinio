
from evolver.evolver import Evolver

def main(debug):
    e = Evolver(debug)
    e.initialize()
    e.evolve()