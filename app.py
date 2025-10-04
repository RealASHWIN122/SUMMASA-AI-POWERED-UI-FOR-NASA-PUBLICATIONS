import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_cytoscape as cyto
import json

# --- Mock Data ------------------------------------------------------------------
# In a real application, this would come from a database or API call.
MOCK_DATA = {
    'radiation': {
        'summary': "Exposure to cosmic radiation results in significant DNA damage in plant and animal models. Studies on the ISS have identified several repair mechanisms, though long-term effects, particularly for Mars missions, remain a key concern. Key genes like RAD51 and p53 are consistently upregulated.",
        'experiments': pd.DataFrame({
            "Organism": ["Arabidopsis", "Mice", "Yeast", "Human Cells"],
            "Count": [18, 12, 9, 7],
        }),
        'knowledge_gaps': {"Known Effects": 60, "Countermeasures": 25, "Long-Term Impact": 15},
        'actionable': {
            'Mission Architects': "Shielding for transport vehicles and habitats is critical. Consider routes that minimize exposure to solar particle events.",
            'Scientists': "Focus on developing radioprotective supplements and gene therapies. More research is needed on the combined effects of radiation and microgravity.",
            'Managers': "Prioritize funding for projects investigating countermeasures and real-time radiation monitoring technologies for crew safety."
        },
        'graph_elements': [
            {'data': {'id': 'rad', 'label': 'Radiation'}, 'position': {'x': 100, 'y': 100}},
            {'data': {'id': 'dna', 'label': 'DNA Damage'}, 'position': {'x': 250, 'y': 100}},
            {'data': {'id': 'repair', 'label': 'Gene Repair Mech.'}, 'position': {'x': 400, 'y': 50}},
            {'data': {'id': 'cancer', 'label': 'Cancer Risk'}, 'position': {'x': 400, 'y': 150}},
            {'data': {'id': 'counter', 'label': 'Countermeasures'}, 'position': {'x': 550, 'y': 100}},
            {'data': {'id': 'mars', 'label': 'Mars Mission Viability'}, 'position': {'x': 700, 'y': 100}},
            {'data': {'source': 'rad', 'target': 'dna'}, 'classes': 'edge'},
            {'data': {'source': 'dna', 'target': 'repair'}, 'classes': 'edge'},
            {'data': {'source': 'dna', 'target': 'cancer'}, 'classes': 'edge'},
            {'data': {'source': 'repair', 'target': 'counter'}, 'classes': 'edge'},
            {'data': {'source': 'cancer', 'target': 'counter'}, 'classes': 'edge'},
            {'data': {'source': 'counter', 'target': 'mars'}, 'classes': 'edge'},
        ]
    },
    'sleep': {
        'summary': "Sleep disruption in microgravity is a persistent issue, primarily linked to circadian rhythm desynchronization and environmental factors. Studies show a decrease in slow-wave sleep, impacting cognitive performance. Light therapy and optimized scheduling are promising countermeasures.",
        'experiments': pd.DataFrame({
            "Organism": ["Humans", "Rodents"],
            "Count": [25, 8],
        }),
        'knowledge_gaps': {"Circadian Rhythm": 50, "Cognitive Impact": 30, "Pharmacology": 20},
        'actionable': {
            'Mission Architects': "Design crew quarters with dynamic lighting systems to simulate a 24-hour cycle. Improve acoustic insulation.",
            'Scientists': "Investigate non-pharmacological interventions like meditation and personalized exercise regimes to improve sleep quality.",
            'Managers': "Fund development of wearable technology to monitor crew sleep patterns and cognitive readiness in real-time."
        },
        'graph_elements': [
            {'data': {'id': 'microg', 'label': 'Microgravity'}, 'position': {'x': 100, 'y': 100}},
            {'data': {'id': 'circ', 'label': 'Circadian Desync'}, 'position': {'x': 250, 'y': 100}},
            {'data': {'id': 'sleep', 'label': 'Poor Sleep Quality'}, 'position': {'x': 400, 'y': 100}},
            {'data': {'id': 'cog', 'label': 'Cognitive Decline'}, 'position': {'x': 550, 'y': 50}},
            {'data': {'id': 'perf', 'label': 'Mission Performance'}, 'position': {'x': 700, 'y': 50}},
            {'data': {'id': 'light', 'label': 'Light Therapy'}, 'position': {'x': 550, 'y': 150}},
            {'data': {'source': 'microg', 'target': 'circ'}, 'classes': 'edge'},
            {'data': {'source': 'circ', 'target': 'sleep'}, 'classes': 'edge'},
            {'data': {'source': 'sleep', 'target': 'cog'}, 'classes': 'edge'},
            {'data': {'source': 'cog', 'target': 'perf'}, 'classes': 'edge'},
            {'data': {'source': 'light', 'target': 'sleep'}, 'classes': 'edge'},
        ]
    },
    'plants': {
        'summary': "Cultivating plants in space is crucial for long-duration missions, providing nutrition, oxygen, and psychological benefits. Research focuses on optimizing growth in microgravity, where altered root behavior and fluid dynamics pose challenges. LED lighting and hydroponic systems are key technologies being refined on the ISS.",
        'experiments': pd.DataFrame({
            "Organism": ["Lettuce", "Radishes", "Chili Peppers", "Arabidopsis"],
            "Count": [22, 15, 10, 28],
        }),
        'knowledge_gaps': {"Nutrient Uptake": 40, "Pollination": 35, "Light Spectrum": 25},
        'actionable': {
            'Mission Architects': "Integrate modular 'space gardens' into habitat designs for Mars missions. Plan for power and water recycling systems.",
            'Scientists': "Develop autonomous systems for monitoring plant health and harvesting. Research crop varieties that are more resilient to space stressors.",
            'Managers': "Invest in advanced hydroponic and aeronic technologies to increase crop yield and reduce resource consumption."
        },
        'graph_elements': [
            {'data': {'id': 'microg', 'label': 'Microgravity'}, 'position': {'x': 100, 'y': 150}},
            {'data': {'id': 'roots', 'label': 'Altered Root Growth'}, 'position': {'x': 250, 'y': 150}},
            {'data': {'id': 'nutrients', 'label': 'Nutrient Uptake'}, 'position': {'x': 400, 'y': 150}},
            {'data': {'id': 'led', 'label': 'LED Lighting'}, 'position': {'x': 400, 'y': 50}},
            {'data': {'id': 'yield', 'label': 'Crop Yield'}, 'position': {'x': 550, 'y': 100}},
            {'data': {'id': 'missions', 'label': 'Mission Self-Sufficiency'}, 'position': {'x': 700, 'y': 100}},
            {'data': {'source': 'microg', 'target': 'roots'}, 'classes': 'edge'},
            {'data': {'source': 'roots', 'target': 'nutrients'}, 'classes': 'edge'},
            {'data': {'source': 'nutrients', 'target': 'yield'}, 'classes': 'edge'},
            {'data': {'source': 'led', 'target': 'yield'}, 'classes': 'edge'},
            {'data': {'source': 'yield', 'target': 'missions'}, 'classes': 'edge'},
        ]
    }
}

