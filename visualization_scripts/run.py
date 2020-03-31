""" 
script loads style file and TPS output file into Cytoscape session

@author: Adam Shedivy

"""

# imports 
from py2cytoscape.data.cynetwork import CyNetwork
from py2cytoscape.data.cyrest_client import CyRestClient
from py2cytoscape.data.style import StyleUtil
import py2cytoscape.util.cytoscapejs as cyjs
import py2cytoscape.cytoscapejs as renderer
from py2cytoscape import cyrest
import networkx as nx
import pandas as pd
import json
import sys
import time
import subprocess
import os
from requests.exceptions import ConnectionError as CE
from json.decoder import JSONDecodeError 

#assert Cytoscape is running on machine

def process_exists(process_name):
    """
    function to assert Cytoscape is running

    Args:
        process_name (str): name of process to check for
        example - 'Cytoscape.exe'

    Returns:
        true if process runnning, else false

    """
    bytes_name = str.encode(process_name)
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name

    # use buildin check_output right away
    output = subprocess.check_output(call)

    # check in last line for process name
    last_line = output.strip().split(b'\r\n')[-1]

    return last_line.lower().startswith(bytes_name.lower())


def find_path(name, path):
    """
    Search Algorithm to find Cytoscape application on machine

    Args:
        name (str): name of application 
        path (str): top directory to start search from 

    Returns:
        path to first match on machine
    """

    # list to hold found matches
    result = []

    # walk directory/file tree 
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result[0]


def vis(output, style):
    """
    REQUIRED ARGS:
        output: output file from tps software
        style: style file for cytoscpe 
    """
    
    #create cyrest client
    cyy = cyrest.cyclient()
    
    # Step 1: Create py2cytoscape client
    cy = CyRestClient()

    # Reset
    cy.session.delete()
    print("---session reset")

    # Step 2: Load network from somewhere
    print("---loading network file")
    tps_net = cy.network.create_from(output)
    print("---Done")
    time.sleep(2)


    # Step 3: Apply layout
    # list of styles to apply
    # only contains the one style loaded from style file 
    print("---apply style file")
    style = cyy.vizmap.load_file(style)
    print("---style name: ", style)
    cyy.vizmap.apply(style[0])

    print("Done! open up cytoscape session")



def main(args):

    # input args from command line
    OUTPUT_FILE = args[1]
    STYLE_FILE = args[2]
    DIRNAME = r"C:\Users\ajshe\OneDrive\Documents\Comp_bio\Cytoscape_v3.7.1"
    CYTOSCAPE = 'Cytoscape.exe'

    if OUTPUT_FILE.lower().endswith(".sif"):
        print ("file has valid extention")
    else:
        print ("invalid extension on output file: ", OUTPUT_FILE)
        sys.exit()
    
    #!TODO check style file extensiona nd format 


    # check if Cytoscape is running 
    isRunning = process_exists('Cytoscape.exe')

    if (isRunning == False):
        print("---Cytoscape not running")

        # find path to Cytoscape on machine 
        cytoPath = find_path(CYTOSCAPE, DIRNAME)

        # open Cytoscape 
        p = subprocess.Popen(cytoPath)

    else:

        # continue on
        print("---Cytoscape running")

    # call vis fuction to load input files in Cytoscape session
    # catch errors: ConnectionError, JSONDecoderError
    connectionCount = 0 
    JSONCount = 0
    switch = False
    start = time.time()
    while switch == False:
        try:

            # run visualization function 
            vis(OUTPUT_FILE, STYLE_FILE)

            # print information --------------------------------
            print("---CyRest client created")
            print("---output file: " + OUTPUT_FILE)
            print("---style file: " + STYLE_FILE)
            print("---ConnectionError catches: ", connectionCount)
            print("---JSONDecoderError catches: ", JSONCount)
            # --------------------------------------------------

            # flip switch value
            switch = True

        except CE as e:
            
            #requests.ConnectionError caught if connection cannot be made with Cytoscape Server
            connectionCount += 1
           # time.sleep(20)
            switch = False
            continue

        except JSONDecodeError as e:

            # error thorwn from trying to create CyClient
            JSONCount += 1
            #time.sleep(20)
            switch = False
            continue
    end = time.time()
    print("---time elapsed: ", end - start)  

    print("---Finish loading output file and style file")
  


if __name__ == '__main__':
    main(sys.argv)