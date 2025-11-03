import logging
import os

from installed_clients.KBParallelClient import KBParallel

# This class is responsible for running multiple instances of
# a given app, given a set of parameter configurations.
class AppExplorerUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  ### General methods ###
  
  # This method runs KBParallel on the given set of tasks.
  def runKBParallel(self, tasks):
    # Configure how KBParallel should run.
    # Note that KBParallel is not a supported app. There is currently no supported way
    # to run other apps from within a KBase app; KBParallel is only used as a way to
    # demonstrate the proposed workflow of the test runner app.
    batch_run_params = {
      'tasks': tasks,
      'runner': 'parallel',
      'concurrent_local_tasks': 1,
      'concurrent_njsw_tasks': 2,
      'max_retries': 2
    }
    
    # Run the tasks
    parallel_runner = KBParallel(self.callback_url)
    result = parallel_runner.run_batch(batch_run_params)
    return result
  
  ### FBAExplorer methods ###
  
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