"""Analysis Module"""

from dataclasses import dataclass
import logging
import numpy as np

from fibresem.core.config import Config


class Analysis:
    """Class containing the analysis engine handler, settings, and result"""

    def __init__(self, parent, engine_handler, output_path=None, config=None):

        if not config:
            config = Config()

        # Set parent image
        self.parent = parent

        # Set information
        self.image_path = self.parent.Path
        self.file_name = self.parent.Filename

        # Retrieve pixel size information from parent image
        self.pixel_size_value = self.parent.Meta["Pixel Size Value"]
        self.pixel_size_unit = self.parent.Meta["Pixel Size Unit"]

        self.params = {
            "optimise_for_thin_fibres": config.getboolean(
                "general", "optimise_for_thin_fibres"
            ),
            "verbose": config.getboolean("general", "verbose"),
        }

        self.method = "simpoly-matlab"
        self.engine_handler = engine_handler

        self.output_path = output_path

        self.result = None

    def start(self, load_externally=False) -> bool:
        """Start analysis"""

        if not self.engine_handler:
            logging.warning("No engine handler defined for analysis!")
            return False

        # Run analysis engine
        result: Result
        result = self.engine_handler.run(analysis=self, load_externally=load_externally)
        result.parent = self
        self.result = result

        # Return success
        return True


@dataclass
class Result:
    """Result class"""

    def __init__(self, analysis_parent=None):
        self.parent = analysis_parent

        self.pixel_average = 0.0
        self.pixel_sdev = 0.0
        self.pixel_diameters = {}

        self.unit = "µm"

    def __str__(self):
        return (
            f"avgp: {self.pixel_average:.3f} px \t"
            f"sdevp: {self.pixel_sdev:.3f} px \t"
            f"avg: {self.average:.3f} {self.unit} \t"
            f"sdev: {self.sdev:.3f} {self.unit} \t"
        )

    @property
    def average(self) -> float:
        """Returns the average converted to actual units"""
        return self.pixel_average * self.conversion_factor

    @property
    def sdev(self) -> float:
        """Return the standard deviation in actual units"""
        return self.pixel_sdev * self.conversion_factor

    @property
    def diameters(self) -> np.array:
        """Return the entire list of fibres in actual units"""
        return self.pixel_diameters * self.conversion_factor

    @property
    def conversion_factor(self) -> float:
        """Returns conversion factor"""

        # If no analysis is provided:
        if self.parent is None:
            return np.nan

        # Make sure pixel size unit is provided
        if self.pixel_size_unit is None or self.pixel_size_unit == "":
            return np.nan

        # Calculate exponent difference
        unit_exponent = {"nm": -9, "um": -6, "µm": -6, "mm": -3, "m": 0}
        try:
            exponent = unit_exponent[self.pixel_size_unit] - unit_exponent[self.unit]
        except KeyError:
            logging.warning("Unknown pixel size unit.")
            return np.nan

        # Return conversion factor
        return self.pixel_size_value * 10**exponent

    @property
    def pixel_size_value(self) -> float:
        """Return the pixel size value in px/unit"""
        if self.parent is None:
            return np.nan

        return self.parent.pixel_size_value

    @property
    def pixel_size_unit(self) -> str:
        """Return the pixel size unit"""
        if self.parent is None:
            return ""

        return self.parent.pixel_size_unit
