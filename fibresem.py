import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
import logging
import pandas as pd

# import tkinter as tk
# from tkinter import filedialog

from lib import readtif
from lib import fibreanalysis

# from lib.fibreanalysis import Analysis
# from lib.fibreanalysis import Result

analysis_method = "matlab"

# Constants
SEM_BAR_HEIGHT = 0.11
OUTPUT_FOLDER_NAME = "cropped"
KEEP_IN_MEMORY = False


def printtoarr():
    # This function 'burns' the information into the image array

    """
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format='raw', dpi=DPI)
    io_buf.seek(0)
    img_arr = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
                        newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
    io_buf.close()
    """


def getFileListOnPath(path: str, filterExtension="") -> list:
    """Returns list of files in path"""

    fileList = []

    # Get list of all files
    for item in os.listdir(path):
        if os.path.isfile(os.path.join(path, item)):
            if item.endswith(filterExtension):
                fileList.append(os.path.join(path, item))

    return fileList


class Config:
    def __init__(self):
        """Configuration Class"""
        pass


class Project:
    def __init__(self, path=".", config=None):
        self.Path = path
        self.FileList = list()
        self.Images = list()

        if analysis_method == "matlab":
            from lib import MatlabEngineHandler

            self.engine_handler = MatlabEngineHandler.MatlabEngineHandler()

    def addImages(self, extension=".tif"):
        """Get a list of all images on project path and add those images to the project"""

        logging.debug("Adding images.")

        # Set self.FileList
        if not self.getFileList(self.Path, extension):
            logging.warning("No files were found.")
            return None

        for imagefilepath in self.FileList:
            print(f"{imagefilepath}")
            self.Images.append(Image(self, imagefilepath))

    def getFileList(self, path=".", extension=".tif") -> bool:
        """Set self.FileList"""

        # Get list of files
        fileList = getFileListOnPath(path, extension)

        # Did we find files?
        if len(fileList) > 0:
            self.FileList = fileList
            return True

        return False

    def run_diameter_analysis(self, method="matlab"):
        """Runs fibre diameter analysis on every image"""

        number_of_images = len(self.Images)

        for i, image in enumerate(self.Images):
            msg = f"Analyzing {i + 1:02d} of {number_of_images + 1:d}: {image.Filename}"
            logging.info(msg)

            image.run_diameter_analysis(
                method=method, engine_handler=self.engine_handler, load_externally=True
            )

    def print_analysis_summary(self):
        """Get summary of analysis results"""

        for image in self.Images:
            print(f"{image.Filename}: \t", end="")

            if image.Analysis is not None and image.Analysis.result is not None:
                print(image.Analysis.result)
            else:
                # No analysis
                print("")

    def analysis_summary(self):
        """Summarise results in dict"""
        index = [img.Filename for img in self.Images]
        data = {"avgp": [img.Analysis.result.pixel_average for img in self.Images]}
        return (index, data)

    def export_analysis(self):
        index, data = self.analysis_summary()

        df = pd.DataFrame(data, index=index)


