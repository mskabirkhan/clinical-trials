import json
import csv
import requests
import re
import pandas as pd
from fuzzywuzzy import process
from bs4 import BeautifulSoup

ROOT_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=covid-19&country=gb'
PAGES_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/rest/download/summary?query=covid-19&country=gb&page={}&mode=current_page'
HDRUK_MEMBERS_CSV = 'HDR-FILE/contacts.csv'


def get_total_pages(ROOT_URL):

  page = requests.get(
    "https://www.clinicaltrialsregister.eu/ctr-search/search?query=covid-19&country=gb", 
    verify = False)
  
  soup = BeautifulSoup(page.content, "html.parser")
  root_contents = requests.get(ROOT_URL, verify=False)
  soup = BeautifulSoup(root_contents.content, 'html.parser')
  div_class = soup.find('div', {'class' :'outcome grid_12'}).text
  page_total = re.search(r'Displaying page 1 of (\d+)', div_class)
  if page_total:
      total_pages = int(page_total.group(1))

  return total_pages


def extract_pages_to_txt(PAGES_URL, total_pages):

  # Extract the total number of pages
  download_pages = []
  for i in range(total_pages):
    download_pages.append(requests.get(PAGES_URL.format(i+1), verify=False))

  merged_download_pages = b''
  for d in download_pages:
    merged_download_pages += d.content

  with open('data/clinical-trials.txt', 'wb') as f:
    f.write(merged_download_pages)
  with open('data/clinical-trials.txt', encoding="utf8") as f:
    clinical_trials_data = f.read()

  return clinical_trials_data


def split_clinical_trial_data(clinical_trials_data):
  # Separate each trail and put into list.
  split_data = clinical_trials_data.split('\n\n')
  split_data.pop(0)

  # Separate each line of each trial.
  split_clinical_trials_data = []
  for trial in split_data:
    split = trial.split('\n')
    split_clinical_trials_data.append(split)

  return split_clinical_trials_data


def create_list_of_dicts(split_clinical_trials_data):
  # Make key value pairs for each trail.
  clinical_trials_dicts = []
  for trial in split_clinical_trials_data:
    d = {}
    count = 1
    for kv in trial:
      if kv[:25] == 'Disease:                 ':
        d['Disease {}:               '.format(count)] = kv[25:]
        count += 1
      else:
        d[kv[:25]] = kv[25:]
    clinical_trials_dicts.append(d)

  keys = []
  for d in clinical_trials_dicts:
    for k,v in d.items():
      keys.append(k)
  for key in keys:
    for d in clinical_trials_dicts:
      for k,v in d.items():    
        try:
          d[key.strip()] = d.pop(key)
        except KeyError:
          pass

  return clinical_trials_dicts


def write_json(data, filename, indent=2):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=indent)


def json_to_csv(json_file, csv_file):
  df = pd.read_json(json_file)
  df.to_csv(csv_file, index = None)


def clinical_trials_fuzzy_match(clinical_trials_csv, contacts_csv):

  contacts_df = pd.read_csv(contacts_csv)
  affiliation_list = []
  for affil in contacts_df['Affiliation'].unique():
    if affil in ['PERSON ACCOUNT', 'COMPANY??', 'PERSONAL ACCOUNT']:
      pass
    else:
      affiliation_list.append(affil)

  clinical_trials_df = pd.read_csv(clinical_trials_csv)
  clinical_trials_HDRUK_df = clinical_trials_df.iloc[0:0]

  for a in affiliation_list:
      for sponsor, score, matchrow in process.extract(a, clinical_trials_df['Sponsor Name:'], limit=100):
          if score >= 90:
            # print('%d%% partial match: "%s" with "%s" ' % (score, a, sponsor))
            clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.append(clinical_trials_df.iloc[matchrow])

  clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.drop_duplicates()
  clinical_trials_HDRUK_df = clinical_trials_HDRUK_df.reset_index(drop=True)

  return clinical_trials_HDRUK_df


def write_csv(clinical_trials_HDRUK_df, clinical_trials_HDRUK_csv):
  clinical_trials_HDRUK_df.to_csv(clinical_trials_HDRUK_csv, index = None)


def csv_to_json(clinical_trials_HDRUK_csv, clinical_trials_HDRUK_json, indent=2):
  with open(clinical_trials_HDRUK_csv) as f:
    clinical_trials_HDRUK_dict_list = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]
  with open(clinical_trials_HDRUK_json, 'w') as f:
    json.dump(clinical_trials_HDRUK_dict_list, f, indent=indent)


def main():

  total_pages = get_total_pages(ROOT_URL)
  clinical_trials_data = extract_pages_to_txt(PAGES_URL, total_pages)

  split_clinical_trials_data = split_clinical_trial_data(clinical_trials_data)
  clinical_trials_dicts = create_list_of_dicts(split_clinical_trials_data)

  write_json(clinical_trials_dicts, 'data/clinical-trials.json')
  json_to_csv(r'data/clinical-trials.json', r'data/clinical-trials.csv')

  clinical_trials_HDRUK_df = clinical_trials_fuzzy_match('data/clinical-trials.csv', HDRUK_MEMBERS_CSV)

  write_csv(clinical_trials_HDRUK_df, r'data/clinical-trials.HDRUK.csv')
  csv_to_json('data/clinical-trials.HDRUK.csv', 'data/clinical-trials.HDRUK.json')


if __name__ == "__main__":
  main()
