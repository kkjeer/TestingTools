import logging
import os
import json

# This class is responsible for converting file contents into json objects.
class InputUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  # This method converts the results of reading a StringDataTable file into a json object.
  def getStringDataTableOutputAsJson(self, table):
    if table is None:
      return None
    result = {}
    data = table['data'][0]['data']
    logging.info(f'table data: {json.dumps(data, indent=2)}')

    for i in range(0, len(data['row_labels'])):
      key = data['row_labels'][i]
      obj = {}
      d = data['data'][i]
      for j in range(0, len(d)):
        label = data['column_labels'][j]
        obj[label] = d[j]
      result[key] = obj
    return result
  
  # This method converts the results of reading an AttributeMapping file into a json object.
  # It assumes the AttributeMapping data was "flipped" (i.e. used rows as columns and vice versa).
  def getFlippedAttributeMappingOutputAsJson(self, mappings):
    if mappings is None:
      return None
    result = {}
    data = mappings['data'][0]['data']
    logging.info(f'mappings data: {json.dumps(data, indent=2)}')

    for i in range(0, len(data['attributes'])):
      r = data['attributes'][i]['attribute']
      row = {}
      for c in data['instances']:
        row[c] = data['instances'][c][i]
      result[r] = row
    return result
  
  # This method converts the results of reading an AttributeMapping file into a json object.
  def getAttributeMappingOutputAsJson(self, mappings):
    if mappings is None:
      return None
    result = {}
    data = mappings['data'][0]['data']
    logging.info(f'mappings data: {json.dumps(data, indent=2)}')

    for r in data['instances']:
      row = {}
      for i in range(0, len(data['instances'][r])):
        param = data['attributes'][i]['attribute']
        val = data['instances'][r][i]
        row[param] = val
      result[r] = row
    return result