# --- Styles & Theming -----------------------------------------------------------
APP_THEME = dbc.themes.CYBORG
CUSTOM_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
LOGO = "https://placehold.co/40x40/000000/FFFFFF?text=EX" # Placeholder for ELECTRIC XTRA logo
CHART_TEMPLATE = 'plotly_dark'

# --- App Initialization ---------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[APP_THEME, CUSTOM_CSS, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Electric Xtra Insights"

# --- Reusable Components -------------------------------------------------------
def create_card(title, content, icon):
    header = html.H5(
        [html.I(className=f"bi {icon} me-2"), " ", title],
        className="card-title",
        style={'color': '#00bfff'}
    )
    body_children = [header, html.Hr()]
    if isinstance(content, list):
        body_children.extend(content)
    else:
        body_children.append(content)
    return dbc.Card(
        dbc.CardBody(body_children),
        className="mb-4",
        style={'borderColor': '#00bfff', 'backgroundColor': '#1a2a44'}
    )

# --- Layout Generators ---------------------------------------------------------
def generate_landing_layout():
    """Creates the initial topic selection screen based on the new template."""
    
    buttons = html.Div(
        [
            dbc.Button(
                "Radiation",
                id={'type': 'topic-button', 'index': 'radiation'},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #ff8c00, #ff5722)', 'borderColor': '#ff8c00', 'minWidth': '150px'}
            ),
            dbc.Button(
                "Sleep",
                id={'type': 'topic-button', 'index': 'sleep'},
                size="lg",
                outline=True,
                className="m-3",
                style={'color': '#00bfff', 'borderColor': '#00bfff', 'minWidth': '150px'}
            ),
            dbc.Button(
                "Plants",
                id={'type': 'topic-button', 'index': 'plants'},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #ff8c00, #ff5722)', 'borderColor': '#ff8c00', 'minWidth': '150px'}
            ),
        ],
        className="d-flex justify-content-center flex-wrap mb-4"
    )
    
    search_bar = dbc.InputGroup(
        [
            dbc.Input(id="search-input", placeholder="Search for a topic...", type="text"),
            dbc.Button(html.I(className="bi bi-search"), id="search-button", color="primary", style={'backgroundColor': '#00bfff', 'borderColor': '#00bfff'}),
        ],
        className="mb-3 w-50 mx-auto",
    )

    hero_section = dbc.Container(
        [
            html.H1("NASA CHUNNI", className="display-1 fw-bold text-white text-center"),
            html.P("ERANGI PODA BHOOMI NN", className="text-center text-white-50 fs-4 mb-5"),
            buttons,
            search_bar,
            dbc.Row(dbc.Col(html.Div(id="search-error"), width={'size': 6, 'offset': 3}))
        ],
        fluid=True,
        className="py-5 text-center d-flex flex-column justify-content-center",
        style={
            'background': 'radial-gradient(circle, rgba(13,23,42,1) 0%, rgba(0,0,0,1) 100%)',
            'minHeight': 'calc(100vh - 56px)' # Full viewport height minus navbar
        }
    )

    return html.Div([hero_section])


