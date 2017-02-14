# Installing the Software Assessment Framework (SAF)

## Requirements
SAF has been developed using Python 3.5, it uses language features and syntax not supported in Python 2.x

## Installation
Use of a Python Virtual Environment [venv](https://docs.python.org/3/library/venv.html) is suggested

### Ubuntu Linux
1. Setup and activate the Virtual Environment

`$ virtualenv -p python3 venv`

`$ source venv/bin/activate`	

2. Clone the SAF GitHub repository:

`$ git clone https://github.com/softwaresaved/software-assessment-framework.git`

3. Install the prerequisite Python packages as described in requirement.txt:

`$ cd software-assessment-framework`

`$ pip install -r requirements.txt`

### MacOS
The installation instructions for MacOS are the same as those for Ubuntu Linux.

### Windows
TBC

### Using conda instead of venv

If you use conda to manage virtual environments, replace step 1 as follows:

1. Set up and activate the conda virtual environment

`$ conda create --name saf python=3.6`

`$ source activate saf`


## Configuration
Some operations employ the GitHub API, and require a GitHub [Personal Access Token](https://github.com/settings/tokens) to be generated and inserted into `config.py`

## Running
run.py contains a simple, contrived example to get you started:

`python run.py`

You should see output to STDERR ending something like:

`Well done! This code is licensed under the Apache 2.0 license.`


