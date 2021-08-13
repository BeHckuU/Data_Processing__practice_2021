
import os
import Functions as f
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Information about files and constants 

fill = '7033'
format = '.json'
detector_names = ['BCM1FPCVD','HFET','HFOC']
frev = 11245 # Hz

# Calibration constants (in μb):

sigma_vis_BCM1FPCVD = 210.3
sigma_vis_HFET = 2503.6
sigma_vis_HFOC = 805.9

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Settings for run

Use_Grubbs_Test = True
early_late = 'Late' 
Save_Figures = False
Save_CSV = False
Do_All = False
Create_dirs = False

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Getting directories names, creating directories for graphs and CSV-files

direct = os.listdir(path = 'Rates')
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

if Create_dirs == True:
    if not os.path.isdir('Figures'):
        os.mkdir('Figures')
        
    if not os.path.isdir('Figures/Bunches_non-linearity'):
        os.mkdir('Figures/Bunches_non-linearity')
    if not os.path.isdir('Figures/Bunches_non-linearity/Early'):
        os.mkdir('Figures/Bunches_non-linearity/Early')
    if not os.path.isdir('Figures/Bunches_non-linearity/Late'):
        os.mkdir('Figures/Bunches_non-linearity/Late')
        
    if not os.path.isdir('Figures/Non-linearity_distribution'):
        os.mkdir('Figures/Non-linearity_distribution')
    if not os.path.isdir('Figures/Non-linearity_distribution/Early'):
        os.mkdir('Figures/Non-linearity_distribution/Early')
    if not os.path.isdir('Figures/Non-linearity_distribution/Late'):
        os.mkdir('Figures/Non-linearity_distribution/Late')
        
    if not os.path.isdir('Figures/Non-linearity_in_first_bunches_(only_early)'):
        os.mkdir('Figures/Non-linearity_in_first_bunches_(only_early)')

    if not os.path.isdir('CSV_Files'):
        os.mkdir('CSV_Files')
        
    if not os.path.isdir('CSV_Files/Non-linearity_in_first_bunches_(only_early)'):
        os.mkdir('CSV_Files/Non-linearity_in_first_bunches_(only_early)')

    if not os.path.isdir('CSV_Files/Bunches_coefficients'):
        os.mkdir('CSV_Files/Bunches_coefficients')
    if not os.path.isdir('CSV_Files/Bunches_coefficients/Early'):
        os.mkdir('CSV_Files/Bunches_coefficients/Early')
    if not os.path.isdir('CSV_Files/Bunches_coefficients/Late'):
        os.mkdir('CSV_Files/Bunches_coefficients/Late')
        
    if not os.path.isdir('CSV_Files/Fills_nonlinearity'):
        os.mkdir('CSV_Files/Fills_nonlinearity')
    if not os.path.isdir('CSV_Files/Fills_nonlinearity/BCM1FPCVD'):
        os.mkdir('CSV_Files/Fills_nonlinearity/BCM1FPCVD')
    if not os.path.isdir('CSV_Files/Fills_nonlinearity/HFET'):
        os.mkdir('CSV_Files/Fills_nonlinearity/HFET')
        
    if not os.path.isdir('CSV_Files/Bunches_coefficients'):
        os.mkdir('CSV_Files/Bunches_coefficients')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Execution

Total_p1_HFET_early = []
Total_p1_BCM1FPCVD_early = []
Total_p1_Errs_HFET_early = []
Total_p1_Errs_BCM1FPCVD_early = []

Total_p1_HFET_late = []
Total_p1_BCM1FPCVD_late = []
Total_p1_Errs_HFET_late = []
Total_p1_Errs_BCM1FPCVD_late = []

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Getting weights

weights_dict, weights_sum = f.CSV_open('Luminosities_6648_7334_twoscans.csv')

