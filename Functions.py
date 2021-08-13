import json
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats
from scipy import odr
import csv

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Functions

# Fitting function

def f(B,x):
    
    return B[0]*x + B[1]

linear = odr.Model(f)

# CSV-oppening

def CSV_open(file_name):
    fills = []
    weights = []
    with open(file_name) as file_1:
        reader = csv.DictReader(file_1)
        for row in reader:
            fills.append(row['Fill'])
            weights.append(float(row['Rec_Lumi']))
        
    weights_sum = sum(weights)
    weights_dict = dict(zip(fills, weights))
    
    return weights_dict, weights_sum

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

# CSV bunch write

def CSV_bunch_write(coefficients_HFET, coefficients_Errs_HFET, coefficients_BCM1FPCVD, 
                    coefficients_Errs_BCM1FPCVD, Detector_name, early_late, fill_i):
    
    data = [['Detector_name', 'bunch', 'p0', 'p1', 'p0 Error', 'p1 Error']]
    
    for key in coefficients_HFET:
        data_i = []
        data_i.append(Detector_name[1])
        data_i.append(key)
        if coefficients_HFET[key][0] != None and coefficients_HFET[key][1] != None:
            data_i.append(coefficients_HFET[key][1])
            data_i.append(coefficients_HFET[key][0])
            data_i.append(coefficients_Errs_HFET[key][1])
            data_i.append(coefficients_Errs_HFET[key][0])
        else:
            data_i.append('None')
            data_i.append('None')
            data_i.append('None')
            data_i.append('None')
        data.append((data_i))
        
    for key in coefficients_BCM1FPCVD:
        data_i = []
        data_i.append(Detector_name[0])
        data_i.append(key)
        if coefficients_BCM1FPCVD[key][0] != None and coefficients_BCM1FPCVD[key][1] != None:
            data_i.append(coefficients_BCM1FPCVD[key][1])
            data_i.append(coefficients_BCM1FPCVD[key][0])
            data_i.append(coefficients_Errs_BCM1FPCVD[key][1])
            data_i.append(coefficients_Errs_BCM1FPCVD[key][0])
        else:
            data_i.append('None')
            data_i.append('None')
            data_i.append('None')
            data_i.append('None')
        data.append((data_i))
    
    with open('CSV_Files/Bunches_coefficients/' + early_late + '/Coefficients_'+fill_i +'.csv', 'w', newline = '') as file_2:
        writer = csv.writer(file_2)
        writer.writerows(data)
    
    return

# CSV fill write

def CSV_fill_write(p1_early, p1_Errs_early, p1_late, p1_Errs_late, dir_keys, detector_name):
    
    data = [['Fill', '<p1> ' + detector_name + ' (Early)', 
             '<p1> '+ detector_name + ' Error (Early)', 
             '<p1> '+ detector_name + ' (Late)', 
             '<p1> '+ detector_name + ' Error (Late)']]
    
    for i in range(len(dir_keys)):
        data_i = []
        data_i.append(dir_keys[i])
        data_i.append(p1_early[i])
        data_i.append(p1_Errs_early[i])
        data_i.append(p1_late[i])
        data_i.append(p1_Errs_late[i])
        data.append((data_i))
    
    with open('CSV_Files/Fills_nonlinearity/' + detector_name + '/Fills_nonlinearity.csv', 'w', newline = '') as file_3:
        writer = csv.writer(file_3)
        writer.writerows(data)
    
    return

# File openning

