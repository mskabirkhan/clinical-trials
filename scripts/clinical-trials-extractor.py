import json
import csv
import requests
import re
import pandas as pd
from fuzzywuzzy import process
from bs4 import BeautifulSoup

# Download the root page.
page = requests.get(
    "https://www.clinicaltrialsregister.eu/ctr-search/search?query=covid-19&country=gb", verify = False)

# Get the webpage status.
print(page.status_code)

soup = BeautifulSoup(page.content, "html.parser")

ROOT_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=covid-19&country=gb'

root_contents = requests.get(ROOT_URL, verify=False)
soup = BeautifulSoup(root_contents.content, 'html.parser')
div_class = soup.find('div', {'class' :'outcome grid_12'}).text
page_total = re.search(r'Displaying page 1 of (\d+)', div_class)
if page_total:
    TOTAL_PAGES = int(page_total.group(1))

# Link to trials page download button.
pages_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/rest/download/summary?query=covid-19&country=gb&page={}&mode=current_page'
download_pages = []

# Extract the total number of pages.
for i in range(TOTAL_PAGES):
  download_pages.append(requests.get(pages_URL.format(i+1), verify=False))

merged_download_pages = b''
for d in download_pages:
  merged_download_pages += d.content

with open('data/clinical-trials.txt', 'wb') as f:
  f.write(merged_download_pages)

with open('data/clinical-trials.txt', encoding="utf8") as f:
  data = f.read()

# Separate each trail.
split_data = data.split('\n\n')
split_data.pop(0)

# Put each trail into a dictionary.
split_data_2 = []
for trial in split_data:
  split = trial.split('\n')
  split_data_2.append(split)

# Make key value pairs for each trail.
dictionaries = []
for trial in split_data_2:
  d = {}
  count = 1
  for pair in trial:
    if pair[:25] == 'Disease:                 ':
      d['Disease {}:               '.format(count)] = pair[25:]
      count += 1
    else:
      d[pair[:25]] = pair[25:]
  dictionaries.append(d)

keys = []
for dictionary in dictionaries:
  for k,v in dictionary.items():
    keys.append(k)
for key in keys:
  for dictionary in dictionaries:
    for k,v in dictionary.items():
      try:
        dictionary[key.strip()] = dictionary.pop(key)
      except KeyError:
        pass

# Save data to a JSON file.
with open('data/clinical-trials.json', 'w') as f:
  json.dump(dictionaries, f, indent=2)

# Save data to a CSV file.
df = pd.read_json(r'data/clinical-trials.json')
df.to_csv(r'data/clinical-trials.csv', index = None)

HDRUK_MEMBERS_CSV = 'PRIVATE/contacts.csv'

contacts_df = pd.read_csv(HDRUK_MEMBERS_CSV)

affiliation_list = []
for affil in contacts_df['Affiliation'].unique():
  if affil in ['PERSON ACCOUNT', 'COMPANY??', 'PERSONAL ACCOUNT']:
    pass
  else:
    affiliation_list.append(affil)

clinical_trials_df = pd.read_csv('data/clinical-trials.csv')

clinical_trials_HDRUK_df = clinical_trials_df.iloc[0:0]

for a in affiliation_list:

    for sponsor, score, matchrow in process.extract(a, clinical_trials_df['Sponsor Name:'], limit=100):
        if score >= 90:
          # print('%d%% partial match: "%s" with "%s" ' % (score, a, sponsor))
          clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.append(clinical_trials_df.iloc[matchrow])

clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.drop_duplicates()
clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.reset_index(drop=True)

# Save HDRUK trial data to JSON.
clinical_trials_HDRUK_df.to_csv(r'data/clinical-trials.HDRUK.csv', index = None)

# Save HDRUK trial data to JSON.
with open('data/clinical-trials.HDRUK.csv') as f:
  clinical_trials_HDRUK_dict_list = [{k: v for k, v in row.items()}
       for row in csv.DictReader(f, skipinitialspace=True)]
with open('data/clinical-trials.HDRUK.json', 'w') as f:
  json.dump(clinical_trials_HDRUK_dict_list, f, indent=2)