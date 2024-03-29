import configparser


class Config(configparser.ConfigParser):
    """Config Class"""

    def __init__(self):
        """Configuration Class"""
        super().__init__()

        self.project_path = None
        self.load_defaults()

    def load_defaults(self):
        """Load default configuration"""

        # Define defaults
        defaults = {
            "general": {
                "analysis_method": "simpoly-matlab",
                "annotate_add_scalebar": True,
                "annotate_add_samplename": True,
                "annotate_crop": True,
                "annotate_crop_ratio": 1.0,
                "sem_bar_height": 0.11,
                "output_folder_name": "cropped",
                "keep_in_memory": False,
                "optimise_for_thin_fibres": True,
                "verbose": False,
            },
            "annotate": {
                "add_scalebar": True,
                "add_samplename": True,
                "samplename_separator": "_",
                "samplename_parts": "0",
            },
            "crop": {
                "ratio": 1.0,
                "sem_bar_height": 0.11,
            },
            "analysis": {
                "engine": "simpoly-matlab",
            },
            "simpoly-matlab-engine": {
                "load_externally": True,
                "optimise_for_thin_fibres": True,
                "verbose_image_output_path": "analysis",
            },
        }

        # Load in defaults
        self.read_dict(defaults)
