# Saccadic Adaptation

<a target="_blank" href="https://colab.research.google.com/github/jsbrittain/saccadapt/blob/main/lookatdata.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

Jupyter notebook used for saccadic adaptation analysis. Simply click the above link to run the notebook online, or follow the setup guide below to get up and running offline.

### Analysis

These scripts explore the dataset graphically, and will develop a pipeline for a saccadic adaptation analysis.

## Open online

The analysis script is provided as a Jupyter notebook which can be opened online using
[Google's colab](https://colab.research.google.com/?utm_source=scs-index) service. Simply
click the colab button above.

To load your own data into the analysis you can click the `Files` button on the sidebar
of colab and upload. Note that files uploaded in this way are not persistent between
sessions. Instead, consider uploading them to Google drive then mount the drive in
colab (again, under `Files`). If you would prefer to analyse your data offline then you
will need to install the notebook locally (see below).

## Offline setup

Ensure you have these dependencies installed on your system: [python3](https://www.python.org/) (tested on 3.11), [pip](https://pip.pypa.io/en/stable/) (should be installed with Python). Everything else (jupyter, pandas, etc) will be installed automatically below.

### Download

Download the repository as a zip file from: [https://github.com/jsbrittain/accelerometer-analysis/zipball/main](https://github.com/jsbrittain/accelerometer-analysis/zipball/main), unzip the file, open a terminal / command prompt and `cd` to that folder.

### Install and run

Launch from the command line using: `./run.sh`

If you want to clear any existing results from the notebook, run the following before opening the file:
`jupyter nbconvert scripts/lookatdata.ipynb --clear-output`

## Feature requests / bug reporting

Submit an [Issue](https://github.com/jsbrittain/saccadapt/issues) to report bugs, or
make feature/analysis requests.
