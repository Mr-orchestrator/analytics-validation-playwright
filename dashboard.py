import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

# Glassmorphism CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>GA4 vs utag.js Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            /* Glassmorphism Background */
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-attachment: fixed;
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            /* Glass Card Effect */
            .glass-card {
                background: rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border-radius: 15px !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
            }
            
            .card {
                background: rgba(255, 255, 255, 0.15) !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
                border-radius: 15px !important;
                border: 1px solid rgba(255, 255, 255, 0.25) !important;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
                transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            }
            
            .card:hover {
                transform: translateY(-5px) !important;
                box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5) !important;
            }
            
            .card-body {
                color: white !important;
            }
            
            .card-header {
                background: rgba(255, 255, 255, 0.2) !important;
                backdrop-filter: blur(10px) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.3) !important;
                color: white !important;
                font-weight: 600 !important;
                border-radius: 15px 15px 0 0 !important;
            }
            
            /* Header Styling */
            h1, h2, h3, h4, h5, h6 {
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .text-muted {
                color: rgba(255, 255, 255, 0.8) !important;
            }
            
            /* Button Styling */
            .btn-primary {
                background: rgba(255, 255, 255, 0.25) !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                color: white !important;
                font-weight: 600 !important;
                transition: all 0.3s ease !important;
            }
            
            .btn-primary:hover {
                background: rgba(255, 255, 255, 0.35) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3) !important;
            }
            
            /* Icon Colors */
            .text-primary { color: #fff !important; }
            .text-success { color: #4ade80 !important; }
            .text-danger { color: #f87171 !important; }
            .text-info { color: #60a5fa !important; }
            
            /* Metric Numbers */
            .font-weight-bold {
                text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4);
            }
            
            /* Table Styling */
            .dash-table-container {
                background: rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 15px !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }
            
            .dash-spreadsheet-container {
                background: transparent !important;
            }
            
            .dash-spreadsheet-inner table {
                background: transparent !important;
            }
            
            .dash-header {
                background: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                font-weight: 600 !important;
            }
            
            .dash-cell {
                background: rgba(255, 255, 255, 0.05) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }
            
            .dash-cell:hover {
                background: rgba(255, 255, 255, 0.15) !important;
            }
            
            /* Loading Spinner */
            ._dash-loading {
                color: white !important;
            }
            
            /* Progress Bar */
            .progress {
                background: rgba(255, 255, 255, 0.2) !important;
                backdrop-filter: blur(5px) !important;
                border-radius: 10px !important;
            }
            
            /* Chart Background */
            .js-plotly-plot, .plot-container {
                background: rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 10px !important;
            }
            
            /* Scrollbar Styling */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def load_runtime_data():
    """
    Load ONLY the latest test run data from runtime_data/last_run.json.
    This file is overwritten on each test run, ensuring only current data is displayed.
    """
    runtime_path = Path("runtime_data/last_run.json")
    if not runtime_path.exists():
        print("No runtime_data/last_run.json found. Dashboard will start empty.")
        return pd.DataFrame(), None

    try:
        with open(runtime_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            return pd.DataFrame(), None

        df = pd.DataFrame(data)
        
        # Extract test execution timestamp from the data
        test_timestamp = df['Timestamp'].iloc[0] if 'Timestamp' in df.columns else None

        # Map from internal keys to dashboard-friendly columns
        df["Test Case"] = df["parameter"]
        df["Expected"] = df["utag_value"]
        df["Actual"] = df["ga4_value"]
        df["Result"] = df["match"].apply(lambda m: "Pass" if bool(m) else "Fail")

        # Keep Date and Time from test execution
        if "hit_number" in df.columns:
            df["Hit"] = df["hit_number"]

        return df[["Date", "Time", "Hit", "Test Case", "Result", "Expected", "Actual"]], test_timestamp
    except Exception as e:
        print(f"Error reading runtime_data/last_run.json: {e}")
        return pd.DataFrame(), None

def create_test_summary_plot(df):
    """Create a bar chart showing test results over time."""
    if df.empty or 'Result' not in df.columns or 'Date' not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No test results available",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        return fig
    
    try:
        # Group by date and result
        summary = df.groupby(['Date', 'Result']).size().reset_index(name='Count')
        
        # Create bar chart
        fig = px.bar(
            summary, 
            x='Date',
            y='Count',
            color='Result',
            title='Latest Test Run Results',
            labels={'Count': 'Number of Tests', 'Date': 'Test Execution Date'},
            color_discrete_map={
                'Pass': '#28a745',
                'Passed': '#28a745',
                'Fail': '#dc3545',
                'Failed': '#dc3545'
            },
            barmode='group'
        )
        
        fig.update_layout(
            xaxis_title='Test Date',
            yaxis_title='Number of Tests',
            legend_title='Result',
            hovermode='x unified',
            xaxis=dict(tickangle=45, gridcolor='rgba(255,255,255,0.2)', color='white'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)', color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            title=dict(font=dict(size=16, color='white')),
            legend=dict(
                bgcolor='rgba(255,255,255,0.1)',
                bordercolor='rgba(255,255,255,0.2)',
                font=dict(color='white')
            )
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating plot: {str(e)}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=12, color="white")
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

def create_metrics_cards(df):
    """Create metric cards for the dashboard."""
    if df.empty:
        return dbc.Alert("No test results available. Run core.py first.", color="warning")
    
    # Calculate metrics
    total_tests = len(df)
    passed = len(df[df['Result'].str.lower() == 'pass'])
    failed = len(df[df['Result'].str.lower() == 'fail'])
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    # Create metric cards
    return dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        html.I(className="fas fa-clipboard-list fa-2x mb-3"),
                        className="text-primary text-center"
                    ),
                    html.H4("Total Tests", className="card-title text-muted text-center"),
                    html.H2(f"{total_tests}", className="font-weight-bold text-center")
                ]),
                className="shadow-sm h-100"
            ),
            md=3, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        html.I(className="fas fa-check-circle fa-2x mb-3"),
                        className="text-success text-center"
                    ),
                    html.H4("Passed", className="card-title text-muted text-center"),
                    html.H2(f"{passed}", className="font-weight-bold text-success text-center")
                ]),
                className="shadow-sm h-100"
            ),
            md=3, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        html.I(className="fas fa-times-circle fa-2x mb-3"),
                        className="text-danger text-center"
                    ),
                    html.H4("Failed", className="card-title text-muted text-center"),
                    html.H2(f"{failed}", className="font-weight-bold text-danger text-center")
                ]),
                className="shadow-sm h-100"
            ),
            md=3, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.Div(
                        html.I(className="fas fa-percentage fa-2x mb-3"),
                        className="text-info text-center"
                    ),
                    html.H4("Pass Rate", className="card-title text-muted text-center"),
                    html.H2(f"{pass_rate:.1f}%", className="font-weight-bold text-center"),
                    dbc.Progress(value=pass_rate, max=100, color="success", className="mt-2")
                ]),
                className="shadow-sm h-100"
            ),
            md=3, className="mb-4"
        )
    ], className="mb-4")

