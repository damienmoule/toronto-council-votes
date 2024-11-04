An app which displays a chart summarizing the voting records of Toronto city councillors. Created with the Dash Python package.

This chart shows the similarity in voting records between Toronto City Councillors. Similarity is expressed as a percentage from 0% (councillors never voted the same way) to 100% (always voted the same). Votes where a councillor was absent do not contribute to their score.
                         
Two datasets are available for council terms dating back to 2010. The first comes from the [Toronto Open Data Portal](https://open.toronto.ca/dataset/members-of-toronto-city-council-voting-record/). This shows the votes recorded form the Toronto Meeting Management Information System (TMMIS). When using this dataset, the similarity for all non-unanimous recorded votes is shown. Votes are only recorded when requested by a councillor or required by council's procedures. Unanimous votes were removed as there are many procedural votes which typically pass unanimously, and I don't find them interesting.
                         
The second dataset is from the scorecards of key votes maintained by Matt Elliot of [City Hall Watcher](https://toronto.cityhallwatcher.com/).
                         
Early Departures refers to councillors who left due to resignation/removal/death and were replaced through by-election within the same term. Temporary Councillors refers to councillors who were appointed by Council to fill a vacany. This is typically only done when there is not enough time for a by-election to take place before the next municipal election.

STRUCTURE

The app (app.py) has two supporting pages (home.py and about.py). The home page displays the figures based on the processed data stored in utils (similarity_chw.xlsx and similarity_tmmis.xlsx). The raw voting data (the .csv files) is processed by the utility scripts (processchwvotes.py and processtmmisvotes.py). 
