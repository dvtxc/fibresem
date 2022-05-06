# External imports

import os
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fibresem.core.config import Config

# Internal imports
from fibresem.matplotlib_scalebar.scalebar import ScaleBar
from fibresem.io import readtif
from fibresem.analysis import fibreanalysis, analysis_engines

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


def get_file_list_on_path(path: str, filterExtension="") -> list:
    """Returns list of files in path"""

    fileList = []

    # Get absolute path
    path = os.path.abspath(path)

    # Get list of all files
    try:
        for item in os.listdir(path):
            if os.path.isfile(os.path.join(path, item)):
                if item.endswith(filterExtension):
                    fileList.append(os.path.join(path, item))
    except OSError as e:
        logging.warning("File path not found.")
        print(e)

    return fileList


class Project:
    """Project(path, config)
    
    This class contains the images of the project
    
    Attributes:
    path
    file_list
    images
    config
    engine_handler
    """

    def __init__(self, path=".", config=Config()):
        self.Path = path
        self.FileList = list()
        self.Images = list()

        self.config = config

        self.engine_handler = None


    def __len__(self):
        """Override len(), return number of images."""

        return len(self.Images)

    def append_matlabengine(self) -> bool:
        """Starts and appends matlab engine"""
        #import fibresem.analysis.matlabenginehandler as matlabengine

        self.engine_handler = analysis_engines.MatlabEngine()
        return self.engine_handler.is_running

    def add_images(self, extension=".tif") -> bool:
        """Get a list of all images on project path and add those images to the project"""

        logging.debug("Adding images.")

        print(f"- Input Path: {self.Path}")

        # Set self.FileList
        if not self.getFileList(self.Path, extension):
            logging.warning("No files were found on path.")
            return False

        for imagefilepath in self.FileList:
            img = Image(self, imagefilepath)
            self.Images.append(img)

            print(f"-- {img.Filename}")

        return True

    def getFileList(self, path=".", extension=".tif") -> bool:
        """Set self.FileList"""

        # Get list of files
        fileList = get_file_list_on_path(path, extension)

        # Did we find files?
        if len(fileList) > 0:
            self.FileList = fileList
            return True

        return False

    def run_diameter_analysis(self, method="matlab", verbose=False):
        """Runs fibre diameter analysis on every image"""

        number_of_images = len(self.Images)

        # Check if engine handler is set up
        if self.engine_handler is None:
            logging.warning("Engine Handler not defined.")

            # Append engine and start engine (if necessary)
            if not self.append_matlabengine():
                logging.warning("Engine Handler could not be appended to project. Aborting Diameter Analysis")
                return

        logging.info("Starting diameter analysis.")
        logging.info(
            "Diameter analysis parameter 'optimise_for_thin_fibres' = %s", self.config.get('general', 'optimise_for_thin_fibres')
        )

        # Run diameter analysis on every image
        for i, image in enumerate(self.Images):
            msg = f"Analyzing {i + 1:02d} of {number_of_images + 1:d}: {image.Filename}"
            logging.info(msg)

            image.run_diameter_analysis(
                method=method,
                engine_handler=self.engine_handler,
                load_externally=True,
                config=self.config,
                verbose=verbose
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
        variables = ["pixel_size_value","pixel_size_unit","pixel_average","pixel_sdev","average","sdev","unit"]

        index = [img.Filename for img in self.Images]

        # Initialise dict
        data = {"sample_name": []}
        for var in variables:
            data[var] = []

        # Fill dict
        for img in self.Images:
            data["sample_name"].append(img.sample_name)

            # Create empty result dataclass as fallback
            result = fibreanalysis.Result()

            # Retrieve result
            if img.Analysis is not None:
                if img.Analysis.result is not None:
                    result = img.Analysis.result

            for var in variables:
                data[var].append(getattr(result, var))

        return (index, data)

    def export_mat(self):
        """Quick function to export to MATLAB (.mat) file"""

        try:
            import scipy.io as sio  #pylint disable=import-outside-toplevel
        except ModuleNotFoundError:
            logging.error("Scipy module not found.")
            print("Please install scipy: python -m pip install scipy")
            return False

        dtypes = [
            ("sample_name", "S128"),
            ("pixel_size_value", np.double),
            ("pixel_size_unit", "U10"),
            ("pixel_average", np.double),
            ("pixel_sdev", np.double),
            ("average", np.double),
            ("sdev", np.double),
            ("unit", "U10"),
            ("pixel_diameters", "O"),
            ("diameters", "O"),
        ]

        num_images = len(self.Images)

        arr = np.zeros((num_images,), dtype=dtypes)

        for i, image in enumerate(self.Images):

            # If no analysis has been performed, skip
            if image.Analysis is None:
                continue

            # Store analysis data
            arr[i]["sample_name"] = image.sample_name
            arr[i]["pixel_size_value"] = image.Analysis.pixel_size_value
            arr[i]["pixel_average"] = image.Analysis.result.pixel_average
            arr[i]["pixel_sdev"] = image.Analysis.result.pixel_sdev
            arr[i]["average"] = image.Analysis.result.average
            arr[i]["sdev"] = image.Analysis.result.sdev
            arr[i]["pixel_diameters"] = image.Analysis.result.pixel_diameters
            arr[i]["diameters"] = image.Analysis.result.diameters

            # Make sure we can handle µm
            try:
                arr[i]["pixel_size_unit"] = image.Analysis.pixel_size_unit
                arr[i]["unit"] = image.Analysis.result.unit
            except UnicodeEncodeError:
                arr[i]["unit"] = image.Analysis.result.unit.encode("utf-8")
                arr[i]["pixel_size_unit"] = image.Analysis.pixel_size_unit.encode("utf-8")
                
        output_path = os.path.join(self.Path, "export.mat")
        sio.savemat(output_path, {"results": arr})

        logging.info("Saved .mat file")

    def export_analysis(self):
        """Export analysis"""

        index, data = self.analysis_summary()

        df = pd.DataFrame(data, index=index)

        output_path = os.path.join(self.Path, "export.xlsx")

        logging.info(f"Exporting analysis to {output_path}")

        try:
            df.to_excel(output_path, "Fibre Analysis")
        except Exception as err:
            logging.error("Could not export fibre analysis")
            print(err)
            return False
        else:
            logging.info("Successfully exported.")



class Image:
    """Image(parent, filepath)"""

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
        return os.path.splitext(self.Filename)[0]
        # return ".".join(self.Filename.split(".")[0:-1])

    @property
    def file_extension(self) -> str:
        return os.path.splitext(self.Path)[1]

    @property
    def sample_name(self) -> str:
        return self.Name.split("_")[0]

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

        logging.debug("-- Cropping")

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

    def annotate(self, add_scalebar=True, add_sample_name=True):
        """
        Add annotations to image:
        - a scalebar in the lower right corner
        - sample name in the lower left corner
        """

        logging.info(f"Annotating {self.Filename}")

        # Is an image loaded?
        if self.Data is None:
            if not self.loadImage():
                return None  # No image loaded

        # Crop image
        if not self.crop_square():
            return None

        img = self.Data

        # Suppress Matplotlib debug output
        logging.getLogger("matplotlib.font_manager").disabled = True

        # Turn interactive plotting off
        plt.ioff()

        # Create Matplotlib figure
        f = plt.figure(
            figsize=(img.shape[1] / 300, img.shape[0] / 300)
        )  # figure with correct aspect ratio
        ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
        ax.imshow(img, cmap="gray", vmin=0, vmax=255)
        ax.axis("off")

        # Add annotations
        if add_scalebar:
            logging.debug("-- Adding scalebar, pixelsize = {}".format(self.Meta["Pixel Size"]))
            self.add_scalebar(ax)

        if add_sample_name:
            logging.debug("-- Adding sample name")
            self.add_sample_name(ax)

        # Save figure
        self.save_figure(plt)

        # Unload image to save memory
        if not KEEP_IN_MEMORY:
            self.unloadImage()

        return True

    def add_scalebar(self, figure_axes):
        if self.Meta["Pixel Size"] == "NaN":
            logging.warning("Could not read pixel size. Scalebar is not added.")
            return None

        if self.Meta["Pixel Size Unit"] is None:
            logging.warning("Could not read pixel size. Scalebar is not added.")
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

    def add_sample_name(self, figure_axes):
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

    def save_figure(self, figureplot) -> bool:
        """Write figure to file"""

        outputFolderName = OUTPUT_FOLDER_NAME
        plt = figureplot

        outputDirectory = os.path.join(self.Project.Path, outputFolderName)
        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)

        outputFile = self.Name + ".png"
        targetPath = os.path.join(outputDirectory, outputFile)

        logging.debug(f"-- Writing output to: {outputFile}")
        
        try:
            plt.savefig(targetPath, bbox_inches="tight", pad_inches=0, dpi=300)
        except OSError as err:
            logging.warning(err)
        else:      
            logging.debug(f"-- Output written")

        plt.close()

        return True

    def run_diameter_analysis(
        self, load_externally=False, method="matlab", engine_handler=None, config=None, verbose=False
    ) -> bool:
        """Runs diameter analysis"""

        # Make sure image is loaded
        if self.Data is None:
            if not self.loadImage():
                return False

        # Make sure everything is loaded for the image analysis
        if method == "matlab":
            if engine_handler is None:
                logging.warning("Tried to run diameter analysis without engine handler.")
                return False

        # Do analysis
        self.Analysis = fibreanalysis.Analysis(
            self,
            engine_handler=engine_handler,
            output_path=os.path.join(self.Project.Path, "output"),
            config=config,
        )
        self.Analysis.start(load_externally=load_externally)

        # Free up memory
        self.unloadImage()

        return True
