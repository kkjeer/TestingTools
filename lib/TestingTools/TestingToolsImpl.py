# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
import logging
import os
from pprint import pformat

from Utils.AppExplorerUtil import AppExplorerUtil
from Utils.FBAExplorerUtil import FBAExplorerUtil
from Utils.TestFeedbackUtil import TestFeedbackUtil
from Utils.FBAExperimentsUtil import FBAExperimentsUtil
from Utils.OutputUtil import OutputUtil
from Utils.InputUtil import InputUtil
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
        fba_refs = app_explorer_util.getFBARefs(kbparallel_result)
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
        #BEGIN run_TestFeedback

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_TestFeedback function. Params=' + pformat(params))

        # Create utilities
        test_feedback_util = TestFeedbackUtil(self.config)
        input_util = InputUtil(self.config)
        output_util = OutputUtil(self.config)
        file_util = FileUtil(self.config, ctx, params)

        # Read the input file (output file of an explorer app)
        input_file = file_util.readFileById(ctx, params['mapping_id'])
        explorer_output = input_util.getFlippedAttributeMappingOutputAsJson(input_file)

        # Add the feedback to the FBA results
        results_with_feedback = test_feedback_util.addFeedbackToExplorerOutput(explorer_output, params['param_group'])

        # Save the annotated results (with feedback) to an output file
        objects_created = []
        mapping_data = output_util.createAttributeMappingData(results_with_feedback)
        output_file = file_util.writeAttributeMappingFile(mapping_data, 'test-feedback-results')
        if output_file is not None:
          objects_created.append(output_file)

        # Build the report
        summary = output_util.createSummary(results_with_feedback)
        reportObj = {
          'objects_created': objects_created,
          'text_message': summary
        }
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': reportObj, 'workspace_name': params['workspace_name']})

        # Construct output
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref']
                  }
                
        #END run_TestFeedback

        # return the results
        return [output]
    
    def run_FBAExperiments(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_FBAExperiments

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_FBAExperiments function. Params=' + pformat(params))

        app_explorer_util = AppExplorerUtil(self.config)
        file_util = FileUtil(self.config, ctx, params)
        output_util = OutputUtil(self.config)
        fba_experiments_util = FBAExperimentsUtil(self.config)

        media = file_util.readFileById(ctx, params['media_id'])

        output_json = {}
        base_task = {
          'module_name': 'fba_tools',
          'function_name': 'run_flux_balance_analysis',
          'version': 'release',
          'parameters': {
            'fba_output_id': f'fba-experiment-output-base',
            'target_reaction': 'bio1',
            'fbamodel_id': params['fbamodel_id'],
            'media_id': params['media_id'],
            'workspace': params['workspace_name']
          }
        }
        base_result = app_explorer_util.runKBParallel([base_task])
        if base_result is not None:
          output_json['Base'] = {
            'compound_id': '---',
            'max_flux': '---',
            'objective_value': base_result['results'][0]['final_job_state']['result'][0]['objective']
          }

        for i in range(0, len(params['experiments'])):
          compound_id = params['experiments'][i]['compound_id']
          logging.info(f'--- FBAExperiments: experiment {i}: compound {compound_id} ---')
          # Create media files based on the variations in the current compound
          edit_media_tasks = fba_experiments_util.createEditMediaTasks(media, params, indices=[i])
          edit_media_result = app_explorer_util.runKBParallel(edit_media_tasks)
          media_refs = app_explorer_util.getMediaRefs(edit_media_result)
          logging.info(f'FBAExperiments: new media refs: {media_refs}')

          fluxes = fba_experiments_util.getFluxes(params, i)

          # Sanity check: for each new media file, verify that it contains the correct max flux for the current compound
          if False:
            for i in range(0, len(media_refs)):
              mr = media_refs[i]
              media = file_util.readFileById(ctx, mr)
              mediacompounds = media['data'][0]['data']['mediacompounds']
              existing_compound = next((x for x in mediacompounds if x['compound_ref'].endswith(compound_id)), None)
              if existing_compound is None:
                logging.warning(f'FBAExperiments: failed to create compound {compound_id} in media {mr}')
              max_flux = existing_compound['maxFlux']
              expected_flux = fluxes[i]
              logging.info(f'FBAExperiments: {compound_id} expected max flux: {expected_flux}, actual: {max_flux}')

          # Run flux balance analysis with the base organism and each newly created media file
          fba_tasks = fba_experiments_util.createFBATasks(media_refs, compound_id, fluxes, params)
          fba_result = app_explorer_util.runKBParallel(fba_tasks)
          logging.info(f'FBAExperiments: FBA KBParallel result: {fba_result}')
          fba_refs = app_explorer_util.getFBARefs(fba_result)
          logging.info(f'FBAExperiments: fba refs: {fba_refs}')
          output = fba_experiments_util.createOutputJson(params, i, fba_result)
          logging.info(f'FBAExperiments: output json: {pformat(output)}')
          output_json = {**output_json, **output}

        # Build the report
        summary = output_util.createSummary(output_json)
        reportObj = {
          'objects_created': [],
          'text_message': summary
        }
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': reportObj, 'workspace_name': params['workspace_name']})

        # Construct output
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref']
                  }
        logging.info('returning:' + pformat(output))
                
        #END run_FBAExperiments

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_FBAExperiments return value ' +
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
