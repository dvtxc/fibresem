import matlab.engine
import os
import logging


class MatlabEngineHandler:
    def __init__(self):
        self.matlab_engine = None

        self.start()

    def start(self):
        # Start Matlab Engine
        print("Starting Matlab Engine ...")

        try:
            eng = matlab.engine.start_matlab()
        except Exception as err:
            logging.error("Could not start MATLAB Engine")
            print(err)

        # Set paths for matlab engine
        eng.addpath("lib", nargout=0)
        eng.addpath(os.path.join("lib", "matlab"), nargout=0)

        # Set Engine
        self.matlab_engine = eng

    def handle(self):
        return self.matlab_engine

    @property
    def is_running(self) -> bool:
        """Check whether matlab engine has already been instantiated"""
        if self.matlab_engine is None:
            return False
        else:
            return True
