import json
import csv
import requests
import re
import pandas as pd
from fuzzywuzzy import process
from bs4 import BeautifulSoup

CLINICAL_TRIALS_ROOT_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query=covid-19&country=gb'
FULL_TRIALS_DOWNLOAD_URL = 'https://www.clinicaltrialsregister.eu/ctr-search/rest/download/full?query=covid-19&country=gb&page={}&mode=current_page'

def find_number_of_pages(ROOT_URL):
  
  root_contents = requests.get(ROOT_URL, verify=False)
  soup = BeautifulSoup(root_contents.content, 'html.parser')
  div_class = soup.find('div', {'class' :'outcome grid_12'}).text
  page_total = re.search(r'Displaying page 1 of (\d+)', div_class)

  TOTAL_PAGES = int(page_total.group(1))

  return TOTAL_PAGES

def get_full_trials(DOWNLOAD_URL, TOTAL_PAGES):

  # Get full clinical trial info from all pages
  download_full_pages = []
  for i in range(TOTAL_PAGES):
    download_full_pages.append(requests.get(DOWNLOAD_URL.format(i+1), verify=False))

  # Merge contents of each page together
  merged_full_download_pages = b''
  for d in download_full_pages:
    merged_full_download_pages += d.content
  with open('data/clinical-trials-full.txt', 'wb') as f:
    f.write(merged_full_download_pages)
  with open('data/clinical-trials-full.txt', encoding="utf8") as f:
    full_trial_data = f.read()

  return full_trial_data

def create_list_of_trial_dicts(full_trial_data):

  split_full_trial_data = full_trial_data.split('\nSummary')

  # Remove unwanted data
  split_full_trial_data.pop(0)

  split_full_trial_data_2 = []
  for trial in split_full_trial_data:
    s = '\nA.'
    split = [s+e for e in trial.split(s) if e]
    split[0] = split[0][3:]
    split_full_trial_data_2.append(split)

  split_full_trial_data_3 = []
  for trial in split_full_trial_data_2:
    s = '\nB.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_3.append(trial)

  split_full_trial_data_4 = []
  for trial in split_full_trial_data_3:
    s = '\nD.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_4.append(trial)

  split_full_trial_data_5 = []
  for trial in split_full_trial_data_4:
    s = '\nE.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_5.append(trial)

  split_full_trial_data_6 = []
  for trial in split_full_trial_data_5:
    s = '\nF.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_6.append(trial)

  split_full_trial_data_7 = []
  for trial in split_full_trial_data_6:
    s = '\nG.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_7.append(trial)

  split_full_trial_data_8 = []
  for trial in split_full_trial_data_7:
    s = '\nN.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_8.append(trial)

  split_full_trial_data_9 = []
  for trial in split_full_trial_data_8:
    s = '\nP.'
    split = [s+e for e in trial[-1].split(s) if e]
    split[0] = split[0][3:]
    trial = trial[:-1] + split
    split_full_trial_data_9.append(trial)

  for trial in split_full_trial_data_9:
    for i in range(len(trial)):
      trial[i] = trial[i][1:]

  split_full_trial_data_10 = []
  for trial in split_full_trial_data_9:
    s = '\n'
    split = [e for e in trial[0].split(s) if e]
    trial = split + trial[1:]
    split_full_trial_data_10.append(trial)

  return split_full_trial_data_10

def create_key_for_sections(split_full_trial_data):
  A_subsets = []
  B_subsets = []
  D_subsets = []
  E_subsets = []
  F_subsets = []
  G_subsets = []
  N_subsets = []
  P_subsets = []
  Summary_subsets = []
  for trial in split_full_trial_data:
    A_subset = [l for l in trial if l.startswith('A.')]
    A_subsets.append(A_subset)
    B_subset = [l for l in trial if l.startswith('B.')]
    B_subsets.append(B_subset)
    D_subset = [l for l in trial if l.startswith('D.')]
    D_subsets.append(D_subset)
    E_subset = [l for l in trial if l.startswith('E.')]
    E_subsets.append(E_subset)
    F_subset = [l for l in trial if l.startswith('F.')]
    F_subsets.append(F_subset)
    G_subset = [l for l in trial if l.startswith('G.')]
    G_subsets.append(G_subset)
    N_subset = [l for l in trial if l.startswith('N.')]
    N_subsets.append(N_subset)
    P_subset = [l for l in trial if l.startswith('P.')]
    P_subsets.append(P_subset)
    Summary_subset = [dict(l.split(':', 1) for l in trial if not l.startswith('A.') and not l.startswith('B.') \
                          and not l.startswith('D.') and not l.startswith('E.') and not l.startswith('F.') \
                          and not l.startswith('G.') and not l.startswith('N.') and not l.startswith('P.'))]
    Summary_subsets.append(Summary_subset)

  for i in range(len(B_subsets)):
    for j in range(len(B_subsets[i])):
      if '\nSponsor ' in B_subsets[i][j]:
        split = [l for l in B_subsets[i][j].split('\n')]
        B_subsets[i][j:j+1] = split[0], split[1]

  for i in range(len(A_subsets)):
    A_subsets[i] = {'A. Protocol Information': A_subsets[i]}
    B_subsets[i] = {'B. Sponsor Information': B_subsets[i]}
    D_subsets[i] = {'D. IMP Identification': D_subsets[i]}
    E_subsets[i] = {'E. General Information on the Trial': E_subsets[i]}
    F_subsets[i] = {'F. Population of Trial Subjects': F_subsets[i]}
    G_subsets[i] = {'G. Investigator Networks to be involved in the Trial': G_subsets[i]}
    N_subsets[i] = {'N. Review by the Competent Authority or Ethics Committee in the country concerned': N_subsets[i]}
    P_subsets[i] = {'P. End of Trial': P_subsets[i]}


  for i in range(len(A_subsets)):
    A_subsets[i].update(B_subsets[i])
    A_subsets[i].update(D_subsets[i])
    A_subsets[i].update(E_subsets[i])
    A_subsets[i].update(F_subsets[i])
    A_subsets[i].update(G_subsets[i])
    A_subsets[i].update(N_subsets[i])
    A_subsets[i].update(P_subsets[i])
    A_subsets[i].update(Summary_subsets[i][0])

  full_trials_list_dict = A_subsets

  # Remove all non GB clinical trials
  count = 0
  for i in range(len(full_trials_list_dict)):
    for k,v in full_trials_list_dict[i-count].items():
      if k == 'Link' and '/GB/' not in v:
        full_trials_list_dict.pop(i-count)
        count += 1

  return full_trials_list_dict

def write_json(data, filename, indent=2):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=indent)

def json_to_csv(json_file, csv_file):
  df = pd.read_json(json_file)
  df.to_csv(csv_file, index = None)

def main():

  # Find each trial page and merge contents of txt files 
  TOTAL_PAGES = find_number_of_pages(CLINICAL_TRIALS_ROOT_URL)
  full_trial_data = get_full_trials(FULL_TRIALS_DOWNLOAD_URL, TOTAL_PAGES)

  # Split trial data and write to json and csv format
  split_full_trial_data = create_list_of_trial_dicts(full_trial_data)
  full_trials_list_dict = create_key_for_sections(split_full_trial_data)
  write_json(full_trials_list_dict, 'data/clinical-trials-full.json')
  json_to_csv(r'data/clinical-trials-full.json', r'data/clinical-trials-full.csv')

if __name__ == "__main__":
    main()
