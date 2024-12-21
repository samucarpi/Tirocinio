import argparse
from generator.main import main as gMain
from tabulator.main import main as tMain

def main():
    parser = argparse.ArgumentParser(description="Esegui il generatore e/o il tabulatore.")
    parser.add_argument(
        "commands",
        nargs="+",
        choices=["generate", "tabulate"],
        help="Specifica i comandi da eseguire: 'generate', 'tabulate', o entrambi."
    )
    args = parser.parse_args()
    if "generate" in args.commands:
        gMain()
    if "tabulate" in args.commands:
        tMain()

if __name__ == "__main__":
    main()