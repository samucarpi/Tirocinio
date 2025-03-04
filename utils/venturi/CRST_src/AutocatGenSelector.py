import Environment as Env

from Chemistry.Exporters.Log import Log
from ServicesBuilder import ServicesBuilder

from ast import literal_eval
from csv import DictReader
from glob import glob
from logging import getLogger

import os
import traceback


def AutocatGenSelector(builder:ServicesBuilder) -> bool:
    """
    Function to select autocatalytic sets produced by the Autocatalytic Set Generator, according to specific criteria.

    It expects a series of creations logs in the input folder specififed in the configs
    and produces a correspondant series of selection logs listing the selected CRSs in the output folder;
    the selections logs names contain the timestamp of the correspondant creation logs.
    
    :return: True if the function executes without errors, False otherwise
    """


    LOGGER = getLogger(__name__)
    
    log_txt_search_path = os.path.join(builder.input_path, f"{Env.AG_LOG_PREFIX}*.{Env.FMT_TXT}")
    log_csv_search_path = os.path.join(builder.input_path, f"{Env.AG_LOG_PREFIX}*.{Env.FMT_CSV}")
    grabbed_files = glob(log_txt_search_path) + glob(log_csv_search_path)
    
    for log_filename in sorted(grabbed_files):
        # separate the filename from the extension
        filepath, file_extension = os.path.splitext(log_filename)
        filename = os.path.basename(filepath)
        mark = filename.replace(Env.AG_LOG_PREFIX+"Log", "")
        file_type = file_extension.replace(".", "")
        selection_logs:Log = Log()
        errMsg = f"Failed to load logs from file {log_filename}: "
        try:
            with open(log_filename, "r") as file:
                LOGGER.info(f"File {log_filename} opened")
                if file_type == Env.FMT_TXT:
                    file_lines = file.readlines()
                elif file_type == Env.FMT_CSV:
                    file_lines = DictReader(file)
                subset_counter = 0
                for line in file_lines:
                    # convert a line, associated to a CRS, into a dictionary
                    if file_type == Env.FMT_TXT:
                        line = line.strip()
                        if line == "":
                            continue
                        entry = literal_eval(line)
                    elif file_type == Env.FMT_CSV:
                        entry = line
                    id_raf, id_caf = (entry.get(f"{Env.ACS_RAF} ID", None), entry.get(f"{Env.ACS_CAF} ID", None))
                    id = id_raf if id_raf else id_caf
                    if not id:
                        continue
                    n_react = int(entry.get("N total reactions", 0))
                    if builder.n_react_range[0] <= n_react <= builder.n_react_range[1]:
                        # clean the entry from unwanted info and add it to the new logs
                        entry.pop("RAFs", None)
                        entry.pop("CAFs", None)
                        entry.pop("Iterations", None)
                        selection_logs.add_entry(entry)
                        subset_counter += 1
        except OSError:
            LOGGER.exception(errMsg+f"couldn't open file")
            return False
        except ValueError:
            LOGGER.error(errMsg)
            return False
        
        # sort function to be applied to the logs, it sorts according to total reactions and catalyzers consumed/total ratio
        sort_funct = lambda x: (int(x["N total reactions"]), float(x["Cat consumed/total ratio"]))
        selection_logs.get_data().sort(key=sort_funct)
        try:
            log_writer = builder.logger_class(selection_logs, builder.output_path)
            print(f"{subset_counter} autocatalytic sets selected from logfile {log_filename}")
            print(log_writer.export(prefix="Selection"+mark))
        except (IOError, OSError, FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
            traceback.print_exc()
            return False

    return True
