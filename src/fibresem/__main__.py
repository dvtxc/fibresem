"""
FIBRESEM
"""


# External
import sys
import logging

# Internal
from fibresem.core.config import Config
from fibresem.core.fibresem import Project
#from fibresem.core.fibresem import Image
import fibresem.scripts

# Constants
LOG_MSGFORMAT = "[%(asctime)s] %(message)s"
LOG_TIMEFORMAT = "%H:%M:%S"


def init(config=Config(), script=""):
    """Initiate"""

    project = Project(config.project_path)

    project.addImages()

    tasks = script.split(" ")

    for task in tasks:
        if task == "crop":
            fibresem.scripts.annotate(project, config)
        elif task == "diam":
            fibresem.scripts.diameter_analysis(project, config)


def main():
    """FIBRESEM"""

    # Setup logging
    logging.basicConfig(
        format=LOG_MSGFORMAT, datefmt=LOG_TIMEFORMAT, level=logging.DEBUG
    )

    # Config
    config = Config()
    config.project_path = r"C:\Dev\python\sem\fibresem\testfiles\originals"

    # Parse project path
    idx = 0

    try:
        idx = sys.argv.index("-dir")
    except ValueError:
        logging.warning("No path provided, using current working folder.")
    else:
        if len(sys.argv) > idx:
            config.project_path = sys.argv[idx + 1]

    # Parse flags
    script = ""

    if "-crop" in sys.argv:
        script += "crop "

    if "-diam" in sys.argv:
        script += "diam "

    init(config=config, script=script)

if __name__ == "__main__":
    # Run main loop
    main()
    