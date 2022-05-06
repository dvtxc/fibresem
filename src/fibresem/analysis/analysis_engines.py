from abc import ABC, abstractmethod
import os
import logging
import numpy as np

from fibresem.analysis.fibreanalysis import Analysis, Result


class EngineHandler(ABC):
    """EngineHandler (Base) Class that provides the functionality to run analysis"""

    def __init__(self):
        self.engine = None
        self.module = None

    @property
    def is_running(self) -> bool:
        """Return the state of the engine"""
        if self.engine is None:
            return False
        else:
            return True

    @abstractmethod
    def start(self) -> bool:
        """Start the engine, in case the engine has to run in the background"""

    @abstractmethod
    def run(self, analysis: Analysis, load_externally = False) -> Result:
        """Run analysis"""


class MatlabEngine(EngineHandler):
    """MATLAB Engine Handler"""

    def __init__(self):
        super().__init__()

        # Try importing the matlab engine
        try:
            import matlab.engine    #pylint: disable=import-outside-toplevel
            import matlab           #pylint: disable=import-outside-toplevel
        except ModuleNotFoundError:
            logging.error("The matlab module is not installed!")
            print(
                """Please install the matlab module as follows:
cd matlabroot/extern/engines/python
python setup.py build --build-base=$HOME\\tmp\\build install --user
Remove --user flag for installation within environment"""
                )
            return
        else:
            logging.info("Matlab module loaded.")

        # Keep module loaded
        self.module = matlab

        # Start matlab engine
        self.start()

    def start(self) -> bool:
        # Start Matlab Engine
        logging.info("Starting Matlab Engine ...")

        try:
            eng = self.module.engine.start_matlab()  #pylint: disable=undefined-variable
        except Exception as err:
            logging.error("Could not start MATLAB Engine")
            print(err)
            return False

        # Set paths for matlab engine
        current_dir = os.path.dirname(__file__)
        eng.addpath(os.path.join(current_dir, "matlab"), nargout=0)
        eng.warning("off", "all", nargout=0)

        # Set Engine
        self.engine = eng

        return True

    def run(self, analysis: Analysis, load_externally = False) -> Result:

        # The matlab module
        matlab = self.module

        # The matlab engine
        eng = self.engine

        if load_externally:
            # Let MATLAB import the file
            imgdata_matlab_array = matlab.uint8([])
        else:
            # Convert ndarray to MATLAB uint8 array
            # Can be slow
            logging.debug("Converting Data ...")
            imgdata_matlab_array = matlab.uint8(analysis.parent.Data.tolist())

        # Handle no pixel size
        if analysis.pixel_size_unit is None:
            pixel_size_value = 1
            pixel_size_unit = "px"
        else:
            pixel_size_value = analysis.pixel_size_value
            pixel_size_unit = analysis.pixel_size_unit

        # fmt: off
        matlab_result = eng.simpoly(
            imgdata_matlab_array,
            "pixelsize", pixel_size_value,
            "pixelsizeunit", pixel_size_unit,
            "optimiseForThinFibres", analysis.params["optimise_for_thin_fibres"],
            "filename", analysis.file_name.replace(".tif",".png"),
            "outputpath", analysis.output_path,
            "load_externally", load_externally,
            "filepath", analysis.image_path,
            "verbose", analysis.params["verbose"],
            nargout=1,
        )
        # fmt: on

        result = Result()
        self.parse_matlab_result(result, matlab_result)

        return result
        

    def parse_matlab_result(self, result: Result, matlab_result):
        """Parse and add the resulting struct returned by MATLAB"""

        # Parse pixel average
        result.pixel_average = matlab_result["avgp"]

        # Parse pixel standard deviation
        result.pixel_sdev = matlab_result["sdevp"]

        # Parse list of all pixel diameters
        result.pixel_diameters = np.asarray(matlab_result["diameters"]._data.tolist())