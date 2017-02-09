# Installing the Software Assessment Framework (SAF)

## Requirements
SAF has been developed using Python 3.5, it uses language features and syntax not supported in Python 2.x

## Installation
Use of a Python Virtual Environment [venv](https://docs.python.org/3/library/venv.html) is suggested

### Ubuntu Linux
* Setup and activate the Virtual Environment
`$ virtualenv -p python3 venv`
`$ source venv/bin/activate`	

* Clone the SAF GitHub repository:
`$ git clone https://github.com/softwaresaved/software-assessment-framework.git`

* Install the prerequisite Python packages as described in requirement.txt:
`$ cd software-assessment-framework`
`$ pip install -r requirements.txt`

### MacOS
TBC

### Windows
TBC

## Configuration
Some operations employ the GitHub API, and require a GitHub [Personal Access Token](https://github.com/settings/tokens) to be generated and inserted into 
`config.py`

## Running
run.py contains a simple, contrived example to get you started:
`python run.py`

You should see output to STDERR ending something like:

`Well done! This code is licensed under the Apache 2.0 license.`


