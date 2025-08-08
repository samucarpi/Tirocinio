import argparse
from termcolor import colored
from generator.main import main as gMainC
from kauffmanGenerator.main import main as gMainK
from tabulator.main import main as tMain
from launcher.main import main as lMain
from mutator.main import main as mMain
from evolver.main import main as eMain

def main():
    parser = argparse.ArgumentParser(description="Esegui il generatore e/o il tabulatore.")
    parser.add_argument(
        "commands",
        nargs="*",
        choices=["generate", "tabulate", "launch", "mutate","evolve"],
        help="Specifica i comandi da eseguire: 'generate', 'tabulate', o entrambi."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Esegui in modalità debug"
    )
    parser.add_argument(
        "-k", "--kauffman",
        action="store_true",
        help="Esegui il generatore di Kauffman"
    )
    parser.add_argument(
        "-c", "--catalysts",
        action="store_true",
        help="Esegui il generatore con regole di catalisi"
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        help="Numero per fissare il seed di randomizzazione"
    )
    args = parser.parse_args()
    debug = args.debug
    seed = args.seed
    if "generate" in args.commands:
        if args.kauffman:
            gMainK(debug)
        elif args.catalysts:
            gMainC(debug)
        else:
            gMainC(debug)
    if "tabulate" in args.commands:
        tMain(debug)
        if not debug:
            print(colored("TABULAZIONE TERMINATA CON SUCCESSO", "green", attrs=["bold"]))
    if "launch" in args.commands:
        if args.kauffman:
            lMain(debug, True)
        elif args.catalysts:
            lMain(debug, False)
        else:
            lMain(debug, False)
        if not debug:
            print(colored("LANCI TERMINATI CON SUCCESSO", "green", attrs=["bold"]))
    if "mutate" in args.commands:
        mMain(debug, seed)
        if not debug:
            print(colored("MUTAZIONE TERMINATA CON SUCCESSO", "green", attrs=["bold"]))
    if "evolve" in args.commands:
        eMain(debug)
        if not debug:
            print(colored("EVOLUZIONE TERMINATA CON SUCCESSO", "green", attrs=["bold"]))
    if not args.commands:
        parser.print_help()

if __name__ == "__main__":
    main()