import numpy
import math
import os
import efel
import collections as cs
import tkinter as tk
from tkinter import filedialog


def fileselect(desc, cnt, initdir):
    # This is a short function accommodating a general file selection
    # cnt: if 0 then use single file, if 1 then use multiple files
    root = tk.Tk()
    root.withdraw()
    if cnt == 0:
        files_pth = filedialog.askopenfilename(initialdir=initdir, title=desc)
    elif cnt == 1:
        files_pth = filedialog.askopenfilenames(initialdir=initdir, title=desc)
    else:
        print('Please specify the number of files to be loaded (0 or 1)')
        return 0
    return files_pth


def dirselect(desc):
    root = tk.Tk()
    root.withdraw()
    file_pth = filedialog.askdirectory(initialdir="/media/sf_Shared_downloads", title=desc)
    return file_pth


def featureselect(desc):
    # This is a short function for reading the feature names from
    # text files in order to extract those features later
    feature_path = fileselect(desc, 0, "/media/sf_Shared_downloads")
    features = numpy.genfromtxt(feature_path, dtype='str')
    return features


def extract_cell_id(fstring, sep_begin, sep_end):
    # Extracting the cell ID from the file path
    ind1 = fstring.rfind(sep_begin)
    ind2 = fstring.rfind(sep_end)
    ident = fstring[ind1 + 1: ind2]
    return ident


def value_Checker(feature_values):
    if feature_values is None:
        feat_val = 0
    elif not feature_values:
        feat_val = 0
    elif feature_values == 0:
        feat_val = 0
    elif (feature_values == math.nan) or (feature_values == float('nan')) or math.isnan(feature_values):
        feat_val = 0
    elif feature_values == float('inf'):
        feat_val = 0
    else:
        feat_val = feature_values
    return feat_val


