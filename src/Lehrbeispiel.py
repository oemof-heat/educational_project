# -*- coding: utf-8 -*-

"""
Installation requirements
-------------------------

This example requires the version v0.3.2 of oemof. Install by:

Optional:

    pip install matplotlib

"""

# ****************************************************************************
# ****** PART 1 - Definition und Optimierung des Energiesystems **************
# ****************************************************************************

###############################################################################
# imports
###############################################################################

# Default logger of oemof
import oemof.solph as solph
from oemof.solph import helpers
from oemof.tools import logger
import oemof.tools.economics as economics

import pyomo.environ as po

import logging
import os
import pandas as pd
import yaml


try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

def run_model(config_path, team_number):

    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)

    if cfg['debug']:
        number_of_time_steps = 3
    else:
        number_of_time_steps = 8760

    solver = cfg['solver']
    debug = cfg['debug']
    periods = number_of_time_steps
    solver_verbose = cfg['solver_verbose']  # show/hide solver output

    logger.define_logging(logfile='model_team_{0}.log'.format(team_number+1),
                          screen_level=logging.INFO,
                          file_level=logging.DEBUG)


    logging.info('Initialize the energy system')
    date_time_index = pd.date_range('1/1/2019', periods=number_of_time_steps,
                                freq='H')

    energysystem = solph.EnergySystem(timeindex=date_time_index)
    
