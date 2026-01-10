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
    
  # This method creates a set of tasks for the edit_media app.
  def createFBATasks(self, media, params):
    if media is None:
      logging.warning(f'media is none - cannot create edit_media tasks')
      return None
    mediacompounds = media['data'][0]['data']['mediacompounds']
    tasks = []
    for i in range(0, len(params['experiments'])):
      experiment = params['experiments'][i]
      compound_id = experiment['compound_id']
      existing_compound = next((x for x in mediacompounds if x['compound_ref'].endswith(compound_id)), None)
      logging.info(f'compound {compound_id} existing: {existing_compound}')
      for flux in range(experiment['from_flux'], experiment['to_flux'] + experiment['increment'], experiment['increment']):
        compounds_to_add = [{
          'add_id': compound_id, 
          'add_maxflux': flux, 
          'add_minflux': '-100', 
          'add_concentration': '0.001'
        }] if existing_compound is None else []
        compounds_to_change = [{
          'change_id': compound_id, 
          'change_maxflux': flux, 
          'change_minflux': str(existing_compound['minFlux']), 
          'change_concentration': str(existing_compound['concentration'])
        }] if existing_compound is not None else []
        tasks.append({
          'module_name': 'fba_tools',
          'function_name': 'edit_media',
          'version': 'release',
          'parameters': {
            'media_id': params['media_id'],
            'media_output_id': f'fba-experiments-media-{compound_id}-{flux}',
            'compounds_to_add': compounds_to_add,
            'compounds_to_change': compounds_to_change,
            'compounds_to_remove': [],
            'workspace': params['workspace_name']
          }
        })
    logging.info(f'edit_media tasks ({len(tasks)}): {tasks}')
    return tasks