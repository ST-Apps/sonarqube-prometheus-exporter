from prometheus_client import start_http_server, Metric, REGISTRY
from requests.auth import HTTPBasicAuth
import re
import json
import requests
import sys
import time
import collections
import humanfriendly

crumbs = False
def flatten(dictionary, parent_key=False, separator='_'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in list(dictionary.items()):
        if crumbs: print(('checking:',key))
        new_key = (re.sub('[^A-Za-z0-9]+', '', str(parent_key)) + separator + re.sub('[^A-Za-z0-9]+', '', key) if parent_key else key).lower()
        
        if isinstance(value, collections.MutableMapping):
            if crumbs: print((new_key,': dict found'))
            if not list(value.items()):
                if crumbs: print(('Adding key-value pair:',new_key,None))
                items.append((new_key,None))
            else:
                items.extend(list(flatten(value, new_key, separator).items()))
        elif isinstance(value, list):
            if crumbs: print((new_key,': list found'))
            if len(value):
                for k, v in enumerate(value):
                    items.extend(list(flatten({str(k): v}, new_key).items()))
            else:
                if crumbs: print(('Adding key-value pair:',new_key,None))
                items.append((new_key,None))
        else:
            if crumbs: print(('Adding key-value pair:',new_key,value))
            items.append((new_key, value))
    return dict(items)

class JsonCollector(object):
  def __init__(self, endpoint, username, password):
    self._endpoint = endpoint + '/api/system/info'
    self._auth = HTTPBasicAuth(username, password)    

  def collect(self):
    # Fetch the JSON and flatten it
    print("Fetching from " + self._endpoint)
    response = flatten(json.loads(requests.get(self._endpoint, auth=self._auth).content.decode('UTF-8')))
    count = 0
    for key,value in list(response.items()):

        # Extract numeric values
        if isinstance(value, (int, float)):
            try:
                metric = Metric(key, '', 'info')
                metric.add_sample(key, value=value, labels={})
                count+=1      
                yield metric
            except:
                print("Skipping metric with key: " + key)
                continue
        
        # Extract sizes
        try:
            value_bytes = humanfriendly.parse_size(str(value))
            key = key + "_bytes"
            try:
                metric = Metric(key, '', 'info')
                metric.add_sample(key, value=value_bytes, labels={})
                count+=1      
                yield metric
            except:
                print("Skipping metric with key: " + key)
                continue
        except:
            pass

        # Extract percentages
        percentage_groups = re.search(r'^(\d+(\.\d+))?%.*$', str(value))
        if percentage_groups:
            value_percentage = float(percentage_groups.group(1))/100
            key = key + "_percent"
            try:
                metric = Metric(key, '', 'info')
                metric.add_sample(key, value=value_percentage, labels={})
                count+=1      
                yield metric
            except:
                print("Skipping metric with key: " + key)
                continue

    print("Exported " + str(count) + " metrics.")

if __name__ == '__main__':
  # Usage: exporter.py port endpoint username password polling
  
  print("Starting with args: " + str(sys.argv[1:]))
  
  start_http_server(int(sys.argv[1]))
  REGISTRY.register(JsonCollector(sys.argv[2], sys.argv[3], sys.argv[4]))

  while True: time.sleep(int(sys.argv[5]))
