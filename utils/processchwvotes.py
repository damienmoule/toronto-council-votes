# -*- coding: utf-8 -*-
"""
Loading the Toronto City Council Voting Data
from City Hall Watcher (Matt Elliot) scorecards

load and process all voting data, calculate voting
similarity matrices and save diagonal matrices
to excel files
"""

import numpy as np
import pandas as pd
from votesimilarity import vote_similarity

chw_files = {'2010-2014':'Council Scorecard 2010-2014.csv',
             '2014-2018':'Council Scorecard 2014-2018.csv',
             '2018-2022':'Council Scorecard 2018-2022.csv',
             '2022-2026':'Council Scorecard 2023-2026.csv'}

tory_3t = 'Council Scorecard 2022-2023.csv'

#each spreadsheet uses a slightly different format
#so need some lists to help process them
dropped_columns = [['Last Name','Ward','Unnamed: 2','Ford Nation Percentage','Ford Nation Percentage.1','Ford Nation Percentage.2','Ford Nation Percentage.3','Ford Nation Percentage.4','Ford Nation Percentage.5','Ford Nation Percentage.6'],
                   ['SORT','SORT.1'],
                   ['SORT','SORT.1'],
                   ['SORT','SORT.1']]

dropped_rows = [[0,46,47,48,49],
                [0,1,47,48,49,50],
                [0,1,2,29,30,31,32],
                [0,1,2,29,30,31]]

councillor_column = ['Councillor','Unnamed: 3','Unnamed: 3','Unnamed: 6']

mayors = ['Rob Ford','John Tory',
          'John Tory', 'Olivia Chow']

chw_writer = pd.ExcelWriter('similarity_chw.xlsx')

for i,(k,f) in enumerate(chw_files.items()):

    #load City Hall Watcher voting data from spreadsheet
    votes = pd.read_csv(f)
    votes = votes.fillna('')

    #rename column with councillor names and make it the dataframe index
    votes = votes.rename(columns={councillor_column[i]:'Councillor'})
    votes['Councillor'] = votes['Councillor'].str.split('\n').str[0]

    #remove unused data
    votes = votes.drop(columns=dropped_columns[i])
    votes = votes.drop(columns=list(votes.filter(regex='Unnamed')))
    votes = votes.drop(dropped_rows[i])

    #for 2022-2026, have to deal with the time before Tory's resignation
    #which is stored in another file and needs to be merged
    if k == '2022-2026':
        #load the pre-resignation file and make the same formatting changes as the rest
        pre_resignation = pd.read_csv(tory_3t)
        pre_resignation = pre_resignation.fillna('')
        pre_resignation = pre_resignation.drop(columns=['SORT','SORT.1','Unnamed: 2',
                                                        'Unnamed: 4','Unnamed: 5','Unnamed: 6',
                                                        'Unnamed: 15','Unnamed: 16','Unnamed: 17',
                                                        'Unnamed: 18'])
        pre_resignation = pre_resignation.drop([0,1,2,29,30,31])
        pre_resignation = pre_resignation.rename(columns={'Unnamed: 3':'Councillor'})
        pre_resignation['Councillor'] = pre_resignation['Councillor'].str.split('\n').str[0]
        #merge the pre-resignation dataframe into the votes dataframe
        votes = votes.merge(pre_resignation,how='outer')

    #for wards that have replacement councillors
    #figure out where to one councillor's time starts and the
    #other's ends and then label accordingly
    replacements = votes[votes['Councillor'].str.contains(' /')]
    
    for index,row in replacements.iterrows():
        vacant_start = (row == 'Vacant').idxmax()
        replacements.loc[index,:vacant_start] = "Absent"
        replacements.loc[index,'Councillor']=row['Councillor']
        votes.loc[index,vacant_start:] = "Absent"

    #label the names in the two dataframes
    votes['Councillor'] = votes['Councillor'].str.split(' /').str[0]
    replacements['Councillor'] = replacements['Councillor'].str.split(' / ').str[1]

    #append the replacements votes as new lines in the main dataframe
    votes = pd.concat([votes,replacements],ignore_index=True)
    votes = votes.set_index('Councillor')
    
    #process the data to make it numerical and remove absents and vacants
    votes = votes.replace(('Yes','No','Absent','Vacant',
                           'Conflict of Interest','Conflict of interest',
                           'yes','no','NO','','Consensus'),
                          (1,0,np.nan,np.nan,
                           np.nan,np.nan,
                           1,0,0,np.nan,1))

    #calculate similarity matrix in voting records between councillors
    similarity = vote_similarity(votes)
    #sort by mayoral agreement
    similarity = similarity.sort_values(by=mayors[i],
                                        ascending=False)
    similarity = similarity.sort_values(by=mayors[i],
                                        axis=1,
                                        ascending=False)

    # Generate a mask for the upper triangle
#    mask = np.triu(np.ones_like(similarity, dtype=bool))
#    similarity = similarity.mask(mask)

    similarity.to_excel(chw_writer, sheet_name=k)

chw_writer.close()