if Do_All == False:
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Openning files
    
    file_HFOC = f.open_file(fill,format,detector_names[2], directories[early_late][fill])
    file_HFET = f.open_file(fill,format,detector_names[1], directories[early_late][fill])
    file_BCM1FPCVD = f.open_file(fill,format,detector_names[0], directories[early_late][fill])
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Getting data
    
    Total_Rates_HFOC, Total_Errs_HFOC = f.get_data(file_HFOC)
    Total_Rates_HFET, Total_Errs_HFET = f.get_data(file_HFET)
    Total_Rates_BCM1FPCVD, Total_Errs_BCM1FPCVD = f.get_data(file_BCM1FPCVD)
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # SBIL and SBIL errors calculation
    
    Total_SBIL_HFOC, Total_SBIL_Errs_HFOC = f.SBIL_calc(Total_Rates_HFOC, 
                                                      Total_Errs_HFOC, frev, sigma_vis_HFOC)
    Total_SBIL_HFET, Total_SBIL_Errs_HFET = f.SBIL_calc(Total_Rates_HFET, 
                                                      Total_Errs_HFET, frev, sigma_vis_HFET)
    Total_SBIL_BCM1FPCVD, Total_SBIL_Errs_BCM1FPCVD = f.SBIL_calc(Total_Rates_BCM1FPCVD, 
                                                                Total_Errs_BCM1FPCVD, frev, 
                                                                sigma_vis_BCM1FPCVD)
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Ratio calculation (relatively to HFOC)
    
    Total_Ratio_HFET, Total_Ratio_Errs_HFET, Total_X_Lref_HFET, Total_X_Lref_Errs_HFET = f.Ratio_calc(Total_SBIL_HFET, 
                                                                            Total_SBIL_HFOC, Total_SBIL_Errs_HFET, 
                                                                            Total_SBIL_Errs_HFOC)
    Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD, Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD = f.Ratio_calc(Total_SBIL_BCM1FPCVD, 
                                                                                            Total_SBIL_HFOC, 
                                                                                            Total_SBIL_Errs_BCM1FPCVD, 
                                                                                            Total_SBIL_Errs_HFOC)
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Approximation coefficients calculation
    
    Total_Coefficients_HFET, Total_coefficient_Errs_HFET, p1_HFET, p1_Errs_HFET = f.coefficients_calc(Total_Ratio_HFET, Total_X_Lref_HFET, 
                                                                        Total_Ratio_Errs_HFET, Total_X_Lref_Errs_HFET)
    Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD , p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.coefficients_calc(Total_Ratio_BCM1FPCVD, 
                                                                                      Total_X_Lref_BCM1FPCVD, 
                                                                                      Total_Ratio_Errs_BCM1FPCVD, 
                                                                                      Total_X_Lref_Errs_BCM1FPCVD)
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Ratio visualization
    
    f.visualisation(Total_Ratio_HFET, Total_Ratio_Errs_HFET, 
                  Total_X_Lref_HFET, Total_X_Lref_Errs_HFET,  Total_Coefficients_HFET, Total_coefficient_Errs_HFET, 'HFET', 'HFOC', '344' )
    f.visualisation(Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD,
                  Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD, Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD, 'BCM1FPCVD', 'HFOC', '344' )
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Non-linearity in first bunches

    p1_first_HFET, p1_first_Errs_HFET = f.First_bunch(p1_HFET, p1_Errs_HFET,detector_names[1], early_late, fill, Save_Figures)
    p1_first_BCM1FPCVD, p1_first_Errs_BCM1FPCVD = f.First_bunch(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD,detector_names[0], early_late, fill, Save_Figures)

    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Grubbs test
        
    if Use_Grubbs_Test == True:
        p1_HFET, p1_Errs_HFET = f.Grubbs(p1_HFET, p1_Errs_HFET)
        p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.Grubbs(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD)
        
        for Fill in p1_HFET:
            if p1_HFET[Fill] == None:
                Total_Coefficients_HFET[Fill][0] = None
                Total_Coefficients_HFET[Fill][1] = None
                Total_coefficient_Errs_HFET[Fill][0] = None
                Total_coefficient_Errs_HFET[Fill][1] = None
                    
        for Fill in p1_BCM1FPCVD:
            if p1_BCM1FPCVD[Fill] == None:
                Total_Coefficients_BCM1FPCVD[Fill][0] = None
                Total_Coefficients_BCM1FPCVD[Fill][1] = None
                Total_coefficient_Errs_BCM1FPCVD[Fill][0] = None
                Total_coefficient_Errs_BCM1FPCVD[Fill][1] = None
        
    if Save_CSV == True:
        f.CSV_bunch_write(Total_Coefficients_HFET, Total_coefficient_Errs_HFET, 
                        Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD, 
                        detector_names, early_late, fill)
   
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Mean non-linearity coefficients
    
    p1_mean_HFET, p1_mean_HFET_Err = f.Histogram(p1_HFET, p1_Errs_HFET, detector_names[1], early_late, fill, Save_Figures)
    p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err = f.Histogram(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, detector_names[0], early_late, fill, Save_Figures)
    
    Total_p1_HFET_early.append(p1_mean_HFET)
    Total_p1_BCM1FPCVD_early.append(p1_mean_BCM1FPCVD)
    Total_p1_Errs_HFET_early.append(p1_mean_HFET_Err)
    Total_p1_Errs_BCM1FPCVD_early.append(p1_mean_BCM1FPCVD_Err)
    
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Non-linearity visualization
    
    f.Bunches_and_p1(0, 3000, p1_HFET, p1_Errs_HFET, p1_mean_HFET, p1_mean_HFET_Err, detector_names[1], early_late, fill, Save_Figures)
    f.Bunches_and_p1(0, 3000, p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err, detector_names[0], early_late, fill, Save_Figures)
    
    

