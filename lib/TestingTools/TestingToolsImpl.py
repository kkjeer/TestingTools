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

        objects_created = []

        base_media = file_util.readFileById(ctx, params['media_id'])

        experiment_json = {}
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
        if base_result is None:
          raise ValueError('FBAExperiments: could not run base experiment.')

        base_fba_ref = base_result['results'][0]['final_job_state']['result'][0]['new_fba_ref']
        base_objective = base_result['results'][0]['final_job_state']['result'][0]['objective']

        files_to_cleanup = [base_fba_ref]

        for i in range(0, len(params['experiments'])):
          compound_id = params['experiments'][i]['compound_id']
          logging.info(f'--- FBAExperiments: experiment {i}: compound {compound_id} ---')
          # Create media files based on the variations in the current compound
          edit_media_tasks = fba_experiments_util.createEditMediaTasks(base_media, params, indices=[i])
          edit_media_result = app_explorer_util.runKBParallel(edit_media_tasks)
          media_refs = app_explorer_util.getMediaRefs(edit_media_result)
          logging.info(f'FBAExperiments: new media refs: {media_refs}')
          if media_refs is not None:
            files_to_cleanup = files_to_cleanup + media_refs

          fluxes = fba_experiments_util.getFluxes(params, i)

          # Run flux balance analysis with the base organism and each newly created media file
          fba_tasks = fba_experiments_util.createFBATasks(media_refs, compound_id, fluxes, params)
          fba_result = app_explorer_util.runKBParallel(fba_tasks)
          logging.info(f'FBAExperiments: FBA KBParallel result: {fba_result}')
          fba_refs = app_explorer_util.getFBARefs(fba_result)
          logging.info(f'FBAExperiments: fba refs: {fba_refs}')
          if fba_refs is not None:
            files_to_cleanup = files_to_cleanup + fba_refs

          # Update the output object with the results of running the experiment
          base_flux = fba_experiments_util.getBaseCompoundFlux(base_media, compound_id)
          output = fba_experiments_util.createOutputJson(params, i, fba_result, base_flux, base_objective)
          logging.info(f'FBAExperiments: output json: {pformat(output)}')
          experiment_json = {**experiment_json, **output}

        # If specified, delete all created media and FBA output files
        logging.info(f'FBAExperiments: cleanup: {params["cleanup"]}')
        if params['cleanup'] == 1:
          logging.info(f'FBAExperiments: deleting files {files_to_cleanup}')
          file_util.deleteFiles(ctx, files_to_cleanup)
        else:
          logging.info(f'FBAExperiments: not deleting files {files_to_cleanup}')

        # Write the experimental data json to an AttributeMapping file
        experiment_mapping_data = output_util.createAttributeMappingData(experiment_json)
        experiment_output_file = file_util.writeAttributeMappingFile(experiment_mapping_data, 'fba-experiments-data')
        if experiment_output_file is not None:
          objects_created.append(experiment_output_file)

        # Get the set of metamorphic relations that hold based on the experimental data
        relations = fba_experiments_util.getMetamorphicRelations(experiment_json, params)
        logging.info(f'FBAExperiments metamorphic relations: {relations}')

        # Write the metamorphic relations to an AttributeMapping file
        relations_mapping_data = output_util.createFlippedAttributeMappingData(relations)
        relations_output_file = file_util.writeAttributeMappingFile(relations_mapping_data, 'fba-metamorphic-relations')
        if relations_output_file is not None:
          objects_created.append(relations_output_file)

        # Build the report
        summary = '<p><strong>Experimental data:</strong></p>' + output_util.createSummary(experiment_json) + '<br /><p><strong>Metamorphic relations:</strong></p>' + output_util.createSummary(relations)
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
        logging.info('returning:' + pformat(output))
                
        #END run_FBAExperiments

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
          raise ValueError('Method run_FBAExperiments return value ' +
                            'output is not type dict as required.')
        # return the results
        return [output]
    
    def run_MetamorphicFeedback(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_MetamorphicFeedback

        # Print statements to stdout/stderr are captured and available as the App log
        logging.info('Starting run_MetamorphicFeedback function. Params=' + pformat(params))

        # Create utilities
        test_feedback_util = TestFeedbackUtil(self.config)
        input_util = InputUtil(self.config)
        output_util = OutputUtil(self.config)
        file_util = FileUtil(self.config, ctx, params)

        # Read the input file (output file of an experiments app)
        input_file = file_util.readFileById(ctx, params['mapping_id'])
        experiments_output = input_util.getFlippedAttributeMappingOutputAsJson(input_file)
        logging.info(f'MetamorphicFeedback: explorer output: {experiments_output}')

        # Build the report
        summary = 'Done running Metamorphic Feedback'
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
                
        #END run_MetamorphicFeedback

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
