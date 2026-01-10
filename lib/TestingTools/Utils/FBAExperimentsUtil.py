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
    
  # This method returns a set of tasks for the edit_media app.
  def createEditMediaTasks(self, media, params, indices=None):
    if media is None:
      logging.warning(f'media is none - cannot create edit_media tasks')
      return None
    mediacompounds = media['data'][0]['data']['mediacompounds']
    tasks = []
    if indices is None:
      indices = [i for i in range(0, len(params['experiments']))]
    for i in indices:
      experiment = params['experiments'][i]
      compound_id = experiment['compound_id']
      existing_compound = next((x for x in mediacompounds if x['compound_ref'].endswith(compound_id)), None)
      logging.info(f'existing compound {compound_id}: {existing_compound}')
      fluxes = self.getFluxes(params, i)
      for flux in fluxes:
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
    return tasks
  
  # This helper method returns the set of fluxes to use to create variations on the base media for a given compound.
  def getFluxes(self, params, index):
    experiment = params['experiments'][index]
    return [flux for flux in range(experiment['from_flux'], experiment['to_flux'] + experiment['increment'], experiment['increment'])]
  
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
  
  # This method returns a set of tasks for the run_flux_balance_analysis app.
  def createFBATasks(self, media_refs, compound_id, fluxes, params):
    if media_refs is None:
      logging.warning('media_refs is None - cannot create FBA tasks')
      return None
    tasks = [
      {
        'module_name': 'fba_tools',
        'function_name': 'run_flux_balance_analysis',
        'version': 'release',
        'parameters': {
          'fba_output_id': f'fba-experiment-output-{compound_id}-{fluxes[i]}',
          'target_reaction': 'bio1',
          'fbamodel_id': params['fbamodel_id'],
          'media_id': media_refs[i],
          'workspace': params['workspace_name']
        }
      }
      for i in range(0, len(media_refs))
    ]
    logging.info(f'run_flux_balance_anlysis tasks: {tasks}')
    return tasks
  
  # This method creates a JSON object that contains the parameters and outputs of each FBA run.
  def createOutputJson(self, params, index, kbparallel_result):
    result = {}
    compound_id = params['experiments'][index]['compound_id']
    fluxes = self.getFluxes(params, index)
    for i in range(0, len(kbparallel_result['results'])):
      key = f'{compound_id} experiment {i}'

      # Get information from the fba result
      r = kbparallel_result['results'][i]['final_job_state']['result'][0]
      objective = r['objective']
      new_fba_ref = r['new_fba_ref']

      obj = {}
      obj['max_flux'] = fluxes[i]
      obj['objective_value'] = str(objective)
      # obj['result_ref'] = new_fba_ref
    
      result[key] = obj
    return result