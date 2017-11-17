# eFEL_extractor
This Python script utilizes BBP's eFEL module. The script reads in the in-vitro electrophysiological experiment data and extracts a predefined list of features (from text files) from them. 
Input: the membrane voltage data in ASCII-coded columnar files (the columns corresponding to the sweeps/traces) and the feature files. 
Output: the summarized feature values for each measurement/cell in a text file. The extracted features are categorized into a group of five: features with originally multiple return values (e.g. AP_amplitude), single-value features, single-value features for negative sweeps and two feature files for given negative and positive (default: -100 pA, 400 pA and 600 pA) current sweeps.
The experiment protocol (time and current values) can be changed via the code. 
Prequisites: a UNIX-based operating system (the code was written in Linux), the eFEL and Tkinter libs.
