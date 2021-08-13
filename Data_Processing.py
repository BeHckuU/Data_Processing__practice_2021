import json
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.stats import norm
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Information about files and constants 

fill = '7321'
format = '.json'
detector_names = ['BCM1FPCVD','HFET','HFOC']
frev = 11245 # Hz

# Calibration constants (in μb):

sigma_vis_BCM1FPCVD = 210.3
sigma_vis_HFET = 2503.6
sigma_vis_HFOC = 805.9
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Functions

# File openning

def open_file(fill,format,detector):
    
    with open('Rates_'+ detector + '_' + fill + format) as file_1:
        file = json.load(file_1)
    
    return file

# Obtaining data from files

def get_data(file):
    Rates_Scan_1 = np.zeros((len(file['Scan_1']),len(file['Scan_1'][0]['Rates'])))
    RateErrs_Scan_1 = np.zeros((len(file['Scan_1']),len(file['Scan_1'][0]['RateErrs'])))
    Rates_Scan_2 = np.zeros((len(file['Scan_2']),len(file['Scan_1'][0]['Rates'])))
    RateErrs_Scan_2 = np.zeros((len(file['Scan_2']),len(file['Scan_1'][0]['RateErrs'])))
    
    for i in range(len(file['Scan_1'])):
        k = 0
        for key in file['Scan_1'][i]['Rates']:
            Rates_Scan_1[i][k] = file['Scan_1'][i]['Rates'][key]
            RateErrs_Scan_1[i][k] = file['Scan_1'][i]['RateErrs'][key]
            k += 1
    for i in range(len(file['Scan_2'])):
        k = 0
        for key in file['Scan_2'][i]['Rates']:
            Rates_Scan_2[i][k] = file['Scan_2'][i]['Rates'][key]
            RateErrs_Scan_2[i][k] = file['Scan_2'][i]['RateErrs'][key]
            k += 1
    return np.vstack((Rates_Scan_1, Rates_Scan_2)), np.vstack((RateErrs_Scan_1, RateErrs_Scan_2))

# SBIL calculation

def SBIL_calculate(Rates,Errs,sigma_vis,frev):
    
    SBIL = frev/sigma_vis * Rates
    SBIL_Errs = frev/sigma_vis * Errs
    
    return SBIL, SBIL_Errs

# SBIL ratio calculation

def ratio_calculate(L,Lref,L_errs,Lref_errs):
    ratio = L/Lref
    ratio_errs = np.power((np.power((L_errs/Lref),2) + ((np.power(L,2)*np.power(Lref_errs,2))/(np.power(Lref,4)))),0.5)
    # for i in range(len(L)):
    #     for j in range(len(L[i])):
    #         if L == 0:        
    #             ratio = L/Lref
    #             ratio_errs = np.power((np.power((L_errs/Lref),2) + ((np.power(L,2)*np.power(Lref_errs,2))/(np.power(Lref,4)))),0.5)
        
    return ratio, ratio_errs
    
# Linear approximation coefficients calculation

def coefficients_calculate(SBIL_ref_luminometer, Ratio):
    
    x_SBIL = []
    y_Ratio = []
    coefficients = []
    p2 = []
    
    for i in range(len(SBIL_ref_luminometer[0,:])):
        coefficients.append(np.polyfit([j[i] for j in SBIL_ref_luminometer if j[i] > 1],[j[i] for j in Ratio] if , 1))
        p2.append(coefficients[i][0])
    return coefficients, p2

# SBIL ratio and linear approximation visualisation 

def visualisation(file, SBIL_ref_luminometer, Ratio, Ratio_Errs, coefficients, Luminometer_Name = str, Ref_Luminometer_Name = str, bunch_number = str):
    
    Keys = dict(zip(list(file['Scan_1'][0]['Rates'].keys()), list(range(0, len(coefficients)))))
    print(Keys[bunch_number])
    print(max(SBIL_ref_luminometer[:,Keys[bunch_number]]))
    fig, ax = plt.subplots()
    ax.set_xlabel('SBIL ' + Ref_Luminometer_Name + ', Hz/μb', fontsize=12)        
    ax.set_ylabel('Ratio ' + Luminometer_Name, fontsize=12)
    ax.grid(which = "major", linewidth = 1)
    x = np.linspace(0,max(SBIL_ref_luminometer[:,Keys[bunch_number]])+0.5,100)
    p = np.poly1d(coefficients[Keys[bunch_number]])
    ax.errorbar([j[Keys[bunch_number]] for j in SBIL_ref_luminometer], [j[Keys[bunch_number]] for j in Ratio],[j[Keys[bunch_number]] for j in Ratio_Errs], fmt = 'ro')
    ax.plot(x, p(x))
    plt.show()
    
    return 

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Openning files

file_HFOC = open_file(fill,format,detector_names[2])
file_HFET = open_file(fill,format,detector_names[1])
file_BCM1FPCVD = open_file(fill,format,detector_names[0])

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Getting rates and rate errors data

HFOC_Rates, HFOC_RateErrs = get_data(file_HFOC)
HFET_Rates, HFET_RateErrs = get_data(file_HFET)
BCM1FPCVD_Rates, BCM1FPCVD_RateErrs = get_data(file_BCM1FPCVD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Calculation of Luminocity, luminocity error and ratio

SBIL_HFOC, SBIL_Errs_HFOC = SBIL_calculate(HFOC_Rates, HFOC_RateErrs, sigma_vis_HFOC, frev)
SBIL_HFET, SBIL_Errs_HFET = SBIL_calculate(HFET_Rates, HFET_RateErrs, sigma_vis_HFET, frev)
SBIL_BCM1FPCVD, SBIL_Errs_BCM1FPCVD = SBIL_calculate(BCM1FPCVD_Rates, BCM1FPCVD_RateErrs, sigma_vis_BCM1FPCVD, frev)

Ratio_HFET, Ratio_Errs_HFET = ratio_calculate(SBIL_HFET, SBIL_HFOC, SBIL_Errs_HFET, SBIL_Errs_HFOC)
Ratio_BCM1FPCVD, Ratio_Errs_BCM1FPCVD = ratio_calculate(SBIL_BCM1FPCVD, SBIL_HFOC, SBIL_Errs_BCM1FPCVD, SBIL_Errs_HFOC)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Coefficients calculation
coefficients_BCM1FPCVD, p2_BCM1FPCVD = coefficients_calculate(SBIL_HFOC, Ratio_BCM1FPCVD)
coefficients_HFET, p2_HFET = coefficients_calculate(SBIL_HFOC, Ratio_HFET)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Nonlinarity visualisation

visualisation(file_HFET, SBIL_HFET, Ratio_HFET, Ratio_Errs_HFET, coefficients_HFET, detector_names[1] , detector_names[2] , '604')

Dist_BCM1FPCVD = sns.distplot(p2_BCM1FPCVD, label = 'Distribution', kde = False, fit = norm, axlabel = 'p2')
plt. show()
# keys_1 = list(file_BCM1FPCVD['Scan_1'][0]['Rates'].keys())
# key_int = []
# keys_range = []
# p2_range = []
# for i in range (len(keys_1)):
#     key_int.append(int(keys_1[i]))
#     if  key_int[i] < 600:
#         keys_range.append(key_int[i]) 
#         p2_range.append(p2_BCM1FPCVD[i])
# plt.scatter(keys_range,p2_BCM1FPCVD)
# plt.show()