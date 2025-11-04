import logging
import os
import json

from installed_clients.WorkspaceClient import Workspace

# This class is responsible for reading and writing files to the user's workspace.
class FileUtil:
  def __init__(self, config, ctx, params):
    self.config = config
    self.ctx = ctx
    self.params = params
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)

  # This is a helper method for writing a file to the workspace.
  def writeFile(self, data, name, file_type, description):
    try:
      ws = Workspace(self.ws_url, token=self.ctx['token'])
      save_result = ws.save_objects(
         {
           'workspace': self.params['workspace_name'],
           'objects': [
              {
                'name': name,
                'type': file_type,
                'data': data,
              }
            ]
          })
      logging.info(f'saved file {name} of type {file_type}: {save_result}')
      id = save_result[0][0]
      version = save_result[0][4]
      workspace_id = save_result[0][6]
      ref = f'{workspace_id}/{id}/{version}'
      return {'ref': ref, 'description': description}
    except Exception as e:
      logging.error(f'failed to save file {name} of type {file_type}: {e}')
      return None

  # Each of these methods is a wrapper for writing a particular file type to the workspace.
  def writeStringTable(self, table_data):
    return self.writeFile(table_data, 'string-data-table', 'MAK.StringDataTable', 'string data table')
    
  def writeSampleSet(self, sample_set_data):
    return self.writeFile(sample_set_data, 'sample-set', 'KBaseSets.SampleSet', 'sample set summary')
    
  def writeAttributeMappingFile(self, mapping_data, file_name):
    name = file_name or 'attribute-mapping'
    return self.writeFile(mapping_data, name, 'KBaseExperiments.AttributeMapping', 'summary of results')