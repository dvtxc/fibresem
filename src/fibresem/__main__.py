"""
FIBRESEM
"""

# External
import logging
import click


# Internal
from fibresem.core.config import Config
from fibresem.core.fibresem import Project
from fibresem.helper.clickhelp import PerCommandArgWantSubCmdHelp

# from fibresem.core.fibresem import Image
import fibresem.scripts
import fibresem.addons.renamer

# Constants
LOG_MSGFORMAT = "[%(asctime)s] %(message)s"
LOG_TIMEFORMAT = "%H:%M:%S"

# Suppress logging from PIL (Python Imaging Library)
logging.getLogger("PIL").setLevel(logging.WARNING)


@click.group(chain=True)
@click.option("-v", "--verbose", is_flag=True)
@click.argument("input_path", cls=PerCommandArgWantSubCmdHelp)
@click.pass_context
def cli(context=None, verbose=False, input_path=None):
    """Simple tool to process and manipulate SEM images of fibrous mats

    To get help for a specific command, e.g. 'diam', use:
        fibresem diam --help"""

    # Setup logging
    logging.basicConfig(
        format=LOG_MSGFORMAT, datefmt=LOG_TIMEFORMAT, level=logging.INFO
    )
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    context.obj = {"argument": input_path}


@cli.result_callback()
def process_pipeline(processors, verbose, input_path):
    """Commands pipeline"""

    # Config
    config = Config()
    config.project_path = r""

    # Set verbosity level in config obj (will be passed to MATLAB later on)
    if verbose:
        config.set("general", "verbose", "True")

    # Parse project path
    config.project_path = input_path

    # Start a project
    project = Project(path=config.project_path, config=config)

    # Go through commands
    for i, processor in enumerate(processors):
        logging.info(f"Running command {i + 1} of {len(processors)}")
        project = processor(project)

    logging.info("Process exited.")


@cli.command("add")
@click.pass_context
def add(ctx):
    """."""

    input_path = ctx.obj["argument"]

    def processor(prj):
        """."""
        prj.Path = input_path
        prj.config.project_path = input_path
        if not prj.add_images():
            return

        return prj

    return processor


@cli.command("rename")
@click.pass_context
@click.argument("overview_file")
def auto_rename(ctx, overview_file=""):
    """auto_rename"""

    def processor(prj):
        """Run the auto renamer"""

        logging.info("Running script: auto_rename")

        success = False

        try:
            success = fibresem.addons.renamer.run(
                project=prj, overview_file=overview_file
            )
        except FileNotFoundError as err:
            logging.warning(err)

        if not success:
            logging.warning("No files were renamed!")

        return prj

    return processor


@cli.command("crop")
@click.pass_context
def annotate(ctx):
    """annotate"""

    def processor(project: Project):
        """Crop and annotate all images"""

        num_images = len(project.Images)
        logging.info(f"Running annotate script on {num_images} images.")

        for i, image in enumerate(project.Images):
            image.annotate()

        return project

    return processor


@cli.command("diam")
@click.pass_context
@click.option("--thick-opt/--no-thick-opt", default=False)
def diameter_analysis(ctx, thick_opt):
    """diameter_analysis"""

    def processor(project: Project):
        """Run diameter analysis on all pictures"""

        logging.info("Running script: diameter_analysis")

        if thick_opt:
            project.config.set("general", "optimise_for_thin_fibres", "False")
        else:
            project.config.set("general", "optimise_for_thin_fibres", "True")

        project.run_diameter_analysis()
        project.print_analysis_summary()
        project.export_analysis()
        project.export_mat()

        return project

    return processor


@cli.command("histo")
@click.pass_context
@click.argument("mat_file")
@click.argument("xls_file")
def histogram(ctx, mat_file, xls_file):
    """Combine into histograms"""

    def processor(project: Project):
        """"""


if __name__ == "__main__":
    cli()
