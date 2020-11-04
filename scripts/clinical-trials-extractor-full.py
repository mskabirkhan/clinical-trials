import json
import csv
import requests
import re
import pandas as pd
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

  indices_B = []
  indices_D_3 = []
  indices_D_8 = []
  for trial in split_full_trial_data_10:
    index_B = [i for i in trial if i.startswith('B.1.1 Name of Sponsor:') \
              or i.startswith('D. IMP Identification')]
    ind_B = []
    for i in index_B:
      ind_B.append(trial.index(i))
    indices_B.append([index_B, ind_B])

    index_D_3 = [i for i in trial if i.startswith('D.IMP:') \
                or i.startswith('D.8 Information on Placebo')]
    ind_D_3 = []
    for i in index_D_3:
      ind_D_3.append(trial.index(i))
    indices_D_3.append([index_D_3, ind_D_3])

    index_D_8 = [i for i in trial if i.startswith('D.8 Placebo:') \
                or i.startswith('E. General Information on the Trial')]
    ind_D_8 = []
    for i in index_D_8:
      ind_D_8.append(trial.index(i))
    indices_D_8.append([index_D_8, ind_D_8])

  for i in range(len(split_full_trial_data_10)):
    for j in range(len(indices_B[i][0])):
      if j < len(indices_B[i][0])-1:
        for k in range(indices_B[i][1][j], indices_B[i][1][j+1]):
          split_full_trial_data_10[i][k] = 'B.S{}.'.format(j+1) + split_full_trial_data_10[i][k][2:]
    for j in range(len(indices_D_3[i][0])):
      if j < len(indices_D_3[i][0])-1:
        for k in range(indices_D_3[i][1][j], indices_D_3[i][1][j+1]):
          split_full_trial_data_10[i][k] = 'D.I{}.'.format(j+1) + split_full_trial_data_10[i][k][2:]
    for j in range(len(indices_D_8[i][0])):
      if j < len(indices_D_8[i][0])-1:
        for k in range(indices_D_8[i][1][j], indices_D_8[i][1][j+1]):
          split_full_trial_data_10[i][k] = 'D.P{}.'.format(j+1) + split_full_trial_data_10[i][k][2:]

  # Select lines containing colon
  for trial in split_full_trial_data_10:
    trial[:] = [l for l in trial if any(sub in l for sub in [':'])]

  # Make key value pairs
  split_full_trial_data_11 = []
  for i in range(len(split_full_trial_data_10)):
    split_full_trial_data_11.append(dict(s.split(':', 1) for s in split_full_trial_data_10[i]))

  # Remove all non GB clinical trials
  count = 0
  for i in range(len(split_full_trial_data_11)):
    for k,v in split_full_trial_data_11[i-count].items():
      if k == 'Link' and '/GB/' not in v:
        split_full_trial_data_11.pop(i-count)
        count += 1

  # Strip trailing blank space in value
  for trial in split_full_trial_data_11:
    for k,v in trial.items():
      value = trial[k].strip()
      trial[k] = value

  return split_full_trial_data_11


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
    A_subset = {key: value for key, value in trial.items() if key.startswith('A.')}
    A_subsets.append(A_subset)
    B_subset = {key: value for key, value in trial.items() if key.startswith('B.')}
    B_subsets.append(B_subset)
    D_subset = {key: value for key, value in trial.items() if key.startswith('D.')}
    D_subsets.append(D_subset)
    E_subset = {key: value for key, value in trial.items() if key.startswith('E.')}
    E_subsets.append(E_subset)
    F_subset = {key: value for key, value in trial.items() if key.startswith('F.')}
    F_subsets.append(F_subset)
    G_subset = {key: value for key, value in trial.items() if key.startswith('G.')}
    G_subsets.append(G_subset)
    N_subset = {key: value for key, value in trial.items() if key.startswith('N.')}
    N_subsets.append(N_subset)
    P_subset = {key: value for key, value in trial.items() if key.startswith('P.')}
    P_subsets.append(P_subset)
    Summary_subset = {key: value for key, value in trial.items() if not key.startswith('A.') and not key.startswith('B.') \
                      and not key.startswith('D.') and not key.startswith('E.') and not key.startswith('F.') \
                      and not key.startswith('G.') and not key.startswith('N.') and not key.startswith('P.')}
    Summary_subsets.append(Summary_subset)

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
  for i in range(len(Summary_subsets)):
    Summary_subsets[i].update(A_subsets[i])

  full_trials_list_dict = Summary_subsets

  return full_trials_list_dict


def write_json(data, filename, indent=2):
  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=indent)


def write_csv(list_of_flattened_dicts, csv_file):
  df = pd.DataFrame(list_of_flattened_dicts)
  df.to_csv(csv_file, index = None)


def main():

  # Find each trial page and merge contents of txt files
  TOTAL_PAGES = find_number_of_pages(CLINICAL_TRIALS_ROOT_URL)
  full_trial_data = get_full_trials(FULL_TRIALS_DOWNLOAD_URL, TOTAL_PAGES)

  # Split trial data and write to json and csv format
  split_full_trial_data = create_list_of_trial_dicts(full_trial_data)
  full_trials_list_dict = create_key_for_sections(split_full_trial_data)
  write_json(full_trials_list_dict, 'data/clinical-trials-full.json')
  write_csv(split_full_trial_data, r'data/clinical-trials-full.csv')



if __name__ == "__main__":
    main()