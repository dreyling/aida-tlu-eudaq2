# aida-tlu-eudaq2
Testing scripts for performance analysis of AIDA TLU, Mimosa Telescope and EUDAQ2 (based on Python with Numpy)

# Usage

## Converting raw to csv (quick non C++ workaround)
Following the example script "raw2csv.sh" in the bin-folder: Use the modified "euCliReader" to create a csv file.

## Converting csv to npy (for faster access)
Following the example "csv2npy.sh": Use the script "csv2npy.py --input=filename.csv" to create npy files

## Access and plot data
See the example script "plot_trigger_run44.py" or use the generic script "plot_trigger.py --input=filename.npy"

Feel free to modify and extend!
