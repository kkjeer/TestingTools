import logging
import os

# This class is responsible for manipulating data from app runs and user-provided feedback.
class TestFeedbackUtil:
  def __init__(self, config):
    self.config = config
    self.callback_url = os.environ['SDK_CALLBACK_URL']
    self.ws_url = config["workspace-url"]
    self.shared_folder = config['scratch']
    logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                        level=logging.INFO)
  
  def addFeedbackToExplorerOutput(self, output_json, categories):
    if output_json is None:
      return None
    
    result = {}

    rows = list(output_json.keys())

    for i in range(0, len(rows)):
      r = rows[i]
      category = self.getCategoryForRun(r, categories)
      if r != '':
        result[r] = {
          **output_json[r],
          'feedback': category['feedback'],
          'expected_value': str(category['expected_value'])
        }

    return result
  
  def getCategoryForRun(self, run, categories):
    for i in range(0, len(categories)):
      run_id = categories[i]['run_id'][0]
      if run_id == run:
        return categories[i]
    return {'feedback': 'unknown', 'expected_value': None}