def create_results_table(df):
    """Create an interactive data table for test results."""
    if df.empty:
        return dbc.Alert("No test results found.", color="warning")
    
    return dash_table.DataTable(
        id='test-results-table',
        columns=[
            {"name": col, "id": col} for col in df.columns
        ],
        data=df.to_dict('records'),
        page_size=20,
        page_action='native',
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        style_table={
            'overflowX': 'auto',
            'border': '1px solid #e0e0e0',
            'borderRadius': '8px'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': '600',
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '14px'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'border': '1px solid #f0f0f0',
            'fontSize': '14px',
            'whiteSpace': 'normal'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(250, 250, 250)'
            },
            {
                'if': {'column_id': 'Result', 'filter_query': '{Result} = "Pass"'},
                'color': '#28a745',
                'fontWeight': '600',
                'backgroundColor': 'rgba(40, 167, 69, 0.1)'
            },
            {
                'if': {'column_id': 'Result', 'filter_query': '{Result} = "Fail"'},
                'color': '#dc3545',
                'fontWeight': '600',
                'backgroundColor': 'rgba(220, 53, 69, 0.1)'
            }
        ],
        export_format='xlsx',
        export_headers='display'
    )

def create_pie_chart(df):
    """Create a pie chart of test results."""
    if df.empty or 'Result' not in df.columns:
        return dcc.Graph(figure=go.Figure())
    
    result_counts = df['Result'].value_counts().reset_index()
    result_counts.columns = ['Result', 'Count']
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=result_counts['Result'],
        values=result_counts['Count'],
        hole=0.5,
        marker_colors=['#28a745' if r == 'Pass' else '#dc3545' 
                      for r in result_counts['Result']],
        textinfo='label+percent',
        textposition='inside'
    ))
    
    fig.update_layout(
        title='Test Results Distribution',
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        title_font=dict(size=16, color='white')
    )
    
    # Update trace styling for glassmorphism
    fig.update_traces(
        textfont=dict(color='white', size=14),
        marker=dict(line=dict(color='rgba(255,255,255,0.3)', width=2))
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Load initial data (latest run only)
df, test_timestamp = load_runtime_data()

# Define the app layout
app.layout = dbc.Container([
    # Header with timestamp
    dbc.Row([
        dbc.Col([
            html.H1("🎯 GA4 vs utag.js Dashboard", className="mb-2"),
            html.P("Displaying ONLY the Latest Test Run", className="text-muted mb-1"),
            html.Div(id="test-timestamp-header", className="mb-3", style={'fontSize': '14px', 'fontWeight': '500'})
        ])
    ]),
    
    # Refresh button
    dbc.Row([
        dbc.Col(
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh Data"],
                id="refresh-button",
                color="primary",
                className="mb-4"
            ),
            width={"size": 2, "offset": 5}
        )
    ], justify="center"),
    
    # Loading component
    dcc.Loading(
        id="loading",
        type="circle",
        children=[html.Div(id="dashboard-content")]
    ),
    
    # Store for data and timestamp
    dcc.Store(id='stored-data', data=df.to_dict('records') if not df.empty else []),
    dcc.Store(id='stored-timestamp', data=test_timestamp)
    
], fluid=True, className="p-4")

