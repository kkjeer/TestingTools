import logging
import os

# This class is responsible for manipulating data from inferred metamorphic relations and user-provided feedback.
class MetamorphicFeedbackUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
  
  def addFeedbackToRelationsOutput(self, output_json, categories):
    if output_json is None:
      return None
    
    result = {}

    rows = list(output_json.keys())

    for i in range(0, len(rows)):
      r = rows[i]
      category = self.getCategoryForRelation(r, categories)
      if r != '':
        result[r] = {
          **output_json[r],
          'feedback': category['feedback'],
          'expected_effect': str(category['expected_effect']),
          'explanation': str(category['explanation'])
        }

    return result
  
  def getCategoryForRelation(self, relation, categories):
    for i in range(0, len(categories)):
      relation_id = categories[i]['relation_id'][0]
      if relation_id == relation:
        return categories[i]
    return {'feedback': 'unknown', 'expected_effect': 'N/A', 'explanation': ''}