class Image:
    def __init__(self, parent, filepath):
        self.Project = parent
        self.Path = filepath
        self.Data = None
        self.Meta = None
        self.Analysis = None

    @property
    def Filename(self) -> str:
        return os.path.split(self.Path)[-1]

    @property
    def Name(self) -> str:
        return "".join(self.Filename.split(".")[0:-1])

    def loadImage(self) -> bool:
        """Load actual image from file"""

        try:
            tifimg, tags = readtif.importtif(self.Path)
        except Exception as err:
            logging.error(f"Could not load {self.Filename}")
            print(err)
            return False

        self.Data = tifimg
        self.Meta = tags

        return True

    def unloadImage(self):
        self.Data = None
        self.Meta = None

    def crop_square(self, copy=False, barheight=SEM_BAR_HEIGHT):
        """Crop to Square and omit the SEM meta bar"""

        newHeight = round(self.Data.shape[0] * (1 - barheight))
        left = round((self.Data.shape[1] - newHeight) / 2)
        right = self.Data.shape[1] - left

        try:
            cropped_image = self.Data[0:newHeight, left:right]
        except Exception as err:
            logging.error(f"Could not crop {self.Filename}")
            print(err)
            return False

        if copy:
            return cropped_image

        self.Data = cropped_image
        return True

    def annotate(self, addscalebar=True, addsamplename=True):
        """
        Add annotations to image:
        - a scalebar in the lower right corner
        - sample name in the lower left corner
        """

        # Is an image loaded?
        if self.Data is None:
            if not self.loadImage():
                return None  # No image loaded

        # Crop image
        if not self.crop_square():
            return None

        img = self.Data

        # Create Matplotlib figure
        f = plt.figure(
            figsize=(img.shape[1] / 300, img.shape[0] / 300)
        )  # figure with correct aspect ratio
        ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
        ax.imshow(img, cmap="gray", vmin=0, vmax=255)
        ax.axis("off")

        # Add annotations
        if addscalebar:
            self.addScalebar(ax)

        if addsamplename:
            self.addSampleName(ax)

        # Save figure
        self.saveFigure(plt)

        # Unload image to save memory
        if not KEEP_IN_MEMORY:
            self.unloadImage()

        return True

    def addScalebar(self, figure_axes):
        if self.Meta["Pixel Size"] == "NaN":
            return None

        # Calculate dynamic border padding and font size, so the annotations are independent from image size
        imgpadding = 0.001 * self.Data.shape[0]
        dynFontSize = round(0.013 * self.Data.shape[0])
        fntScalebar = {"weight": "bold", "size": dynFontSize}
        fntAnnotation = {"weight": "normal", "size": dynFontSize}

        # Create scalebar
        scalebar = ScaleBar(
            self.Meta["Pixel Size Value"],
            self.Meta["Pixel Size Unit"],
            length_fraction=0.25,
            width_fraction=0.022,
            location="lower right",
            color="w",
            box_alpha=0,
            scale_loc="top",
            border_pad=imgpadding,
            font_properties=fntScalebar,
            sep=0.2,
        )

        # Add to figure
        figure_axes.add_artist(scalebar)

    def addSampleName(self, figure_axes):
        dynFontSize = round(0.013 * self.Data.shape[0])

        # Add sample name in lower left corner
        samplenameParts = self.Name.split("_")
        string = " ".join(samplenameParts[0:1])

        figure_axes.text(
            0.05 * self.Data.shape[0],  # x coordinate text
            0.95 * self.Data.shape[0],  # y coordinate text
            string,  # text string
            color=(1, 1, 1),  # color
            size=dynFontSize * 0.7,  # size
        )

    def saveFigure(self, figureplot):
        # Save
        outputFolderName = OUTPUT_FOLDER_NAME
        plt = figureplot

        outputDirectory = os.path.join(self.Project.Path, outputFolderName)
        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)

        outputFile = self.Name + ".png"
        targetPath = os.path.join(outputDirectory, outputFile)
        plt.savefig(targetPath, bbox_inches="tight", pad_inches=0, dpi=300)
        plt.close()

    def run_diameter_analysis(
        self, load_externally=False, method="matlab", engine_handler=None
    ) -> bool:
        """Runs diameter analysis"""

        # Make sure image is loaded
        if self.Data is None:
            if not self.loadImage():
                return False

        # Make sure everything is loaded for the image analysis
        if method == "matlab":
            if engine_handler is None:
                logging.warning("Matlab engine not started.")
                return False

        # Do analysis
        self.Analysis = fibreanalysis.Analysis(
            self,
            engine_handler=engine_handler,
            output_path=os.path.join(self.Project.Path, "output"),
        )
        self.Analysis.start(load_externally=load_externally)

        # Free up memory
        self.unloadImage()

        return True


if __name__ == "__main__":
    """Main file of fibresem"""

    # Setup logging
    LOG_MSGFORMAT = "[%(asctime)s] %(message)s"
    LOG_TIMEFORMAT = "%H:%M:%S"
    logging.basicConfig(
        format=LOG_MSGFORMAT, datefmt=LOG_TIMEFORMAT, level=logging.DEBUG
    )

    baseDir = r"C:\dev\python\sem\fibresem\testfiles\test1"
    fileExt = ".tif"

    project = Project(baseDir)
    project.addImages()

    project.run_diameter_analysis()

    project.print_analysis_summary()

    """for image in project.Images:
        image.loadImage()
        image.Analysis = fibreanalysis.Analysis(
            image,
            engine_handler=project.engine_handler,
            output_path=os.path.join(project.Path, "output"),
        )
        image.Analysis.start()
        image.annotate()
        image.unloadImage()
    """
    outputFolderName = "cropped"
