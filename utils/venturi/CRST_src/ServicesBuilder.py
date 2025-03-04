import Environment as Env

from Chemistry.Entities.CAF import CAF
from Chemistry.Entities.Chemostat import Chemostat
from Chemistry.Entities.Protocell import Protocell
from Chemistry.Entities.RAF import RAF
from Chemistry.Exporters.CsvExporter import CsvExporter
from Chemistry.Exporters.TxtExporter import TxtExporter
from Chemistry.Transformers.AddRandomReactionStrategy import AddRandomReactionStrategy
from Chemistry.Transformers.CAFifier import CAFifier
from Chemistry.Transformers.RAFifier import RAFifier
from Chemistry.Validators.BaseIntegrityValidator import BaseIntegrityValidator
from Chemistry.Validators.NullIntegrityValidator import NullIntegrityValidator
from Chemistry.Validators.FormulaIntegrityValidator import FormulaIntegrityValidator

from logging import getLogger

import configparser
import os.path
import re
import sys


class ServicesBuilder():
    """
    The builder of the services of the suite
    """

    LOGGER = getLogger(__name__)


    def __init__(self, subprogram:str, verbose:bool, config_file_rel_path:str=""):
        """
        Initializer

        :param subprogram: the subprogram called 
        :return None:
        :raise ValueError: if the configuration file contains invalid input
        """

        def_config_file_path = os.path.join(Env.BASE_DIR, Env.CONFIG_FILE_FOLDER, Env.CONFIG_FILE_NAME)
        if config_file_rel_path == "":
            config_file_path = def_config_file_path
        else:
            config_file_path = config_file_rel_path
        
        self.config = configparser.ConfigParser()
        # read the config file, the function "read" also takes care of closing the file
        config_content_list = self.config.read(config_file_path)
        self.LOGGER.info(f"Config file path: {config_file_path}")
        if len(config_content_list) == 0:
            self.config.read(def_config_file_path)
            self.LOGGER.info(f"Config file was not read correctly, new config file path: {def_config_file_path}")
        
        ## input and output paths
        self.input_path = os.path.join(Env.BASE_DIR, self.config["DEFAULT"]["input_path"])
        """The input path"""
        if not os.path.exists(self.input_path):
            raise ValueError(f"Folder {self.input_path} not present")
        self.LOGGER.info(f"Input path: {self.input_path}")
        
        self.output_path = os.path.join(Env.BASE_DIR, self.config["DEFAULT"]["output_path"])
        """The output path"""
        if not os.path.exists(self.output_path):
            raise ValueError(f"Folder {self.output_path} not present")
        self.LOGGER.info(f"Output path: {self.output_path}")
        
        if self.input_path == self.output_path:
            raise ValueError("The input and output folders are the same")
        
        # set an attribute representing the verboseness of the prints
        self.verbose = True if verbose else False
        # also set the redirection to stdout or dev/null depending on output verboseness
        self.verbose_output_file = sys.stdout if verbose else open(os.devnull, 'w')
        self.LOGGER.info(f"Verbose: {self.verbose}")

        self.integrity_checker = None
        """The CRS integrity checker class"""
        integrity_check_stg = self.config["DEFAULT"]["intchk_strategy"]
        if integrity_check_stg not in Env.STG_INTCHK_TYPES:
            integrity_check_stg = Env.DEF_INTCHK_STG
        if integrity_check_stg == Env.STG_INTCHK_BASE:
            self.integrity_checker = BaseIntegrityValidator()
        elif integrity_check_stg == Env.STG_INTCHK_NONE:
            self.integrity_checker = NullIntegrityValidator()
        elif integrity_check_stg == Env.STG_INTCHK_FORM:
            self.integrity_checker = FormulaIntegrityValidator()
        self.LOGGER.info(f"Integrity checker: {self.integrity_checker.__class__.__name__}")


        try:
            match subprogram:
                case "cta":
                    self._init_CTA()
                case "ag":
                    self._init_AG()
                case "ags":
                    self._init_AGS()
        except:
            raise


    def _init_CTA(self):
        """Init Chemistry To Autocatalytic set (CTA) services and resources"""

        self._init_ACS_class()


    def _init_AG(self):
        """Init ACS Generation (AG) services and resources"""

        self._init_logger()
        
        self.CF_file = os.path.join(Env.BASE_DIR, self.config["AG"]["CF_file_path"])
        """(AG) The containers-foods file path"""
        if not os.path.exists(self.CF_file):
            raise ValueError(f"Folder {self.CF_file} not present")
        self.LOGGER.info(f"Containers-foods file path: {self.CF_file}")

        # check the alphabet
        alphabet_regex = Env.TOKENS.get(Env.CT_SP)
        self.alphabet = self.config["AG"]["alphabet"]
        if not re.match(pattern=alphabet_regex,string=self.alphabet):
            raise ValueError(f"Alphabet {self.alphabet} not compatible with {alphabet_regex}")
        self.LOGGER.info(f"Alphabet: {self.alphabet}")
        

        # ACS and transformer classes
        self._init_ACS_class()

        self.food_cat = True
        try:
            self.food_cat = self.config.getboolean("AG", "food_cat")
            """(AG) Wheter food is a valid catalyzer for reactions added"""
        except:
            self.LOGGER.exception()

        self.transformer_class = None
        """(AG) The transformer class"""
        if self.ACS_class == RAF:
            self.transformer_class = RAFifier
        elif self.ACS_class == CAF:
            self.transformer_class = CAFifier
            # in case of CAF creation, food need to be selectable as catalyzer
            self.food_cat = True
        self.LOGGER.info(f"Transformer class: {self.transformer_class.__name__}")
        self.LOGGER.info(f"Food catalyzer: {self.food_cat}")

        # CRS type
        CRS_type_string = self.config["AG"]["CRS_type"]
        if CRS_type_string not in Env.CRS_TYPES:
            self.LOGGER.warning(f"The CRS class requested {CRS_type_string} is not valid, defaulting to {Env.DEF_CRS_TYPE}")
            CRS_type_string = Env.DEF_CRS_TYPE
        self.CRS_class = Protocell if CRS_type_string == Env.CRS_PTC else Chemostat
        self.LOGGER.info(f"CRS class: {self.CRS_class.__name__}")
        """(AG) The CRS class requested"""

        # ACS generation parameters
        try:
            self.number_subsets=int(self.config["AG"]["n_ACS"])
            """(AG) The number of AutoCatalytic Sets requested"""
            self.max_name_length=int(self.config["AG"]["max_sp_name_len"])
            """(AG) The maximum length of chemical species names"""
            n_species_string = self.config["AG"]["n_species"]
            if n_species_string == "all":
                n_species_string = 0
            self.number_species=int(n_species_string)
            """(AG) The number of species requested in the intermediate CRS"""
            self.reactions_goal=int(self.config["AG"]["n_react"])
            """(AG) The number of reactions requested for the intermediate CRS"""
            self.cleave_perc=int(self.config["AG"]["cleave_perc"])
            """(AG) The requested percentage of cleavages on total reactions"""
            self.cond_perc=int(self.config["AG"]["cond_perc"])
            """(AG) The requested percentage of condensations on total reactions"""
            self.exch_perc=int(self.config["AG"]["exch_perc"])
            """(AG) The requested percentage of exchanges on total reactions"""
            cat_range = [int(self.config["AG"]["n_cat_min"]), int(self.config["AG"]["n_cat_max"])]
        except:
            # just pass the exception to the driver
            raise

        if not 0 < self.number_subsets <= Env.MAX_NSUBSETS:
            self.LOGGER.warning(
                f"The number of subsets requested {self.number_subsets} is not valid, defaulting to {Env.DEF_NSUBSETS}")
            self.number_subsets = Env.DEF_NSUBSETS
        self.LOGGER.info(f"Number of subsets: {self.number_subsets}")
        
        if not Env.MIN_SP_NLEN <= self.max_name_length <= Env.MAX_SP_NLEN:
            self.LOGGER.warning(
                f"Maximum species name length requested {self.max_name_length} not valid, defaulting to {Env.DEF_SP_NLEN}")
            self.max_name_length = Env.DEF_SP_NLEN
        self.LOGGER.info(f"Maximum species name length: {self.max_name_length}")
        self.LOGGER.info(f"Number of species: {self.number_species}")

        if self.reactions_goal < 0:
            self.LOGGER.warning(
                f"Reactions goal of {self.reactions_goal} not valid, stopping adding reactions at the first autocat set found")
            self.reactions_goal = 0
        self.LOGGER.info(f"Reactions goal: {self.reactions_goal}")

        self.reactions_weights = dict(zip(Env.R_TYPES, [0 for _ in Env.R_TYPES]))
        r_types_percentages = {
            Env.R_CLEAVE: (self.cleave_perc, Env.DEF_CLEAVE_PERC),
            Env.R_COND: (self.cond_perc, Env.DEF_COND_PERC),
            Env.R_EXCH: (self.exch_perc, Env.DEF_EXCH_PERC)
        }
        reset_perc = True if sum(x[0] for x in r_types_percentages.values()) != 100 else False
        for r_type in r_types_percentages:
            perc, def_perc = r_types_percentages.get(r_type)
            if not 0 <= perc <= 100 or reset_perc:
                self.LOGGER.warning(
                    f"{r_type} percentage of {perc} not valid, "
                    f"defaulting to {def_perc} per cent {r_type}s")
                perc = def_perc
            if perc == 0:
                del self.reactions_weights[r_type]
            else:
                self.reactions_weights[r_type] = perc/100
        self.LOGGER.info(f"Reactions weights: {list(self.reactions_weights.items())}")

        if cat_range[0] > cat_range[1]:
            cat_range = list(reversed(cat_range))
        if not 0 < cat_range[0]:
            self.LOGGER.warning(
                f"The range of numbers of catalyzers requested {cat_range} is not valid,"
                f" defaulting to [{Env.DEF_NCAT_MIN}, {Env.DEF_NCAT_MAX}]")
            cat_range[0] = Env.DEF_NCAT_MIN
            cat_range[1] = Env.DEF_NCAT_MAX
        self.cat_range = cat_range
        """(AG) The range for the number of catalyzers to be present in created reactions"""
        self.LOGGER.info(f"Number of catalyzers range: {self.cat_range}")

        self.strategy = None
        """(AG) The object representing the strategy to add reactions"""
        strategy_string = self.config["AG"]["addr_strategy"]
        if not strategy_string in Env.STG_ADDR_TYPES:
            self.LOGGER.warning(f"The strategy requested {strategy_string} is not valid, defaulting to {Env.DEF_ADDR_STG}")
            strategy_string = Env.DEF_ADDR_STG
        if strategy_string == Env.STG_ADDR_RND:
            self.strategy = AddRandomReactionStrategy(
                alphabet=self.alphabet,
                reactions_weights = self.reactions_weights,
                cat_range = self.cat_range,
                no_food_cat=not self.food_cat
            )
        self.LOGGER.info(f"Add reaction strategy: {self.strategy.__class__.__name__}")


    
    def _init_AGS(self):
        """Init ACS Generated Selection (AGS) services"""
        
        self._init_logger()

        try:
            r_range = [int(self.config["AGS"]["n_react_min"]), int(self.config["AGS"]["n_react_max"])]
        except:
            raise
        if r_range[0] > r_range[1]:
            r_range = list(reversed(r_range))
        if not Env.DEF_SEL_N_REACT_MIN <= r_range[0] and r_range[1] <= Env.DEF_SEL_N_REACT_MAX:
            self.LOGGER.warning(
                f"The range of numbers of reactions requested {r_range} is not valid,"
                f" defaulting to [{Env.DEF_SEL_N_REACT_MIN}, {Env.DEF_SEL_N_REACT_MAX}]")
            r_range[0] = Env.DEF_SEL_N_REACT_MIN
            r_range[1] = Env.DEF_SEL_N_REACT_MAX
        self.n_react_range = r_range
        """(AGS) The range for the number of reactions that must be present in the selected ACSs"""
        self.LOGGER.info(f"Number of reactions range: {self.n_react_range}")
    

    def _init_logger(self):
        """Init the logger class"""

        self.logger_class = None
        """(AG-AGS) The logger class"""
        export_format = self.config["DEFAULT"]["log_export_fmt"]
        if export_format not in Env.LOG_FMTS:
            export_format = Env.DEF_LOG_FMT
        if export_format == Env.FMT_CSV:
            self.logger_class = CsvExporter
        elif export_format == Env.FMT_TXT:
            self.logger_class = TxtExporter
        self.LOGGER.info(f"Logger class: {self.logger_class.__name__}")


    def _init_ACS_class(self):
        """Init the autocatalytic set class requested"""

        # ACS type and transformer
        ACS_type = self.config["DEFAULT"]["ACS_type"]
        if ACS_type not in Env.ACS_TYPES:
            ACS_type = Env.DEF_ACS_TYPE
        self.ACS_class = RAF if ACS_type == Env.ACS_RAF else CAF
        """The autocatalytic set class requested"""
        self.LOGGER.info(f"Autocatalytic set class: {self.ACS_class.__name__}")