import json
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats
from scipy import odr
import os
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Information about files and constants 

fill = '7314'
format = '.json'
detector_names = ['BCM1FPCVD','HFET','HFOC']
frev = 11245 # Hz
direct = os.listdir(path = 'Rates')
# directories = []
fill_i = None
late_early = []
dir_keys = []
directories_early = []
directories_late = []
for i in range(len(direct)):
    
    if i % 2 == 0:
        directories_early.append(direct[i])
        dir_keys.append(direct[i][0:4])
    else:
        directories_late.append(direct[i])
directories = {'Early': dict(zip(dir_keys, directories_early)), 'Late': dict(zip(dir_keys, directories_late))}

    
    
    
# Calibration constants (in μb):

sigma_vis_BCM1FPCVD = 210.3
sigma_vis_HFET = 2503.6
sigma_vis_HFOC = 805.9
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Functions

# Fitting function

def f(B,x):
    
    return B[0]*x + B[1]

linear = odr.Model(f)

# File openning

def open_file(fill,format,detector,directory):
    
    with open('Rates/'+ directory +'/Rates_'+ detector + '_' + fill + format) as file_1:
        file = json.load(file_1)
    
    return file

# Getting information from file

def get_data(file):

    Keys = list(file['Scan_1'][0]['Rates'].keys())
    
    Rates_1 = []
    Rates_2 = []
    RateErrs_1 = []
    RateErrs_2 = []
    
    for i in range(len(Keys)):
        Rates = []
        RateErrs = []
        for j in range(len(file['Scan_1'])):
            Rates.append(file['Scan_1'][j]['Rates'][Keys[i]])
            RateErrs.append(file['Scan_1'][j]['RateErrs'][Keys[i]])
        Rates_1.append(Rates)
        RateErrs_1.append(RateErrs)
        
    for i in range(len(Keys)):
        Rates = []
        RateErrs = []
        for j in range(len(file['Scan_2'])):
            Rates.append(file['Scan_2'][j]['Rates'][Keys[i]])
            RateErrs.append(file['Scan_2'][j]['RateErrs'][Keys[i]])
        Rates_2.append(Rates)
        RateErrs_2.append(RateErrs)
        
    for i in range(len(Rates_1)):
        Rates_1[i].extend(Rates_2[i])
        RateErrs_1[i].extend(RateErrs_2[i])
        
    Total_Rates = dict(zip(Keys,Rates_1))
    Total_Errs = dict(zip(Keys,RateErrs_1))
                        
    return Total_Rates, Total_Errs

# SBIL and SBIL errors calculation

def SBIL_calc(Total_Rates, Total_Errs, frev, sigma_vis):
    
    
    SBIL = []
    SBIL_Errs = [] 
    Keys = Total_Rates.keys()
    
    for key in Total_Rates:
        SBIL_i = []
        SBIL_Errs_i = []
        for i in range(len(Total_Rates[key])):
            SBIL_i.append(Total_Rates[key][i] * frev/sigma_vis)
            SBIL_Errs_i.append(Total_Errs[key][i] * frev/sigma_vis)
        SBIL.append(SBIL_i)
        SBIL_Errs.append(SBIL_Errs_i)
    Total_SBIL = dict(zip(Keys, SBIL))
    Total_SBIL_Errs = dict(zip(Keys, SBIL_Errs))
    return Total_SBIL, Total_SBIL_Errs

# Ratio and ratio error calculation

def Ratio_calc(L, Lref, L_Errs, Lref_Errs):
    
    Keys = L.keys()
    Ratio = []
    Ratio_Errs = []
    X_Lref = []
    X_Lref_Errs = []
    
    for key in L:
        Ratio_i = []
        Ratio_Errs_i = []
        X_Lref_i = []
        X_Lref_i_Errs = []
        for i in range(len(L[key])):
            if L[key][i] > 1 and Lref[key][i] > 1:
                Ratio_i.append(L[key][i]/Lref[key][i])
                Ratio_Errs_i.append(np.power((np.power((L_Errs[key][i]/Lref[key][i]),2) + 
                                              ((np.power(L[key][i],2)*np.power(Lref_Errs[key][i],2))
                                               /(np.power(Lref[key][i],4)))),0.5))
                X_Lref_i.append(Lref[key][i])
                X_Lref_i_Errs.append(Lref_Errs[key][i])
                
        Ratio.append(Ratio_i)
        Ratio_Errs.append(Ratio_Errs_i)
        X_Lref.append(X_Lref_i)
        X_Lref_Errs.append(X_Lref_i_Errs)
        
    Total_Ratio = dict(zip(Keys,Ratio))
    Total_Ratio_Errs = dict(zip(Keys,Ratio_Errs))
    Total_X_Lref = dict(zip(Keys,X_Lref))
    Total_X_Lref_Errs = dict(zip(Keys,X_Lref_Errs))
    
    return Total_Ratio, Total_Ratio_Errs, Total_X_Lref, Total_X_Lref_Errs

