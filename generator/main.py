from generator.generator import Generator

def main(debug):
    g=Generator(debug)
    g.initialization()
    g.reaction()
    g.output()