# -*- coding: utf-8 -*-
"""
Dash app to create a dashboard showing 
a diagonal heatmap of Toronto City Council 
vote similarity scores

Damien Moule
"""

import dash
from dash import Dash
import dash_bootstrap_components as dbc

#set up app
#enable separate pages to be used in the dashboard
#use dash bootstrap component themes and icons
app = Dash(__name__,
           use_pages=True,
           suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.MINTY,
                                 dbc.icons.BOOTSTRAP])

#if testing locally comment out this line
#and go to http://127.0.0.1:8050/ to view
server = app.server

#navigation bar
navbar = dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink("About",
                                        href=dash.page_registry['pages.about']['path'])),
                dbc.NavItem(dbc.NavLink(class_name="bi bi-github",
                                        href="https://github.com/damienmoule")),
                dbc.NavItem(dbc.NavLink(class_name="bi bi-twitter",
                                        href="https://x.com/damienmoule"))
            ],
            brand="Toronto City Council Voting Similarity",
            brand_href=dash.page_registry['pages.home']['path'],
            color="primary",
            dark=True
         )

#layout has the navbar at the top and then 
#either the home page or the about page beneath
app.layout = dbc.Container(
    [
         navbar,
         #individual pages beneath
         dash.page_container,

    ],
    fluid=True,
)

if __name__ == '__main__':
    app.run(debug=True)
