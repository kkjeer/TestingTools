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
  
  # This method runs KBParallel on the given set of tasks.
  def runKBParallel(self, tasks):
    logging.info(f'KBParallel: running {len(tasks)} tasks')
    if tasks is None:
      logging.warning('KBParallel: tasks are None')
      return None
    # TODO: create a batch method that can run more than 100 tasks by breaking them up into multiple KBParallel calls
    if len(tasks) > 100:
      logging.warning(f'KBParallel: cannot run more than 100 tasks')
      return None
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
  
  # This method returns the set of refs to output objects created by a KBParallel run of run_flux_balance_analysis tasks.
  def getFBARefs(self, kbparallel_result):
    fba_refs = []
    for r in kbparallel_result['results']:
      new_fba_ref = r['final_job_state']['result'][0]['new_fba_ref']
      fba_refs.append(new_fba_ref)
    return fba_refs
  
  # This method returns the set of refs to the set of media files created by a KBParallel run of edit_media tasks.
  def getMediaRefs(self, kbparallel_result):
    if kbparallel_result is None:
      return None
    media_refs = []
    for r in kbparallel_result['results']:
      if r['is_error']:
        media_refs.append('')
        continue
      new_media_ref = r['final_job_state']['result'][0]['new_media_ref']
      media_refs.append(new_media_ref)
    return media_refs