# Linear approximation coefficients and errors calculation (ODR method)

def coefficients_calc(Total_Ratio, Total_X_Lref, Total_Ratio_Errs, Total_Lref_Errs):
    
    Keys = Total_Ratio.keys()
    coefficients = []
    p2_i = []
    p2_Errs_i = []
    for key in Total_Ratio:
        
        if len(Total_Ratio[key]) >= 3 and len(Total_X_Lref[key]) >= 3:
            mydata = odr.RealData(Total_X_Lref[key], Total_Ratio[key], 
                                  Total_Lref_Errs[key], Total_Ratio_Errs[key])
            myodr = odr.ODR(mydata, linear, beta0=[0,0])
            myoutput = myodr.run()
            coefficients.append(myoutput.beta)
            p2_i.append(myoutput.beta[0])
            p2_Errs_i.append(myoutput.sd_beta[0])
        else:
            coefficients.append(None)
            p2_i.append(None)
            p2_Errs_i.append(None)
        
    Total_coefficients = dict(zip(Keys, coefficients))
    p2 = dict(zip(Keys,p2_i))
    p2_Errs = dict(zip(Keys, p2_Errs_i))
    
    return Total_coefficients, p2, p2_Errs
    
# Visualisation of SBIL ratio and linear approximation

def visualisation(Total_Ratio, Total_Ratio_Errs, Total_X_Lref, Errs, coefficients, 
                  Luminometer_Name = str, Ref_Luminometer_Name = str, bunch_number = str):
    
    fig, ax = plt.subplots()
    ax.set_xlabel('SBIL ' + Ref_Luminometer_Name + ', Hz/μb ' + 
                  '| Bunch:' + bunch_number, fontsize=12)        
    ax.set_ylabel('Ratio ' + Luminometer_Name , fontsize=12)
    ax.grid(which = "major", linewidth = 1)
    x = np.linspace(min(Total_X_Lref[bunch_number])-0.1, max(Total_X_Lref[bunch_number])+0.1,100)
    y = x * coefficients[bunch_number][0] + coefficients[bunch_number][1]
    ax.errorbar(Total_X_Lref[bunch_number], Total_Ratio[bunch_number], 
                Total_Ratio_Errs[bunch_number], Errs[bunch_number],
                fmt = 'rs', linestyle = 'None',
                ecolor = 'k', elinewidth = 0.8, 
                capsize = 2, capthick = 0.8)
    ax.plot(x, y ,'k')
    plt.show()
    
    return

# Visualization of non-linearity calculated in range of bunches

def Bunches_and_p2(From, To, p2, p2_Errs, detector_name = str):
    
    number = []
    p2_part = []
    p2_Errs_part = []
    keys_part = []
    
    for i in range(From, To + 1):
        number.append(str(i))
    
    for i in number:
        for key in p2:
            if i == key and p2[key] != None:
                keys_part.append(int(key))
                p2_part.append(p2[key])
                p2_Errs_part.append(p2_Errs[key])
            
    fig = plt.figure(figsize = (20,8))
    plt.xlabel('Bunches [Fill: ' + fill +']' , fontsize=12)        
    plt.ylabel(detector_name +' Non-linearity Hz/μb' , fontsize=12)
    ax = fig.add_subplot(1,1,1)
    ax.grid(which="major", linewidth = 1)
    ax.errorbar(keys_part, p2_part, p2_Errs_part, fmt = 'rs', markersize = 4 , 
                linestyle = 'None', ecolor = 'k', elinewidth = 0.6, 
                capsize = 2, capthick = 0.8)
    plt.show()

    return

# Visualization of non-linearity distribution

