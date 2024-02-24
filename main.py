import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import requests
import os
from dotenv import load_dotenv

import networkx as nx

from wordcloud import WordCloud

import textwrap



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
                        'https://use.fontawesome.com/releases/v5.8.1/css/all.css']

class LastFmDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.layout = self.layout()

    ## PÁGINA HTML
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

            html.Div(id='user-info', style={
                'padding': '20px', 
                'margin': '20px', 
                'fontSize': '15px',
                'borderRadius': '15px',
            }), 


            html.Div([
                html.Div(id='tree-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                }),
                html.Div(id='sunburst-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontWeight':'bold',
                }),
                html.Div(id='recent-track-bar-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontWeight':'bold',
                }),
                html.Div(id='network-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '25px',
                }),
                html.Div(id='top-track-bubble', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),     
            ], style={
                'border': '2px solid #663ac4', 
                'borderRadius': '15px',
            }),

            html.Br(),

            html.Div([
                html.Div(id='top-albums-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                }),
                html.Div(id='top-artists-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),
                html.Div(id='top-tracks-graph', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),     
            ], style={
                'border': '2px solid #663ac4', 
                'borderRadius': '15px',
            }),  
            
            html.Br(),
            
            html.Div([
                html.Div(id='top-track-pie', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),
                html.Div(id='top-album-pie', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),
                html.Div(id='top-artist-pie', style={
                    'padding': '20px', 
                    'margin': '20px', 
                    'fontSize': '15px',
                }),     
            ], style={
                'border': '2px solid #663ac4', 
                'borderRadius': '15px',
            })
   
        ], style={'width': '100%', 'margin': 'auto'})

    ## REQUESTS API
    def get_json_data(self, method, user, period):
        url = f"http://ws.audioscrobbler.com/2.0/?method={method}&user={user}&api_key={self.api_key}&period={period}&format=json"
        response = requests.get(url)
        return response.json()
    
    def get_artist_data(self, method, artist):
        url = f"http://ws.audioscrobbler.com/2.0/?method={method}&artist={artist}&api_key={self.api_key}&format=json"
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
    
    ## GRÁFICOS
    def plot_data(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        return go.Bar(
            x=names, 
            y=playcounts, 
            marker_color='rgb(82,41,177)',
            text=playcounts,
            textposition='outside',
            hovertemplate="<b>%{x}</b><br><br>%{y} plays",
            marker=dict(
                line=dict(color='rgb(0,0,0)', width=1.5),  
            ),
            opacity=0.7,
        )

    def plot_data_pie(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))

        name = ", ".join(names)

        return go.Pie(
            labels=names, 
            values=playcounts, 
            name=name, 
            hole=.3, 
            textinfo='label', 
            textposition='inside', 
            insidetextorientation='radial', 
            textfont=dict(size=18),
            marker=dict(
                colors=['#FEBFB3', '#E1396C', '#96D38C', '#D0F9B1'],
                line=dict(color='#000000', width=2)
            ),
            hoverinfo='label+percent',
            hoverlabel=dict(
                bgcolor='black',
                font=dict(color='white', size=16)
            )
        )

    def plot_wordcloud(self, data, key):
        names = [item["name"] for item in data[f"top{key}s"][key]]

        text = " ".join(names)

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

        wordcloud.to_file("wordcloud.png")

    def plot_data_tree(self, data):
        labels = []
        parents = []
        artist_count = 0
        colors = ['#FFADAD', '#FFD6A5', '#FDFFB6', '#CAFFBF', '#9BF6FF', '#A0C4FF', '#BDB2FF', '#FFC6FF'] 

        color_dict = {}

        for track in data["recenttracks"]["track"]:
            artist = track["artist"]["#text"]
            album = " " + track["album"]["#text"]
            track_name = "" + track["name"]

            if artist not in labels:
                if artist_count >= 5:  # limit to 4 artists
                    break
                labels.append(artist)
                parents.append("")
                color_dict[artist] = colors[artist_count]
                artist_count += 1

            if album not in labels and artist in labels:
                labels.append(album)
                parents.append(artist)

            if album in labels:
                labels.append(track_name)
                parents.append(album)

        marker_colors = [color_dict.get(label, '#FFFFFF') for label in labels]

        return go.Treemap(
            labels=labels,
            parents=parents,
            textfont=dict(size=23, color='black'),
            marker=dict(
                colors=marker_colors,
                line=dict(width=1.5, color='black')
            ),
            tiling=dict(
                pad=5
            )
        )

    def plot_data_sunburst(self, data):
        labels = []
        parents = []
        artist_count = 0
        colors = ['#3b234a', '#523961', '#baafc4', '#c3bbc9', '#dcd6f7']
        color_dict = {}

        for track in data["recenttracks"]["track"]:
            artist = textwrap.fill(track["artist"]["#text"], 30)
            album = " " + textwrap.fill(track["album"]["#text"], 30)
            track_name = "" + textwrap.fill(track["name"], 30)

            if artist not in labels:
                if artist_count >= 5:
                    continue
                labels.append(artist)
                parents.append("")
                color_dict[artist] = colors[artist_count]
                artist_count += 1

            if album not in labels and artist in labels:
                labels.append(album)
                parents.append(artist)
                color_dict[album] = color_dict[artist]

            if album in labels:
                labels.append(track_name)
                parents.append(album)
                color_dict[track_name] = color_dict[artist]

        marker_colors = [color_dict[label] for label in labels]

        return go.Sunburst(
            labels=labels,
            parents=parents,
            textfont=dict(size=25, color='white'),
            marker=dict(
                colors=marker_colors,
                line=dict(width=3, color='black')
            ),
            leaf=dict(opacity=0.9),
            branchvalues='total',
            hoverinfo='label+percent parent',
            maxdepth=2 
        )

    def plot_data_bubble(self, data, key):
        names = []
        playcounts = []

        for item in data[f"top{key}s"][key]:
            names.append(item["name"])
            playcounts.append(int(item["playcount"]))


        colors = ['#F4D03F', '#F5B041', '#DC7633', '#6E2C00']
        color_scale = [colors[i % len(colors)] for i in range(len(names))]

        return go.Scatter(
            x=names,
            y=[key]*len(names),
            mode='markers',
            marker=dict(
                size=playcounts,
                sizemode='area',
                sizeref=2.*max(playcounts)/(40.**2),
                sizemin=4,
                color=color_scale,
                line=dict(width=2, color='DarkSlateGrey') 
            ),
            text=names,
            hoverinfo='text',
            hoverlabel=dict( 
                bgcolor='black',
                font=dict(color='white', size=16)
            )
        )

    def plot_network_graph(self, data):
        G = nx.Graph()
        node_colors = []

        for track in data['recenttracks']['track']:
            artist_name = track['artist']['#text']
            album_name = track['album']['#text']
            track_name = track['name']

            if artist_name not in G:
                G.add_node(artist_name, type='artista')
                node_colors.append('rgba(255, 0, 0, 0.8)') 

            if album_name not in G:
                G.add_node(album_name, type='album')
                G.add_edge(artist_name, album_name)
                node_colors.append('rgba(0, 255, 0, 0.8)') 

            if track_name not in G:
                G.add_node(track_name, type='musica')
                G.add_edge(album_name, track_name)
                node_colors.append('rgba(0, 0, 255, 0.8)') 

        pos = nx.spring_layout(G, seed=42)

        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])

        node_trace = go.Scatter(
            x=[], y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                color=node_colors,
                size=10,
                line=dict(color='black', width=2)))

        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([f'{node} ({G.nodes[node]["type"]})'])

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Network Graph of Recent Tracks',
                            titlefont=dict(size=16),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        
        return fig

    def plot_data_stacked_bar(self, data):
        artists = []
        albums = []
        tracks = []

        for track in data["recenttracks"]["track"]:
            artist = track["artist"]["#text"]
            album = track["album"]["#text"]
            track_name = track["name"]

            artists.append(artist)
            albums.append(album)
            tracks.append(track_name)

        fig = go.Figure(data=[
            go.Bar(name='Artists', x=list(set(artists)), y=[artists.count(artist) for artist in set(artists)]),
            go.Bar(name='Albums', x=list(set(albums)), y=[albums.count(album) for album in set(albums)]),
            go.Bar(name='Tracks', x=list(set(tracks)), y=[tracks.count(track) for track in set(tracks)])
        ])

        fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'}, title_text='Music Data')
        return fig

    def run(self):
        @self.app.callback(
            [Output('user-info', 'children'),
            Output('tree-graph', 'children'),
            Output('sunburst-graph', 'children'),
            Output('recent-track-bar-graph', 'children'),
            Output('network-graph', 'children'),
            Output('top-track-bubble', 'children'),
            Output('top-albums-graph', 'children'),
            Output('top-artists-graph', 'children'),
            Output('top-tracks-graph', 'children')],
            Output('top-track-pie', 'children'),
            Output('top-artist-pie', 'children'),
            Output('top-album-pie', 'children'),
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
                                'textShadow': '1px 1px 1px #ffffff',
                            }),
                        style={'textAlign': 'center'}
                    ),
                    html.Br(),
                    html.A(
                        html.Img(src=user_info['user']['image'][-1]['#text'], style={
                            'border': '2px solid #5a189a',
                            'borderRadius': '50%',
                            'boxShadow': '0px 10px 15px rgba(0, 0, 0, 0.1)',
                            'display': 'block',
                            'marginLeft': 'auto',
                            'marginRight': 'auto',
                            'width': '200px',
                            'height': '200px', 
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
                        'textAlign': 'center', 
                    }),
                    html.P(f"Artist count: {user_info['user']['artist_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                        'textAlign': 'center',
                    }),
                    html.P(f"Track count: {user_info['user']['track_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                        'textAlign': 'center',
                    }),
                    html.P(f"Album count: {user_info['user']['album_count']}", style={
                        'color': '#4d194d',
                        'fontSize': '18px',
                        'fontWeight': 'bold',
                        'padding': '10px',
                        'backgroundColor': '#f3e8ee',
                        'borderRadius': '10px',
                        'marginBottom': '10px',
                        'textAlign': 'center', 
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
                        'data': [self.plot_data_sunburst(data)], 
                        'layout': go.Layout(
                            title=f'Recent Played Tracks from {user}', 
                            autosize=True, 
                            height=600,
                        )
                    }),    
                    
                    dcc.Graph(figure=self.plot_data_stacked_bar(data)),

                    dcc.Graph(figure=self.plot_network_graph(data)),

                    dcc.Graph(figure={
                        'data': [
                            self.plot_data_bubble(data_albums, 'album'),
                            self.plot_data_bubble(data_artists, 'artist'),
                            self.plot_data_bubble(data_tracks, 'track')
                        ], 
                        'layout': go.Layout(
                            title=f'Recent Played Items from {user}', 
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
                    
                    dcc.Graph(figure={
                        'data': [self.plot_data_pie(data_albums, 'album')], 
                        'layout': go.Layout(
                            title=f'Top Played Album from {user} ({period})', 
                            autosize=True, 
                            height=600,
                        )
                    }),
                    
                    dcc.Graph(figure={
                        'data': [self.plot_data_pie(data_artists, 'artist')], 
                        'layout': go.Layout(
                            title=f'Top Played Artists from {user} ({period})', 
                            autosize=True, 
                            height=600,
                        )
                    }),
                    )

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY")
    dashboard = LastFmDashboard(api_key)
    dashboard.run()
    dashboard.app.run_server(debug=True, host='0.0.0.0', port=os.getenv('PORT', 8050))




