import logging
import os
from FileUtil import FileUtil

# This class contains utilities for the FBAExperiments app.
class FBAExperimentsUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  # This method creates a set of tasks for the edit_media app.
  def createFBATasks(self, media, params):
    if media is not None:
      logging.info(f'read base media: {media}')
    tasks = []
    for i in range(0, len(params['experiments'])):
      experiment = params['experiments'][i]
      compound_id = experiment['compound_id']
      for flux in range(experiment['from_flux'], experiment['to_flux'] + experiment['increment'], experiment['increment']):
        tasks.append({
          'module_name': 'fba_tools',
          'function_name': 'edit_media',
          'version': 'release',
          'parameters': {
            'media_id': params['media_id'],
            'media_output_id': f'fba-experiments-media-{compound_id}-{flux}',
            'compounds_to_add': [],
            'compounds_to_change': [
              {
                'change_id': experiment['compound_id'],
                'change_maxflux': flux
              }
            ],
            'compounds_to_remove': [],
            'workspace': params['workspace_name']
          }
        })
    logging.info(f'edit_media tasks ({len(tasks)}): {tasks}')
    return tasks