def generate_dashboard_layout(keyword):
    """Creates the detailed dashboard view for a selected topic."""
    if keyword not in MOCK_DATA:
        return dbc.Alert("Error: Topic not found.", color="danger")
    
    data = MOCK_DATA[keyword]
    graph_config = {'staticPlot': True}

    summary_card = create_card("AI-Powered Summary", dcc.Markdown(data['summary']), "bi-robot")
    knowledge_graph = create_card("Knowledge Graph", cyto.Cytoscape(
        id='knowledge-graph',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=data['graph_elements'],
        stylesheet=[
            {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#00bfff', 'color': 'white', 'font-size': '12px'}},
            {'selector': 'edge', 'style': {'line-color': '#4e5d78', 'width': 2, 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#4e5d78'}},
        ],
        # --- LOCKING THE GRAPH ---
        userPanningEnabled=False,
        userZoomingEnabled=False,
        boxSelectionEnabled=False,
        autoungrabify=True, # Prevents nodes from being grabbed
        autounselectify=True
    ), "bi-diagram-3-fill")

    fig_bar = px.bar(
        data['experiments'], x='Organism', y='Count',
        title=f'Experiments by Organism for "{keyword.capitalize()}"',
        template=CHART_TEMPLATE, color_discrete_sequence=['#ff69b4']
    )
    fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    bar_chart = create_card("Experiment Distribution", dcc.Graph(figure=fig_bar, config=graph_config, style={'height': '350px'}), "bi-bar-chart-line-fill")

    fig_pie = px.pie(
        names=list(data['knowledge_gaps'].keys()), values=list(data['knowledge_gaps'].values()),
        title='Knowledge Gaps', template=CHART_TEMPLATE, hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )
    fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    pie_chart = create_card("Areas of Study", dcc.Graph(figure=fig_pie, config=graph_config, style={'height': '350px'}), "bi-pie-chart-fill")

    actionable_insights = create_card("Actionable Insights", [
        dbc.Tabs([
            dbc.Tab(dcc.Markdown(data['actionable']['Mission Architects']), label="Architects"),
            dbc.Tab(dcc.Markdown(data['actionable']['Scientists']), label="Scientists"),
            dbc.Tab(dcc.Markdown(data['actionable']['Managers']), label="Managers"),
        ])
    ], "bi-lightbulb-fill")
    
    graph_info = create_card("Graph Node Details", html.P("Click a node to see details.", id='graph-click-output'), "bi-info-circle-fill")

    return html.Div([
        dbc.Button("Go Back", id="back-button", className="mb-3", color="light", outline=True),
        dbc.Row([dbc.Col(summary_card, md=12)]),
        dbc.Row([dbc.Col([knowledge_graph, graph_info], md=7), dbc.Col([bar_chart, pie_chart], md=5)]),
        dbc.Row([dbc.Col(actionable_insights, md=12)])
    ])

# --- Main App Layout ------------------------------------------------------------
header = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row(
                [dbc.Col(html.Img(src=LOGO, height="40px")), dbc.Col(dbc.NavbarBrand("ELECTRIC XTRA", className="ms-2 text-white"))],
                align="center", className="g-0",
            ),
            href="#", style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Home", href="#", active="exact", style={'color': '#ff8c00'})),
            dbc.NavItem(dbc.NavLink("Features", href="#")),
            dbc.NavItem(dbc.NavLink("About", href="#")),
            dbc.NavItem(dbc.NavLink("Contact", href="#")),
        ], className="ms-auto", navbar=True)
    ]),
    color="#0d172a", dark=True, sticky="top"
)

