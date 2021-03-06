import subprocess
import glob
import os
import time
import psutil
from workflow.utilities import PrepTemporalCytoscapeTPS
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from json.decoder import JSONDecodeError
from py2cytoscape.data.cyrest_client import CyRestClient
from py2cytoscape import cyrest

class Runner:
    '''
    the Runner object encapsulates the WorkflowRun object in order to execute
    the TPS software
    '''
    def __init__(self, 
        workflow_runner):
        self.workflow_runner = workflow_runner

    def run_tps(self):
        try:
            subprocess.run(
                self.workflow_runner.build,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print('an error has occurred while trying to run TPS')

        self.output_files = self.__check_outputs()
        return self

    def __check_outputs(self):
        print('check output', self.workflow_runner.out_folder)
        outputs = glob.glob(self.workflow_runner.out_folder + 
            f'*\{self.workflow_runner.tps_input_settings.output_label}*', recursive=False)

        _out_folder = self.workflow_runner.out_folder
        _out_label = self.workflow_runner.tps_input_settings.output_label
        files = None
        try:
            for file in outputs:
                if not os.path.exists(file):
                    raise Exception('output file {} was not generated, check TPS build'.format(file))
                
            files = {'activity-windows': os.path.join(_out_folder, _out_label+'-activity-windows.tsv'),
                'network-file': os.path.join(_out_folder, _out_label+'-output.sif'),
                'network-file-data': os.path.join(_out_folder, _out_label+'-output.tsv'),
                'temporal-interpretation': os.path.join(_out_folder, _out_label+'-temporal-interpretation.tsv')}
        except Exception:
            print('error has occurred after run')
        
        return files


class Annotations:
    '''
    the Annotations object generates node annotations from defined annotations
    input settings and a Runner object (in order to pass outputs of TPS)
    '''
    def __init__(self, annot_input_settings,
                        runner: Runner):

        self.annot_input_settings = annot_input_settings
        self.runner = runner
        self.output_files = self.runner.output_files
        self.out_folder = self.runner.workflow_runner.out_folder
        self.out_annot_file = os.path.join(self.out_folder, self.annot_input_settings['outAnnotFile'])
        self.out_style_file = os.path.join(self.out_folder, self.annot_input_settings['outStyleFile'])

    def generate_annotations(self):
        print(f'output folder: {self.out_folder}')
        PrepTemporalCytoscapeTPS(
            self.annot_input_settings['peptideMapFile'],
            self.annot_input_settings['timeSeriesFile'],
            self.annot_input_settings['peptideFirstScores'],
            self.annot_input_settings['peptidePrevScoreFile'],
            self.output_files['activity-windows'],
            self.output_files['network-file'],
            self.annot_input_settings['goldStandardFile'],
            self.annot_input_settings['pvalThresh'],
            self.annot_input_settings['logTransform'],
            self.annot_input_settings['styleTemplateFile'],
            self.out_annot_file,
            self.out_style_file,
            addZero=self.annot_input_settings['addZero']
        )

        return self

    def __refactor_annotations(self):
        pass
    
    def __refactor_column(self):
        pass


class Visualize:
    '''
    the Visualize object is a set of methods to import TPS output files 
    and generated node annotations into a local Cytoscape session

    '''
    def __init__(self, cytoscape_input_settings,
                runner: Runner, annotations: Annotations):
        self.cytoscape_input_settings = cytoscape_input_settings
        self.runner = runner
        self.save_file = os.path.abspath(os.path.join(
            self.runner.workflow_runner.out_folder, self.cytoscape_input_settings.session
        ))
        self.annotations = annotations
        self.data_types = 's,s,b,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl,dl'
    
    def __process_exists(self, process_name):

        if process_name in (p.name() for p in psutil.process_iter()):
            return True
        return False

    def __find_path(self, name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if name in files:
                result.append(os.path.join(root, name))
                break
        if not result:
            print(f'Cytoscape path: {path} not valid')
            return None
        return result[0]
    
    def __visualize_outputs(self):
        _annot_file = os.path.abspath(self.annotations.out_annot_file)
        _style_file = os.path.abspath(self.annotations.out_style_file)

        cyclient = cyrest.cyclient()
        cy = CyRestClient()
        #cy.session.delete()
        cy.network.create_from(self.runner.output_files['network-file'])
        time.sleep(2)
        style = cyclient.vizmap.load_file(_style_file)
        cyclient.vizmap.apply(style[0])
        cyclient.table.import_file(
            afile=_annot_file,
            firstRowAsColumnNames=True,
            keyColumnIndex='1',
            startLoadRow='0',
            dataTypeList=self.data_types
        )
        cyclient.session.save_as(session_file=self.save_file)

    def check_cytpscape(self):
        check = self.__process_exists(self.cytoscape_input_settings.name)

        if not check:
            path = self.__find_path(self.cytoscape_input_settings.name, self.cytoscape_input_settings.path)
            subprocess.Popen(path)
        else:
            print('Cytoscape already running')

    def load_cytoscape(self):
        self.check_cytpscape()
        connection_count = 0
        json_count = 0
        http_count = 0
        switch = False
        start = time.time()
        while not switch:
            try:
                print('loading tps and annotation outputs ... ')
                self.__visualize_outputs()
                switch = True
            except ConnectionError as e:
                connection_count += 1
                time.sleep(2)
                continue
            except JSONDecodeError as e:
                json_count += 1
                time.sleep(2)
                continue
            except HTTPError as e:
                http_count += 1
                time.sleep(2)
                continue
        end = time.time()

        print(f'time elapsed: {end-start}')
