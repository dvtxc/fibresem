from fibresem.core.fibresem import Project
from fibresem.core.fibresem import Image


def init(path="."):
    """Initiate"""

    project = Project(path)

    project.addImages()

    project.run_diameter_analysis()

    project.print_analysis_summary()

    project.export_analysis()
