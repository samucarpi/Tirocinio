from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
"""The base directory hosting the CRS tools"""

CONFIG_FILE_FOLDER = "ConfigFiles"
"""The folder, starting from the base directory, containing the configuration file"""
CONFIG_FILE_NAME = "config.ini"
"""The name of the default configuration file"""

MAX_WTIME = int(30)
"""Maximum wait time in seconds, used in performance checks"""

CRS_CSTR = "Chemostat"
"""Name of CRS type CSTR"""
CRS_PTC = "Protocell"
"""Name of CRS type 'protocell'"""
CRS_TYPES = {CRS_CSTR, CRS_PTC}
"""
CRS types
"""
DEF_CRS_TYPE = CRS_PTC
"""Default CRS type"""

ACS_RAF = "RAF"
"""Name of autocatalytic set type RAF"""
ACS_CAF = "CAF"
"""Name of autocatalytic set type CAF"""
ACS_TYPES = {ACS_RAF, ACS_CAF}
"""
Atutocatalytic sets (ACS) types
"""
DEF_ACS_TYPE = ACS_RAF
"""Default ACS type"""

STG_INTCHK_NONE = "none"
"""Strategy to disable CRS integrity checks"""
STG_INTCHK_BASE = "base"
"""Normal strategy for CRS integrity checks"""
STG_INTCHK_FORM = "formula"
"""Strict strategy for CRS integrity checks"""
STG_INTCHK_TYPES = {STG_INTCHK_NONE, STG_INTCHK_BASE, STG_INTCHK_FORM}
"""Strategies available to add reactions to the inert CRS"""
DEF_INTCHK_STG = STG_INTCHK_BASE

R_CLEAVE = "Cleavage"
"""
Cleavage reaction
    with general formula: reag + cat -> reag_left_part + reag_right_part + cat
"""
R_COND = "Condensation"
"""
Condensation reaction
    with general formula: reagA + reagB + cat -> reagAreagB + cat
"""
R_EXCH = "Exchange"
"""
Exchange reaction
    with general formula: reagA + reagB + cat -> prodA + prodB + cat
    where the couple (reagA, reagB) and the couple (prodA, prodB) elements can be divided in parts such that all these parts
    can be found in both couples (e.g. AB|BA + B|ABA + cat -> AB|B + BA|ABA + cat)
"""
R_TYPES = {R_CLEAVE, R_COND, R_EXCH}
"""
Reaction types
"""

EI_IN = "Injection"
EI_OUT = "Depletion"
EI_OSM = "Osmosis"
EI_TYPES = {EI_IN, EI_OUT, EI_OSM}
"""
External interaction types
"""

CRS_NCONT = int(1)
"""Number of container species in the CRS"""


"""
Chemistry file parsing specifications
"""
CT_ADD = "ChemTokADD"
"""Token representing addition of a reagent in a chemical reaction"""
CT_DIR = "ChemTokDIR"
"""Token representing the direction of the reaction, which divides reagents from products, or the direction of the interaction"""
CT_HIATUS = "ChemTokHIATUS"
"""Token representing the separator between a reaction or interaction and its constant"""
CT_SP = "ChemTokSpeciesName"
"""Token representing a generic chemical species name"""
CT_NUMB = "ChemTokSciNotNumber"
"""Token representing a number in scientific notation"""

TOKENS = {
    CT_ADD:"+",
    CT_DIR:">",
    CT_HIATUS:";",
    CT_SP:r"[*A-Za-z]+$",
    CT_NUMB:r"-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?"
}
"""
Chemistry tokens definitions
"""

PR_S_DEF = "SpeciesDef"
"""Chemical species definition: chemical_species_name quantity alpha_coefficient"""
PR_REACT = "ReactionDef"
"""Reaction definition: reag1 + reag2 +... + reagN > prod1 + prod2 + ... + prodN ; const"""
PR_EI = "ExtInteractionDef"
"""
External interaction definitions:

    Depletion: chemical_species_name > ; const
    Injection: > chemical_species_name ; injection_rate
    Osmosis: ext_conc > chemical_species_name ; const
"""
PR_SCFS_DEF = "SimpleContFoodSpeciesDef"
"""
Simple container-food species definition: chemical_species_name
"""
PARSERPRODUCTIONS = {PR_S_DEF, PR_REACT, PR_EI, PR_SCFS_DEF}
"""
Parser productions
"""


"""
Random Autocatalytic set (ACS) generation specifications
"""
DEF_NSUBSETS = int(1)
"""Default number of subsets generated"""
MAX_NSUBSETS = int(10000)
"""Maximum number of subsets generated"""
MAX_SP_NLEN = int(8)
"""Maximum species name length"""
MIN_SP_NLEN = int(4)
"""Minimum species name length"""
DEF_SP_NLEN = int(6)
"""Default species name length"""
MAX_N_SPECIES = int(10000)
"""Maximum number of species for the intermediate CRS"""
MIN_N_SPECIES = int(10)
"""Minimum number of species for the intermediate CRS"""
DEF_SP_QNT = float(1.e-15)
"""Default generic species initial quantity (for a species that is not food or container)"""
DEF_C_QNT = float(1.35e-16)
"""Default container initial quantity"""
DEF_F_QNT = float(1.e-16)
"""Default food initial quantity"""
DEF_PTC_SP_ALPHA = float(0.05)
"""Default protocell generic species alpha coefficient (for a species that is not food or container)"""
DEF_CSTR_SP_ALPHA = float(0)
"""Default chemostat generic species alpha coefficient (for a species that is not food or container)"""
DEF_CF_ALPHA = float(0)
"""Default container and food species alpha coefficient"""
DEF_REACT_K = float(0.02)
"""Default reaction kinetic constant"""
DEF_OSM_K = float(1.e-18)
"""Default osmosis diffusion rate"""
DEF_OSM_ECONC = float(10)
"""Default osmosis external concentration"""
DEF_IN_K = float(1.e-18)
"""Default injection rate"""
DEF_OUT_K = float(0.05)
"""Default depletion rate"""
STG_ADDR_RND = "random"
"""Strategy to add random reactions"""
STG_ADDR_TYPES = {STG_ADDR_RND}
"""Strategies available to add reactions to the inert CRS"""
DEF_ADDR_STG = STG_ADDR_RND
"""Default add reaction strategy"""
DEF_CLEAVE_PERC = int(50)
"""
Default percentage of cleavages on total reactions

The value must be between 0 and 100, where 0 means all reactions should be cleavages
"""
DEF_COND_PERC = int(50)
"""Default percentage of condendations on total reactions"""
DEF_EXCH_PERC = int(0)
"""Default percentage of exchanges on total reactions"""
DEF_NCAT_MIN = int(1)
"""Default minimum number of catalyzers per reaction"""
DEF_NCAT_MAX = int(1)
"""Default maximum number of catalyzers per reaction"""

FMT_CSV = "csv"
"""CSV format extension"""
FMT_TXT = "txt"
"""Text format extension"""
LOG_FMTS = {FMT_CSV, FMT_TXT}
"""Log formats"""
DEF_LOG_FMT = FMT_CSV

AG_SUBFOLDER_PREFIX = "AutoCatSets"
"""The subfolder prefix in the output path where generated autocatalytic systems are placed"""
AG_LOG_PREFIX = "Creation"
"""The prefix to be used to save the creation log file"""

"""
CRS selection specifications
"""
DEF_SEL_N_REACT_MIN = 2
DEF_SEL_N_REACT_MAX = 20