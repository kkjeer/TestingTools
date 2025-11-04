# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import logging
import os
from pprint import pformat

from Utils.AppExplorerUtil import AppExplorerUtil
from Utils.FBAExplorerUtil import FBAExplorerUtil
from Utils.OutputUtil import OutputUtil
from Utils.FileUtil import FileUtil

from installed_clients.KBaseReportClient import KBaseReport
#END_HEADER


class TestingTools:
    '''
    Module Name:
    TestingTools

    Module Description:
    A KBase module: TestingTools
This sample module contains one small method that filters contigs.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        
        # Any configuration parameters that are important should be parsed and
        # saved in the constructor.
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_TestingTools(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_TestingTools

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_TestingTools function. Params=' + pformat(params))

        # Build the report
        reportObj = {
            'objects_created': [],
            'text_message': ''
        }
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': reportObj, 'workspace_name': params['workspace_name']})

        # Construct output
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref']
                  }
        logging.info('returning:' + pformat(output))
                
        #END run_TestingTools

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_TestingTools return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_FBAExplorer(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_FBAExplorer

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_FBAExplorer function. Params=' + pformat(params))
        
        # Create utilities
        app_explorer_util = AppExplorerUtil(self.config)
        fba_explorer_util = FBAExplorerUtil(self.config)
        output_util = OutputUtil(self.config)
        file_util = FileUtil(self.config, ctx, params)
        
        # Run the FBA app instances using KBParallel
        tasks = fba_explorer_util.createFBATasks(params)
        kbparallel_result = app_explorer_util.runKBParallel(tasks)
        logging.info(f'FBAExplorer: KBParallel result: {kbparallel_result}')
        fba_refs = fba_explorer_util.getFBARefs(kbparallel_result)
        output_json = fba_explorer_util.createOutputJson(tasks, kbparallel_result)
        
        # Set of objects created during this app run (will be linked to in the report at the end)
        # To start, this includes a link for each FBA output created during the KBParallel run
        objects_created = [{'ref': fba_refs[i], 'description': f'results of running fba configuration {i}'} for i in range(0, len(fba_refs))]
        
        # Write the output json to an AttributeMapping file
        mapping_data = output_util.createFlippedAttributeMappingData(output_json)
        logging.info(f'FBAExplorer: attribute mapping data: {mapping_data}')
        output_file = file_util.writeAttributeMappingFile(mapping_data, 'fba-explorer-results')
        if output_file is not None:
          objects_created.append(output_file)
          
        # HTML table displayed to the user in the report at the end
        summary = output_util.createSummary(output_json)

        # Build a report
        reportObj = {
          'objects_created': objects_created,
          'text_message': summary
        }
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': reportObj, 'workspace_name': params['workspace_name']})

        # Construct the output to send back
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref']
                  }
        logging.info('returning:' + pformat(output))
                
        #END run_FBAExplorer

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_FBAExplorer return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    
    def run_TestFeedback(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_TestingTools

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_TestFeedback function. Params=' + pformat(params))

        # Build the report
        reportObj = {
            'objects_created': [],
            'text_message': ''
        }
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': reportObj, 'workspace_name': params['workspace_name']})

        # Construct output
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref']
                  }
        logging.info('returning:' + pformat(output))
                
        #END run_TestFeedback

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_TestFeedback return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
