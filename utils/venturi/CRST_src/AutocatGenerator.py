import Environment as Env

from Chemistry.Analyzers.CatNetwork import CatNetwork 
from Chemistry.Exporters.Log import Log
from Chemistry.Exporters.TxtExporter import TxtExporter
from Chemistry.Generators.FromContFoodFileGenerator import FromContFoodFileGenerator
from Chemistry.Transformers.Censor import Censor
from ServicesBuilder import ServicesBuilder

from logging import getLogger

import os
import sys
import traceback


def AutocatGenerator(builder:ServicesBuilder) -> bool:
    """
    Function to generate a number of autocatalytic sets starting from a specific foods and containers set, after the addition
    of a randomly generated set of chemical species (at this point the system will be called "inert CRS"),
    followed by the addition of a randomly generated set of reactions (at this point the system will be called "intermediate CRS").
    It is possible to eliminate the randomness involed in the inert CRS creation by specificying "all"
    as number of species in the configs, this way all possible species are added to the starting set.
    Instead, different strategies are applyable to determine the set of reactions of the intermediate CRS;
    at the moment, only a random approach is available: the reaction type (cleavage or condensation) is chosen randomly
    (but the chance can be tuned with the cleave percentage config parameter), the reagents involved are chosen randomly, while
    the products depend on this choice, finally the catalyst is only one per reaction and it is chosen randomly.
    There are two possible criteria to decide the set of random reactions of the intermediate CRS:
    1. incremental, in which the CRS is checked regularly, every N reactions added, for RAF presence, and the first RAF is returned;
    2. goal-oriented, in which the CRS if checked only when a certain number of reactions have been added to the CRS.
    The set of foods and containers must be specified as a simple list of species names in a text file,
    the species names need to contain only characters listed in the alphabet config parameter;
    the file location has to be specified in the configuration file.
    The set of generated autocatalytic systems is produced in the output folder specififed in the configs:
    specifically a creation log detailing all the systems accompanies the chemistry file representing the intermediate CRS,
    and a folder starting with the prefix "AutoCatSets" contains all the autocatalytic systems produced.

    :return: True if the function executes without errors, False otherwise
    """

    MAX_NATTEMPS = 100*Env.MAX_NSUBSETS
    LOGGER = getLogger(__name__)


    try:
        generator = FromContFoodFileGenerator(builder.integrity_checker, builder.CF_file, builder.CRS_class)
    except FileExistsError:
        traceback.print_exc()
        return False
    # generate the inert CRS that will be the base of the autocat sets generation
    inert_CRS = generator.create()
    if inert_CRS == None:
        print("Input data not coherent, inert CRS generation failed", file=sys.stderr)
        return False
    # and expand it to the needed number of chemical species
    transformer = Censor(inert_CRS, builder.alphabet, builder.max_name_length)
    transformer.set_target_species_number(builder.number_species)
    inert_CRS = transformer.transform()
    print("\nInert CRS created successfully\n"+inert_CRS.to_string(), file=builder.verbose_output_file)
    try:
        writer = TxtExporter(inert_CRS, builder.output_path)
        print(writer.export(prefix="Inert"))
    except (IOError, OSError, FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
        traceback.print_exc()
        return False
    
    set_type = builder.ACS_class.get_type()
    transformer_class = builder.transformer_class
    strategy = builder.strategy

    # generate autocatalytic sets
    creation_logs = Log()
    requested_n_subsets = builder.number_subsets
    subset_counter = 0
    iteration = 0
    output_sub_folder = os.path.join(builder.output_path, Env.AG_SUBFOLDER_PREFIX+TxtExporter.get_timestamp())

    while (subset_counter < requested_n_subsets):
        iteration += 1
        strategy.reset()
        transformer = transformer_class(inert_CRS, strategy, reactions_goal=builder.reactions_goal)
        new_CRS = transformer.transform(ofile=builder.verbose_output_file, logger=LOGGER)
        if new_CRS == None:
            print(f"No {set_type} found at iteration {iteration}")
            continue
        subset_counter += 1
        new_subset = transformer.getSubset()
        shrinked_CRS = new_subset.get_shrinked_CRS()
        all_species = shrinked_CRS.get_all_species_names()
        cat_net = CatNetwork(shrinked_CRS)
        creation_logs.add_entry({
            f"{set_type} ID":subset_counter,
            "N species":len(all_species),
            "Max name length":max([len(name) for name in all_species]),
            "N total reactions":shrinked_CRS.get_reaction_count(),
            "N cleavages":shrinked_CRS.get_reaction_count(Env.R_CLEAVE),
            "N condensations":shrinked_CRS.get_reaction_count(Env.R_COND),
            "N catalyzers": len(cat_net.catalysts_list),
            "N auto-catalyzers": len(cat_net.get_autocat_species()),
            "N catalyzers consumed": len(cat_net.get_consumed_species()),
            "Cat consumed/total ratio": '%.2f' % (len(cat_net.get_consumed_species())/len(cat_net.catalysts_list)),
            "N reactions catalyzed distribution": "->",
            **cat_net.get_reactions_catalyzed_distribution()
        })
        print(f"{set_type} found at iteration {iteration}")
        print(shrinked_CRS.to_string(verbose=True), file=builder.verbose_output_file)
        # export the CRS to txt
        try:
            writer = TxtExporter(shrinked_CRS, output_sub_folder, create_folder=True)
            print(writer.export(suffix=f"n{subset_counter}"))
        except (IOError, OSError, FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
            traceback.print_exc()
            return False
        if iteration >= MAX_NATTEMPS:
            print(f"Reached maximum number of attempts {MAX_NATTEMPS}")
            break
    
    creation_logs.add_head_entry({
        f"{set_type}s": subset_counter,
        "Iterations": iteration})
    try:
        log_writer = builder.logger_class(creation_logs, builder.output_path)
        print(log_writer.export(prefix=Env.AG_LOG_PREFIX))
    except (IOError, OSError, FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
        traceback.print_exc()
        return False
    print(f"{subset_counter} {set_type}s generated and exported in {iteration} iterations")

    return True
