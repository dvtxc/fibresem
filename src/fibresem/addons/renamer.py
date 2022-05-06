"""Renaming files"""

import logging
import os
from distutils.util import strtobool
import pandas as pd

from fibresem.core.fibresem import Project, Image


def read_overview_table(
    fpath: str,
) -> pd.DataFrame:  # python 3.10: (pd.DataFrame|None):
    """Read overview table (txt file)"""

    if not fpath:
        # Empty path
        return None

    fpath = os.path.abspath(fpath)

    try:
        overview_frame = pd.read_table(fpath, on_bad_lines="warn")
    except FileNotFoundError:
        print("Could not find {fpath}")
        return None
    except Exception as err:
        print("Could not load overview file.")
        print(err)
        return None

    # Check if overview file contains at least 'img' column
    if "img" not in overview_frame.columns:
        logging.warning("Image column 'img' not provided.")
        return None

    # Check if image number in overview file is integer
    if overview_frame.dtypes.img.kind != "i":  # pylint: disable=no-member
        logging.warning("Image column ('img') contains non-integer values.")
        return None

    return overview_frame


def format_new_name(props: dict) -> str:
    """Converts the properties (props) into a formatted string"""

    new_name = []

    # Sample name
    if "sample" in props:
        new_name.append(str(props["sample"]))

    # Image Width
    if "width" in props:
        new_name.append(f"{props['width']:04d}u")

    # Dish
    for key in ["d", "dish", "s", "stub"]:
        if key in props:
            new_name.append("s" + str(props[key]))

    # Position on dish
    for key in ["l", "loc", "p", "pos", "punch"]:
        if key in props:
            new_name.append("p" + str(props[key]))

    # Image number
    if "img" in props:
        new_name.append(f"img{props['img']:02d}")

    # Remarks
    if "remarks" in props:
        if props["remarks"] and props["remarks"] != "-":
            new_name.append(str(props["remarks"]))

    return "_".join(new_name)


def rename_project_files(project: Project, overview: pd.DataFrame, **kwargs) -> bool:
    """Rename all files in a project"""

    # Check length
    if len(project) != len(overview):
        logging.warning(
            "Overview file does not have the same number of lines as the number of images."
        )
        return False

    # Go through every image in project
    for i, image in enumerate(project.Images):
        # Construct new name
        props = overview.iloc[i].to_dict()

        try:
            new_name = format_new_name(props)
        except TypeError as err:
            logging.warning("Could not parse name")
            print(f"Did not parse: {image.Filename}, reason: {err}")
            new_name = image.Filename

        # Rename
        rename(image, new_name, **kwargs)

    return True


def rename(image: Image, new_name: str, dry_run: False) -> bool:
    """Rename single file"""

    current_image_path = os.path.normpath(image.Path)

    image_directory = os.path.dirname(current_image_path)
    image_file_ext = image.file_extension
    new_image_path = os.path.join(image_directory, new_name + image_file_ext)

    if dry_run:
        print(f"{image.Filename} ---> {new_name + image_file_ext}")
        return True

    # Do actual renaming
    try:
        os.rename(current_image_path, new_image_path)
    except OSError as err:
        logging.warning(err)
        return False
    else:
        # Renaming successfull, update file path in project
        image.Path = new_image_path

    return True


def find_overview_file(
    project: Project, overview_path=""
) -> str:  # python 3.10 syntax: str | None:
    """Tries to find the overview file"""

    project_root = project.Path

    # Search for default 'overview.txt' in project root
    if not overview_path:
        logging.debug(
            "No overview path specified. Looking for overview.txt in project root"
        )
        overview_abs_path = os.path.join(project_root, "overview.txt")
        if os.path.isfile(overview_abs_path):
            return os.path.join(project_root, "overview.txt")

    # Search for file name in project root
    if not os.path.isabs(overview_path):
        logging.debug("Looking for overview file in project root")
        overview_abs_path = os.path.join(project_root, overview_path)
        if os.path.isfile(overview_abs_path):
            return overview_abs_path

    # Search for absolute file path
    if os.path.isabs(overview_path):
        logging.debug("Absolute path for overview file provided.")
        if os.path.isfile(overview_path):
            return overview_path

    # Nothing found
    return None


def user_yes_no_query(question):
    """Simple yes/no query"""

    print(f"{question} [y/n]")
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            print("Please respond with 'y' or 'n'.")


def run(project: Project, overview_file=""):
    """Run the auto-renamer"""

    # Find overview file
    overview_abs_path = find_overview_file(project, overview_file)
    if overview_abs_path is None:
        raise FileNotFoundError("Could not find overview text file")

    # Read and interpret overview file
    overview = read_overview_table(overview_abs_path)
    logging.info("Overview table loaded")
    print(overview)

    # Perform dry run
    logging.info("Performing dry run")
    if not rename_project_files(project, overview, dry_run=True):
        logging.warning("Renaming exitted with an error.")
        return False

    if not user_yes_no_query("Proceed renaming? This action cannot be undone!"):
        return False

    # Perform actual renaming
    if not rename_project_files(project, overview, dry_run=False):
        logging.warning("Renaming exitted with an error.")
        return False

    return True


if __name__ == "__main__":
    pass
