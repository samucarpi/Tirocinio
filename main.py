import argparse
from Generator.main import main as generator_main
from Tabulator.main import main as tabulator_main

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
        generator_main()
    if "tabulate" in args.commands:
        tabulator_main()

if __name__ == "__main__":
    main()