def open_file(fill_i,format,detector,directory):
    
    with open('Rates/'+ directory +'/Rates_'+ detector + '_' + fill_i + format) as file_1:
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
    p1_i = []
    p1_Errs_i = []
    coefficient_Errs = []
    for key in Total_Ratio:
        
        if len(Total_Ratio[key]) >= 3 and len(Total_X_Lref[key]) >= 3:
            mydata = odr.RealData(Total_X_Lref[key], Total_Ratio[key], 
                                  Total_Lref_Errs[key], Total_Ratio_Errs[key])
            myodr = odr.ODR(mydata, linear, beta0=[0,0])
            myoutput = myodr.run()
            coefficients.append(myoutput.beta)
            p1_i.append(myoutput.beta[0])
            p1_Errs_i.append(myoutput.sd_beta[0])
            coefficient_Errs.append(myoutput.sd_beta)
        else:
            coefficients.append(np.array([None,None]))
            p1_i.append(None)
            p1_Errs_i.append(None)
            coefficient_Errs.append(np.array([None, None]))
    Total_coefficients = dict(zip(Keys, coefficients))
    Total_coefficient_Errs = dict(zip(Keys, coefficient_Errs))
    p1 = dict(zip(Keys,p1_i))
    p1_Errs = dict(zip(Keys, p1_Errs_i))
    
    return Total_coefficients, Total_coefficient_Errs, p1, p1_Errs
    
# Visualisation of SBIL ratio and linear approximation

