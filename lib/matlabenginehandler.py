import matlab.engine


class MatlabEngineHandler:
    def __init__(self):
        self.MatlabEngine = None

        self.start()

    def start(self):
        # Start Matlab Engine
        print("Starting Matlab Engine ...")
        eng = matlab.engine.start_matlab()
        eng.addpath("lib", nargout=0)

        # Set Engine
        self.MatlabEngine = eng

    def handle(self):
        return self.MatlabEngine
