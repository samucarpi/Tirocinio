from Chemistry.Exporters.TxtExporter import TxtExporter
from Chemistry.Generators.FromFullChemFileGenerator import FromFullChemFileGenerator
from ServicesBuilder import ServicesBuilder

from glob import glob

import os.path
import sys
import traceback


def ChemToAutocat(builder:ServicesBuilder) -> bool:
    """
    Function to obtain an autocatalytic and food-generated set of reactions (RAF/CAF) from a full chemistry detailed in a file
    written with the specifics detailed in "chimica_spiegazione.txt".

    A series of full chemistry files is expected to be in the input folder,
    a correspondant series of files representing RAFs/CAFs (if present) is produced in the output folder.
    
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
            continue
        print("CRS loaded successfully")
        print(curr_CRS.to_string(verbose=builder.verbose), file=builder.verbose_output_file)

        # calculate the maximal RAF/CAF
        print(f"Calculating maximal {builder.ACS_class.get_type()}", file=builder.verbose_output_file)
        try:
            autocat_set = builder.ACS_class(curr_CRS)
        except ValueError as err:
            print(err.args[0])
            continue

        # restrict the CRS to the reactions of the maximal RAF/CAF
        redux = autocat_set.get_shrinked_CRS()

        # print results
        title = builder.ACS_class.get_description()
        print(title+"\n"+redux.to_string(verbose=builder.verbose), file=builder.verbose_output_file)

        # export the CRS to txt
        try:
            writer = TxtExporter(redux, builder.output_path)
            print(writer.export(suffix=builder.ACS_class.get_type()))
        except (IOError, OSError, FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
            traceback.print_exc()
            return False

    return True