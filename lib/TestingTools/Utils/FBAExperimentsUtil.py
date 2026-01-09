import logging
import os

# This class contains utilities for the FBAExperiments app.
class FBAExperimentsUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  # This method creates a set of tasks for the run_edit_media app.
  def createFBATasks(self, params):
    tasks = [
      {
        'module_name': 'fba_tools',
        'function_name': 'run_edit_media',
        'version': 'release',
        'parameters': {
          'media_id': params['experiments'][i]['media_id'],
          'media_output_id': f'fba-experiments-media-{i}',
          'compounds_to_add': [],
          'compounds_to_change': [],
          'compounds_to_remove': [],
          'workspace': params['workspace_name']
        }
      }
      for i in range(0, len(params["param_group"]))
    ]
    logging.info(f'run_edit_media tasks: {tasks}')
    return tasks