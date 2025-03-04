##CRS Tools v 1.6.2
A variety of tools to manage a Chemical Reactions System (CRS).
To run the scripts contained in this suite, the following software has to be be installed:
    Python 3.11 interpreter, or newer
    pipenv
A virtual environment needs to be created and activated in the folder containing this readme, running the commands:
    pipenv sync
    pipenv shell
The source code must be hosted in a dedicated directory in the file system, since the tools work with paths that are relative
to this same directory, called "base".
In the base directory a folder named "ConfigFiles" must be present; the config_example.ini must be copied in it and renamed
"config.ini". The config file example reported here contains many comments explaining how to customize the tools.
All the scripts can be accessed launching the "main" Driver.py


# ChemToAutocat
Software to find Reflexively Autocatalytic and Food-generated sets of reactions (RAFs)
or Constructively Autocatalytic and Food-generated sets of reactions (CAFs)
in Chemical Reaction Systems (CRSs) represented in complete chemistry files as indicated in the file "chimica_spiegazione.txt"
The CRSs must be located in the input directory specififed in the configs, which has to be present in the base project directory.
The resulting CRSs, if present, are exported in the output directory specified in the configs.

The script ChemToAutocat.py has to be run from terminal using the main:
    ./Driver.py [-v] cta
The program generates a text file representation of a RAF or CAF, if present in the CRS.
The type of autocatalytic system searched (RAF or CAF) has to be specified in the config.ini


# AutocatGenerator
Software to generate a number of autocatalytic sets starting from a specific foods and containers set,
after the addition of a randomly generated set of chemical species (at this point the system will be called "inert CRS"),
followed by the addition of a set of reactions (at this point the system will be called "intermediate CRS").
It is possible to eliminate the randomness involed in the inert CRS creation by specificying "all"
as number of species in the configs, this way all possible species are added to the starting set.
Instead, different strategies are applyable to determine the set of reactions of the intermediate CRS;
at the moment, only a random approach is available: the reaction type (cleavage or condensation) is chosen randomly
(but the chance can be tuned with the cleave percentage config parameter), the reagents involved are chosen randomly, while
the products depend on this choice, finally the catalyst is only one per reaction and it is chosen randomly.
The CRSs generated are exported in the output directory specified in the configs, together with the creation logs reporting details.
There are two possible criteria to decide the set of reactions of the intermediate CRS:
1. incremental, in which the CRS is checked regularly, every N reactions added, for autocatalytic set presence,
    and the first set is returned;
2. goal-oriented, in which the CRS if checked only when a certain number of reactions have been added to the CRS.
The set of foods and containers must be specified as a simple list of species names in a text file,
in which every line represents a single entry;
the species names need to contain only characters listed in the alphabet config parameter;
the file location has to be specified in the configuration file.
The set of generated autocatalytic systems is produced in the output folder specififed in the configs:
specifically a creation log detailing all the systems accompanies the chemistry file representing the intermediate CRS,
and a folder starting with the prefix "AutoCatSets" contains all the autocatalytic systems produced.

The script AutocatGenerator.py has to be run from terminal using the main:
    ./Driver.py [-v] ag


# AutocatGenSelector
Software to select autocatalytic sets prodcued by the generator script according to specific criteria,
which can be tuned in the configs.
At the moment, the sets can be selected based on a range of numbers of reactions in the final CRS
and are ordered in the logs by growing number of reactions and growing catalyzer consumed/total catalyzers ratio.
The software expects a series of creations logs in the input folder specififed in the configs
and produces a correspondant series of selection log listing the selected CRSs in the output folder;
the selections logs names contain the timestamp of the correspondant creation logs.

The script AutocatGenSelector.py has to be run from terminal using the main:
    ./Driver.py [-v] ags


# DrawGraph
Software that obtains CRSs from full chemistry files and then, for each of them, draws a graph representing the entire CRS
and a graph limited to the catalyses network.
The CRSs must be located in the input directory specififed in the configs, which has to be present in the base project directory.

The script DrawGraph.py has to be run from terminal using the main:
    ./Driver.py [-v] dg
The program draws the graph of the underlying CRSs on screen.
The image can then be saved through the image viewer software for future references.