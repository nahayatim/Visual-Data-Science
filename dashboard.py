import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Load the final data
final_data = pd.read_csv("final_data.csv")

# Initialize the app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "World Happiness Dashboard"

# Layout
app.layout = dbc.Container([
    # Title
    dbc.Row(
        dbc.Col(html.H1("World Happiness Dashboard", className="text-center my-4"), width=12)
    ),
    
    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Select Year:", className="fw-bold"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in sorted(final_data['Year'].unique())],
                multi=True,
                placeholder="Select year(s)"
            )
        ], width=4),
        
        dbc.Col([
            html.Label("Select Country:", className="fw-bold"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in sorted(final_data['Country name'].unique())],
                multi=True,
                placeholder="Select country(s)"
            )
        ], width=4),
        
        dbc.Col([
            html.Label("Select Range for Happiness Score:", className="fw-bold"),
            dcc.RangeSlider(
                id='score-slider',
                min=final_data['Happiness Score'].min(),
                max=final_data['Happiness Score'].max(),
                step=0.1,
                marks={i: str(i) for i in range(int(final_data['Happiness Score'].min()), int(final_data['Happiness Score'].max()) + 1)},
                value=[final_data['Happiness Score'].min(), final_data['Happiness Score'].max()]
            )
        ], width=12, className="mt-3"),
    ], className="mb-4"),
    
    # KPI Cards
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Key Metrics", className="card-title text-center"),
                    html.Div(id='kpi-card', className="text-center")
                ])
            ), width=12
        )
    ], className="mb-4"),
    
    # Visualizations
    dbc.Row([
        dbc.Col(dcc.Graph(id='scatter-plot', style={'height': '400px'}), width=6),
        dbc.Col(dcc.Graph(id='heatmap', style={'height': '400px'}), width=6),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart', style={'height': '400px'}), width=12)
    ]),
], fluid=True)

# Callbacks
@app.callback(
    [
        Output('scatter-plot', 'figure'),
        Output('heatmap', 'figure'),
        Output('line-chart', 'figure'),
        Output('kpi-card', 'children')
    ],
    [
        Input('year-dropdown', 'value'),
        Input('country-dropdown', 'value'),
        Input('score-slider', 'value')
    ]
)
def update_dashboard(selected_years, selected_countries, score_range):
    # Filter data
    filtered_data = final_data.copy()
    if selected_years:
        filtered_data = filtered_data[filtered_data['Year'].isin(selected_years)]
    if selected_countries:
        filtered_data = filtered_data[filtered_data['Country name'].isin(selected_countries)]
    filtered_data = filtered_data[
        (filtered_data['Happiness Score'] >= score_range[0]) & (filtered_data['Happiness Score'] <= score_range[1])
    ]

    # Scatter plot
    scatter_fig = px.scatter(
        filtered_data, x='GDP per Capita', y='Happiness Score', color='Country name',
        size='Social support', hover_name='Country name',
        title='Happiness Score vs GDP per Capita',
        labels={'GDP per Capita': 'GDP per Capita', 'Happiness Score': 'Happiness Score'}
    )

    # Heatmap
    heatmap_fig = px.imshow(
        filtered_data.corr(numeric_only=True),
        title="Correlation Heatmap",
        color_continuous_scale='Viridis'
    )

    # Line chart
    line_fig = px.line(
        filtered_data, x='Year', y='Happiness Score', color='Country name',
        title='Happiness Score Over Years'
    )

    # KPIs
    avg_score = filtered_data['Happiness Score'].mean()
    avg_gdp = filtered_data['GDP per Capita'].mean()
    avg_social_support = filtered_data['Social support'].mean()
    kpi_content = html.Div([
        html.P(f"Avg Happiness Score: {avg_score:.2f}", className="mb-1"),
        html.P(f"Avg GDP per Capita: {avg_gdp:.2f}", className="mb-1"),
        html.P(f"Avg Social Support: {avg_social_support:.2f}", className="mb-1")
    ])

    return scatter_fig, heatmap_fig, line_fig, kpi_content

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
