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
###########################################################################################################
# client used for vizmap functions 
# edit made in table.py:
# "C:\Users\ajshe\AppData\Roaming\Python\Python35\site-packages\py2cytoscape\cyrest\table.py", line 575
# changed else to finally 1/24/2020
###########################################################################################################

#assert Cytoscape is running on machine

def process_exists(process_name):
    bytes_name = str.encode(process_name)
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name

    # use buildin check_output right away
    output = subprocess.check_output(call)

    # check in last line for process name
    last_line = output.strip().split(b'\r\n')[-1]
    return last_line.lower().startswith(bytes_name.lower())


def find_path(name, path):
    result = []
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
    
    print("output file: " + output)
    print("style file: " + style)
    

    #create cyrest client
    cyy = cyrest.cyclient()
    print("CyRest client created")

    # Step 1: Create py2cytoscape client
    cy = CyRestClient()

    # Reset
    cy.session.delete()
    print("session reset")

    # Step 2: Load network from somewhere
    print("loading network file")
    tps_net = cy.network.create_from(output)
    print("Done")
    time.sleep(2)


    # Step 3: Apply layout
    # list of styles to apply
    # only contains the one style loaded from style file 
    print("apply style file")
    style = cyy.vizmap.load_file(style)
    print("style name: ", style)
    cyy.vizmap.apply(style[0])

    print("Done! open up cytoscape session")



def main(args):

    OUTPUT_FILE = args[1]
    STYLE_FILE = args[2]
    DIRNAME = r"C:\Users"
    CYTOSCAPE = 'Cytoscape.exe'

    # check if Cytoscape is running 
    isRunning = process_exists('Cytoscape.exe')

    if (isRunning == False):
        print("Cytoscape not running")

        # find path to Cytoscape on machine 
        cytoPath = find_path(CYTOSCAPE, DIRNAME)

        # open Cytoscape 
        p = subprocess.Popen(cytoPath)

        # pause execution, wait for Cytoscape to load
        time.sleep(50)

    else:

        # continue on
        print("Cytoscape running")

    # call vis fuction to load input files in Cytoscape session
    vis(OUTPUT_FILE, STYLE_FILE)


if __name__ == '__main__':
    main(sys.argv)