def Histogram(p2_dict, p2_Errs_dict, detector_name = str):
    
    p2 = []
    p2_Errs = []
    for key in p2_dict:
        if p2_dict[key] != None:
            p2.append(p2_dict[key])
            p2_Errs.append(p2_Errs_dict[key])
    # if detector_name == 'HFET':
    #     x_text = -0.0025
    #     y_text = 500
    # if detector_name == 'BCM1FPCVD':
    #     x_text = -0.0075
    #     y_text = 150
    # p2_mean = str(round(np.mean(p2),8))
    mean_p2 = str(round(np.mean(p2),8))
    mean_Err_p2 = str(round(np.sum(p2_Errs)/np.sqrt(len(p2_Errs)),8))
    plt.figure()
    plt.text(0.03,0.97, '<p2> = ' + mean_p2 + ' ± ' + mean_Err_p2, bbox=dict(alpha=0.5), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel(detector_name + ' Nonlinearity Hz/μb  ['+ fill + ']')
    plt.ylabel('Counts')
    sns.distplot(p2, kde = False, fit = stats.norm)
    # plt.text(x_text, y_text, '<p2> = ' + p2_mean)
    plt.show()
    
    return np.mean(p2), np.sum(p2_Errs)/np.sqrt(len(p2_Errs) * (len(p2_Errs)-1))

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Openning files

file_HFOC = open_file(fill,format,detector_names[2], directories['Early'][fill])
file_HFET = open_file(fill,format,detector_names[1], directories['Early'][fill])
file_BCM1FPCVD = open_file(fill,format,detector_names[0], directories['Early'][fill])

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Getting data

Total_Rates_HFOC, Total_Errs_HFOC = get_data(file_HFOC)
Total_Rates_HFET, Total_Errs_HFET = get_data(file_HFET)
Total_Rates_BCM1FPCVD, Total_Errs_BCM1FPCVD = get_data(file_BCM1FPCVD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SBIL and SBIL errors calculation

Total_SBIL_HFOC, Total_SBIL_Errs_HFOC = SBIL_calc(Total_Rates_HFOC, 
                                                  Total_Errs_HFOC, frev, sigma_vis_HFOC)
Total_SBIL_HFET, Total_SBIL_Errs_HFET = SBIL_calc(Total_Rates_HFET, 
                                                  Total_Errs_HFET, frev, sigma_vis_HFET)
Total_SBIL_BCM1FPCVD, Total_SBIL_Errs_BCM1FPCVD = SBIL_calc(Total_Rates_BCM1FPCVD, 
                                                            Total_Errs_BCM1FPCVD, frev, 
                                                            sigma_vis_BCM1FPCVD)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ratio calculation (relatively to HFOC)

Total_Ratio_HFET, Total_Ratio_Errs_HFET, Total_X_Lref_HFET, Total_X_Lref_Errs_HFET = Ratio_calc(Total_SBIL_HFET, 
                                                                        Total_SBIL_HFOC, Total_SBIL_Errs_HFET, 
                                                                        Total_SBIL_Errs_HFOC)
Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD, Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD = Ratio_calc(Total_SBIL_BCM1FPCVD, 
                                                                                       Total_SBIL_HFOC, 
                                                                                       Total_SBIL_Errs_BCM1FPCVD, 
                                                                                       Total_SBIL_Errs_HFOC)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Approximation coefficients calculation

Total_Coefficients_HFET, p2_HFET, p2_Errs_HFET = coefficients_calc(Total_Ratio_HFET, Total_X_Lref_HFET, 
                                                                   Total_Ratio_Errs_HFET, Total_X_Lref_Errs_HFET)
Total_Coefficients_BCM1FPCVD, p2_BCM1FPCVD, p2_Errs_BCM1FPCVD = coefficients_calc(Total_Ratio_BCM1FPCVD, 
                                                                                  Total_X_Lref_BCM1FPCVD, 
                                                                                  Total_Ratio_Errs_BCM1FPCVD, 
                                                                                  Total_X_Lref_Errs_BCM1FPCVD)



visualisation(Total_Ratio_HFET, Total_Ratio_Errs_HFET, 
              Total_X_Lref_HFET, Total_X_Lref_Errs_HFET,  Total_Coefficients_HFET, 'HFET', 'HFOC', '344' )
visualisation(Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD,
              Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD, Total_Coefficients_BCM1FPCVD, 'BCM1FPCVD', 'HFOC', '344' )


Bunches_and_p2(0, 3000, p2_HFET, p2_Errs_HFET, detector_names[1])
Bunches_and_p2(0, 3000, p2_BCM1FPCVD, p2_Errs_BCM1FPCVD, detector_names[0])


p2_mean_HFET, p2_mean_HFET_Err = Histogram(p2_HFET, p2_Errs_HFET, detector_names[1])
p2_mean_BCM1FPCVD, p2_mean_BCM1FPCVD_Err = Histogram(p2_BCM1FPCVD, p2_Errs_BCM1FPCVD, detector_names[0])