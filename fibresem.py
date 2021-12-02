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

    # Parse project path
    project_path = r"C:\dev\python\sem\fibresem\testfiles\test1"
    idx = 0

    try:
        idx = sys.argv.index("-dir")
    except ValueError:
        logging.warning("No path provided, using current working folder.")
    else:
        if len(sys.argv) > idx:
            project_path = sys.argv[idx + 1]

    # Parse flags
    if "-crop" in sys.argv:
        pass

    fs.init(path=project_path)


if __name__ == "__main__":
    # Run main loop
    main()
