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
    
  # This method reads a workspace file using its file ref.
  # This is the preferred way to read files.
  def readFileById(self, ctx, file_ref):
    if file_ref is None or file_ref == '':
      logging.error('cannot read empty file ref')
      return None
    try:
      ws = Workspace(self.ws_url, token=ctx['token'])
      obj = ws.get_objects2({'objects' : [{'ref' : file_ref}]})
      return obj
    except Exception as e:
      logging.error(f'could not read file {file_ref}: {e}')
      return None
    
  # This method reads a workspace file using its file name (rather than its ref).
  # This is a slower way to read a file (compared to using its ref), and should only be used if the ref is not available.
  # (See https://github.com/kbaseapps/SpeciesTreeBuilder/blob/dce166f6d1673018a001b750c191b9a2deda0c71/lib/src/workspace/ObjectSpecification.java).
  def readFileByName(self, ctx, file_name, workspace_name):
    if file_name is None or file_name == '':
      logging.error('cannot read empty file name')
      return None
    try:
      ws = Workspace(self.ws_url, token=ctx['token'])
      obj = ws.get_objects2({'objects' : [{'name' : file_name, 'find_reference_path': 1, 'workspace': workspace_name}]})
      logging.info(f'read file {file_name}: {obj}')
      return obj
    except Exception as e:
      logging.error(f'could not read file {file_name}: {e}')
      return None

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
      return {'ref': ref, 'description': description or 'summary of results'}
    except Exception as e:
      logging.error(f'failed to save file {name} of type {file_type}: {e}')
      return None

  # Each of these methods is a wrapper for writing a particular file type to the workspace.
  def writeStringTable(self, table_data, file_name, description=''):
    name = file_name or 'string-data-table'
    return self.writeFile(table_data, name, 'MAK.StringDataTable', description)
    
  def writeSampleSet(self, sample_set_data, file_name, description=''):
    name = file_name or 'sample-set'
    return self.writeFile(sample_set_data, name, 'KBaseSets.SampleSet', description)
    
  def writeAttributeMappingFile(self, mapping_data, file_name, description=''):
    name = file_name or 'attribute-mapping'
    return self.writeFile(mapping_data, name, 'KBaseExperiments.AttributeMapping', description)
  
  # This method deletes a set of objects from the workspace, given a set of references to the objects.
  def deleteFiles(self, ctx, refs):
    if refs is None or len(refs) < 1:
      logging.error('cannot delete empty file refs')
      return None
    try:
      ws = Workspace(self.ws_url, token=ctx['token'])
      obj = ws.get_objects2({'objects' : [{'ref' : r} for r in refs]})
      return obj
    except Exception as e:
      logging.error(f'could not delete file {refs}: {e}')
      return None