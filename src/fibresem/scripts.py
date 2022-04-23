import logging

from fibresem.core.fibresem import Project
from fibresem.core.fibresem import Image
from fibresem.core.config import Config
import fibresem.addons.renamer

def annotate(project: Project, config=Config()):
    """Crop and annotate all images"""

    num_images = len(project.Images)
    logging.info(f"Running annotate script on {num_images} images.")

    for i, image in enumerate(project.Images):
        image.annotate()


def diameter_analysis(project: Project, config=Config()):
    """Run diameter analysis on all pictures"""

    logging.info("Running script: diameter_analysis")

    project.run_diameter_analysis()
    project.print_analysis_summary()
    project.export_analysis()
    project.export_mat()

def auto_rename(project: Project, config=Config(), overview_file=""):
    """Run the auto renamer"""

    logging.info("Running script: auto_rename")

    fibresem.addons.renamer.run(project=project, overview_file=overview_file)
