from fibresem.core.fibresem import Project
from fibresem.core.fibresem import Image
from fibresem.core.config import Config


def annotate(project, config=Config()):
    for image in project.Images:
        image.annotate()


def diameter_analysis(project, config=Config()):

    project.run_diameter_analysis()

    project.print_analysis_summary()

    project.export_analysis()
