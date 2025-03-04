from Chemistry.Analyzers.CatNetwork import CatNetwork
from Chemistry.Analyzers.CompleteNetwork import CompleteNetwork
from Chemistry.Analyzers.GraphDrawer import GraphDrawer
from Chemistry.Generators.FromFullChemFileGenerator import FromFullChemFileGenerator
from ServicesBuilder import ServicesBuilder

from glob import glob

import os.path
import sys
import traceback


def DrawGraph(builder:ServicesBuilder) -> bool:
    """
    Function to create a Chemical Reaction System (CRS) from a full chemistry and draw two types of grahs:
    the first represents the entire reaction system, the second only the catalyses network

    :return: True if the function executes without errors, False otherwise
    """
    
    # get all the chemistry files in the input path
    search_path = os.path.join(builder.input_path, "*.txt")
    grabbed_files = glob(search_path)
    for file in grabbed_files:
        # load the CRS from a chemistry file
        try:
            generator = FromFullChemFileGenerator(builder.integrity_checker, file)
        except FileExistsError:
            traceback.print_exc()
            return False
        print(f"Loading CRS from file {file}")
        curr_CRS = generator.create()
        if curr_CRS == None:
            print("Input data not coherent, CRS load failed", file=sys.stderr)
            return False
        print("CRS loaded successfully")
        print(curr_CRS.to_string(verbose=builder.verbose), file=builder.verbose_output_file)

        print("Drawing complete network")
        network = CompleteNetwork(curr_CRS)
        print(list(network.reaction_keys_dict.items()),  file=builder.verbose_output_file)
        drawer = GraphDrawer(network.G)
        drawer.draw()
        print("Drawing catalyses network")
        network = CatNetwork(curr_CRS, show_r_formulas=True)
        drawer = GraphDrawer(network.G)
        drawer.draw()

    return True