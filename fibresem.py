# External
import sys
import logging

# Internal
import fibresem as fs


def main():
    """FIBRESEM"""

    # Setup logging
    LOG_MSGFORMAT = "[%(asctime)s] %(message)s"
    LOG_TIMEFORMAT = "%H:%M:%S"
    logging.basicConfig(
        format=LOG_MSGFORMAT, datefmt=LOG_TIMEFORMAT, level=logging.DEBUG
    )

    # Config
    config = fs.Config()
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

    fs.init(config=config, script=script)


if __name__ == "__main__":
    # Run main loop
    main()
