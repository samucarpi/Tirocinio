import argparse
from termcolor import colored
from generator.main import main as gMain
from tabulator.main import main as tMain
from launcher.main import main as lMain

def main():
    parser = argparse.ArgumentParser(description="Esegui il generatore e/o il tabulatore.")
    parser.add_argument(
        "commands",
        nargs="*",
        choices=["generate", "tabulate", "launch"],
        help="Specifica i comandi da eseguire: 'generate', 'tabulate', o entrambi."
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Esegui in modalità debug"
    )
    args = parser.parse_args()
    debug = args.debug
    if "generate" in args.commands:
        gMain(debug)
        print(colored("GENERAZIONE TERMINATA CON SUCCESSO", "green", attrs=["bold"]))
    if "tabulate" in args.commands:
        tMain(debug)
        print(colored("TABULAZIONE TERMINATA CON SUCCESSO", "green", attrs=["bold"]))
    if "launch" in args.commands:
        lMain(debug)
        print(colored("LANCI TERMINATI CON SUCCESSO", "green", attrs=["bold"]))
    if not args.commands:
        parser.print_help()

if __name__ == "__main__":
    main()