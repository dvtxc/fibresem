import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar


# import tkinter as tk
# from tkinter import filedialog

from lib import readtif
from lib import fibreanalysis

# from lib.fibreanalysis import Analysis
# from lib.fibreanalysis import Result

analysis_method = "matlab"

# cropping
def crop_square(tifimg):
    # Crop to Square and omit the SEM meta bar

    barheight = 0.11
    newHeight = round(tifimg.shape[0] * (1 - barheight))
    left = round((tifimg.shape[1] - newHeight) / 2)
    right = tifimg.shape[1] - left

    tifimg = tifimg[0:newHeight, left:right]

    return tifimg


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


def getPixelSize(tags):
    pass


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

        if analysis_method == "matlab":
            from lib.matlabenginehandler import MatlabEngineHandler

            self.EngineHandler = MatlabEngineHandler()

    def addImages(self, extension=".tif"):
        # Set self.FileList
        if not self.getFileList(self.Path, extension):
            # logging.warning("No files were found.")
            return None

        for imagefilepath in self.FileList:
            self.Images.append(Image(self, imagefilepath))

    def getFileList(self, path=".", extension=".tif") -> bool:
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
        self.Analysis = None

    @property
    def Filename(self) -> str:
        return os.path.split(self.Path)[-1]

    def loadImage(self):
        tifimg, tags = readtif.importtif(self.Path)
        tifimg = crop_square(tifimg)
        self.Data = tifimg
        self.Meta = tags

    def unloadImage(self):
        self.Data = None
        self.Meta = None

    def annotate(self):

        if self.Data is None:
            return None  # No image loaded

        tifimg = self.Data

        # Create Matplotlib figure
        f = plt.figure(
            figsize=(tifimg.shape[1] / 300, tifimg.shape[0] / 300)
        )  # figure with correct aspect ratio
        ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
        ax.imshow(tifimg, cmap="gray", vmin=0, vmax=255)
        ax.axis("off")

        self.addScalebar(ax)
        self.addSampleName(ax)

        # Save
        outputFolderName = "cropped"
        outputPath = os.path.join(self.Project.Path, outputFolderName)
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)

        targetName = os.path.join(outputPath, self.Filename.replace(".tif", ".png"))
        plt.savefig(targetName, bbox_inches="tight", pad_inches=0, dpi=300)
        print("Output written")
        plt.close()

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
        filenameparts = self.Filename.split("_")
        string = filenameparts[0]  # + "_" + filenameparts[2]
        figure_axes.text(
            0.05 * self.Data.shape[0],  # x coordinate text
            0.95 * self.Data.shape[0],  # y coordinate text
            string,  # text string
            color=(1, 1, 1),  # color
            size=dynFontSize * 0.7,  # size
        )


if __name__ == "__main__":
    # MAIN()

    baseDir = r"I:\Projekte\Projekte\121250_PolyKARD\5-Data\01_Electrospinning\SEM\SEM 2021.11.16_FTS"
    baseDir = r"C:\Dev\python\sem\fibresem\testfiles\originals"
    fileExt = ".tif"

    project = Project(baseDir)
    project.addImages()

    for image in project.Images:
        image.loadImage()
        image.Analysis = fibreanalysis.Analysis(
            image, engineHandler=project.EngineHandler
        )
        image.Analysis.start()
        image.annotate()
        image.unloadImage()

    outputFolderName = "cropped"
