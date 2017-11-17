import numpy
import math
import os
import efel
import tkinter as tk
from tkinter import filedialog


def fileselect(desc, cnt, initdir):
    # This is a short function accommodating a general file selection
    # cnt: if 0 then use single file, if 1 then use multiple files
    root = tk.Tk()
    root.withdraw()
    if cnt == 0:
        files_pth = filedialog.askopenfilename(initialdir = initdir, title = desc)
    elif cnt == 1:
        files_pth = filedialog.askopenfilenames(initialdir = initdir, title = desc)
    else:
        print('Please specify the number of files to be loaded (0 or 1)')
        return 0
    return files_pth


def dirselect(desc):
    root = tk.Tk()
    root.withdraw()
    file_pth = filedialog.askdirectory(initialdir = "/media/sf_Shared_downloads", title=desc)
    return file_pth


def featureselect(desc):
    # This is a short function for reading the feature names from
    # text files in order to extract those features later
    feature_path = fileselect(desc,0,"/media/sf_Shared_downloads")
    features = numpy.genfromtxt(feature_path, dtype='str')
    return features


def extract_cell_id(fstring, sep_begin, sep_end):
    # Extracting the cell ID from the file path
    ind1 = fstring.rfind(sep_begin)
    ind2 = fstring.rfind(sep_end)
    ident = fstring[ind1 + 1: ind2]
    return ident


