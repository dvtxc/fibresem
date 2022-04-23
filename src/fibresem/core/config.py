import configparser


class Config(configparser.ConfigParser):
    def __init__(self):
        """Configuration Class"""
        super().__init__()

        self.project_path = None
        self.load_defaults()

    def load_defaults(self):
        """Load default configuration"""

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
            }
        }

        self.read_dict(defaults)
