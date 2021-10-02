import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar

# import tkinter as tk
# from tkinter import filedialog

from lib import readtif

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


class Project:
    def __init__(self, path="."):
        self.Path = path
        self.FileList = list()
        self.Images = list()

    def addImages(self, extension=".tif"):
        """Get a list of all images on project path and add those images to the project"""

        # Set self.FileList
        if not self.getFileList(self.Path, extension):
            # logging.warning("No files were found.")
            return None

        for imagefilepath in self.FileList:
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


class Image:
    def __init__(self, parent, filepath):
        self.Project = parent
        self.Path = filepath
        self.Data = None
        self.Meta = None

    @property
    def Filename(self) -> str:
        return os.path.split(self.Path)[-1]

    @property
    def Name(self) -> str:
        return "".join(self.Filename.split(".")[0:-1])

    def loadImage(self) -> bool:
        """Load the tif image and store as np.ndarray"""

        # Read tif file
        try:
            tifimg, tags = readtif.importtif(self.Path)
            self.Data = tifimg
            self.Meta = tags
        except:
            return False

        # Crop to square
        self.crop_square()

        # Return success
        return True

    def unloadImage(self):
        self.Data = None
        self.Meta = None

    def crop_square(self, barheight=SEM_BAR_HEIGHT):
        """Crop to Square and omit the SEM meta bar"""

        newHeight = round(self.Data.shape[0] * (1 - barheight))
        left = round((self.Data.shape[1] - newHeight) / 2)
        right = self.Data.shape[1] - left

        self.Data = self.Data[0:newHeight, left:right]

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


if __name__ == "__main__":
    # MAIN()

    baseDir = r"C:\dev\python\sem\fibresem\testfiles\test1"
    fileExt = ".tif"

    project = Project(baseDir)
    project.addImages()

    for image in project.Images:
        print(image.Name)
        image.annotate()


"""
def save_cropped(pathin, pathout):
    tifimg, tags = readtif.importtif(pathin)

    img = crop_square(tifimg)

    save_img(img, pathout)


def save_img(imgarray, pathout):
    f = plt.figure(
        figsize=(imgarray.shape[1] / 300, imgarray.shape[0] / 300)
    )  # figure with correct aspect ratio
    ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
    ax.imshow(tifimg, cmap="gray", vmin=0, vmax=255)
    ax.axis("off")

    plt.savefig(pathout, bbox_inches="tight", pad_inches=0, dpi=300)
    print("Output written")


def read(pathin):
    tifimg, tags = readtif.importtif(pathin)
    return (tifimg, tags)
"""
