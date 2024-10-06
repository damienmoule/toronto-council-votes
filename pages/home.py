# -*- coding: utf-8 -*-
"""
Home page of dashboard

Display a diagonal heatmap of council vote
similarity scores
"""

import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from pathlib import Path

#initate page and path
dash.register_page(__name__,path='/')

base = Path.cwd()

#load tmmis voting data from spreadsheets
tmmis_file = pd.ExcelFile(base.joinpath("utils","similarity_tmmis.xlsx"))
tmmis_dict = dict.fromkeys(tmmis_file.sheet_names)
for keys in tmmis_dict:
    tmmis_dict[keys] = pd.read_excel(tmmis_file,
                                     keys,
                                     index_col=0)
tmmis_file.close()

#load city hall watcher voting data from spreadsheets
chw_file = pd.ExcelFile(base.joinpath("utils","similarity_chw.xlsx"))
chw_dict = dict.fromkeys(chw_file.sheet_names)
for keys in chw_dict:
    chw_dict[keys] = pd.read_excel(chw_file,
                                   keys,
                                   index_col=0)
chw_file.close()

#load the list of temporary councillors and early departures
temp_and_early = pd.read_csv('utils/temporary_early_departures.csv',index_col=0)

#combine the two datasets into a single dictionary and get keys for use in callbacks 
votes_dict = {'All Recorded Votes (TMMIS)':tmmis_dict,
              'Key Votes (City Hall Watcher)':chw_dict}
data_keys = list(votes_dict.keys())
term_keys = list(tmmis_dict.keys())
sort_keys = list(votes_dict[data_keys[0]][term_keys[3]])

#control panel for heatmap
controls = dbc.Card(
    [
         #dropdown menu for data source (TMMIS or city hall watcher)
         dbc.Row(
             [
                 html.Label('Data Source:'),
                 dcc.Dropdown(data_keys,
                              data_keys[0],
                              id='data-source',
                              clearable=False,
#                              style={'font-size':10}
                              ),
             ]
         ),
         #dropdown menu for council term
         dbc.Row(
             [
                 html.Label('Term:'),
                 dcc.Dropdown(term_keys,
                              term_keys[-1],
                              id='term',
                              clearable=False,
#                              style={'font-size':10}
                              ),       
             ]
         ),
         #dropdown menu to sort by councillor
         dbc.Row(
             [
                 html.Label('Sort By Similarity To:'),
                 dcc.Dropdown(id='sort',
                              clearable=False,
#                              style={'font-size':10}
                              ),
             ]
         ),
         #checkboxes for temporary councillors and early departures
         dbc.Row(
             [
                 html.Label('Include:'),
                 dcc.Checklist(
                     options=[
                               {'label':' Early Departures','value':'Early Departures'},
                               {'label':' Temporary Councillors','value':'Temporary Councillors'}
                             ],
                               id='filter-options')
             ]
         ),
    ],
    body = True
)

#layout of the heatmap page
layout = dbc.Container(
    [
         dbc.Row(
             [
                 dbc.Col(controls, md=3),
                 dbc.Col(dcc.Graph(id='vote-heatmap'), 
                         md=9)
             ]
         )
    ],
    fluid=True,
)

@callback(
    Output('vote-heatmap','figure'),
    Output('sort','options'),
    Output('sort','value'),
    Input('data-source','value'),
    Input('term','value'),
    Input('filter-options','value'),
    Input('sort','value')
    )

#heatmap of voting similarity, modified by dataset, term, 
#temporary councillors and sorted by user defined input
def update_heatmap(data_source,term,filter_options,sort_by):
    #start from the full voting dataframe for the current term,
    #remove and sort councillors as necessary
    df = votes_dict[data_source][term]

    #check if the temporary councillors or early departures
    #options have been selected. If not, remove them from
    #the dataframe
    for option,names in temp_and_early.loc[term].items():
        if not filter_options or option not in filter_options:
            if pd.isna(names) != True: #some terms have no early departures/temp councillors
                dropped_councillors = names.split(';')
                for dropped in dropped_councillors:
                    if dropped in df:
                        df = df.drop(dropped,axis=1)
                        df = df.drop(dropped,axis=0)   
    
    #sort by the name selected in the sort dropdown
    if sort_by in df:
        df = df.sort_values(by=sort_by,
                            ascending=False)
        df = df.sort_values(by=sort_by,
                            axis=1,
                            ascending=False)
        #need to handle a case where there's a 100% agreement
        #and the sort puts the wrong name first
        #so instead force the search term to be first
        cols = list(df)
        if cols[0] != sort_by:
            cols.insert(0,cols.pop(cols.index(sort_by)))
            df = df.loc[:,cols]
            df = df.loc[cols,:]
            
    #refresh the keys in the dropdowns
    sort_keys = sorted(list(df))
    sort_value = list(df)[0]
    if len(sort_keys)>43:
        name_font_size = 6
    else:
        name_font_size = 9

    #create a mask for the top right corner of the heatmap
    mask = np.triu(np.ones_like(df, dtype=bool))
    df = df.mask(mask)
    
    #heatmap
    fig = go.Figure(data=go.Heatmap(z=df.to_numpy().round(2)*100,
                                x=df.index.values,
                                y=df.columns.values,
                                colorscale='tealrose_r',
                                colorbar_ticksuffix='%',
                                hoverongaps=False,
                                hovertemplate='%{x} <br>%{y} </br>Vote Similarity: %{z}%',
                                name=''))

    #figure options
    fig.update_layout(
                  width=700, height=600,
                  xaxis_showgrid=False,
                  xaxis={'side': 'bottom'},
                  yaxis_showgrid=False,
                  yaxis_autorange='reversed', 
                  margin=dict(l=20,r=20,t=20,b=120),
                  plot_bgcolor='white',
                  font=dict(size=name_font_size)
                  )

    fig.update_traces(colorbar_thickness=20,
                      selector=dict(type='heatmap'))                              
    
    return fig, sort_keys, sort_value