def visualisation(Total_Ratio, Total_Ratio_Errs, Total_X_Lref, Errs, coefficients, coefficients_Errs, 
                  Luminometer_Name = str, Ref_Luminometer_Name = str, bunch_number = str):
    
    p1 = str(toFixed(coefficients[bunch_number][0],8))
    p1_Err = str(toFixed(coefficients_Errs[bunch_number][0],8))
    p0 = str(toFixed(coefficients[bunch_number][1],8))
    p0_Err = str(toFixed(coefficients_Errs[bunch_number][1],8))
    
    fig, ax = plt.subplots()
    ax.set_xlabel('SBIL ' + Ref_Luminometer_Name + ', Hz/μb ' + 
                  '| Bunch:' + bunch_number, fontsize=12)        
    ax.set_ylabel('Ratio ' + Luminometer_Name , fontsize=12)
    ax.grid(which = "major", linewidth = 1)
    plt.text(0.97,0.97, 'p1 = ' + p1 + ' ± ' + p1_Err +'\np0 = ' + p0 + ' ± ' + p0_Err, bbox=dict(alpha=1, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="right")
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

def Bunches_and_p1(From, To, p1, p1_Errs, p1_mean, p1_mean_Err, detector_name = str, early_late = str, fill_i = str, save = bool):
    
    number = []
    p1_part = []
    p1_Errs_part = []
    keys_part = []
    
    for i in range(From, To + 1):
        number.append(str(i))
    
    for i in number:
        for key in p1:
            if i == key and p1[key] != None:
                keys_part.append(int(key))
                p1_part.append(p1[key])
                p1_Errs_part.append(p1_Errs[key])
     
    mean_p1_str = str(round(p1_mean,8))    
    mean_Err_str = str(toFixed(p1_mean_Err,8))
    
    fig = plt.figure(figsize = (20,8))
    plt.text(0.03,0.97, '<p1> = ' + mean_p1_str + ' ± ' + mean_Err_str, bbox=dict(alpha=0.75, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel('BCID [Fill: ' + fill_i +']' , fontsize=12)        
    plt.ylabel(detector_name +' Non-linearity (Hz/μb)' , fontsize=12)
    ax = fig.add_subplot(1,1,1)
    ax.grid(which="major", linewidth = 1)
    ax.errorbar(keys_part, p1_part, p1_Errs_part, fmt = 'rs', markersize = 4 , 
                linestyle = 'None', ecolor = 'k', elinewidth = 0.6, 
                capsize = 2, capthick = 0.8)
    plt.show()
    if save == True:
        fig.savefig('Figures/Bunches_non-linearity/'+ early_late +'/Bunches_non-linearity_'+ detector_name + '_' + fill_i)
    
    return

# Visualization of non-linearity distribution

def Histogram(p1_dict, p1_Errs_dict, detector_name = str, early_late = str, fill_i = str, save = bool):
    
    p1 = []
    p1_Errs = []
    for key in p1_dict:
        if p1_dict[key] != None:
            p1.append(p1_dict[key])
            p1_Errs.append(p1_Errs_dict[key])
            
    mean_p1 = np.mean(p1)
    # sko_i = []
    
    # for i in range(len(p1)):  
    #     sko_i.append(np.power((p1[i] - mean_p1),2))
    
    
    
    mean_p1 = np.mean(p1)
    mean_p1_str = str(round(mean_p1,8))
    # mean_sko = float(np.sqrt(np.sum(sko_i))/np.sqrt(len(p1)*(len(p1)-1)))
    mean_sko = np.std(p1)
    mean_Err_p1 = np.sqrt(np.power(mean_sko,2) + np.power(np.mean(p1_Errs),2))
    
    mean_Err_str = str(toFixed(mean_Err_p1,8))
    # mean_Err_str = str(round(mean_Err_p1,8))
    fig = plt.figure()
    plt.text(0.03,0.97, '<p1> = ' + mean_p1_str + ' ± ' + mean_Err_str, bbox=dict(alpha=0.75, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel(detector_name + ' Nonlinearity Hz/μb  [fill:'+ fill_i + ']')
    plt.ylabel('Counts')
    sns.distplot(p1, kde = False, fit = stats.norm)
    plt.show()
    if save == True:
        fig.savefig('Figures/Non-linearity_distribution/'+ early_late +'/Non-linearity_distribution'+ detector_name + '_' + fill_i)
    
    return mean_p1, mean_Err_p1

# Grubbs test

def Grubbs(p1_dict, p1_Errs_dict):

    p1 = []
    p1_Errs = []
    keys = []
    for key in p1_dict:
        if p1_dict[key] != None:
            p1.append(p1_dict[key])
            p1_Errs.append(p1_dict[key])
            keys.append(key)
    Gcrit = 0;
    Gstat = 100;
    del_keys = []
    while Gstat > Gcrit:
        std_dev = np.std(p1)
        avg_p1 = np.mean(p1)
        abs_val_minus_avg = []
        for j in range(len(p1)):
            abs_val_minus_avg.append(abs(p1[j] - avg_p1))
        max_dev = max(abs_val_minus_avg)
        max_ind = np.argmax(abs_val_minus_avg)
        Gstat = max_dev / std_dev 
        alpha = 5
        t_dist = stats.t.ppf(1 - alpha / (2 * len(p1)), len(p1) - 2)
        numerator = (len(p1) - 1) * np.sqrt(np.square(t_dist))
        denominator = np.sqrt(len(p1)) * np.sqrt(len(p1) - 2 + np.square(t_dist))
        Gcrit = numerator/denominator
        if Gstat > Gcrit:
            p1.pop(max_ind)
            del_keys.append(keys[max_ind])
            keys.pop(max_ind)
    for i in del_keys:
        p1_dict[i] = None
        p1_Errs_dict[i] = None
    
    return p1_dict, p1_Errs_dict

# Graph of p1 dependance on fill number

def p1_Fill (p1_early, p1_Errs_early, p1_late, p1_Errs_late, fills_str, weights_dict, weights_sum, detector_name = str):
    
    fills = []
    coefficients_early = []
    coefficients_late = []
    weight_fills = list(weights_dict.keys())
    p1_weights_early = []
    p1_weights_late = []
    p1_weights_Errs_early = []
    p1_weights_Errs_late = []
    for i in range(len(fills_str)):
        for j in range(len(weight_fills)):
            if fills_str[i] == weight_fills[j]:
                fills.append(int(fills_str[i]))
                
                p1_weights_early.append(weights_dict[weight_fills[j]] * p1_early[i] / weights_sum)
                p1_weights_late.append(weights_dict[weight_fills[j]] * p1_late[i] / weights_sum)
                p1_weights_Errs_early.append(weights_dict[weight_fills[j]] * p1_Errs_early[i] / weights_sum)
                p1_weights_Errs_late.append(weights_dict[weight_fills[j]] * p1_Errs_late[i] / weights_sum)

                # p1_weights_early.append(1 * p1_early[i] / 1)
                # p1_weights_late.append(1 * p1_late[i] / 1)
                # p1_weights_Errs_early.append(1 * p1_Errs_early[i] / 1)
                # p1_weights_Errs_late.append(1 * p1_Errs_late[i] / 1)
                
    mean_p1_early = np.mean(p1_weights_early)
    sko_i = []
    for i in range(len(p1_weights_early)):
        sko_i.append(np.power((p1_weights_Errs_early[i] - mean_p1_early), 2))  
                
    mean_sko = float(np.sqrt(np.sum(sko_i))/np.sqrt(len(p1_weights_early)*(len(p1_weights_early)-1)))
    mean_Err_p1_early = np.sqrt(np.power(mean_sko,2) + np.power(np.mean(p1_weights_Errs_early),2))
    
    mean_p1_early_str = str(round(mean_p1_early,8))
    mean_Err_p1_early_str = str(round(mean_Err_p1_early,8))
    
    mean_p1_late = np.mean(p1_weights_late)
    sko_i = []
    for i in range(len(p1_weights_late)):
        sko_i.append(np.power((p1_weights_Errs_late[i] - mean_p1_late), 2))  
                
    mean_sko = float(np.sqrt(np.sum(sko_i))/np.sqrt(len(p1_weights_late)*(len(p1_weights_late)-1)))
    mean_Err_p1_early = np.sqrt(np.power(mean_sko,2) + np.power(np.mean(p1_weights_Errs_late),2))
    
    mean_p1_late_str = str(round(mean_p1_late,8))
    mean_Err_p1_late_str = str(round(mean_Err_p1_early,8))

    fig = plt.figure(figsize= (8,5))
    plt.text(0.03,0.97, '<p1> of fills from 6648 to 7334 = ' + mean_p1_early_str + ' ± ' + mean_Err_p1_early_str, bbox=dict(alpha=0.75, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel(detector_name + ' Nonlinearity Hz/μb (Early)')
    plt.ylabel('Counts')
    sns.distplot(p1_weights_early, kde = False)    
    
    plt.show()
    
    fig = plt.figure(figsize = (8,5))
    plt.text(0.03,0.97, '<p1> of fills from 6648 to 7334 = ' + mean_p1_late_str + ' ± ' + mean_Err_p1_late_str, bbox=dict(alpha=0.75, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel(detector_name + ' Nonlinearity Hz/μb (Late)')
    plt.ylabel('Counts')
    sns.distplot(p1_weights_late, kde = False)  
    
    plt.show()

    mydata1 = odr.RealData(fills, y = p1_weights_early, sy = p1_weights_Errs_early)
    myodr1 = odr.ODR(mydata1, linear, beta0=[0,0])
    myoutput1 = myodr1.run()
    coefficients_early = myoutput1.beta
    p1_early = myoutput1.beta[0]
    p1_Errs_early = myoutput1.sd_beta[0]
    coefficient_Err_early = myoutput1.sd_beta
    
    
    x = np.linspace(min(fills), max(fills), 10)
    y_early = []
    y_late = []
    
    for i in range(len(x)):
        y_early.append(x[i] * coefficients_early[0] + coefficients_early[1])

    fig = plt.figure(figsize = (20,8))
    plt.xlabel('Fill' , fontsize=12)        
    plt.ylabel(detector_name + ' Non-linearity Hz/μb', fontsize=12)
    ax = fig.add_subplot(1,1,1)
    ax.grid(which="major", linewidth = 1)
    early = ax.errorbar(fills, p1_weights_early, p1_weights_Errs_early, fmt = 'rs', markersize = 4 , 
                linestyle = 'None', ecolor = 'r', elinewidth = 0.6, 
                capsize = 2, capthick = 0.8)
    
    
    ax.plot(x, y_early ,'r')
    
    mydata2 = odr.RealData(fills, y = p1_weights_late, sy = p1_weights_Errs_late)
    myodr2 = odr.ODR(mydata2, linear, beta0=[0,0])
    myoutput2 = myodr2.run()
    coefficients_late = myoutput2.beta
    p1_late = myoutput2.beta[0]
    p1_Errs_late = myoutput2.sd_beta[0]
    coefficient_Err_late = myoutput2.sd_beta
    
    late = ax.errorbar(fills, p1_weights_late, p1_weights_Errs_late, fmt = 'bs', markersize = 4 , 
                linestyle = 'None', ecolor = 'b', elinewidth = 0.6, 
                capsize = 2, capthick = 0.8)
    
    x = np.linspace(min(fills), max(fills), 10)
    
    for i in range(len(x)):
        y_late.append(x[i] * coefficients_late[0] + coefficients_late[1])
    
    ax.plot(x, y_late ,'b')
    
    a_early = str(round(coefficients_early[0], 8))
    a_late = str(round(coefficients_late[0], 8))
    a_early_error = str(round(coefficient_Err_early[0], 8))
    a_late_error = str(round(coefficient_Err_late[0], 8))
    
    plt.text(0.03,0.97, 'Early: Slope = ' + a_early + ' ± ' + a_early_error
             + '\nLate: Slope = ' + a_late + ' ± ' + a_late_error, bbox=dict(alpha=0.75, fc="w", ec="k"), 
         transform=plt.gca().transAxes, va = "top", ha="left")
    
    plt.legend([early, late],['Early', 'Late'])
    plt.show()
    
    return

def First_bunch(p1, p1_Errs, detector_name = str, early_late = str, fill_i = str, save = bool):
    
    first_bunches = []
    keys = []
    p1_first = []
    p1_Errs_first = []
    keys_first = []
    for key in p1:
        if key != 'sum':
            keys.append(int(key))
    
    keys.sort()
    first_bunches.append(min(keys))
    for i in range(len(keys)-1):
        if keys[i+1] != keys[i] + 1:
            first_bunches.append(keys[i+1])
    
    for key in first_bunches:
        if p1[str(key)] != None:
            keys_first.append(key)
            p1_first.append(p1[str(key)])
            p1_Errs_first.append(p1_Errs[str(key)])
            
    p1_first_mean = np.mean(p1_first)
    sko_i = []
    
    for i in range(len(p1_first)):  
        sko_i.append(np.power((p1_first[i] - p1_first_mean),2))
    
    mean_sko = float(np.sqrt(np.sum(sko_i))/np.sqrt(len(p1)*(len(p1)-1)))
    mean_Err_p1 = np.sqrt(np.power(mean_sko,2) + np.power(np.mean(p1_Errs_first),2))
    mean_Err_str = toFixed(mean_Err_p1,8)
    
    fig = plt.figure(figsize = (6.6,4))
    plt.text(0.03,0.97, '<p1> = ' + str(round(p1_first_mean,8)) + ' ± ' + mean_Err_str, bbox=dict(alpha=0.5), 
        transform=plt.gca().transAxes, va = "top", ha="left")
    plt.xlabel(detector_name + ' Nonlinearity of first bunches Hz/μb  [fill:'+ fill_i + ']')
    plt.ylabel('Counts')
    sns.distplot(p1_first, kde = False)
    plt.show()
    if save == True:
        fig.savefig('Figures/Non-linearity_in_first_bunches_(only_early)/Non-linearity_distribution_in_first_bunches_'+ detector_name + '_' + fill_i)
        
        data = [['Detector_name', 'bunch', 'p1', 'p1 Error']]
        for i in range(len(keys_first)):
            data_i = []
            data_i.append(detector_name)
            data_i.append(str(keys_first[i]))
            data_i.append(p1_first[i])
            data_i.append(p1_Errs_first[i])
            data.append((data_i))
    
        with open('CSV_Files/Non-linearity_in_first_bunches_(only_early)/Non-linearity_in_first_bunches_(only_early)_' + detector_name + '_' + fill_i + '.csv', 'w', newline = '') as file_4:
            writer = csv.writer(file_4)
            writer.writerows(data)
        
    return p1_first, p1_Errs_first