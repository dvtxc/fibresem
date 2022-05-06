# fibresem

[![Latest version](https://img.shields.io/pypi/v/fibresem.svg?style=flat&label=Latest&color=%234B78E6&logo=&logoColor=white)](https://pypi.python.org/pypi/fibresem)

A small python repo to analyse SEM images of fibrous materials.

## Requirements

The diameter analysis requires the [MATLAB® Engine API for Python](https://mathworks.com/help/matlab/matlab-engine-for-python.html). Since this repository is written in Python 3.9, this requires **MATLAB® 2021b** or newer.

## Installation

Install the python fibresem module:

    $ pip install fibresem

The module can now be run as follows:

    $ py -m fibresem

To use the fibre diameter analysis, install the MATLAB® Engine API for Python as follows:

    $ cd {matlabroot}/extern/engines/python
    $ python setup.py build --build-base=$HOME/tmp/build install --user

Remove ``--user`` flag for installation within environment.

## Usage

    python -m fibresem [OPTIONS] INPUT_PATH COMMAND1 [ARGS]...

E.g.:

    python -m fibresem C:\testfiles\ rename overview.txt crop diam --thick-opt

To get help for a specific command, e.g. ``diam``, use:

    fibresem diam --help

Options:

* ``-v, --verbose``
* ``--help``

Commands:
* ``crop``    annotate
* ``diam``    diameter_analysis
* ``rename``  auto_rename


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


## Auto-renaming

    py -m fibresem INPUT_PATH rename OVERVIEW_FILE

The ``OVERVIEW_FILE`` should have a structure similar to the following:

    img	dish	pos	width	remarks	sample
    1	1	2	20	-	PU.088
    2	1	2	100	-	PU.088
    3	1	2	200	-	PU.088


## References
<a id="1">[1]</a> 
Murphy, R., Turcott, A., Banuelos, L., Dowey, E., Goodwin, B., & Cardinal, K. O. (2020). SIMPoly: A Matlab-Based Image Analysis Tool to Measure Electrospun Polymer Scaffold Fiber Diameter. Tissue engineering. Part C, Methods, 26(12), 628–636. https://doi.org/10.1089/ten.TEC.2020.0304