app.layout = html.Div([
    dcc.Store(id='app-state', data={'view': 'landing', 'topic': None}),
    header,
    dcc.Loading(id="loading-spinner", type="circle", children=html.Div(id="page-content")) # Removed p-4 for full-width hero
])

# --- Callbacks ------------------------------------------------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('app-state', 'data')
)
def router(data):
    """Main router to switch between views."""
    view = data.get('view')
    if view == 'landing':
        return generate_landing_layout()
    elif view == 'dashboard':
        topic = data.get('topic')
        # Add padding back for the dashboard view
        return html.Div(generate_dashboard_layout(topic), className="p-4") 
    return html.Div("404 - Page not found")

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Output('search-error', 'children'),
    Input('search-button', 'n_clicks'),
    State('search-input', 'value'),
    prevent_initial_call=True,
)
def search_topic(n_clicks, search_value):
    """Handle search bar submissions."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    topic = (search_value or '').lower().strip()
    if topic in MOCK_DATA:
        return {'view': 'dashboard', 'topic': topic}, None
    else:
        error_msg = f"Topic '{search_value}' not found. Please try one of the suggestion buttons."
        return dash.no_update, dbc.Alert(error_msg, color="danger", dismissable=True, className="mt-3")

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'topic-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_topic(n_clicks):
    """Handle topic button clicks to switch to the dashboard view."""
    ctx = dash.callback_context
    if not any(n_clicks) or not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id_str = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id_str)
    topic = button_id['index']
    
    return {'view': 'dashboard', 'topic': topic}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-button', 'n_clicks'),
    prevent_initial_call=True
)
def go_back(n_clicks):
    """Handle the 'Go Back' button click to return to the landing page."""
    return {'view': 'landing', 'topic': None}

@app.callback(
    Output('graph-click-output', 'children'),
    Input('knowledge-graph', 'tapNodeData'),
    prevent_initial_call=True
)
def display_tap_node_data(data):
    if data:
        return f"You clicked on node: **{data['label']}**. In a real app, this would trigger a new search or display detailed publication data related to this topic."
    return "Click a node to see details."

# --- Run Application ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

