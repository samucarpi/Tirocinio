import argparse
from generator.main import main as gMain
from tabulator.main import main as tMain

def main():
    parser = argparse.ArgumentParser(description="Esegui il generatore e/o il tabulatore.")
    parser.add_argument(
        "commands",
        nargs="+",
        choices=["generate", "tabulate", "debug"],
        help="Specifica i comandi da eseguire: 'generate', 'tabulate', o entrambi. Se si vuole eseguire il codice in modalità debug, aggiungere 'debug'."
    )
    args = parser.parse_args()
    if "debug" in args.commands:
        debug=True
    else:
        debug=False
    if "generate" in args.commands:
        gMain(debug)
        print("\n-----------------------------------\nGENERAZIONE TERMINATA CON SUCCESSO\n-----------------------------------\n")
    if "tabulate" in args.commands:
        tMain(debug)
        print("\n-----------------------------------\nTABULAZIONE TERMINATA CON SUCCESSO\n-----------------------------------\n")
        

if __name__ == "__main__":
    main()