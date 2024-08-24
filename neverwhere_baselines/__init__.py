from ml_logger import logger
from ml_logger.job import RUN, instr

RUN.prefix = "/lucidsim/neverwhere/nv_baselines/{file_stem}/{job_name}"
# does not make sense, should remove. - Ge
RUN.job_name = "corl_analysis"
RUN.job_counter = False

assert logger, "for export"

if __name__ == "__main__":
    fn = instr(lambda: None, __diff=False)
    print(logger.prefix)
    print(logger.get_dash_url())
