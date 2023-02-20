# Educational Project

This repository contains material for the illustration of energy system analysis for graduate students. The teaching material is prepared in German, coding contains a mix of German and Englisch. The technical setting is the heat supply for a district. Several technological options may be used to satisfy the heat demand. Cost settings and other key parameters can be freely configured in order to cover different scenarios. These scenarios are refered to different teams assuming that different groups of students investigate their specific setting. oemof code is provided which allows to run the optimization and to analyse the results. Also, the material includes slides for presenting the technical setting and preliminary exercises. All material may be adapted for individual use.

# Subfolder Structure
This repository includes the subdirectories with the following contents:

data: all data to define the given parameters for each team/scenario

data_postprocessed: Auswertungsergebnisse_Text.csv = List of parameter names which is used to generate files in the subfolders: subfolders with results for each team/scenario

data_raw: time series data for solar irradiation, electric and thermal power demand

experiment_config: file to control the calculation process

results: calculation results

src: python sources

# Installation
The following steps are recommended to install the educational project on a Windows PC.

1.	Download and install Anaconda Navigator: https://www.anaconda.com/products/individual
2.	Open Anaconda Navigator
3.	Create new environment for python 3.7
4.	Activate your environment
5.	Open Terminal in your environment
6.	Download educational projekt (Lehrbeispiel) from this repository and store all files with the given folder structure on your harddrive in a defined project-folder
7.	In Terminal Window: Navigate to the project-folder
8.	Install all required packages using the command “pip install –r requirements.txt”
9.	Download and install Solver 'cbc' für Python 3.7: https://oemof-solph.readthedocs.io/en/latest/readme.html#installing-a-solver

# Operation
The following steps are recommended to run the energy-system-planning-workshop on a Windows PC.

1.	Define calculation setup in the file “config.yml” in the folder “experiment_config” using a standard editor.
2.	Define boundary conditions for the optimization by adapting data in file “parameters_Team_XX” (XX for scenario/team ) in folder “data”.
3.	Open Anaconda Navigator
4.	Activate environment which was created in the installation process
5.	Open Terminal in this environment
6.	Navigate to folder src in the Terminal Window
7.	Start optimization in Terminal Window with: “python main.py”
8.	Wait computation to finish in Terminal Window
9.	Analyse results in folder “results”

# Contact
christoph.pels-leusden(at)bht-berlin.de

# License
Copyright (C) 2023 Berliner Hochschule für Technik Berlin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
