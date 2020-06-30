'''
Main driver code for end to end TPS workflow

@Author Adam Shedivy 

'''

from visualization_utilities import vis, find_path, process_exists
from table_generation import PrepTemporalCytoscapeTPS
from table_refactor import refactor_col_delim_heat, refactor_col_delim
from requests.exceptions import ConnectionError as CE
from json.decoder import JSONDecodeError
import os
import pandas as pd
import numpy as np
from datetime import date
import subprocess
import sys
import time
import csv


def main():
    '''
    Outine:
        - run TPS
        - gather input data
        - prepare annotations file
        - run visualization

    '''

    today = date.today()

    # * Run TPS!

    # * create Base directory
    baseDir = os.path.abspath(os.path.join('..'))
    tps_in_dir = os.path.join(baseDir, 'data', 'timeseries')
    tps_out_dir = os.path.join(
        baseDir, 'results', 'results_reproduce_egfr_tps_' + str(today))
    if not os.path.exists(tps_out_dir):
        os.makedirs(tps_out_dir)
        print('Created {}'.format(tps_out_dir))
    print(baseDir)
    print(tps_in_dir)
    print(tps_out_dir)

    # * Move files into directory
    output_sif_orig = os.path.join(baseDir, 'output.sif')
    activity_tsv_orig = os.path.join(baseDir, 'activity-windows.tsv')
    output_dest = os.path.join(baseDir, 'workflow', 'output.sif')
    activity_dest = os.path.join(baseDir, 'workflow', 'activity-windows.tsv')

    os.replace(output_sif_orig, output_dest)
    os.replace(activity_tsv_orig, activity_dest)

    # input args from command line
    OUTPUT_FILE = os.path.join(baseDir, 'workflow' , 'output.sif')
    STYLE_FILE = os.path.join(baseDir, 'workflow','tps_style.xml')

    # dir name set manually
    DIRNAME = r"C:\Users\ajshe\OneDrive\Documents\Comp_bio\Cytoscape_v3.7.1"
    CYTOSCAPE = 'Cytoscape.exe'

    if OUTPUT_FILE.lower().endswith(".sif"):
        print("file has valid extention")
    else:
        print("invalid extension on output file: ", OUTPUT_FILE)
        sys.exit()

    # get absolute paths if nessesary
    OUTPUT_FILE = os.path.abspath(OUTPUT_FILE)
    STYLE_FILE = os.path.abspath(STYLE_FILE)
    print("---absolute output path: ", OUTPUT_FILE)
    print("---absolute style path: ", STYLE_FILE)

    # * Gather data used to generate node anotations
    # Use the version with the header line
    pepMapFile = os.path.join(tps_in_dir, 'peptide-mapping.tsv')
    pepFirstFile = os.path.join(tps_in_dir, 'p-values-first.tsv')
    pepPrevFile = os.path.join(tps_in_dir, 'p-values-prev.tsv')
    print(pepMapFile)
    print(pepFirstFile)
    print(pepPrevFile)

    # Use the version for which log2 fold change has been precomputed
    timeSeriesFile = os.path.join(
        baseDir, 'data', 'timeseries', 'log2FoldChange011215.txt')
    #timeSeriesFile = r"C:\\Users\\ajshe\\Anaconda3\\envs\\py2cyto\\tps\\data\\timeseries\\log2FoldChange011215.txt"
    print(timeSeriesFile)

    windowsFile = os.path.join(baseDir, 'workflow', 'activity-windows.tsv')
    networkFile = os.path.join(baseDir, 'workflow', 'output.sif')
    print(windowsFile)
    print(networkFile)

    # Use the same EGFR gold standard for Olsen 2006 and Ale's data
    goldStandardFile = os.path.join(
        baseDir, 'data', 'resources', 'eight-egfr-reference-all.txt')

    styleTemplateFile = os.path.join(
        baseDir, 'notebooks', 'tps_style_template.xml')

    out_dir = os.path.join(baseDir, 'results', str(
        today) + '-and-wolf-yadlin-TPS-cytoscape')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print('Created {}'.format(out_dir))
    outFile = os.path.join(
        out_dir, 'wolf-yadlin-cytoscape-annotations-' + str(today) + '.txt')
    outStyleFile = os.path.join(out_dir, 'tps_style.xml')

    # * run Utility function
    pvalThresh = 0.01  # Same threhsold used in TPS
    logTransform = False
    pepsPerProt = PrepTemporalCytoscapeTPS(pepMapFile, timeSeriesFile, pepFirstFile,
                                           pepPrevFile, windowsFile, networkFile,
                                           goldStandardFile, pvalThresh, logTransform, styleTemplateFile,
                                           outFile,
                                           outStyleFile,
                                           addZero=True)  # don't provide logDefault

    # * get annotations file
    ANNOTATIONS_FILE = outFile
    print("---absolute annotations path: ", ANNOTATIONS_FILE)

    # * Prepare data and directories
    data_delim = pd.read_csv(ANNOTATIONS_FILE, delimiter='\t').drop('Unnamed: 19', 1)
    temp_d = data_delim
    cols = data_delim.columns.values[3:]
    cols
    for o in cols:
        data_delim[o] = refactor_col_delim(temp_d, o)

    new_file2 = os.path.join(out_dir, 'annotations_data.csv')
    new_data = os.path.join(out_dir, 'refactored_annotations.txt')
    data_delim.to_csv(new_file2, mode='w', index=False)

    csv_file2 = new_file2
    txt_file2 = new_data
    with open(txt_file2, "a") as my_output_file:
        with open(csv_file2, "r") as my_input_file:
            [my_output_file.write("\t".join(row)+'\n')
             for row in csv.reader(my_input_file)]
        my_output_file.close()

    REFACTORED_ANNOTATIONS = txt_file2
    SAVE_FILE = os.path.join(out_dir, 'TPS_session')
    

    # check if Cytoscape is running
    is_running = process_exists('Cytoscape.exe')

    if (is_running == False):
        print("---Cytoscape not running")

        # find path to Cytoscape on machine
        cyto_path = find_path(CYTOSCAPE, DIRNAME)

        # open Cytoscape
        p = subprocess.Popen(cyto_path)

    else:

        # continue on
        print("---Cytoscape running")

    # call vis fuction to load input files in Cytoscape session
    # catch errors: ConnectionError, JSONDecoderError
    connection_count = 0
    JSON_count = 0
    switch = False
    start = time.time()
    while switch is False:
        try:

            # run visualization function
            vis(OUTPUT_FILE, STYLE_FILE, REFACTORED_ANNOTATIONS, SAVE_FILE)
            
            # * Move files into directory
            results_output_dest = os.path.join(out_dir, 'output.sif')
            results_activity_dest = os.path.join(out_dir, 'activity-windows.tsv')

            os.replace(output_dest, results_output_dest)
            os.replace(activity_dest, results_activity_dest)

            # print information --------------------------------
            print("---CyRest client created")
            print("---output file: " + OUTPUT_FILE)
            print("---style file: " + STYLE_FILE)
            print("---ConnectionError catches: ", connection_count)
            print("---JSONDecoderError catches: ", JSON_count)
            # --------------------------------------------------

            # flip switch value
            switch = True

        except CE as e:

            # requests.ConnectionError caught if connection cannot be made with Cytoscape Server
            connection_count += 1
            time.sleep(2)
            switch = False
            continue

        except JSONDecodeError as e:

            # error thorwn from trying to create CyClient
            JSON_count += 1
            time.sleep(2)
            switch = False
            continue
    end = time.time()
    print("---time elapsed: ", end - start)

    print("---Finish loading output file and style file")


if __name__ == '__main__':
    main()