# Callback to update dashboard
@app.callback(
    [Output('dashboard-content', 'children'),
     Output('stored-data', 'data'),
     Output('stored-timestamp', 'data'),
     Output('test-timestamp-header', 'children')],
    [Input('refresh-button', 'n_clicks')]
)
def update_dashboard(n_clicks):
    # Reload LATEST data only
    df, test_timestamp = load_runtime_data()
    
    # Create timestamp display
    if test_timestamp:
        timestamp_display = html.Div([
            html.I(className="fas fa-clock me-2"),
            html.Span(f"Latest Test Executed: {test_timestamp}", style={'color': 'white'})
        ])
    else:
        timestamp_display = html.Div([
            html.Span("No test data available", style={'color': 'rgba(255,255,255,0.7)'})
        ])
    
    if df.empty:
        content = dbc.Alert(
            "No test results found. Please run core.py first.",
            color="warning",
            style={'background': 'rgba(255,193,7,0.2)', 'border': '1px solid rgba(255,193,7,0.5)', 'color': 'white'}
        )
        return content, [], None, timestamp_display
    
    # Create dashboard content
    content = [
        # Info banner - Latest run only
        dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            html.Strong("Latest Test Run Only: "),
            html.Span(f"This dashboard displays results from the most recent test execution. Previous test data is not shown. Last run: {test_timestamp}")
        ], color="info", className="mb-4", style={
            'background': 'rgba(23, 162, 184, 0.2)',
            'border': '1px solid rgba(23, 162, 184, 0.5)',
            'color': 'white'
        }),
        
        # Metrics cards
        create_metrics_cards(df),
        
        # Charts row
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Latest Run - Test Results"),
                    dbc.CardBody(create_pie_chart(df))
                ], className="shadow-sm"),
                md=4, className="mb-4"
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Latest Run - Test Summary"),
                    dbc.CardBody(
                        dcc.Graph(
                            figure=create_test_summary_plot(df),
                            config={'displayModeBar': True}
                        )
                    )
                ], className="shadow-sm"),
                md=8, className="mb-4"
            )
        ]),
        
        # Results table
        dbc.Card([
            dbc.CardHeader("Latest Run - Detailed Test Results"),
            dbc.CardBody(create_results_table(df))
        ], className="shadow-sm")
    ]
    
    return content, df.to_dict('records'), test_timestamp, timestamp_display

if __name__ == "__main__":
    print("=" * 80)
    print("GA4 vs utag_data – Automation Dashboard")
    print("=" * 80)
    print("\nStarting dashboard server...")
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("\nPress Ctrl+C to stop the dashboard")
    print("=" * 80 + "\n")
    
    app.run_server(debug=True, port=8050, use_reloader=False)
