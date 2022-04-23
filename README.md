# fibresem

[![Latest version](https://img.shields.io/pypi/v/fibresem.svg?style=flat&label=Latest&color=%234B78E6&logo=&logoColor=white)](https://pypi.python.org/pypi/fibresem)

A small python repo to analyse SEM images of fibrous materials.

## Usage

    python -m fibresem [OPTIONS] INPUT_PATH COMMAND1 [ARGS]...

E.g.:

    python -m fibresem C:\testfiles\ rename overview.txt crop diam --thick-opt

To get help for a specific command, e.g. ``diam``, use:

    fibresem diam --help

## Auto-renaming

    py -m fibresem INPUT_PATH rename OVERVIEW_FILE

## Annotating

Cropping and annotating can be done with the ``crop`` command.

    py -m fibresem INPUT_PATH crop

* Crops .tif file, removes SEM Bar
* Adds scalebar based on Pixel Size
* Adds sample name
* Saves the image as a .png image in a separate ``/output/`` folder.

## Diameter analysis

Diameter analysis can be done with ``diam`` command using the Simpoly algorithm developed by Murphy et al.[[1]](#1) Requires MATLAB.

    py -m fibresem INPUT_PATH diam [options]

Additional options:

* ``--thick-opt/--no-thick-opt`` default: false

### Installation

Please install the matlab module as follows:

    $ cd {matlabroot}/extern/engines/python
    $ python setup.py build --build-base=$HOME/tmp/build install --user

Remove ``--user`` flag for installation within environment.

## Options

    Options:
    -v, --verbose
    --help         Show this message and exit.

    Commands:
    crop    annotate
    diam    diameter_analysis
    rename  auto_rename


## References
<a id="1">[1]</a> 
Murphy, R., Turcott, A., Banuelos, L., Dowey, E., Goodwin, B., & Cardinal, K. O. (2020). SIMPoly: A Matlab-Based Image Analysis Tool to Measure Electrospun Polymer Scaffold Fiber Diameter. Tissue engineering. Part C, Methods, 26(12), 628–636. https://doi.org/10.1089/ten.TEC.2020.0304