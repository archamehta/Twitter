import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

# Load the dataset
df = pd.read_csv('./Assignment3/ProcessedTweets.csv')

# Convert 'Month' column to datetime format
df['Month'] = pd.to_datetime(df['Month'], format='%B')

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout
app.layout = html.Div([
    html.H1("Twitter Data Visualization", style={'text-align': 'center'}),
    html.Div([
        html.Div([
            html.Label('Month', style={'text-align': 'center'}),
            dcc.Dropdown(
                id='month-dropdown',
                options=[
                    {'label': month.strftime('%B'), 'value': month} for month in df['Month'].unique()
                ],
                value=df['Month'].min(),
                clearable=False
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Sentiment Slider', style={'text-align': 'center'}),
            dcc.RangeSlider(
                id='sentiment-slider',
                min=df['Sentiment'].min(),
                max=df['Sentiment'].max(),
                step=0.1,
                marks={i: str(i) for i in range(int(df['Sentiment'].min()), int(df['Sentiment'].max()) + 1)},
                value=[df['Sentiment'].min(), df['Sentiment'].max()],
                allowCross=False
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Subjectivity Slider', style={'text-align': 'center'}),
            dcc.RangeSlider(
                id='subjectivity-slider',
                min=df['Subjectivity'].min(),
                max=df['Subjectivity'].max(),
                step=0.1,
                marks={i/10: str(i/10) for i in range(11)},
                value=[df['Subjectivity'].min(), df['Subjectivity'].max()],
                allowCross=False
            )
        ], style={'width': '33%', 'display': 'inline-block'})
    ], style={'margin-bottom': '20px'}),
    dcc.Graph(id='scatter-plot',
              config={'displayModeBar': True, 'editable': True},
              style={'height': '80vh', 'width': '100%'}),
    html.Div(id='selected-tweets')
])

# Define callback for updating scatter plot and tweet display table
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('selected-tweets', 'children')],
    [Input('month-dropdown', 'value'),
     Input('sentiment-slider', 'value'),
     Input('subjectivity-slider', 'value')]
)
def update_figures(selected_month, sentiment_range, subjectivity_range):
    # Filtering data based on selected month, sentiment, and subjectivity
    filtered_df = df[(df['Month'] == selected_month) &
                     (df['Sentiment'] >= sentiment_range[0]) &
                     (df['Sentiment'] <= sentiment_range[1]) &
                     (df['Subjectivity'] >= subjectivity_range[0]) &
                     (df['Subjectivity'] <= subjectivity_range[1])]

    # Extract tweets from filtered DataFrame
    tweets = filtered_df['RawTweet']
    
    # Convert tweets to HTML table rows
    tweets_rows = [html.Tr(html.Td(tweet)) for tweet in tweets]
    tweets_table = html.Table(tweets_rows, style={'margin': 'auto', 'text-align': 'center'})
    
    # Update scatter plot without highlighting any points and disable hover
    scatter_fig = go.Figure()
    scatter_fig.add_trace(go.Scatter(x=filtered_df['Dimension 1'], y=filtered_df['Dimension 2'], 
                                     mode='markers', marker=dict(color=filtered_df['Sentiment'], colorscale='Viridis', opacity=0.5),
                                     hoverinfo='skip'))
    scatter_fig.update_layout(title=dict(text='Dimensionality Reduction Plot', 
                                     x=0.5,  # Center title horizontally
                                     xanchor='center',  # Anchor point for x position
                                     yanchor='top'),  # Anchor point for y position
                          xaxis=dict(title='Dimension 1'),
                          yaxis=dict(title='Dimension 2'),
                          clickmode='event+select',)
    return scatter_fig, tweets_table

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
