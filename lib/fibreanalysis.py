"""Analysis Module"""
import fibresem
import numpy as np


class Analysis:
    def __init__(self, parent, engineHandler=None):
        """..."""

        # Set parent image
        self.Parent = parent

        # Retrieve pixel size information from parent image
        self.PixelSizeValue = self.Parent.Meta["Pixel Size Value"]
        self.PixelSizeUnit = self.Parent.Meta["Pixel Size Unit"]

        self.Params = dict()
        self.Params["optimiseForThinFibres"] = True

        self.Method = "simpoly-matlab"
        self.EngineHandler = engineHandler

        if self.Method == "simpoly-matlab":
            """
            Initialise simpoly-matlab
            cd matlabroot/extern/engines/python
            python setup.py build --build-base=$HOME\tmp\build install --user

            """
            import matlab.engine
            import matlab

    def start(self):
        """Start analysis"""

        # Start Matlab Engine
        # print("Starting Matlab Engine ...")
        # eng = matlab.engine.start_matlab()
        # eng.addpath("lib", nargout=0)

        if self.Method == "simpoly-matlab":
            """
            Initialise simpoly-matlab
            cd matlabroot/extern/engines/python
            python setup.py build --build-base=$HOME\tmp\build install --user

            """
            import matlab.engine
            import matlab

        # Convert ndarray to MATLAB uint8 array
        print("Converting Data ...")
        imgdata = self.Parent.Data
        imgdata_matlab_array = matlab.uint8(self.Parent.Data.tolist())

        # fmt: off
        result = self.EngineHandler.MatlabEngine.simpoly(
            imgdata_matlab_array,
            "pixelsize", self.PixelSizeValue,
            "pixelsizeunit", self.PixelSizeUnit,
            "optimiseForThinFibres", True,
            nargout=1,
        )

        pass
        # fmt: on


class Result:
    def __init__(self, analysisparent):
        self.Parent = analysisparent

        self.PixelAverage = 0.0
        self.PixelSdev = 0.0
        self.Diameters = list()

        self.Unit = "µm"

    @property
    def Average(self) -> float:
        pass

    @property
    def Sdev(self) -> float:
        pass

    @property
    def Diameters(self) -> list:
        pass
