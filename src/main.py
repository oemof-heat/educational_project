# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:15:33 2020

@author: Nini-Admin
"""

import os
from Lehrbeispiel import run_model
from Lehrbeispiel_Auswertung import display_results
import yaml


def main():
    # Choose configuration file to run model with
    exp_cfg_file_name = 'config.yaml'
    config_file_path = os.path.abspath(
        '../experiment_config/' + exp_cfg_file_name)
    with open(config_file_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)

    # global teamdata
    if cfg['run_model']:
        for n in range(cfg['number_of_teams']):
            run_model(config_path=config_file_path, team_number=n)

    # Basic analysis
    if cfg['display_results']:
        for n in range(cfg['number_of_teams']):
                display_results(config_path=config_file_path, team_number=n)



main()