else:
    
    early_late = 'Early' 
    for key in directories[early_late]:
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Openning files
        
        file_HFOC = f.open_file(key,format,detector_names[2], directories[early_late][key])
        file_HFET = f.open_file(key,format,detector_names[1], directories[early_late][key])
        file_BCM1FPCVD = f.open_file(key,format,detector_names[0], directories[early_late][key])
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Getting data
        
        Total_Rates_HFOC, Total_Errs_HFOC = f.get_data(file_HFOC)
        Total_Rates_HFET, Total_Errs_HFET = f.get_data(file_HFET)
        Total_Rates_BCM1FPCVD, Total_Errs_BCM1FPCVD = f.get_data(file_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # SBIL and SBIL errors calculation
        
        Total_SBIL_HFOC, Total_SBIL_Errs_HFOC = f.SBIL_calc(Total_Rates_HFOC, 
                                                          Total_Errs_HFOC, frev, sigma_vis_HFOC)
        Total_SBIL_HFET, Total_SBIL_Errs_HFET = f.SBIL_calc(Total_Rates_HFET, 
                                                          Total_Errs_HFET, frev, sigma_vis_HFET)
        Total_SBIL_BCM1FPCVD, Total_SBIL_Errs_BCM1FPCVD = f.SBIL_calc(Total_Rates_BCM1FPCVD, 
                                                                    Total_Errs_BCM1FPCVD, frev, 
                                                                    sigma_vis_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio calculation (relatively to HFOC)
        
        Total_Ratio_HFET, Total_Ratio_Errs_HFET, Total_X_Lref_HFET, Total_X_Lref_Errs_HFET = f.Ratio_calc(Total_SBIL_HFET, 
                                                                                Total_SBIL_HFOC, Total_SBIL_Errs_HFET, 
                                                                                Total_SBIL_Errs_HFOC)
        Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD, Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD = f.Ratio_calc(Total_SBIL_BCM1FPCVD, 
                                                                                                Total_SBIL_HFOC, 
                                                                                                Total_SBIL_Errs_BCM1FPCVD, 
                                                                                                Total_SBIL_Errs_HFOC)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Approximation coefficients calculation
        
        Total_Coefficients_HFET, Total_coefficient_Errs_HFET, p1_HFET, p1_Errs_HFET = f.coefficients_calc(Total_Ratio_HFET, Total_X_Lref_HFET, 
                                                                            Total_Ratio_Errs_HFET, Total_X_Lref_Errs_HFET)
        Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD , p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.coefficients_calc(Total_Ratio_BCM1FPCVD, 
                                                                                          Total_X_Lref_BCM1FPCVD, 
                                                                                          Total_Ratio_Errs_BCM1FPCVD, 
                                                                                          Total_X_Lref_Errs_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio visualization
        
        # f.visualisation(Total_Ratio_HFET, Total_Ratio_Errs_HFET, 
        #               Total_X_Lref_HFET, Total_X_Lref_Errs_HFET,  Total_Coefficients_HFET, 'HFET', 'HFOC', '344' )
        # f.visualisation(Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD,
        #               Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD, Total_Coefficients_BCM1FPCVD, 'BCM1FPCVD', 'HFOC', '344' )
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Non-linearity in first bunches
        
        p1_first_HFET, p1_first_Errs_HFET = f.First_bunch(p1_HFET, p1_Errs_HFET,detector_names[1], early_late, key, Save_Figures)
        p1_first_BCM1FPCVD, p1_first_Errs_BCM1FPCVD = f.First_bunch(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD,detector_names[0], early_late, key, Save_Figures)

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Grubbs test
        
        
        if Use_Grubbs_Test == True:
            p1_HFET, p1_Errs_HFET = f.Grubbs(p1_HFET, p1_Errs_HFET)
            p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.Grubbs(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD)
            
            for Fill in p1_HFET:
                if p1_HFET[Fill] == None:
                    Total_Coefficients_HFET[Fill][0] = None
                    Total_Coefficients_HFET[Fill][1] = None
                    Total_coefficient_Errs_HFET[Fill][0] = None
                    Total_coefficient_Errs_HFET[Fill][1] = None
                    
            for Fill in p1_BCM1FPCVD:
                if p1_BCM1FPCVD[Fill] == None:
                    Total_Coefficients_BCM1FPCVD[Fill][0] = None
                    Total_Coefficients_BCM1FPCVD[Fill][1] = None
                    Total_coefficient_Errs_BCM1FPCVD[Fill][0] = None
                    Total_coefficient_Errs_BCM1FPCVD[Fill][1] = None
            
        if Save_CSV == True:
            f.CSV_bunch_write(Total_Coefficients_HFET, Total_coefficient_Errs_HFET, 
                            Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD, 
                            detector_names, early_late, key)
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Mean non-linearity coefficients
        
        p1_mean_HFET, p1_mean_HFET_Err = f.Histogram(p1_HFET, p1_Errs_HFET, detector_names[1], early_late, key, Save_Figures)
        p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err = f.Histogram(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, detector_names[0], early_late, key, Save_Figures)
        
        Total_p1_HFET_early.append(p1_mean_HFET)
        Total_p1_BCM1FPCVD_early.append(p1_mean_BCM1FPCVD)
        Total_p1_Errs_HFET_early.append(p1_mean_HFET_Err)
        Total_p1_Errs_BCM1FPCVD_early.append(p1_mean_BCM1FPCVD_Err)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Non-linearity visualization
        
        f.Bunches_and_p1(0, 3000, p1_HFET, p1_Errs_HFET, p1_mean_HFET, p1_mean_HFET_Err, detector_names[1], early_late, key, Save_Figures)
        f.Bunches_and_p1(0, 3000, p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err, detector_names[0], early_late, key, Save_Figures)
        
    
    
    early_late = 'Late' 
    
    for key in directories[early_late]:
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Openning files
        
        file_HFOC = f.open_file(key,format,detector_names[2], directories[early_late][key])
        file_HFET = f.open_file(key,format,detector_names[1], directories[early_late][key])
        file_BCM1FPCVD = f.open_file(key,format,detector_names[0], directories[early_late][key])
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Getting data
        
        Total_Rates_HFOC, Total_Errs_HFOC = f.get_data(file_HFOC)
        Total_Rates_HFET, Total_Errs_HFET = f.get_data(file_HFET)
        Total_Rates_BCM1FPCVD, Total_Errs_BCM1FPCVD = f.get_data(file_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # SBIL and SBIL errors calculation
        
        Total_SBIL_HFOC, Total_SBIL_Errs_HFOC = f.SBIL_calc(Total_Rates_HFOC, 
                                                          Total_Errs_HFOC, frev, sigma_vis_HFOC)
        Total_SBIL_HFET, Total_SBIL_Errs_HFET = f.SBIL_calc(Total_Rates_HFET, 
                                                          Total_Errs_HFET, frev, sigma_vis_HFET)
        Total_SBIL_BCM1FPCVD, Total_SBIL_Errs_BCM1FPCVD = f.SBIL_calc(Total_Rates_BCM1FPCVD, 
                                                                    Total_Errs_BCM1FPCVD, frev, 
                                                                    sigma_vis_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio calculation (relatively to HFOC)
        
        Total_Ratio_HFET, Total_Ratio_Errs_HFET, Total_X_Lref_HFET, Total_X_Lref_Errs_HFET = f.Ratio_calc(Total_SBIL_HFET, 
                                                                                Total_SBIL_HFOC, Total_SBIL_Errs_HFET, 
                                                                                Total_SBIL_Errs_HFOC)
        Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD, Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD = f.Ratio_calc(Total_SBIL_BCM1FPCVD, 
                                                                                                Total_SBIL_HFOC, 
                                                                                                Total_SBIL_Errs_BCM1FPCVD, 
                                                                                                Total_SBIL_Errs_HFOC)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Approximation coefficients calculation
        
        Total_Coefficients_HFET, Total_coefficient_Errs_HFET, p1_HFET, p1_Errs_HFET = f.coefficients_calc(Total_Ratio_HFET, Total_X_Lref_HFET, 
                                                                            Total_Ratio_Errs_HFET, Total_X_Lref_Errs_HFET)
        Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD, p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.coefficients_calc(Total_Ratio_BCM1FPCVD, 
                                                                                          Total_X_Lref_BCM1FPCVD, 
                                                                                          Total_Ratio_Errs_BCM1FPCVD, 
                                                                                          Total_X_Lref_Errs_BCM1FPCVD)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Ratio visualization
        
        # f.visualisation(Total_Ratio_HFET, Total_Ratio_Errs_HFET, 
        #               Total_X_Lref_HFET, Total_X_Lref_Errs_HFET,  Total_Coefficients_HFET, 'HFET', 'HFOC', '344' )
        # f.visualisation(Total_Ratio_BCM1FPCVD, Total_Ratio_Errs_BCM1FPCVD,
        #               Total_X_Lref_BCM1FPCVD, Total_X_Lref_Errs_BCM1FPCVD, Total_Coefficients_BCM1FPCVD, 'BCM1FPCVD', 'HFOC', '344' )
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Non-linearity in first bunches
        
        # p1_first_HFET, p1_first_Errs_HFET = First_bunch(p1_HFET, p1_Errs_HFET,detector_names[1], early_late, key, Save_Figures)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Grubbs test
        
        if Use_Grubbs_Test == True:
            p1_HFET, p1_Errs_HFET = f.Grubbs(p1_HFET, p1_Errs_HFET)
            p1_BCM1FPCVD, p1_Errs_BCM1FPCVD = f.Grubbs(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD)
            
            for Fill in p1_HFET:
                if p1_HFET[Fill] == None:
                    Total_Coefficients_HFET[Fill][0] = None
                    Total_Coefficients_HFET[Fill][1] = None
                    Total_coefficient_Errs_HFET[Fill][0] = None
                    Total_coefficient_Errs_HFET[Fill][1] = None
                    
            for Fill in p1_BCM1FPCVD:
                if p1_BCM1FPCVD[Fill] == None:
                    Total_Coefficients_BCM1FPCVD[Fill][0] = None
                    Total_Coefficients_BCM1FPCVD[Fill][1] = None
                    Total_coefficient_Errs_BCM1FPCVD[Fill][0] = None
                    Total_coefficient_Errs_BCM1FPCVD[Fill][1] = None
            
        if Save_CSV == True:
            f.CSV_bunch_write(Total_Coefficients_HFET, Total_coefficient_Errs_HFET, 
                            Total_Coefficients_BCM1FPCVD, Total_coefficient_Errs_BCM1FPCVD, 
                            detector_names, early_late, key)
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Mean non-linearity coefficients
        
        p1_mean_HFET, p1_mean_HFET_Err = f.Histogram(p1_HFET, p1_Errs_HFET, detector_names[1], early_late, key, Save_Figures)
        p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err = f.Histogram(p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, detector_names[0], early_late, key, Save_Figures)
        
        Total_p1_HFET_late.append(p1_mean_HFET)
        Total_p1_BCM1FPCVD_late.append(p1_mean_BCM1FPCVD)
        Total_p1_Errs_HFET_late.append(p1_mean_HFET_Err)
        Total_p1_Errs_BCM1FPCVD_late.append(p1_mean_BCM1FPCVD_Err)
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Non-linearity visualization
        
        f.Bunches_and_p1(0, 3000, p1_HFET, p1_Errs_HFET, p1_mean_HFET, p1_mean_HFET_Err, detector_names[1], early_late, key, Save_Figures)
        f.Bunches_and_p1(0, 3000, p1_BCM1FPCVD, p1_Errs_BCM1FPCVD, p1_mean_BCM1FPCVD, p1_mean_BCM1FPCVD_Err, detector_names[0], early_late, key, Save_Figures)
        
    
    f.p1_Fill(Total_p1_HFET_early, Total_p1_Errs_HFET_early, Total_p1_HFET_late, Total_p1_Errs_HFET_late, dir_keys, weights_dict, weights_sum, detector_names[1])
    f.p1_Fill(Total_p1_BCM1FPCVD_early, Total_p1_Errs_BCM1FPCVD_early, Total_p1_BCM1FPCVD_late, Total_p1_Errs_BCM1FPCVD_late, dir_keys, weights_dict, weights_sum, detector_names[0])
    
    if Save_CSV == True:
        f.CSV_fill_write(Total_p1_HFET_early, Total_p1_Errs_HFET_early, Total_p1_HFET_late, Total_p1_Errs_HFET_late, dir_keys, detector_names[1])
        f.CSV_fill_write(Total_p1_BCM1FPCVD_early, Total_p1_Errs_BCM1FPCVD_early, Total_p1_BCM1FPCVD_late, Total_p1_Errs_BCM1FPCVD_late, dir_keys, detector_names[0])