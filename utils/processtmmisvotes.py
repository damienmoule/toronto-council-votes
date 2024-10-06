# -*- coding: utf-8 -*-
"""
Loading the Toronto City Council Voting Data
from two TMMIS voting records

load and process all voting data, calculate voting
similarity matrices and save diagonal matrices
to excel files
"""

import numpy as np
import pandas as pd
from votesimilarity import vote_similarity
    
tmmis_files = {'2010-2014':'member-voting-record-2010-2014.csv',
               '2014-2018':'member-voting-record-2014-2018.csv',
               '2018-2022':'member-voting-record-2018-2022.csv',
               '2022-2026':'member-voting-record-2022-2026.csv'}

mayors = ['Rob Ford','John Tory',
          'John Tory', ['Olivia Chow','Ausma Malik']] #Malik added as a tie breaker in the sort

tmmis_writer = pd.ExcelWriter('similarity_tmmis.xlsx')
    
for i,(k,f) in enumerate(tmmis_files.items()):
    
    #load TMMIS all voting data from spreadsheet
    votes = pd.read_csv(f, usecols=[2,3,4,5,6,8,9,10,11])
    votes = votes.fillna('')
    votes = votes.replace('BailÃ£o','Bailão')
    if k == '2014-2018':
        votes = votes.replace('Berardinetti','Holland')

    #committees = ['City Council','Executive Committee']
    #select only city council votes (ignore committees)
    votes = votes[votes['Committee']=='City Council']

    #remove unanimous votes
    votes[['VoteRes','Count1']] = votes['Result'].str.split(',',expand=True)
    votes[['Count1','Count2']] = votes['Count1'].str.split('-',expand=True)
    votes = votes[votes['Count1']!='0']
    votes = votes[votes['Count2']!='0']
    
    #remove general bills which have poor descriptions
    #which messes up the unique identifier
    item_filter = votes['Agenda Item #'].str.contains('BL')
    votes = votes[~item_filter]

    #need to make a unique identifier for each vote 
    #since many have duplicated names
    votes['VoteDes']= votes['Agenda Item #'] + " " \
                    + votes['Motion Type'] + " " \
                    + votes['Vote Description'] + " " \
                    + votes['Result'] + " " \
                    + votes['Date/Time']
    votes['Councillor'] = votes['First Name'] \
                        + ' ' + votes['Last Name']
    votes = votes.drop(columns=['First Name', 'Last Name','Committee',
                                'Agenda Item #','Motion Type',
                                'Vote Description','Date/Time',
                                'Result','VoteRes','Count1','Count2'])

    #there are a few duplicated votes in the data, 
    #so we need to drop them
    votes = votes.drop_duplicates()

    #reshape with votes as columns 
    votes = votes.pivot(index='VoteDes',
                        columns=['Councillor'], 
                        values=['Vote'])
    votes = votes.droplevel(level=0, axis=1).transpose()

    #process the data to make it numerical and remove absents and vacants
    votes = votes.replace(('Yes','No','Absent','Vacant'),
                          (1,0,np.nan,np.nan))

    #calculate similarity matrix in voting records between councillors
    similarity = vote_similarity(votes)
    #sort by mayoral agreement
    similarity = similarity.sort_values(by=mayors[i],
                                        ascending=False)
    similarity = similarity.sort_values(by=mayors[i],
                                        axis=1,
                                        ascending=False)

    #generate mask for the upper triangle
#    mask = np.triu(np.ones_like(similarity, dtype=bool))
#    similarity = similarity.mask(mask)
    
    similarity.to_excel(tmmis_writer, sheet_name=k)

tmmis_writer.close()