import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import requests
import os
from dotenv import load_dotenv

import networkx as nx
import matplotlib.pyplot as plt

from wordcloud import WordCloud


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
                value='SrVesper',
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
            html.Div(id='user-info', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
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
            html.Div(id='top-track-bubble', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
            html.Div(id='top-track-pie', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }),
            html.Div(id='tree-graph', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '25px',
                'borderRadius': '15px',

            }),
            html.Div(id='network-graph', style={
                'border': '2px solid #663ac4', 
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '25px',
                'borderRadius': '15px',

            }),
        ], style={'width': '100%', 'margin': 'auto'})

    def get_json_data(self, method, user, period):
        url = f"http://ws.audioscrobbler.com/2.0/?method={method}&user={user}&api_key={self.api_key}&period={period}&format=json"
        response = requests.get(url)
        return response.json()
    
    def get_user_info(self, user):
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={self.api_key}&format=json"
        response = requests.get(url)
        return response.json()
    
    def get_recent_tracks(self, user):
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={self.api_key}&format=json"
        response = requests.get(url)
        return response.json()
    
    def plot_data(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        return go.Bar(x=names, y=playcounts, marker_color='rgb(82,41,177)')
    
    def plot_data_pie(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        name = ", ".join(names)

        return go.Pie(labels=names, values=playcounts, name=name, hole=.3, textinfo='label')

    def plot_wordcloud(self, data, key):
        names = [item["name"] for item in data[f"top{key}s"][key]]

        text = " ".join(names)

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        wordcloud.to_file("wordcloud.png")

    def plot_data_tree(self, data):
        labels = []
        parents = []

        for track in data["recenttracks"]["track"]:
            artist = "Artista: " + track["artist"]["#text"]
            album = "Álbum: " + track["album"]["#text"]
            track_name = "Música: " + track["name"]

            if artist not in labels:
                labels.append(artist)
                parents.append("")

            if album not in labels:
                labels.append(album)
                parents.append(artist)

            labels.append(track_name)
            parents.append(album)

        return go.Treemap(
            labels=labels,
            parents=parents
        )

    def plot_data_bubble(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        return go.Scatter(
            x=names,
            y=[key]*len(names),
            mode='markers',
            marker=dict(
                size=playcounts,
                sizemode='area',
                sizeref=2.*max(playcounts)/(40.**2),
                sizemin=4
            ),
            text=names
        )

    def plot_network_graph(self, data):
        G = nx.Graph()

        for track in data['recenttracks']['track']:
            artist_name = track['artist']['#text']
            album_name = track['album']['#text']
            track_name = track['name']

            G.add_node(artist_name, type='artista')
            G.add_node(album_name, type='album')
            G.add_edge(artist_name, album_name)

            G.add_node(track_name, type='musica')
            G.add_edge(album_name, track_name)

        pos = nx.spring_layout(G, seed=42)

        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f'{node} ({G.nodes[node]["type"]})')

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            text=node_text,
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Recent Tracks',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        node_adjacencies = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))

        node_trace.marker.color = node_adjacencies

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        return fig

    def run(self):
        @self.app.callback(
            [Output('user-info', 'children'),
            Output('top-albums-graph', 'children'),
            Output('top-artists-graph', 'children'),
            Output('top-tracks-graph', 'children')],
            Output('top-track-bubble', 'children'),
            Output('top-track-pie', 'children'),
            Output('tree-graph', 'children'),
            Output('network-graph', 'children'),
            [Input('submit-button', 'n_clicks')],
            [dash.dependencies.State('user-input', 'value'),
            dash.dependencies.State('period-input', 'value')]
        )
        def update_graph(n_clicks, user, period):
            if n_clicks is not None:
                user_info = self.get_user_info(user)

                data_albums = self.get_json_data("user.gettopalbums", user, period)
                data_artists = self.get_json_data("user.gettopartists", user, period)
                data_tracks = self.get_json_data("user.gettoptracks", user, period)

                data = self.get_recent_tracks(user)

                self.plot_wordcloud(data_artists, 'artist')

                return (
                    html.Div([
                        html.Div(
                            html.A(user_info['user']['name'], 
                                href=user_info['user']['url'],
                                target='_blank',
                                style={
                                    'color': '#5a189a',
                                    'textTransform': 'uppercase',
                                    'fontSize': '24px',
                                    'fontWeight': 'bold',
                                    'padding': '10px',
                                    'borderBottom': '2px solid #5a189a',
                                    'marginBottom': '20px',
                                }),
                            style={'textAlign': 'center'}
                        ),
                        html.A(
                            html.Img(src=user_info['user']['image'][-1]['#text'], style={
                                'border': '2px solid #5a189a',
                                'borderRadius': '15px',
                                'boxShadow': '0px 10px 15px rgba(0, 0, 0, 0.1)',
                                'display': 'block',
                                'marginLeft': 'auto',
                                'marginRight': 'auto'
                            }),
                            href=user_info['user']['url'],
                            target='_blank'
                        ),

                        html.Br(),
                      html.P(f"Playcount: {user_info['user']['playcount']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                    }),
                    html.P(f"Artist count: {user_info['user']['artist_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                    }),
                    html.P(f"Track count: {user_info['user']['track_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                    }),
                    html.P(f"Album count: {user_info['user']['album_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                    }),
                    ]),
                        dcc.Graph(figure={
                        'data': [self.plot_data_tree(data)], 
                        'layout': go.Layout(
                            title=f'Tree Map of Recent Tracks from {user}', 
                            autosize=True, 
                            height=600
                        )
                    }),
                        dcc.Graph(figure={
                                'data': [self.plot_data(data_albums, 'album')], 
                                'layout': go.Layout(
                                    title=f'Top Played Albums from {user} ({period})', 
                                    yaxis=dict(title='Playcount', automargin=True), 
                                    autosize=True, 
                                    height=600, 
                                    xaxis=dict(tickangle=-45, automargin=True)
                                )
                            }),
                        dcc.Graph(figure={
                                'data': [self.plot_data(data_artists, 'artist')], 
                                'layout': go.Layout(
                                    title=f'Top Played Artists from {user} ({period})', 
                                    yaxis=dict(title='Playcount', automargin=True), 
                                    autosize=True, 
                                    height=600, 
                                    xaxis=dict(tickangle=-45, automargin=True)
                                )
                            }),
                        dcc.Graph(figure={
                                'data': [self.plot_data(data_tracks, 'track')], 
                                'layout': go.Layout(
                                    title=f'Top Played Tracks from {user} ({period})', 
                                    yaxis=dict(title='Playcount', automargin=True), 
                                    autosize=True, 
                                    height=600, 
                                    xaxis=dict(tickangle=-45, automargin=True)
                                )
                            }),
                        dcc.Graph(figure={
                            'data': [self.plot_data_pie(data_tracks, 'track')], 
                            'layout': go.Layout(
                                title=f'Top Played Tracks from {user} ({period})', 
                                autosize=True, 
                                height=600,
                            )
                        }),
                        dcc.Graph(figure=self.plot_network_graph(data)),
                        dcc.Graph(figure={
                            'data': [
                                self.plot_data_bubble(data_albums, 'album'),
                                self.plot_data_bubble(data_artists, 'artist'),
                                self.plot_data_bubble(data_tracks, 'track')
                            ], 
                            'layout': go.Layout(
                                title=f'Top Played Items from {user} ({period})', 
                                autosize=True, 
                                height=600,
                                showlegend=False,
                                yaxis=dict(
                                    title='Type',
                                    tickmode='array',
                                    tickvals=['album', 'artist', 'track'],
                                    ticktext=['Albums', 'Artists', 'Tracks']
                                ),
                                xaxis=dict(tickangle=-45, automargin=True, title='Items')
                            )
                        }),
                        )

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")
    dashboard = LastFmDashboard(api_key)
    dashboard.run()
    dashboard.app.run_server(debug=True, host='localhost', port=os.getenv('PORT', 8050))