def main():
    """Main"""

    #files_path = fileselect('Choose data files', 1, "/media/sf_Shared_downloads/HBP_data/Unknown/STEP_LONG")
    #files_path = fileselect('Choose data files', 1,
    #                      "/media/sf_Shared_downloads/mobile_taxonomy_170410/mobile_taxonomy/HEKAdata/zsolt/CCK_Population/Selected")
    # feature_names_single = sorted(numpy.genfromtxt("/media/sf_Shared_downloads/Feature_Files/eFeatures_single.txt", dtype='str'))
    # feature_names_single_neg = numpy.genfromtxt("/media/sf_Shared_downloads/Feature_Files/eFeatures_single_negative.txt", dtype='str')
    # feature_names_multiple = sorted(numpy.genfromtxt("/media/sf_Shared_downloads/Feature_Files/eFeatures_multiple.txt", dtype='str'))
    # feature_names_pos= sorted(numpy.genfromtxt("/media/sf_Shared_downloads/Feature_Files/eFeatures_separate_positive.txt", dtype='str'))
    # feature_names_neg = sorted(numpy.genfromtxt("/media/sf_Shared_downloads/Feature_Files/eFeatures_separate_negative.txt", dtype='str'))


    feature_names_single  = sorted(['steady_state_voltage', 'ISI_log_slope','decay_time_constant_after_stim', 'APlast_amp','AP2_amp','voltage_base','AP1_amp'])
    feature_names_single_neg = ['time_constant']

    feature_names_multiple = sorted(['AP_height','AHP_depth_abs', 'AHP_depth_abs_slow', 'AHP_slow_time',
                              'AP_width', 'AP_amplitude','AP_duration_half_width', 'AHP_depth',
                            'fast_AHP', 'AHP_time_from_peak', 'AP_begin_voltage','AP_rise_time','AP_fall_time', 'AP_rise_rate', 'AP_fall_rate'])

    feature_names_pos = sorted(['Spikecount', 'AP1_amp', 'AP2_amp', 'ISI_CV', 'APlast_amp', 'inv_first_ISI', 'inv_second_ISI', 'inv_third_ISI',
                                'inv_fourth_ISI', 'inv_fifth_ISI', 'inv_last_ISI', 'adaptation_index2', 'time_to_last_spike', 'inv_time_to_first_spike','mean_frequency', 'number_initial_spikes'])
    feature_names_neg = sorted(['voltage_deflection_begin', 'voltage_deflection'])

    files_path = fileselect('Choose data files', 1, "/media/sf_Shared_downloads/HBP_data_grouped")

    #save_location = "/media/sf_Shared_downloads/HBP_data/eFEL processed/Unknown/STEP_LONG"
    save_location = "/media/sf_Shared_downloads/Test/HBP_data_grouped/eFEL_processed/OTHER/HBP"
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    save_loc = save_location + '/Summary.txt'
    data_file = open(save_loc, 'w+')

    # SETTING PROTOCOL
    # Using LONG_STEP protocol:
    # 27 steps, 200 ms baseline, 800ms stimulus, 400 ms baseline, 1000 ms break between steps
    # STEP LONG:
    #current_val = [10, -10, 20, -20, 30, -30, 40, -40, 50, -50, 60, -60, 70, -70, 80, -80, 90, -90, 100, -100, 150, 200, 250, 300, 400, 500, 600]
    # STEP HBP:
    current_val = [ 20, -20, 40, -40, 60, -60, 80, -80, 100, -100, 120, -120, 140, -140, 160, -160, 180, -180, 200, 220, 240, 260, 280, 300, 400, 500, 600]

    # The required number of sampling points during
    Exp_datapoints = 7000
    rec_length = 1400  # in ms
    stim_start = 200
    stim_end = 1000


    # For the extraction of certain features for a certain current injection
    currentIndPos1 = current_val.index(400)
    currentIndPos2 = current_val.index(600)
    currentIndNeg = current_val.index(-100)
    negativeIndices = []
    for cur in current_val:
        if (cur < 0):
            negativeIndices.append(current_val.index(cur))

    # Making feature header for the summary table
    fnpos1 = []
    for f1 in feature_names_pos:
        fnpos1.append(f1 + "_" + str(current_val[currentIndPos1]))
    fnpos2 = []
    for f2 in feature_names_pos:
        fnpos2.append(f2 + "_" + str(current_val[currentIndPos2]))
    fnneg = []
    for f in feature_names_neg:
        fnneg.append(f + "_" + str(current_val[currentIndNeg]))
    fnsingle = []
    for f in feature_names_single:
        fnsingle.append(f + "_mean")
    fnsteady = []
    for f in feature_names_multiple:
        fnsteady.append(f + "_steady")
    fnreobase = []
    for f in feature_names_multiple:
        fnreobase.append(f + "_rheobase")

    feature_header = ['CellID'] + \
                     fnsingle + \
                     ['RheobaseSweep','SteadySweep']+ \
                     feature_names_single_neg +\
                     fnreobase + \
                     fnsteady + \
                    fnpos1 + \
                    fnpos2 + \
                    fnneg


    print("\t".join(feature_header), file=data_file)


    filecounter = 0
    load_ind = 0.0

    for fpath in files_path:

        # Filepath
        filecounter = filecounter + 1

        cellID = extract_cell_id(fpath, '/', '_')
        print("Processing file: " + cellID)
        data = numpy.genfromtxt(fpath)


        # Creating data structure
        traces = []
        trace_count = len(data[0, :])
        trace_indices = numpy.arange(0, trace_count)

        if (trace_count != len(current_val)):
            print("Number of sweeps does not match the protocol")
            print("Sweeps in data:", str(len(data[0, :])))
            load_ind = load_ind + 1.0
            continue

        # Generating time array, checking the number of records
        rec_count = len(data[:, 0])
        if (rec_count != Exp_datapoints):
            print("Number of records does not match the protocol")
            print("Number of data records:", str(rec_count))
            load_ind = load_ind + 1.0
            continue
        time_step = rec_length / rec_count
        time = numpy.arange(time_step, rec_length + time_step, time_step)

        # Loading data into each trace instance

        for ind in trace_indices:
            trace_instance = {}
            trace_instance['stim_start'] = [stim_start]
            trace_instance['stim_end'] = [stim_end]
            trace_instance['T'] = time
            trace_instance['V'] = data[:, ind]
            traces.append(trace_instance)

        # trace_result is a dictionary, with keys as the requested eFeatures
        traces_results_s = efel.getFeatureValues(traces, feature_names_single)
        traces_results_s_neg = efel.getFeatureValues(traces, feature_names_single_neg)
        #traces_results_s_neg = efel.getFeatureValues(traces, ['time_constant'])
        traces_results_m = efel.getFeatureValues(traces, feature_names_multiple)
        traces_results_pos = efel.getFeatureValues(traces, feature_names_pos)
        traces_results_neg = efel.getFeatureValues(traces, feature_names_neg)
        traces_spikes = efel.getFeatureValues(traces, ['Spikecount'])

        # Finding steady sweep: the first sweep with at least 8 spikes
        # If that does not exist, the sweep with the most spikes
        steadySweep = 0
        traceIndex = 0
        highestSpikeCount = 0
        for trace_spikes in traces_spikes:
            spikeCount = trace_spikes['Spikecount']
            if spikeCount is not None:
                if (spikeCount > 8):
                    steadySweep = traceIndex
                    break
                if (spikeCount > highestSpikeCount):
                    highestSpikeCount = spikeCount
                    steadySweep = traceIndex
            traceIndex = traceIndex + 1

        rheobaseSweep = 0
        traceIndex = 0
        for trace_spikes in traces_spikes:
            spikeCount = trace_spikes['Spikecount']
            if spikeCount is not None:
                if (spikeCount > 0):
                    rheobaseSweep = traceIndex
                    break
            traceIndex = traceIndex + 1



        # trace_result is a dictionary, with keys as the requested eFeatures

        # Features which contain 1 value for a single sweep
        # In the summary, the results are the averaged values for each sweep


        mean_results_s = {}
        for feature_name in feature_names_single:
            mean_results_s[feature_name] = []

        for trace_results in traces_results_s:
            trace_results2 = cs.OrderedDict(sorted(trace_results.items()))
            for feature_name, feature_valuess in trace_results2.items():
                if (feature_valuess is not None) and len(feature_valuess):
                    for feature_values in feature_valuess:
                        feat_val = value_Checker(feature_values)
                        mean_results_s[feature_name].append(feat_val)
                else:
                    mean_results_s[feature_name].append(0)

        for feature_name, feature_values in mean_results_s.items():
            smmr = 0.0
            cntr = 0
            # val_copy = mean_results_s[feature_name]
            for el in feature_values:
                if (el != 0) and (el != float('nan')):
                    cntr = cntr + 1
                    smmr = smmr + el
            # mean_results_s[feature_name] = []
            if (cntr != 0) and ~(math.isnan(cntr)) and (cntr != float('nan')):
                mean_results_s[feature_name] = smmr / cntr
            else:
                mean_results_s[feature_name] = '0'

        # The following block handles the single-value features
        # which are only viable for negative currents

        mean_results_s_neg = {}
        for feature_name in feature_names_single_neg:
            mean_results_s_neg[feature_name] = []

        traces_results_s_neg = [traces_results_s_neg[ind] for ind in negativeIndices]

        for trace_results in traces_results_s_neg:
            trace_results2 = cs.OrderedDict(sorted(trace_results.items()))
            for feature_name, feature_valuess in trace_results2.items():
                if (feature_valuess is not None) and len(feature_valuess):
                    for feature_values in feature_valuess:
                        feat_val = value_Checker(feature_values)
                        mean_results_s_neg[feature_name].append(feat_val)
                else:
                   mean_results_s_neg[feature_name].append(0)

        for feature_name, feature_values in mean_results_s_neg.items():
            smmr = 0.0
            cntr = 0
            # val_copy = mean_results_s_neg[feature_name]
            for el in feature_values:
                if (el != 0) and (el != float('nan')):
                    cntr = cntr + 1
                    smmr = smmr + el
            # mean_results_s_neg[feature_name] = []
            if (cntr != 0) and ~(math.isnan(cntr)) and (cntr != float('nan')):
                mean_results_s_neg[feature_name] = smmr / cntr
            else:
                mean_results_s_neg[feature_name] = '0'



        # Features which contain multiple values for a single sweep
        # In the summary, the results are arrays with averaged values for each sweep

        mean_results_m = {}
        for feature_name in feature_names_multiple:
            mean_results_m[feature_name] = []


        for trace_results in traces_results_m:
            trace_results2 = cs.OrderedDict(sorted(trace_results.items()))
            for feature_name, feature_values in trace_results2.items():
                if (feature_values is not None) and len(feature_values):
                    cntr = 0
                    smmr = 0.0
                    for el in feature_values:
                        if (el != math.nan) and (el != float("nan") and (el != 0)):
                            cntr = cntr + 1
                            smmr = smmr + el
                    if (cntr != 0) and (cntr != math.nan) and (cntr != float('nan')):
                        mean_results_m[feature_name].append(smmr / cntr)
                    else:
                        mean_results_m[feature_name].append(0)
                else:
                    mean_results_m[feature_name].append(0)

        #Cross-checking dimensions
        for feature_name,feature_values in mean_results_m.items():
            if len(feature_values) != len(current_val):
                print("List dimension mismatch in ",feature_name)
                print("Feat values, length:", str(feature_values))
                print("Feat length", str(len(feature_values)))
                quit()


        mean_results_m_reobase = {}
        for feature_name, feature_values in mean_results_m.items():
            mean_results_m_reobase[feature_name] = feature_values[rheobaseSweep]

        mean_results_m_steady = {}
        for feature_name, feature_values in mean_results_m.items():
            mean_results_m_steady[feature_name] = feature_values[steadySweep]



        # "Separate/extra" features, aka feature response values for a certain current step
        # These are all single-value-per-sweep features

        posCurrentResults1 = {}
        for feature_name in feature_names_pos:
            feature_name = feature_name + "_" + str(current_val[currentIndPos1])
            posCurrentResults1[feature_name] = []

        trace_results = traces_results_pos[currentIndPos1]
        trace_results2 = cs.OrderedDict(sorted(trace_results.items()))

        for feature_name, feature_valuess in trace_results2.items():
            feature_name = feature_name + "_" + str(current_val[currentIndPos1])
            if (feature_valuess is not None) and len(feature_valuess):
                for feature_values in feature_valuess:
                    feat_val = value_Checker(feature_values)
                    posCurrentResults1[feature_name] = feat_val
            else:
                posCurrentResults1[feature_name] = 0


        posCurrentResults2 = {}
        for feature_name in feature_names_pos:
            feature_name = feature_name + "_" + str(current_val[currentIndPos2])
            posCurrentResults2[feature_name] = []

        trace_results = traces_results_pos[currentIndPos2]
        trace_results2 = cs.OrderedDict(sorted(trace_results.items()))

        for feature_name, feature_valuess in trace_results2.items():
            feature_name = feature_name + "_" + str(current_val[currentIndPos2])
            if (feature_valuess is not None) and len(feature_valuess):
                for feature_values in feature_valuess:
                    feat_val = value_Checker(feature_values)
                    posCurrentResults2[feature_name] = feat_val
            else:
                posCurrentResults2[feature_name] = 0


        negCurrentResults = {}
        for feature_name in feature_names_neg:
            feature_name = feature_name + "_" + str(current_val[currentIndNeg])
            negCurrentResults[feature_name] = []

        trace_results = traces_results_neg[currentIndNeg]
        trace_results2 = cs.OrderedDict(sorted(trace_results.items()))

        for feature_name, feature_valuess in trace_results2.items():
            feature_name = feature_name + "_" + str(current_val[currentIndNeg])
            if (feature_valuess is not None) and len(feature_valuess):
                for feature_values in feature_valuess:
                    feat_val = value_Checker(feature_values)

                    negCurrentResults[feature_name] = feat_val
            else:
                negCurrentResults[feature_name] = 0

        dataarray = [cellID]
        #print(str(filecounter) + ";" + cellID + ";", file=data_file)
        for feature_name, feature_values in sorted(mean_results_s.items()):
            dataarray.append(str(feature_values))
        dataarray.append(str(current_val[rheobaseSweep]))
        dataarray.append(str(current_val[steadySweep]))
        for feature_name, feature_values in sorted(mean_results_s_neg.items()):
            dataarray.append(str(feature_values))
        for feature_name, feature_values in sorted(mean_results_m_reobase.items()):
            dataarray.append(str(feature_values))
        for feature_name, feature_values in sorted(mean_results_m_steady.items()):
            dataarray.append(str(feature_values))
        for feature_name, feature_values in sorted(posCurrentResults1.items()):
            dataarray.append(str(feature_values))
        for feature_name, feature_values in sorted(posCurrentResults2.items()):
            dataarray.append(str(feature_values))
        for feature_name, feature_values in sorted(negCurrentResults.items()):
            dataarray.append(str(feature_values))

        print("\t".join(dataarray), file=data_file)

        #print("\r\n", file=data_file)

        # for feature_name, feature_values in sorted(mean_results_s.items()):
        #     print(feature_name + ':  ' + ' '.join([str(feature_values)]) + "\r\n", file=data_file)
        # print("\n",data_file)
        # for feature_name, feature_values in sorted(mean_results_m.items()):
        #     print(feature_name + ':  ' + ' '.join([str(y) for y in feature_values]) + "\r\n", file=data_file)
        # for feature_name, feature_values in sorted(posCurrentResults1.items()):
        #     print(feature_name + ':  ' + ' '.join([str(feature_values)]) + "\r\n", file=data_file)
        #

        # Printing loading
        load_ind = load_ind + 1.0
        print(str(round(load_ind / (len(files_path)) * 100, 1)) + "% ready")


    data_file.close()

if __name__ == '__main__':
    main()
