# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

"""
Installation requirements
-------------------------

This example requires the version v0.3.2 of oemof. Install by:

Optional:

    pip install matplotlib

"""

###############################################################################
# imports
###############################################################################

import oemof.solph as solph
import oemof.tools.economics as eco

import numpy as np
import pandas as pd
from pathlib import Path
import calendar
import yaml
import os

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def display_results(config_path, team_number):
    
    abs_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
    # ****************************************************************************
    # ********** PART 2 - Auswertung der Ergebnisse ******************************
    # ****************************************************************************
    # Laden der Config-Datei
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.CLoader)

    
    # Einlesen Datei (Variablendefinition)
    file_name_param_01 = cfg['design_parameters_file_name'][team_number]
    file_path_param_01 = (abs_path + '/data/'
                          + file_name_param_01)
    param_df_01 = pd.read_csv(file_path_param_01, index_col=1,
                              sep=';', encoding = 'unicode_escape')
    param_value = param_df_01['value']

    if cfg['debug']:
        number_of_time_steps = 3
    else:
        number_of_time_steps = 8760

    # Laden der Optimierungsergebnisse    
    energysystem = solph.EnergySystem()
    abs_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
    energysystem.restore(
        dpath=abs_path + "/results",
        filename="model_team_{0}.oemof".format(team_number+1))
    string_results = solph.views.convert_keys_to_strings(
        energysystem.results['main'])
    results = energysystem.results['main']
    
    
    # Zeitreihen der Ergebnisse
    Erdgasverbrauch = string_results['Gasnetz', 'Erdgas']['sequences']
    
    heat_demand = string_results['Waerme', 'Waermebedarf']['sequences']
    el_demand = string_results['Strom', 'Strombedarf']['sequences']
    shortage_electricity = string_results['Strombezug','Strom']['sequences']
    shortage_heat = string_results['Waermebezug', 'Waerme']['sequences']
    Ueberschuss_el = string_results['Strom','excess_bel']['sequences']
    Ueberschuss_th = string_results['Waerme','excess_bth']['sequences']
    
    PV_el = string_results['PV', 'Strom']['sequences']
    Sol_th  = string_results['Solarthermie', 'Waerme']['sequences']
    Gaskessel_th = string_results['Gaskessel', 'Waerme']['sequences']
    Gaskessel_gas = string_results['Erdgas','Gaskessel']['sequences']
    BHKW_th = string_results['BHKW', 'Waerme']['sequences']
    BHKW_el = string_results['BHKW', 'Strom']['sequences']
    BHKW_gas = string_results['Erdgas', 'BHKW']['sequences']
    Waermepumpe_th = string_results['Waermepumpe', 'Waerme']['sequences']
    Waermepumpe_el = string_results['Strom', 'Waermepumpe']['sequences']
    
    Stromspeicher_in = string_results['Strom', 'Stromspeicher']['sequences']
    Stromspeicher_out = string_results['Stromspeicher', 'Strom']['sequences']
    Waermespeicher_in = string_results['Waerme', 'Waermespeicher']['sequences']
    Waermespeicher_out = string_results['Waermespeicher', 'Waerme']['sequences']
    
    electricity_bus = solph.views.node(results, 'Strom')
    thermal_bus = solph.views.node(results, 'Waerme')
    
    
    # ****************************************************************************
    # Größe der Invest-Komponenten
    # ****************************************************************************
    
    PV_Invest_kW = (solph.views.node(results, 'PV')[
                'scalars'][(('PV', 'Strom'), 'invest')])
    
    PV_Invest_m2 = (PV_Invest_kW)/(1*param_value['cf_PV'])
        
    Solarthermie_Invest_kW = (solph.views.node(results, 'Solarthermie')[
                'scalars'][(('Solarthermie', 'Waerme'), 'invest')])

    Solarthermie_Invest_m2 = (Solarthermie_Invest_kW)/(1*param_value['cf_Sol'])    
        
    Gaskessel_Invest = (solph.views.node(results, 'Gaskessel')[
                       'scalars'][(('Gaskessel', 'Waerme'), 'invest')])
    
    BHKW_Invest = (solph.views.node(results, 'BHKW')[
            'scalars'][(('BHKW', 'Waerme'), 'invest')])
    
    Waermepumpe_Invest = (solph.views.node(results, 'Waermepumpe')[
            'scalars'][(('Waermepumpe', 'Waerme'), 'invest')])
    
    Stromspeicher_Invest = (solph.views.node(results, 'Stromspeicher')[
            'scalars'][(('Stromspeicher', 'None'), 'invest')])
    
    Waermespeicher_Invest = (solph.views.node(results, 'Waermespeicher')[
            'scalars'][(('Waermespeicher', 'None'), 'invest')])
    
    print("Die Größe der PV-Anlage beträgt:  {:.2f}"
          .format(PV_Invest_kW), "kW")
    print("Die Größe der Solarthermieanlage beträgt:  {:.2f}"
          .format(Solarthermie_Invest_kW), "kW")    
    print("Die Größe des Gaskessels beträgt:  {:.2f}"
          .format(Gaskessel_Invest), "kW")
    print("Die Größe des BHKW's beträgt:  {:.2f}"
          .format(BHKW_Invest), "kW")
    print("Die Größe der Wärmepumpe beträgt:  {:.2f}"
          .format(Waermepumpe_Invest), "kW")
    print("Die Größe des Stromspeichers beträgt:  {:.2f}"
          .format(Stromspeicher_Invest), "kWh")
    print("Die Größe des Wärmespeichers beträgt:  {:.2f}"
          .format(Waermespeicher_Invest), "kWh")
    
    
    # ****************************************************************************
    # Co2-Emissionen
    # ****************************************************************************
    
    em_co2 = (Erdgasverbrauch.flow.sum()
             *param_value['emission_gas']
             + shortage_electricity.flow.sum()
             *param_value['emission_el']
             + shortage_heat.flow.sum()
             *param_value['emission_th']) #(kWh/a)*(g/kWh)
    print("CO2-Emissionen: {:.2f}".format(em_co2/1e6), "t/a")
    
    
    # ****************************************************************************
    # Investitionskosten
    # ****************************************************************************
    
    cap_PV = (PV_Invest_kW
              * param_value['capex_PV'])
    cap_Solarthermie = (Solarthermie_Invest_kW
                        * param_value['capex_Sol'])
    cap_Gaskessel = (Gaskessel_Invest
                        * param_value['capex_Gaskessel'])
    cap_BHKW = (BHKW_Invest                                   
                      * param_value['capex_BHKW'])
    cap_Waermepumpe = (Waermepumpe_Invest  
                    * param_value['capex_Waermepumpe'])
    cap_Stromspeicher = (Stromspeicher_Invest                     
                            * param_value['capex_Stromspeicher'])
    cap_Waermespeicher = (Waermespeicher_Invest                         
                            * param_value['capex_Waermespeicher'])
    
    
    # Berechnung der jaehrlichen Kosten
    annuity_PV = eco.annuity(
            cap_PV,
            param_value['n_PV'],
            param_value['wacc'])
    annuity_Solarthermie = eco.annuity(
            cap_Solarthermie,
            param_value['n_Sol'],
            param_value['wacc'])
    annuity_Gaskessel = eco.annuity(
            cap_Gaskessel,
            param_value['n_Gaskessel'],
            param_value['wacc'])
    annuity_BHKW = eco.annuity(
            cap_BHKW,
            param_value['n_BHKW'],
            param_value['wacc'])
    annuity_Waermepumpe = eco.annuity(
            cap_Waermepumpe,
            param_value['n_Waermepumpe'],
            param_value['wacc'])
    annuity_Stromspeicher = eco.annuity(
            cap_Stromspeicher,
            param_value['n_Stromspeicher'],
            param_value['wacc'])
    annuity_Waermespeicher = eco.annuity(
            cap_Waermespeicher,
            param_value['n_Waermespeicher'],
            param_value['wacc'])
    
    total_annuity = (annuity_PV+annuity_Solarthermie
                     +annuity_Gaskessel+annuity_BHKW+annuity_Waermepumpe
                     +annuity_Stromspeicher+annuity_Waermespeicher)
    
    
    # Berechnung der variablen Kosten
    vc_Erdgas = Erdgasverbrauch.flow.sum()*param_value['vc_gas']
    vc_CO2 = Erdgasverbrauch.flow.sum()*param_value['vc_CO2']
    vc_Strombezug = (shortage_electricity.flow.sum()
                         * param_value['vc_el'])
    vc_Waermebezug = (shortage_heat.flow.sum()
                         * param_value['vc_th'])
    var_costs_es = vc_Erdgas + vc_CO2 + vc_Strombezug + vc_Waermebezug
    
    
    # Berechnung der Gesamtkosten
    sum_costs = var_costs_es+total_annuity
    
    print("Gesamtenergiekosten pro Jahr: {:.2f}".format(
         (sum_costs) / 1e6), "Mio. €/a")
    
    
    # ****************************************************************************
    # Verhaeltnis zwischen Bezug und Gesamtbedarf
    # ****************************************************************************
    
    Verhaeltnis_el= (el_demand.flow.sum()-shortage_electricity.flow.sum())/el_demand.flow.sum()
    Verhaeltnis_th= (heat_demand.flow.sum()-shortage_heat.flow.sum())/heat_demand.flow.sum()
    Deckungsgrad= (Verhaeltnis_el+Verhaeltnis_th)/2
    print("Elektrischer Deckungsgrad: {:.5f}"
          .format(Verhaeltnis_el))
    print("Thermischer Deckungsgrad: {:.5f}"
          .format(Verhaeltnis_th))
    print("Der Gesamtdeckungsgrad beträgt: {:.5f}"
          .format(Deckungsgrad))
    
    
    # ****************************************************************************
    # Berechnungen zu den Speichern
    # ****************************************************************************
    
    if Stromspeicher_Invest > 0:
        Vollladezyklenzahl_Stromspeicher=(Stromspeicher_in.flow.sum())/Stromspeicher_Invest
        Verhaeltnis_Ausspeichern_Bedarf_Stromspeicher=(Stromspeicher_out.flow.sum())/el_demand.flow.sum()
    else:
        Vollladezyklenzahl_Stromspeicher='Kein Stromspeicher installiert.'
        Verhaeltnis_Ausspeichern_Bedarf_Stromspeicher='Kein Stromspeicher installiert.'
    
    if Waermespeicher_Invest > 0:
        Vollladezyklenzahl_Waermespeicher=(Waermespeicher_in.flow.sum())/Waermespeicher_Invest
        Verhaeltnis_Ausspeichern_Bedarf_Waermespeicher=(Waermespeicher_out.flow.sum())/el_demand.flow.sum()
    else:
        Vollladezyklenzahl_Waermespeicher='Kein Waermespeicher installiert.'
        Verhaeltnis_Ausspeichern_Bedarf_Waermespeicher='Kein Waermespeicher installiert.'    
    
    # ****************************************************************************
    # Speichern der Ergebnisse
    # ****************************************************************************
   
    # Anlegen von Ordnern für die Ergebnisse nach Teams
    newpath = r'../results/results_{0}'.format(team_number+1)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        
    # Anlegen von Ordnern für die Zwischenergebnisse nach Teams    
    newpath_02 = r'../data_postprocessed/data_postprocessed_{0}'.format(team_number+1)
    if not os.path.exists(newpath_02):
        os.makedirs(newpath_02)    
    
    # Speichern der Zahlenwerte
    d={'1' : [round(sum_costs / 1e3, 1)],
       '2' : [round(em_co2/1e6, 1)],
       '3' : [round(Deckungsgrad, 4)],
       '4' : [round(PV_Invest_kW,1)],
       '5' : [round(PV_Invest_m2,1)],
       '6' : [round(Solarthermie_Invest_kW,1)],
       '7' : [round(Solarthermie_Invest_m2,1)],
       '8' : [round(Gaskessel_Invest,1)],
       '9' : [round(BHKW_Invest,1)],
       '10': [round(Waermepumpe_Invest,1)],
       '11': [round(Stromspeicher_Invest,4)],
       '12': [round(Waermespeicher_Invest,1)],
       '13': [''],
       '14': [round(el_demand.flow.sum()/1000,1)],
       '15': [round(Ueberschuss_el.flow.sum()/1000,1)],
       '16': [round((PV_el.flow.sum()+BHKW_el.flow.sum()
                                             +shortage_electricity.flow.sum())
                                            /1000,1)],
       '17': [round(PV_el.flow.sum()/1000,1)],
       '18': [round(BHKW_el.flow.sum()/1000,1)],
       '19': [round(shortage_electricity.flow.sum()/1000,1)],
       '20': [''],
       '21': [round(heat_demand.flow.sum()/1000,1)],
       '22': [round(Ueberschuss_th.flow.sum()/1000,1)],
       '23': [round((Sol_th.flow.sum()+Gaskessel_th.flow.sum()
                                     +BHKW_th.flow.sum()+Waermepumpe_th.flow.sum()
                                     +shortage_heat.flow.sum())/1000,1)],
       '24': [round(Sol_th.flow.sum()/1000,1)],
       '25': [round(Gaskessel_th.flow.sum()/1000,1)],
       '26': [round(BHKW_th.flow.sum()/1000,1)],
       '27': [round(Waermepumpe_th.flow.sum()/1000,1)],
       '28': [round(shortage_heat.flow.sum()/1000,1)],
       '29': [''],
       '30': [Vollladezyklenzahl_Stromspeicher],
       '31': [Verhaeltnis_Ausspeichern_Bedarf_Stromspeicher],
       '32': [Vollladezyklenzahl_Waermespeicher],
       '33': [Verhaeltnis_Ausspeichern_Bedarf_Waermespeicher],
       '34': [''],
       '35': [round(Gaskessel_gas.flow.sum()*param_value['emission_gas']/1e6,1)],
       '36': [round(BHKW_gas.flow.sum()*param_value['emission_gas']/1e6,1)],
       '37': [round(shortage_electricity.flow.sum()
                                       *param_value['emission_el']/1e6,1)],
       '38': [round(shortage_heat.flow.sum()
                                       *param_value['emission_th']/1e6,1)],
       '39': [''],
       '40': [round(total_annuity/1e3,1)],
       '41': [round(annuity_PV/1e3,1)],
       '42': [round(annuity_Solarthermie/1e3,1)],
       '43': [round(annuity_Gaskessel/1e3,1)],
       '44': [round(annuity_BHKW/1e3,1)],
       '45': [round(annuity_Waermepumpe/1e3,1)],
       '46': [round(annuity_Stromspeicher/1e3,1)],
       '47': [round(annuity_Waermespeicher/1e3,1)],
       '48': [round(var_costs_es/1e3,1)],
       '49': [round(vc_Erdgas/1e3,1)],
       '50': [round(vc_CO2/1e3,1)],
       '51': [round(vc_Strombezug/1e3,1)],
       '52': [round(vc_Waermebezug/1e3,1)],
       '53': [''],
       '54' : [Verhaeltnis_el],
       '555' : [Verhaeltnis_th]
       }
    Auswertungsergebnisse_Zahlen = pd.DataFrame(data=d)
    Auswertungsergebnisse_Zahlen_transposed = Auswertungsergebnisse_Zahlen.transpose()
    
    Auswertungsergebnisse_Zahlen_transposed.to_csv("../data_postprocessed/data_postprocessed_{0}/Auswertungsergebnisse_Zahlen_{0}.csv".format(team_number+1),
                                                   sep=';')
  
        # Einlesden Datei (Text)
    file_name_02 = ('../data_postprocessed/Auswertungsergebnisse_Text.csv')
    data_02 = pd.read_csv(file_name_02)
   
    # Einlesen Datei (Zahlen)
    file_name_03 = ('../data_postprocessed/data_postprocessed_{0}/Auswertungsergebnisse_Zahlen_{0}.csv'.format(team_number+1))
    data_03 = pd.read_csv(file_name_03, sep=';',
                        header=0, names=['0','Zahl'],
                        usecols=['Zahl'])
    
    # Kombination der Dateien und Speichern als Ergebnissdatei
    merged=pd.concat([data_02,data_03],
                     axis=1)
    
    merged.to_csv('../results/results_{0}/Auswertungsergebnisse_{0}.csv'.format(team_number+1),
                  sep=';', header=None, index=False)
    
    # ****************************************************************************
    # Zeitreihenerstellung fuer die graphische Darstellung
    # ****************************************************************************
    
    # Jahreszeitreihe Strom
    zeitreihen_el = pd.DataFrame()
    if sum(shortage_electricity.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Strombezug'] = shortage_electricity.flow[0:number_of_time_steps]
    if sum(PV_el.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['PV'] = PV_el.flow[0:number_of_time_steps]
    if sum(BHKW_el.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['BHKW_el'] = BHKW_el.flow[0:number_of_time_steps]
    if sum(Stromspeicher_out.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Stromspeicher_out'] = abs(Stromspeicher_out.flow[0:number_of_time_steps])
    if sum(el_demand.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Strombedarf'] = el_demand.flow[0:number_of_time_steps]*(-1)
    if sum(Ueberschuss_el.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Stromueberschuss'] = Ueberschuss_el.flow[0:number_of_time_steps]*(-1)
    if sum(Waermepumpe_el.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Waermepumpe_el'] = Waermepumpe_el.flow[0:number_of_time_steps]*(-1)
    if sum(Stromspeicher_in.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_el['Stromspeicher_in'] = abs(Stromspeicher_in.flow[0:number_of_time_steps])*(-1)
        
    zeitreihen_el_sortiert=zeitreihen_el.reindex(zeitreihen_el.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_el_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_{0}.csv'.format(team_number+1))
    
    
    # Zeitreihe Strom fuer eine typische Woche im Winter
    zeitreihen_el_Winter = pd.DataFrame()
    if sum(shortage_electricity.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Strombezug'] = shortage_electricity.flow[144:312]
    if sum(PV_el.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['PV'] = PV_el.flow[144:312]
    if sum(BHKW_el.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['BHKW_el'] = BHKW_el.flow[144:312]
    if sum(Stromspeicher_out.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Stromspeicher_out'] = abs(Stromspeicher_out.flow[144:312])
    if sum(el_demand.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Strombedarf'] = el_demand.flow[144:312]*(-1)
    if sum(Ueberschuss_el.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Stromueberschuss'] = Ueberschuss_el.flow[144:312]*(-1)
    if sum(Waermepumpe_el.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Waermepumpe_el'] = Waermepumpe_el.flow[144:312]*(-1)
    if sum(Stromspeicher_in.flow[144:312]) > 0.1:
        zeitreihen_el_Winter['Stromspeicher_in'] = abs(Stromspeicher_in.flow[144:312])*(-1)
    
    
    zeitreihen_el_Winter_sortiert=zeitreihen_el_Winter.reindex(zeitreihen_el_Winter.abs().sum().sort_values(ascending=False).index, axis=1)    
    zeitreihen_el_Winter_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Winter_{0}.csv'.format(team_number+1))    
    
    
    # Zeitreihe Strom fuer eine typische Woche im Fruehling
    zeitreihen_el_Fruehling = pd.DataFrame()
    if sum(shortage_electricity.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Strombezug'] = shortage_electricity.flow[2328:2496]
    if sum(PV_el.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['PV'] = PV_el.flow[2328:2496]
    if sum(BHKW_el.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['BHKW_el'] = BHKW_el.flow[2328:2496]
    if sum(Stromspeicher_out.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Stromspeicher_out'] = abs(Stromspeicher_out.flow[2328:2496])
    if sum(el_demand.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Strombedarf'] = el_demand.flow[2328:2496]*(-1)
    if sum(Ueberschuss_el.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Stromueberschuss'] = Ueberschuss_el.flow[2328:2496]*(-1)
    if sum(Waermepumpe_el.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Waermepumpe_el'] = Waermepumpe_el.flow[2328:2496]*(-1)
    if sum(Stromspeicher_in.flow[2328:2496]) > 0.1:
        zeitreihen_el_Fruehling['Stromspeicher_in'] = abs(Stromspeicher_in.flow[2328:2496])*(-1)
    
    zeitreihen_el_Fruehling_sortiert=zeitreihen_el_Fruehling.reindex(zeitreihen_el_Fruehling.abs().sum().sort_values(ascending=False).index, axis=1)    
    zeitreihen_el_Fruehling_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Fruehling_{0}.csv'.format(team_number+1))
    
    
    # Zeitreihe Strom fuer eine typische Woche im Sommer
    zeitreihen_el_Sommer = pd.DataFrame()
    if sum(shortage_electricity.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Strombezug'] = shortage_electricity.flow[5184:5352]
    if sum(PV_el.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['PV'] = PV_el.flow[5184:5352]
    if sum(BHKW_el.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['BHKW_el'] = BHKW_el.flow[5184:5352]
    if sum(Stromspeicher_out.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Stromspeicher_out'] = abs(Stromspeicher_out.flow[5184:5352])
    if sum(el_demand.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Strombedarf'] = el_demand.flow[5184:5352]*(-1)
    if sum(Ueberschuss_el.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Stromueberschuss'] = Ueberschuss_el.flow[5184:5352]*(-1)
    if sum(Waermepumpe_el.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Waermepumpe_el'] = Waermepumpe_el.flow[5184:5352]*(-1)
    if sum(Stromspeicher_in.flow[5184:5352]) > 0.1:
        zeitreihen_el_Sommer['Stromspeicher_in'] = abs(Stromspeicher_in.flow[5184:5352])*(-1)
    
    zeitreihen_el_Sommer_sortiert=zeitreihen_el_Sommer.reindex(zeitreihen_el_Sommer.abs().sum().sort_values(ascending=False).index, axis=1)    
    zeitreihen_el_Sommer_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Sommer_{0}.csv'.format(team_number+1))    

    
    # Zeitreihe Strom fuer eine typische Woche im Herbst
    zeitreihen_el_Herbst = pd.DataFrame()
    if sum(shortage_electricity.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Strombezug'] = shortage_electricity.flow[6863:7031]
    if sum(PV_el.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['PV'] = PV_el.flow[6863:7031]
    if sum(BHKW_el.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['BHKW_el'] = BHKW_el.flow[6863:7031]
    if sum(Stromspeicher_out.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Stromspeicher_out'] = abs(Stromspeicher_out.flow[6863:7031])
    if sum(el_demand.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Strombedarf'] = el_demand.flow[6863:7031]*(-1)
    if sum(Ueberschuss_el.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Stromueberschuss'] = Ueberschuss_el.flow[6863:7031]*(-1)
    if sum(Waermepumpe_el.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Waermepumpe_el'] = Waermepumpe_el.flow[6863:7031]*(-1)
    if sum(Stromspeicher_in.flow[6863:7031]) > 0.1:
        zeitreihen_el_Herbst['Stromspeicher_in'] = abs(Stromspeicher_in.flow[6863:7031])*(-1)
    
    zeitreihen_el_Herbst_sortiert=zeitreihen_el_Herbst.reindex(zeitreihen_el_Herbst.abs().sum().sort_values(ascending=False).index, axis=1)    
    zeitreihen_el_Herbst_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Herbst_{0}.csv'.format(team_number+1)) 
    
    
    # Jahreszeitreihe Waerme
    zeitreihen_th = pd.DataFrame()
    if sum(shortage_heat.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermebezug'] = shortage_heat.flow[0:number_of_time_steps]
    if sum(Sol_th.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Solarthermie'] = Sol_th.flow[0:number_of_time_steps]
    if sum(Gaskessel_th.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Gaskessel'] = Gaskessel_th.flow[0:number_of_time_steps]
    if sum(BHKW_th.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['BHKW_th'] = BHKW_th.flow[0:number_of_time_steps]
    if sum(Waermepumpe_th.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermepumpe_th'] = Waermepumpe_th.flow[0:number_of_time_steps]
    if sum(Waermespeicher_out.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermespeicher_out'] = abs(Waermespeicher_out.flow[0:number_of_time_steps])
    if sum(heat_demand.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermebedarf'] = heat_demand.flow[0:number_of_time_steps]*(-1)
    if sum(Ueberschuss_th.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermeueberschuss'] = Ueberschuss_th.flow[0:number_of_time_steps]*(-1)
    if sum(Waermespeicher_in.flow[0:number_of_time_steps]) > 0.1:
        zeitreihen_th['Waermespeicher_in'] = abs(Waermespeicher_in.flow[0:number_of_time_steps])*(-1)
    
    zeitreihen_th_sortiert=zeitreihen_th.reindex(zeitreihen_th.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_th_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_{0}.csv'.format(team_number+1))
    
    
    # Zeitreihe Waerme fuer eine typische Woche im Winter
    zeitreihen_th_Winter = pd.DataFrame()
    if sum(shortage_heat.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermebezug'] = shortage_heat.flow[144:312]
    if sum(Sol_th.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Solarthermie'] = Sol_th.flow[144:312]
    if sum(Gaskessel_th.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Gaskessel'] = Gaskessel_th.flow[144:312]
    if sum(BHKW_th.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['BHKW_th'] = BHKW_th.flow[144:312]
    if sum(Waermepumpe_th.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermepumpe_th'] = Waermepumpe_th.flow[144:312]
    if sum(Waermespeicher_out.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermespeicher_out'] = abs(Waermespeicher_out.flow[144:312])
    if sum(heat_demand.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermebedarf'] = heat_demand.flow[144:312]*(-1)
    if sum(Ueberschuss_th.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermeueberschuss'] = Ueberschuss_th.flow[144:312]*(-1)
    if sum(Waermespeicher_in.flow[144:312]) > 0.1:
        zeitreihen_th_Winter['Waermespeicher_in'] = abs(Waermespeicher_in.flow[144:312])*(-1)
    
    zeitreihen_th_Winter_sortiert=zeitreihen_th_Winter.reindex(zeitreihen_th_Winter.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_th_Winter_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Winter_{0}.csv'.format(team_number+1))
    
    
    # Zeitreihe Waerme fuer eine typische Woche im Fruehling
    zeitreihen_th_Fruehling = pd.DataFrame()
    if sum(shortage_heat.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermebezug'] = shortage_heat.flow[2328:2496]
    if sum(Sol_th.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Solarthermie'] = Sol_th.flow[2328:2496]
    if sum(Gaskessel_th.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Gaskessel'] = Gaskessel_th.flow[2328:2496]
    if sum(BHKW_th.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['BHKW_th'] = BHKW_th.flow[2328:2496]
    if sum(Waermepumpe_th.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermepumpe_th'] = Waermepumpe_th.flow[2328:2496]
    if sum(Waermespeicher_out.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermespeicher_out'] = abs(Waermespeicher_out.flow[2328:2496])
    if sum(heat_demand.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermebedarf'] = heat_demand.flow[2328:2496]*(-1)
    if sum(Ueberschuss_th.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermeueberschuss'] = Ueberschuss_th.flow[2328:2496]*(-1)
    if sum(Waermespeicher_in.flow[2328:2496]) > 0.1:
        zeitreihen_th_Fruehling['Waermespeicher_in'] = abs(Waermespeicher_in.flow[2328:2496])*(-1)
    
    zeitreihen_th_Fruehling_sortiert=zeitreihen_th_Fruehling.reindex(zeitreihen_th_Fruehling.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_th_Fruehling_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Fruehling_{0}.csv'.format(team_number+1))
    
    
    # Zeitreihe Waerme fuer eine typische Woche im Sommer
    zeitreihen_th_Sommer = pd.DataFrame()
    if sum(shortage_heat.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermebezug'] = shortage_heat.flow[5184:5352]
    if sum(Sol_th.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Solarthermie'] = Sol_th.flow[5184:5352]
    if sum(Gaskessel_th.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Gaskessel'] = Gaskessel_th.flow[5184:5352]
    if sum(BHKW_th.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['BHKW_th'] = BHKW_th.flow[5184:5352]
    if sum(Waermepumpe_th.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermepumpe_th'] = Waermepumpe_th.flow[5184:5352]
    if sum(Waermespeicher_out.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermespeicher_out'] = abs(Waermespeicher_out.flow[5184:5352])
    if sum(heat_demand.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermebedarf'] = heat_demand.flow[5184:5352]*(-1)
    if sum(Ueberschuss_th.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermeueberschuss'] = Ueberschuss_th.flow[5184:5352]*(-1)
    if sum(Waermespeicher_in.flow[5184:5352]) > 0.1:
        zeitreihen_th_Sommer['Waermespeicher_in'] = abs(Waermespeicher_in.flow[5184:5352])*(-1)
    
    zeitreihen_th_Sommer_sortiert=zeitreihen_th_Sommer.reindex(zeitreihen_th_Sommer.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_th_Sommer_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Sommer_{0}.csv'.format(team_number+1))
    

    # Zeitreihe Waerme fuer eine typische Woche im Herbst
    zeitreihen_th_Herbst = pd.DataFrame()
    if sum(shortage_heat.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermebezug'] = shortage_heat.flow[6863:7031]
    if sum(Sol_th.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Solarthermie'] = Sol_th.flow[6863:7031]
    if sum(Gaskessel_th.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Gaskessel'] = Gaskessel_th.flow[6863:7031]
    if sum(BHKW_th.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['BHKW_th'] = BHKW_th.flow[6863:7031]
    if sum(Waermepumpe_th.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermepumpe_th'] = Waermepumpe_th.flow[6863:7031]
    if sum(Waermespeicher_out.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermespeicher_out'] = abs(Waermespeicher_out.flow[6863:7031])
    if sum(heat_demand.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermebedarf'] = heat_demand.flow[6863:7031]*(-1)
    if sum(Ueberschuss_th.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermeueberschuss'] = Ueberschuss_th.flow[6863:7031]*(-1)
    if sum(Waermespeicher_in.flow[6863:7031]) > 0.1:
        zeitreihen_th_Herbst['Waermespeicher_in'] = abs(Waermespeicher_in.flow[6863:7031])*(-1)
    
    zeitreihen_th_Herbst_sortiert=zeitreihen_th_Herbst.reindex(zeitreihen_th_Herbst.abs().sum().sort_values(ascending=False).index, axis=1)
    zeitreihen_th_Herbst_sortiert.to_csv('../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Herbst_{0}.csv'.format(team_number+1))
    
    
    # ****************************************************************************
    # Graphische Darstellung - Definition der Farben
    # ****************************************************************************
    
    def make_color_list(keys):
        """Return list with colors for plots sorted by keys to make sure each
        component/technology appears in the same color in every plot
        (improves recognition)."""
        # Define colors
        col_options = ['darkblue',
                       'gold',
                       'blueviolet',
                       'darkred',
                       'darkgray',
                       'darkgreen',
                       'fuchsia',
                       'black',
                       'lightskyblue',
                       'darkorange',
                       'greenyellow',
                       'crimson',
                       'saddlebrown',
                       'indianred',
                       'lightgray',
                       'tan']
        
        col_list = []
        for k in keys:
            # Strom
            if k=='BHKW_el':
                col_list.append(col_options[0])
            elif k=='PV':
                col_list.append(col_options[1])
            elif k=='Stromspeicher_out':
                col_list.append(col_options[2])
            elif k == 'Strombezug':
                col_list.append(col_options[3])
            elif k == 'Strombedarf':
                col_list.append(col_options[4])
            elif k == 'Waermepumpe_el':
                col_list.append(col_options[5])           
            elif k == 'Stromspeicher_in':
                col_list.append(col_options[6])
            elif k == 'Stromueberschuss':
                col_list.append(col_options[7])            
                
            # Waerme
            elif k == 'BHKW_th':
                col_list.append(col_options[8])
            elif k == 'Solarthermie':
                col_list.append(col_options[9])
            elif k == 'Waermepumpe_th':
                col_list.append(col_options[10])
            elif k == 'Gaskessel':
                col_list.append(col_options[11])
            elif k == 'Waermespeicher_out':
                col_list.append(col_options[12])
            elif k == 'Waermebezug':
                col_list.append(col_options[13])
            elif k == 'Waermebedarf':
                col_list.append(col_options[14])
            elif k == 'Waermespeicher_in':
                col_list.append(col_options[15])
            elif k == 'Waermeueberschuss':
                col_list.append(col_options[7])
        return col_list
    
    
    # ****************************************************************************
    # Graphische Darstellung Strombus
    # ****************************************************************************
     
    filename5 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_{0}.csv".format(team_number+1)
    param_df5 = pd.read_csv(filename5, index_col=0, encoding= 'unicode_escape')
    if plt is not None:
        # Get list with colors sorted for this DataFrame
        color_list = make_color_list(param_df5.keys())
        param_df5.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Stromflüsse', size=25)
        plt.ylabel('Stromflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df5.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels, bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 8760, step=730), calendar.month_name[1:13],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Stromflüsse_{0}.png'.format(team_number+1), dpi=150,
        bbox_inches='tight')
    
    
    # typische Woche Winter (07.01.2019-13.01.2019)
    filename6 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Winter_{0}.csv".format(team_number+1)
    param_df6 = pd.read_csv(filename6, index_col=0, encoding= 'unicode_escape')
    if plt is not None:
        color_list = make_color_list(param_df6.keys())
        param_df6.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Stromflüsse (07.01-13.01.2019)', size=25)
        plt.ylabel('Stromflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df6.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels, bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Stromflüsse_Winter_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight') 
    
    
    # typische Woche Fruehling (08.04.2019-14.04.2019)
    filename7 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Fruehling_{0}.csv".format(team_number+1)
    param_df7 = pd.read_csv(filename7, index_col=0, encoding= 'unicode_escape')
    if plt is not None:
        color_list = make_color_list(param_df7.keys())
        param_df7.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Stromflüsse (08.04-14.04.2019)', size=25)
        plt.ylabel('Stromflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df7.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels, bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Stromflüsse_Fruehling_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight') 
        
        
    # typische Woche Sommer (05.08.2019-11.08.2019)
    filename8 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Sommer_{0}.csv".format(team_number+1)
    param_df8 = pd.read_csv(filename8, index_col=0, encoding= 'unicode_escape')    
    if plt is not None:
        color_list = make_color_list(param_df8.keys())
        param_df8.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Stromflüsse (05.08.-11.08.2019)', size=25)
        plt.ylabel('Stromflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df8.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels, bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Stromflüsse_Sommer_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')
    
    
    # typische Woche Herbst (14.10.2019-20.10.2019)
    filename9 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_el_Herbst_{0}.csv".format(team_number+1)
    param_df9 = pd.read_csv(filename9, index_col=0, encoding= 'unicode_escape')    
    if plt is not None:
        color_list = make_color_list(param_df9.keys())
        param_df9.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Stromflüsse (14.10.-20.10.2019)', size=25)
        plt.ylabel('Stromflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df9.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels, bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Stromflüsse_Herbst_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')
        
        
    # ****************************************************************************
    # Graphische Darstellung Waermebus
    # ****************************************************************************
    
    filename10 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_{0}.csv".format(team_number+1)
    param_df10 = pd.read_csv(filename10, index_col=0, encoding= 'unicode_escape')
    if plt is not None:
        color_list = make_color_list(param_df10.keys())
        param_df10.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Wärmeflüsse', size=25)
        plt.ylabel('Wärmeflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df10.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels,bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
        prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 8760, step=730), calendar.month_name[1:13],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Wärmeflüsse_{0}.png'.format(team_number+1), dpi=150, bbox_inches='tight')
    
    
    # typische Woche Winter (07.01.2019-13.01.2019)
    filename11 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Winter_{0}.csv".format(team_number+1)
    param_df11 = pd.read_csv(filename11, index_col=0, encoding= 'unicode_escape')   
    if plt is not None:
        color_list = make_color_list(param_df11.keys())
        param_df11.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Wärmeflüsse (07.01-13.01.2019)', size=25)
        plt.ylabel('Wärmeflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df11.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels,bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Wärmeflüsse_Winter_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')
        
        
    # typische Woche Fruehling (08.04.2019-14.04.2019)
    filename12 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Fruehling_{0}.csv".format(team_number+1)
    param_df12 = pd.read_csv(filename12, index_col=0, encoding= 'unicode_escape')   
    if plt is not None:
        color_list = make_color_list(param_df12.keys())
        param_df12.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Wärmeflüsse (08.04-14.04.2019)', size=25)
        plt.ylabel('Wärmeflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df12.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels,bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Wärmeflüsse_Fruehling_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')  
        
        
    # typische Woche Sommer (05.08.2019-11.08.2019)
    filename13 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Sommer_{0}.csv".format(team_number+1)
    param_df13 = pd.read_csv(filename13, index_col=0, encoding= 'unicode_escape')     
    if plt is not None:
        color_list = make_color_list(param_df13.keys())
        param_df13.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Wärmeflüsse (05.08.-11.08.2019)', size=25)
        plt.ylabel('Wärmeflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df13.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels,bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Wärmeflüsse_Sommer_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')
    

    # typische Woche Herbst (14.10.2019-20.10.2019)
    filename14 = Path(__file__).parent / "../data_postprocessed/data_postprocessed_{0}/Zeitreihe_th_Herbst_{0}.csv".format(team_number+1)
    param_df14 = pd.read_csv(filename14, index_col=0, encoding= 'unicode_escape')     
    if plt is not None:
        color_list = make_color_list(param_df14.keys())
        param_df14.plot(kind='area', stacked=True, color=color_list, linewidth=0)
        plt.title('Wärmeflüsse (14.10.-20.10.2019)', size=25)
        plt.ylabel('Wärmeflüsse [kWh/h]', size=25)
        current1 = pd.DataFrame(list(plt.gca().get_legend_handles_labels()))
        current=current1.transpose()
        sorter=param_df14.sum().sort_values(ascending=False).index.tolist()
        sorterIndex = dict(zip(sorter,range(len(sorter))))
        current['Sortiere']= current[1].map(sorterIndex)
        current.sort_values(by='Sortiere', inplace=True)
        new_handles = current[0]
        new_labels = current[1]
        plt.legend(new_handles, new_labels,bbox_to_anchor=(1.02,1), loc='upper left', borderaxespad=0,
                   prop={'size':25})
        plt.yticks(size=25)
        plt.xticks(np.arange(0, 168, step=24), calendar.day_name[0:7],
        rotation=45, size=25)
        figure = plt.gcf()
        figure.set_size_inches(30,15)
        plt.savefig('../results/results_{0}/Wärmeflüsse_Herbst_{0}.png'.format(team_number+1), dpi=150,
                    bbox_inches='tight')
        