#    timestr = time.strftime("%Y%m%d")
    
    
    ##########################################################################
    # Einlesen der Zeitreihen und Variablen aus den Dateien
    ##########################################################################

    abs_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))

    file_path_ts = abs_path + '/data_raw/' + cfg[
        'time_series_file_name']
    data = pd.read_csv(file_path_ts, sep=';')


    file_name_param_01 = cfg['design_parameters_file_name'][team_number]
    file_path_param_01 = (abs_path + '/data/'
                          + file_name_param_01)
    param_df_01 = pd.read_csv(file_path_param_01, index_col=1,
                              sep=';', encoding = 'unicode_escape')
    param_value = param_df_01['value']
 
    
    # periodische Kosten
    epc_PV = economics.annuity(capex=param_value['capex_PV'],
                               n=param_value['n_PV'],
                               wacc=param_value['wacc'])
    epc_Solarthermie = economics.annuity(capex=param_value['capex_Sol'],
                                         n=param_value['n_Sol'],
                                         wacc=param_value['wacc'])
    epc_gas_boiler = economics.annuity(capex=param_value['capex_Gaskessel'],
                                       n=param_value['n_Gaskessel'],
                                       wacc=param_value['wacc'])
    epc_BHKW = economics.annuity(capex=param_value['capex_BHKW'],
                                 n=param_value['n_BHKW'],
                                 wacc=param_value['wacc'])
    epc_heat_pump = economics.annuity(capex=param_value['capex_Waermepumpe'],
                                      n=param_value['n_Waermepumpe'],
                                      wacc=param_value['wacc'])
    epc_el_storage = economics.annuity(capex=param_value['capex_Stromspeicher'],
                                       n=param_value['n_Stromspeicher'],
                                       wacc=param_value['wacc'])
    epc_th_storage = economics.annuity(capex=param_value['capex_Waermespeicher'],
                                       n=param_value['n_Waermespeicher'],
                                       wacc=param_value['wacc'])
    
    
    ##########################################################################
    # Erstellung der Oemof-Komponenten
    ##########################################################################
    
    logging.info('Create oemof objects')
    
    ### Definition der bus'es #################################################
    
    # Erdgasbus
    b_gas = solph.Bus(label="Erdgas")
    
    # Strombus
    b_el = solph.Bus(label="Strom")
    
    # Waermebus
    b_th = solph.Bus(label="Waerme")
    
    # Hinzufügen zum Energiesystem
    energysystem.add(b_gas, b_el, b_th)
    
    
    ### Definition des Ueberschusses #########################################
    
    # Senke fuer Stromueberschusss
    energysystem.add(solph.Sink(
            label='excess_bel',
            inputs={b_el: solph.Flow()}))
    
    # Senke fuer Waermeueberschuss
    energysystem.add(solph.Sink(
            label='excess_bth',
            inputs={b_th: solph.Flow()}))
    
    
    ### Definition Quellen #################################################
    
    # Quelle: Erdgasnetz
    energysystem.add(solph.Source(
            label='Gasnetz',
            outputs={b_gas: solph.Flow(
            variable_costs=param_value['vc_gas']
                            +param_value['vc_CO2'])})) #[€/kWh]
    
    # Quelle: Stromnetz
    energysystem.add(solph.Source(
            label='Strombezug',
            outputs={b_el: solph.Flow(
            variable_costs=param_value['vc_el'])})) #[€/kWh]
    
    # Quelle: Waermenetz/Fernwaerme
    energysystem.add(solph.Source(
            label='Waermebezug',
            outputs={b_th: solph.Flow(
            variable_costs=param_value['vc_th'])})) #[€/kWh]
    
    # Quelle: Solaranlage
    if param_value['A_Kollektor_gesamt'] > 0:    
        energysystem.add(solph.Source(
                label='PV',
                outputs={b_el:solph.Flow(
                        fix=(data['Sol_irradiation [Wh/sqm]']*0.001
                                      *param_value['cf_PV']),         #[kWh/m²]
                        investment=solph.Investment(
                        ep_costs=epc_PV,
                        minimum=param_value['A_min_PV']*1*param_value['cf_PV']
                        ))}))
                        
    # Quelle: Solarthermieanlage
    if param_value['A_Kollektor_gesamt'] > 0:    
        energysystem.add(solph.Source(
                label='Solarthermie',
                outputs={b_th:solph.Flow(
                        fix=(data['Sol_irradiation [Wh/sqm]']*0.001
                                      *param_value['cf_Sol']),  #[kWh/m²]
                        investment=solph.Investment(
                        ep_costs=epc_Solarthermie,
                        minimum=param_value['A_min_Sol']*1*param_value['cf_Sol']
                        ))}))
        
        
    ### Definition Bedarf ################################################
      
    # Strombedarf
    energysystem.add(solph.Sink(
            label='Strombedarf',
            inputs={b_el: solph.Flow(
                fix=data['P*'],
                nominal_value=param_value['W_el'], #[kWh]
                )}))
     
    # Waermebedarf
    energysystem.add(solph.Sink(
            label='Waermebedarf',
            inputs={b_th: solph.Flow(
                fix=data['Q*'],
                nominal_value=param_value['W_th'], #[kWh]
                )}))     
        
        
    ### Definition Systemkomponenten #########################################
    
    # Transformer: Gaskessel
    if param_value['max_Gaskessel'] > 0:
        energysystem.add(solph.Transformer(
                label="Gaskessel",
                inputs={b_gas: solph.Flow()},
                outputs={b_th: solph.Flow(investment=solph.Investment(
                                  ep_costs=epc_gas_boiler,
                                  minimum=param_value['min_Gaskessel'],    #[kW]
                                  maximum=param_value['max_Gaskessel']))}, #[kW]
                conversion_factors={b_th: param_value['cf_Gaskessel']}))
    
    # Transformer: BHKW
    if param_value['max_BHKW'] > 0:
        energysystem.add(solph.Transformer(
                label="BHKW",
                inputs={b_gas: solph.Flow()},
                outputs={b_el: solph.Flow(),
                         b_th:solph.Flow(investment=solph.Investment(
                                 ep_costs=epc_BHKW,
                                 minimum=param_value['min_BHKW'],          #[kW]
                                 maximum=param_value['max_BHKW']))},       #[kW]
                conversion_factors={b_el: param_value['cf_BHKW_el'],
                                    b_th:0.85-param_value['cf_BHKW_el']}))
    
    # Transformer: Waermepumpe
    if param_value['max_Waermepumpe'] > 0:
        energysystem.add(solph.Transformer(
                label="Waermepumpe",
                inputs={b_el: solph.Flow()},
                outputs={b_th: solph.Flow(investment=solph.Investment(
                                  ep_costs=epc_heat_pump,
                                  minimum=param_value['min_Waermepumpe'],    #[kW]
                                  maximum=param_value['max_Waermepumpe']))}, #[kW]
                conversion_factors={b_th: param_value['COP_Waermepumpe']}))
    
    # Speicher: Stromspeicher
    if param_value['max_Stromspeicher'] > 0:
        Stromspeicher = solph.components.GenericStorage(
                label='Stromspeicher',
                inputs={b_el: solph.Flow()},
                outputs={b_el: solph.Flow()},
                loss_rate=param_value['lr_Stromspeicher'],
                initial_storage_level=param_value['isl_Stromspeicher'],
                inflow_conversion_factor=param_value['cf_Stromspeicher_ein'],
                outflow_conversion_factor=param_value['cf_Stromspeicher_aus'],
                investment=solph.Investment(ep_costs=epc_el_storage,
                                    minimum=param_value['min_Stromspeicher'],  #[kWh]
                                    maximum=param_value['max_Stromspeicher'])) #[kWh]
        energysystem.add(Stromspeicher)
    
    # Speicher: Waermespeicher
    if param_value['max_Waermespeicher'] > 0:
        Waermespeicher = solph.components.GenericStorage(
                label='Waermespeicher',
                inputs={b_th: solph.Flow()},
                outputs={b_th: solph.Flow()},
                loss_rate=param_value['lr_Waermespeicher'],
                initial_storage_level=param_value['isl_Waermespeicher'],
                inflow_conversion_factor=param_value['cf_Waermespeicher_ein'],
                outflow_conversion_factor=param_value['cf_Waermespeicher_aus'],
                investment=solph.Investment(ep_costs=epc_th_storage,
                                    minimum=param_value['min_Waermespeicher'],  #[kWh]
                                    maximum=param_value['max_Waermespeicher'])) #[kWh]
        energysystem.add(Waermespeicher)
    
    
        
    logging.info('Optimise the energy system')
    
    # Initialisierung des Modells
    model = solph.Model(energysystem)
    
    
    ##########################################################################
    # Constraint fuer Kollektorgesamtflaeche
    ##########################################################################
    
    PV_installed = energysystem.groups['PV']
    Sol_installed = energysystem.groups['Solarthermie']
    
    myconstrains = po.Block()
    model.add_component('MyBlock', myconstrains)
    myconstrains.collector_area = po.Constraint(
            expr=((((model.InvestmentFlow.invest[PV_installed, b_el])/(1*param_value['cf_PV']))
            + ((model.InvestmentFlow.invest[Sol_installed, b_th])/(1*param_value['cf_Sol']))) <= param_value['A_Kollektor_gesamt']))
        
    
    ##########################################################################
    # Optimierung des Systems und Speichern des Ergebnisses
    ##########################################################################
    if debug:
        filename = os.path.join(
            helpers.extend_basic_path('lp_files'), 'model_team_{0}.lp'.format(team_number+1))
        logging.info('Store lp-file in {0}.'.format(filename))
        model.write(filename, io_options={'symbolic_solver_labels': True})
    
    # if tee_switch is true solver messages will be displayed
    logging.info('Solve the optimization problem of team {0}'.format(team_number+1))
    model.solve(solver=solver, solve_kwargs={'tee': solver_verbose})
    
    logging.info('Store the energy system with the results.')
    
    # add results to the energy system to make it possible to store them.
    energysystem.results['main'] = solph.processing.results(model)
    energysystem.results['meta'] = solph.processing.meta_results(model)
    results = energysystem.results['main']
    
    
    energysystem.dump(dpath=abs_path + "/results",
                      filename="model_team_{0}.oemof".format(team_number+1))