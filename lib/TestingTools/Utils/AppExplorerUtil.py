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
  
  def getFBAResults(self, ctx, kbparallel_result, file_util):
    empty = {'fba_ref': '', 'objective': ''}
    extracted = self.extractResults(kbparallel_result)
    if extracted is None:
      return [empty]
    results = []
    for r in extracted:
      info = self.getFBAInformationFromExtractedResult(ctx, r, file_util)
      results.append(info)
      continue
      if r is None:
        results.append(empty)
      # get values from cobrapy app results
      elif 'report_name' in r and r['report_name'].startswith('COBRApy') and 'obj' in r and 'workspace_name' in r:
        output_name = r['obj']
        output_file = file_util.readFileByName(ctx, output_name, r['workspace_name'])
        if output_file is None or 'data' not in output_file or output_file['data'] is None or output_file['data'][0] is None:
          results.append(empty)
          continue
        fba_ref = ''
        objective = ''
        data = output_file['data'][0]
        if 'path' in data and data['path'] is not None:
          fba_ref = output_file['data'][0]['path'][0]
        if 'data' in data and data['data'] is not None and 'objectiveValue' in data['data']:
          objective = str(data['data']['objectiveValue'])
        results.append({'fba_ref': fba_ref, 'objective': objective})
      # get values from fba_tools app results
      elif 'new_fba_ref' in r and 'objective' in r:
        results.append({'fba_ref': r['new_fba_ref'], 'objective': r['objective']})
      else:
        results.append(empty)
    return results
  
  def getFBAInformationFromExtractedResult(self, ctx, r, file_util):
    empty = {'fba_ref': '', 'objective': ''}
    if r is None or r['is_error']:
      return empty
    if 'report_name' in r and r['report_name'].startswith('COBRApy') and 'obj' in r and 'workspace_name' in r:
      output_name = r['obj']
      output_file = file_util.readFileByName(ctx, output_name, r['workspace_name'])
      if output_file is None or 'data' not in output_file or output_file['data'] is None or output_file['data'][0] is None:
        return empty
      fba_ref = ''
      objective = ''
      data = output_file['data'][0]
      if 'path' in data and data['path'] is not None:
        fba_ref = output_file['data'][0]['path'][0]
      if 'data' in data and data['data'] is not None and 'objectiveValue' in data['data']:
        objective = str(data['data']['objectiveValue'])
      return {'fba_ref': fba_ref, 'objective': objective}
    elif 'new_fba_ref' in r and 'objective' in r:
      return {'fba_ref': r['new_fba_ref'], 'objective': r['objective']}
    return empty
  
  # This method returns the set of refs to output objects created by a KBParallel run of run_flux_balance_analysis tasks.
  def getFBARefs(self, ctx, kbparallel_result, file_util):
    results = self.extractResults(kbparallel_result)
    logging.info(f'getFBARefs: kbparalell results: {results}')
    if kbparallel_result['results'] is None:
      return []
    fba_refs = []
    for r in kbparallel_result['results']:
      info = self.getFBAInformationFromExtractedResult(ctx, r, file_util)
      fba_refs.append(info['fba_ref'])
      continue
      if r is None or r['is_error'] or r['final_job_state'] is None or r['final_job_state']['result'] is None or r['final_job_state']['result'][0] is None or r['final_job_state']['result'][0]['new_fba_ref']:
        fba_refs.append('')
        continue
      new_fba_ref = r['final_job_state']['result'][0]['new_fba_ref']
      fba_refs.append(new_fba_ref)
    return fba_refs
  
  # This method returns the set of refs to the set of media files created by a KBParallel run of edit_media tasks.
  def getMediaRefs(self, kbparallel_result):
    results = self.extractResults(kbparallel_result)
    logging.info(f'getMediaRefs: kbparalell results: {results}')
    if kbparallel_result is None:
      return None
    media_refs = []
    for r in kbparallel_result['results']:
      if r is None or r['is_error'] or r['final_job_state'] is None or r['final_job_state']['result'] is None or r['final_job_state']['result'][0] is None or r['final_job_state']['result'][0]['new_media_ref']:
        media_refs.append('')
        continue
      new_media_ref = r['final_job_state']['result'][0]['new_media_ref']
      media_refs.append(new_media_ref)
    return media_refs
  
  def extractResults(self, kbparallel_result):
    if kbparallel_result is None:
      return None
    if kbparallel_result['results'] is None:
      return None
    results = []
    for r in kbparallel_result['results']:
      if r is None or r['is_error'] or r['final_job_state'] is None or r['final_job_state']['result'] is None or r['final_job_state']['result'][0] is None:
        results.append(None)
      results.append(r['final_job_state']['result'][0])
    return results