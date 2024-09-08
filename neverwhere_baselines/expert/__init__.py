from pathlib import Path
from ml_logger.job import RUN, instr
from termcolor import colored

assert instr  # single-entry for the instrumentation thunk factory
RUN.project = "neverwhere"  # Specify the project name
RUN.job_name += "/{job_counter}"

# WARNING: do NOT change these prefixes.
RUN.prefix = "{project}/icra_experiments/ziyu_debug/expert/{job_name}"
RUN.script_root = Path(__file__).parent  # specify that this is the script root.

print(colored("set", "blue"), colored("RUN.script_root", "yellow"), colored("to", "blue"), RUN.script_root)