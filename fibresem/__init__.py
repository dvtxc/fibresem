from fibresem.core.fibresem import Project
from fibresem.core.fibresem import Image
from fibresem.config import Config
import fibresem.scripts


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
