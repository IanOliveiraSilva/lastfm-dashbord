import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import urllib.request

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                        'https://use.fontawesome.com/releases/v5.8.1/css/all.css']

class LastFmDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.layout = self.layout()

    def layout(self):
        return html.Div([
            html.H1(
                'Last.fm Dashbord', 
                style={
                    'textAlign': 'center', 
                    'padding': '20px', 
                    'fontWeight':'bold',
                    'color': 'black',
                    'borderRadius': '15px', 
                }
            ),
            html.Div(
            children=[
            dcc.Input(
                id='user-input', 
                type='text', 
                placeholder='Enter Last.fm username', 
                style={
                     'width': '50%', 
                'height': '50px',
                'fontSize': '20px',
                'padding': '10px',
                'borderRadius': '15px',
                'border': '1px solid #7a4bd8',
                'outline': 'none',
                'boxShadow': '0px 0px 5px 1px #5229b1'
                }
            ),
            html.Br(),
            html.Br(),
            dcc.Dropdown(
                id='period-input',
                options=[
                    {'label': '7 days', 'value': '7day'},
                    {'label': '1 month', 'value': '1month'},
                    {'label': '3 months', 'value': '3month'},
                    {'label': '6 months', 'value': '6month'},
                    {'label': '12 months', 'value': '12month'}
                ],
                placeholder='Period: ',
                value='7day',
                style={
                    'width': '50%', 
                'fontSize': '20px',
                'borderRadius': '15px',
                }
            ),
            html.Br(),
            html.Button(
                'Submit', 
                id='submit-button', 
                style={
                   'width': '50%', 
                'backgroundColor': '#a16dfe', 
                'fontSize': '20px', 
                'color': 'white', 
                'border': 'none', 
                'padding': '1px', 
                'textDecoration': 'none', 
                'margin': '4px 2px', 
                'cursor': 'pointer', 
                'borderRadius': '12px', 
                'boxShadow': '0 2px #999'
                }
            ),
            ],
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center'
    }
),
            html.Div(id='top-albums-graph', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
            html.Div(id='top-artists-graph', style={
                'border': '2px solid #7a4bd8', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
            html.Div(id='top-tracks-graph', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
        ], style={'width': '100%', 'margin': 'auto'})

    def get_json_data(self, method, user, period):
        url = f"http://ws.audioscrobbler.com/2.0/?method={method}&user={user}&api_key={self.api_key}&period={period}&format=json"
        response = requests.get(url)
        return response.json()

    def plot_data(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        return go.Bar(x=names, y=playcounts, marker_color='rgb(82,41,177)')

    def run(self):
        @self.app.callback(
            [Output('top-albums-graph', 'children'),
             Output('top-artists-graph', 'children'),
             Output('top-tracks-graph', 'children')],
            [Input('submit-button', 'n_clicks')],
            [dash.dependencies.State('user-input', 'value'),
             dash.dependencies.State('period-input', 'value')]
        )
        def update_graph(n_clicks, user, period):
            if n_clicks is not None:
                data_albums = self.get_json_data("user.gettopalbums", user, period)
                data_artists = self.get_json_data("user.gettopartists", user, period)
                data_tracks = self.get_json_data("user.gettoptracks", user, period)

                return (
                    dcc.Graph(figure={'data': [self.plot_data(data_albums, 'album')], 
                    'layout': go.Layout(title=f'Top Played Albums from {user} ({period})', yaxis=dict(title='Playcount'), autosize=True, height=600, xaxis_tickangle=-45)}),
                    dcc.Graph(figure={'data': [self.plot_data(data_artists, 'artist')], 
                    'layout': go.Layout(title=f'Top Played Artists from {user} ({period})', yaxis=dict(title='Playcount'), autosize=True, height=600, xaxis_tickangle=-45)}),
                    dcc.Graph(figure={'data': [self.plot_data(data_tracks, 'track')], 
                    'layout': go.Layout(title=f'Top Played Tracks from {user} ({period})', yaxis=dict(title='Playcount'), autosize=True, height=600, xaxis_tickangle=-45)}),
                    
                )

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")
    dashboard = LastFmDashboard(api_key)
    dashboard.run()
    dashboard.app.run_server(debug=True, host='localhost', port=os.getenv('PORT', 8050))




