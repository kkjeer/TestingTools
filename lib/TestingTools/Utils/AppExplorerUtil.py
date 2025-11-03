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