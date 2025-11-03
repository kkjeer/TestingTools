import logging
import os
import uuid

# This class contains utilities for the FBAExplorer app.
class FBAExplorerUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  # This method creates a set of tasks for the run_flux_balance_analysis app.
  def createFBATasks(self, params):
    tasks = [
      {
        'module_name': 'fba_tools',
        'function_name': 'run_flux_balance_analysis',
        'version': 'release',
        'parameters': {
          'fba_output_id': f'fbaexplorer-fba-output-{i}',
          'target_reaction': '4HBTE_c0',
          **params['param_group'][i],
          'workspace': params['workspace_name']
        }
      }
      for i in range(0, len(params["param_group"]))
    ]
    logging.info(f'run_flux_balance_anlysis tasks: {tasks}')
    return tasks
  
  # This method returns the set of refs to output objects created by a KBParallel run.
  def getFBARefs(self, kbparallel_result):
    fba_refs = []
    for r in kbparallel_result['results']:
      new_fba_ref = r['final_job_state']['result'][0]['new_fba_ref']
      fba_refs.append(new_fba_ref)
    return fba_refs
  
  # This method creates a JSON object that contains the parameters and outputs of each FBA run.
  def createOutputJson(self, tasks, kbparallel_result):
    result = {}

    param_names = list(tasks[0]['parameters'].keys())
    param_names = [item for item in param_names if item != "workspace"]

    for i in range(0, len(tasks)):
      t = tasks[i]
      p = t['parameters']

      key = f'Run {i}'

      # Get information from the fba result
      r = kbparallel_result['results'][i]['final_job_state']['result'][0]
      objective = r['objective']
      new_fba_ref = r['new_fba_ref']

      obj = {}
      for param in param_names:
        obj[param] = str(p[param])
      obj['objective_value'] = str(objective)
      obj['result_ref'] = new_fba_ref
    
      result[key] = obj
    return result