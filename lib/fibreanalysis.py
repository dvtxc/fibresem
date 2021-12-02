"""Analysis Module"""
# import fibresem


class Analysis:
    def __init__(self, parent, engine_handler=None, output_path=None):
        """..."""

        # Set parent image
        self.parent = parent

        # Set information
        self.image_path = self.parent.Path
        self.file_name = self.parent.Filename

        # Retrieve pixel size information from parent image
        self.pixel_size_value = self.parent.Meta["Pixel Size Value"]
        self.pixel_size_unit = self.parent.Meta["Pixel Size Unit"]

        self.params = {"optimise_for_thin_fibres": True}

        self.method = "simpoly-matlab"
        self.engine_handler = engine_handler

        self.output_path = output_path

        self.result = None

        if self.method == "simpoly-matlab":
            """
            Initialise simpoly-matlab
            cd matlabroot/extern/engines/python
            python setup.py build --build-base=$HOME\tmp\build install --user

            """
            import matlab.engine
            import matlab

    def start(self, load_externally=False):
        """Start analysis"""

        # Start Matlab Engine
        # print("Starting Matlab Engine ...")
        # eng = matlab.engine.start_matlab()
        # eng.addpath("lib", nargout=0)

        if self.method == "simpoly-matlab":
            """
            Initialise simpoly-matlab
            cd matlabroot/extern/engines/python
            python setup.py build --build-base=$HOME\tmp\build install --user

            """
            import matlab.engine
            import matlab

        if load_externally:
            # Let MATLAB import the file
            imgdata_matlab_array = matlab.uint8([])
        else:
            # Convert ndarray to MATLAB uint8 array
            # Can be slow
            print("Converting Data ...")
            imgdata_matlab_array = matlab.uint8(self.parent.Data.tolist())

        # fmt: off
        matlab_result = self.engine_handler.matlab_engine.simpoly(
            imgdata_matlab_array,
            "pixelsize", self.pixel_size_value,
            "pixelsizeunit", self.pixel_size_unit,
            "optimiseForThinFibres", True,
            "filename", self.file_name.replace(".tif",".png"),
            "outputpath", self.output_path,
            "load_externally", load_externally,
            "filepath", self.image_path,
            nargout=1,
        )
        # fmt: on

        self.result = Result(self, matlab_result)


class Result:
    def __init__(self, analysis_parent, matlab_result=None):
        self.parent = analysis_parent

        self.pixel_average = 0.0
        self.pixel_sdev = 0.0
        self.pixel_diameters = {}

        self.unit = "µm"

        if matlab_result is not None:
            self.parse_matlab_result(matlab_result)

    def __str__(self):
        return (
            f"avgp: {self.pixel_average:.3f} px \t"
            f"sdevp: {self.pixel_sdev:.3f} px \t"
            f"avg: {self.average:.3f} {self.unit} \t"
            f"sdev: {self.sdev:.3f} {self.unit} \t"
        )

    def parse_matlab_result(self, matlab_result):
        """Parse and add the resulting struct returned by MATLAB"""

        # Parse pixel average
        self.pixel_average = matlab_result["avgp"]

        # Parse pixel standard deviation
        self.pixel_sdev = matlab_result["sdevp"]

        # Parse list of all pixel diameters
        self.pixel_diameters = matlab_result["diameters"]._data.tolist()

    @property
    def average(self) -> float:
        """Returns the average converted to actual units"""
        return self.pixel_average * self.conversion_factor

    @property
    def sdev(self) -> float:
        return self.pixel_sdev * self.conversion_factor

    @property
    def diameters(self) -> list:
        return None

    @property
    def conversion_factor(self) -> float:
        """Returns conversion factor"""

        pixel_size_value = self.parent.pixel_size_value
        pixel_size_unit = self.parent.pixel_size_unit

        unit_exponent = {"um": -9, "nm": -9, "µm": -6, "mm": -3}
        exponent = unit_exponent[pixel_size_unit] - unit_exponent[self.unit]

        return pixel_size_value * 10 ** exponent
