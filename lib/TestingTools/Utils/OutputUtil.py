import logging
import os

# This class is responsible for constructing objects that will be used in output files and reports.
class OutputUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    
  # This method creates data to populate a StringDataTable file.
  def createStringDataTableData(self, output_json):
    rows = list(output_json.keys())
    cols = list(output_json[rows[0]].keys())

    table_data = {
      'row_ids': rows,
      'row_labels': rows,
      'column_ids': cols,
      'column_labels': cols,
      'row_groups_ids': [],
      'column_groups_ids': [],
      'data': []
    }

    for r in rows:
      table_data['data'].append(list(output_json[r].values()))

    return table_data
  
  # This method creates data to populate an AttributeMapping file.
  # The data is "flipped" - it uses the "column" keys of the json as the rows and the "row" keys as columns.
  def createFlippedAttributeMappingData(self, output_json, unit_key='objective_value'):
    rows = list(output_json.keys())
    cols = list(output_json[rows[0]].keys())
    instances = {}
    for c in cols:
      instances[c] = [str(output_json[key][c]) for key in output_json]
    mapping_data = {
      'attributes': [
        {'attribute': row, 
         'source': 'upload', 
         'unit': output_json[row][unit_key], 
        } for row in rows],
      'instances': instances,
      'ontology_mapping_method': 'User curation'
    }
    return mapping_data
  
  # This method creates data to populate an AttributeMapping file.
  def createAttributeMappingData(self, output_json):
    rows = list(output_json.keys())
    cols = list(output_json[rows[0]].keys())
    instances = {}
    for key in output_json:
      instances[key] = [str(output_json[key][param]) for param in output_json[key]]
    mapping_data = {
      'attributes': [{'attribute': param, 'source': 'upload', 'unit': ''} for param in cols],
      'instances': instances,
      'ontology_mapping_method': 'User curation'
    }
    return mapping_data
  
  # This method creates a stringified HTML table using the given json object.
  # This table can be appended to the app summary that is displayed to the user.
  def createSummary(self, output_json):
    rows = list(output_json.keys())
    cols = list(output_json[rows[0]].keys())

    # Top row: column names
    summary = "<table>"
    summary += "<tr>"
    for h in cols:
      summary += f'<th style="padding: 5px">{h}</th>'
    summary += "</tr>"

    # Add each row to the table
    for i in range(0, len(rows)):
      row = rows[i]

      # Open new row
      summary += "<tr style=\"border-top: 1px solid #505050;\">"

      # Define the style of each column
      bg = "#f4f4f4" if i % 2 == 1 else "transparent"
      style = f'style="padding: 5px 8px; background-color: {bg};"'

      # Add the value for each column
      for col in output_json[row]:
        summary += f'<td {style}">{output_json[row][col]}</td>'

      # Close row
      summary += "</tr>"

    summary += "</table>"
    return summary