def main():
    """Main"""


    files_path = fileselect('Choose data files',1,"/media/sf_Shared_downloads/mobile_taxonomy_170410/mobile_taxonomy/HEKAdata/zsolt/PV_step_default/Fixed")
    #feature_names_single = featureselect('Choose single feature file')
    feature_names_single = numpy.genfromtxt("/media/sf_Shared_downloads/eFeatures_single.txt", dtype='str')

    #feature_names_multiple = featureselect('Choose multiple feature file')
    feature_names_multiple = numpy.genfromtxt("/media/sf_Shared_downloads/eFeatures_multiple.txt", dtype='str')

    feature_names_extra = numpy.genfromtxt("/media/sf_Shared_downloads/eFeatures_separate.txt", dtype='str')

    #feature_names = [ 'AP1_amp', 'AP2_amp', 'decay_time_constant_after_stim', 'Spikecount']
    # feature_names = [
    #         'ISI_log_slope', 'mean_frequency', 'adaptation_index2', 'ISI_CV',
    #         'AP_height', 'AHP_depth_abs', 'AHP_depth_abs_slow',
    #         'AHP_slow_time', 'AP_width', 'AP_amplitude', 'AP1_amp', 'AP2_amp', 'APlast_amp',
    #         'AP_duration_half_width', 'AHP_depth', 'fast_AHP', 'AHP_time_from_peak',
    #         'voltage_deflection', 'voltage_deflection_begin', 'voltage_base',
    #         'steady_state_voltage', 'Spikecount',
    #         'time_to_last_spike', 'time_to_first_spike', 'inv_time_to_first_spike',
    #         'inv_first_ISI', 'inv_second_ISI', 'inv_third_ISI', 'inv_fourth_ISI',
    #         'inv_fifth_ISI', 'inv_last_ISI',
    #         'decay_time_constant_after_stim', 'AP_begin_voltage',
    #         'AP_rise_time', 'AP_fall_time', 'AP_rise_rate', 'AP_fall_rate']
    #save_dir= dirselect('Choose save location')
    save_dir = "/media/sf_Shared_downloads/Processed/CCK"

    # Using LONG_STEP protocol:
    # 27 steps, 200 ms baseline, 800ms stimulus, 400 ms baseline, 1000 ms break between steps
    current_val = [10, -10, 20, -20, 30, -30, 40, -40, 50, -50, 60, -60, 70,
                   -70, 80, -80, 90, -90, 100, -100, 150, 200, 250, 300, 400, 500, 600]
    # For the extraction of certain features for a certain current injection
    current_ind = current_val.index(400)


    load_ind = 0.0
    for fpath in files_path:

        # Filepath
        cellID = extract_cell_id(fpath,'/','_')
        data = numpy.genfromtxt(fpath)
        print("Processing file: " + cellID)
        save_location = (save_dir + '/' + cellID + '_eFEL')
        if not os.path.exists(save_location):
            os.makedirs(save_location)


        # Creating data structure
        traces = []
        trace_count = numpy.arange(0, len(data[0, :]))
        rec_count = len(data[:, 0])
        rec_length = 1400  # in ms
        time_step = rec_length / rec_count
        stim_start = 200
        stim_end = 1000
        time = numpy.arange(time_step, rec_length + time_step, time_step)

        # Loading data into each trace instance
        for ind in trace_count:

            trace_instance = {}
            trace_instance['stim_start'] = [stim_start]
            trace_instance['stim_end'] = [stim_end]
            trace_instance['T'] = time
            trace_instance['V'] = data[:, ind]
            traces.append(trace_instance)

        traces_results_s = efel.getFeatureValues(traces, feature_names_single)
        traces_results_m = efel.getFeatureValues(traces, feature_names_multiple)
        traces_results_extra = efel.getFeatureValues(traces, feature_names_extra)


        # trace_result is a dictionary, with keys as the requested eFeatures

        # Features which contain 1 value for a single sweep
        # In the summary, the results are the averaged values for each sweep

        mean_results_s = {}
        for feature_name in feature_names_single:
            mean_results_s[feature_name] = []

        for trace_results in traces_results_s:
            for feature_name, feature_valuess in trace_results.items():
                if feature_valuess is not None:
                    for feature_values in feature_valuess:
                        if feature_values is None:
                            feat_val = 0
                        elif feature_values == 0:
                            feat_val = 0
                        elif (feature_values == math.nan) or (feature_values == 'nan'):
                            feat_val = 0
                        else:
                            feat_val = feature_values
                        mean_results_s[feature_name].append(feat_val)

        for feature_name, feature_values in mean_results_s.items():
             smmr = 0.0
             cntr = 0
             #val_copy = mean_results_s[feature_name]
             for el in feature_values:
                 if el != 0:
                     cntr = cntr + 1
                     smmr = smmr + el
             #mean_results_s[feature_name] = []
             if (cntr != 0) or ~(math.isnan(cntr)):
                mean_results_s[feature_name] = smmr/cntr
             else:
                 mean_results_s[feature_name] = '0'

        # Features which contain multiple values for a single sweep
        # In the summary, the results are arrays with averaged values for each sweep

        mean_results_m = {}
        for feature_name in feature_names_multiple:
             mean_results_m[feature_name] = []

        for trace_results in traces_results_m:
             for feature_name, feature_values in trace_results.items():
                 if feature_values is not None:
                     cntr = 0
                     smmr = 0.0
                     for el in feature_values:
                         if el != math.nan:
                             cntr = cntr + 1
                             smmr = smmr + el
                     if (cntr != 0) and (cntr != math.nan):
                         mean_results_m[feature_name].append(smmr/cntr)
                     else:
                         mean_results_m[feature_name].append(0)

        # "Separate/extra" features, aka feature response values for a certain current step
        # These are all single-value-per-sweep features

        current_results_e = {}
        for feature_name in feature_names_extra:
            feature_name = feature_name + "_" + str(current_val[current_ind])
            current_results_e[feature_name] = []
        trace_results = traces_results_extra[current_ind]
        for feature_name, feature_valuess in trace_results.items():
            if feature_valuess is not None:
                for feature_values in feature_valuess:
                    if feature_values is None:
                        feat_val = 0
                    elif feature_values == 0:
                        feat_val = 0
                    elif (feature_values == math.nan) or (feature_values == 'nan'):
                        feat_val = 0
                    else:
                        feat_val = feature_values
                    feature_name = feature_name + "_" + str(current_val[current_ind])
                    current_results_e[feature_name] = feat_val




        save_loc = save_location + '/' + cellID + '_Summary.txt'
        data_file = open(save_loc, 'w+')

        for feature_name, feature_values in sorted(mean_results_s.items()):
            print(feature_name + ':  ' + ' '.join([str(feature_values)]) + "\r\n", file=data_file)
        print("\n",data_file)
        for feature_name, feature_values in sorted(mean_results_m.items()):
            print(feature_name + ':  ' + ' '.join([str(y) for y in feature_values]) + "\r\n", file=data_file)
        for feature_name, feature_values in sorted(current_results_e.items()):
            print(feature_name + ':  ' + ' '.join([str(feature_values)]) + "\r\n", file=data_file)
        data_file.close()

        # Printing loading
        load_ind = load_ind + 1.0
        print(str(round( load_ind / (len(files_path)) * 100, 1)) + " % ready")


if __name__ == '__main__':
    main()
