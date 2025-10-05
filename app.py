import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_cytoscape as cyto
import json
import pathlib

def _json_to_mock(json_path="mock_data.json"):
    raw = json.loads(pathlib.Path(json_path).read_text())
    for main, cfg in raw.items():
        for sub, sub_cfg in cfg["subtopics"].items():
            sub_cfg["experiments"] = pd.DataFrame(sub_cfg["experiments"])
    return raw

MOCK_DATA = _json_to_mock()   # same name your callbacks already use



# --- Mock Data ------------------------------------------------------------------
# This remains the same.
MOCK_DATA = {
    'radiation': {
        'display_name': 'Radiation',
        'subtopics': {
            'dna_damage': {
                'title': 'DNA Damage & Repair',
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
            # ... other radiation subtopics ...
        },
        'default_subtopic': 'dna_damage'
    },
    # ... other main topics ...
}

# --- Styles & Theming -----------------------------------------------------------
APP_THEME = dbc.themes.CYBORG
CUSTOM_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
LOGO = "https://placehold.co/40x40/000000/FFFFFF?text=EX"
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
    """Creates the initial topic selection screen."""
    buttons = html.Div(
        [
            dbc.Button(
                topic_data['display_name'],
                id={'type': 'topic-button', 'index': topic_key},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #ff8c00, #ff5722)', 'borderColor': '#ff8c00', 'minWidth': '150px'}
            ) for topic_key, topic_data in MOCK_DATA.items()
        ],
        className="d-flex justify-content-center flex-wrap mb-4"
    )
    search_bar = dbc.InputGroup(
        [
            dbc.Input(id="search-input", placeholder="Search for any topic...", type="text"),
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
            'minHeight': 'calc(100vh - 56px)'
        }
    )
    return html.Div([hero_section])

def generate_subtopic_layout(main_topic_key):
    """Generates the layout for selecting subtopics."""
    if main_topic_key not in MOCK_DATA or 'subtopics' not in MOCK_DATA[main_topic_key]:
        return dbc.Alert("Error: Subtopics not found for this main topic.", color="danger")
    main_topic_data = MOCK_DATA[main_topic_key]
    subtopic_buttons = [
        dbc.Button(
            sub_data['title'],
            id={'type': 'subtopic-button', 'main_topic': main_topic_key, 'subtopic_key': sub_key},
            size="lg",
            className="m-3",
            style={'background': 'linear-gradient(90deg, #6a5acd, #483d8b)', 'borderColor': '#6a5acd', 'minWidth': '200px'}
        ) for sub_key, sub_data in main_topic_data['subtopics'].items()
    ]
    return dbc.Container(
        [
            dbc.Row(dbc.Col(dbc.Button("Back to Topics", id="back-to-topics-button", className="mb-4", color="light", outline=True))),
            html.H2(f"Select a Subtopic for {main_topic_data['display_name']}", className="text-center text-white mb-5"),
            html.Div(subtopic_buttons, className="d-flex justify-content-center flex-wrap mb-4"),
        ],
        fluid=True,
        className="py-5 text-center d-flex flex-column justify-content-center",
        style={
            'background': 'radial-gradient(circle, rgba(13,23,42,1) 0%, rgba(0,0,0,1) 100%)',
            'minHeight': 'calc(100vh - 56px)'
        }
    )

# MODIFIED: This function now handles custom queries

def generate_dashboard_layout(main_topic_key, subtopic_key):
    """Creates the detailed dashboard view for a selected topic or a custom query."""
    data = {}
    
    # CASE 1: Handle a custom query that is not in MOCK_DATA
    if subtopic_key == 'custom_query':
        data = {
            'title': f"On-Demand Analysis for: {main_topic_key.title()}",
            'summary': "This is a custom query. In a real application, a backend model would generate a summary here based on the search term.",
            'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
            'knowledge_gaps': {"Awaiting Analysis": 100},
            'actionable': {
                'Mission Architects': "No pre-defined actions for this custom query.",
                'Scientists': "Further research is required based on this query.",
                'Managers': "Evaluate the potential of this new research area."
            },
            'graph_elements': [
                {'data': {'id': 'query', 'label': main_topic_key.title()}},
                {'data': {'id': 'placeholder', 'label': 'Analysis Pending...'}},
                {'data': {'source': 'query', 'target': 'placeholder'}, 'classes': 'edge'},
            ]
        }
    # CASE 2: Handle a valid topic/subtopic from MOCK_DATA
    elif main_topic_key in MOCK_DATA and subtopic_key in MOCK_DATA[main_topic_key]['subtopics']:
        data = MOCK_DATA[main_topic_key]['subtopics'][subtopic_key]
    # CASE 3: Handle an error state
    else:
        return dbc.Alert("Error: Data for this topic could not be found.", color="danger")

    graph_config = {'staticPlot': True}
    summary_card = create_card("AI-Powered Summary", dcc.Markdown(data['summary']), "bi-robot")
    knowledge_graph = create_card("Knowledge Graph", cyto.Cytoscape(
        id='knowledge-graph',
        layout={'name': 'cose'}, # Use a dynamic layout like 'cose'
        style={'width': '100%', 'height': '400px'},
        elements=data['graph_elements'],
        stylesheet=[
            {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#00bfff', 'color': 'white', 'font-size': '12px'}},
            {'selector': 'edge', 'style': {'line-color': '#4e5d78', 'width': 2, 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'target-arrow-color': '#4e5d78'}},
        ],
    ), "bi-diagram-3-fill")

    fig_bar = px.bar(
        data['experiments'], x=data['experiments'].columns[0], y=data['experiments'].columns[1],
        title='Data Distribution',
        template=CHART_TEMPLATE, color_discrete_sequence=['#ff69b4']
    )
    fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    bar_chart = create_card("Data Distribution", dcc.Graph(figure=fig_bar, config=graph_config, style={'height': '350px'}), "bi-bar-chart-line-fill")

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
    
    back_button_id = "back-to-subtopics-button" if subtopic_key != 'custom_query' else "back-to-topics-button"
    back_button_text = "Go Back to Subtopics" if subtopic_key != 'custom_query' else "Back to Home"

    return html.Div([
        dbc.Button(back_button_text, id=back_button_id, className="mb-3", color="light", outline=True),
        html.H3(f"{data['title']}", className="text-white mb-4"),
        dbc.Row([dbc.Col(summary_card, md=12)]),
        dbc.Row([dbc.Col(knowledge_graph, md=7), dbc.Col([bar_chart, pie_chart], md=5)]),
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
            dbc.NavItem(dbc.NavLink("Home", href="/", active="exact", style={'color': '#ff8c00'})),
        ], className="ms-auto", navbar=True)
    ]),
    color="#0d172a", dark=True, sticky="top"
)

app.layout = html.Div([
    dcc.Store(id='app-state', data={'view': 'landing', 'main_topic': None, 'subtopic': None}),
    header,
    dcc.Loading(id="loading-spinner", type="circle", children=html.Div(id="page-content"))
])

# --- Callbacks ------------------------------------------------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('app-state', 'data')
)
def router(data):
    """Main router to switch between views."""
    view = data.get('view')
    main_topic = data.get('main_topic')
    subtopic = data.get('subtopic')

    if view == 'landing':
        return generate_landing_layout()
    elif view == 'subtopic_selection':
        return generate_subtopic_layout(main_topic)
    elif view == 'dashboard':
        return html.Div(generate_dashboard_layout(main_topic, subtopic), className="p-4")
    return html.Div("404 - Page not found")

# MODIFIED: This function now handles custom queries
@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Output('search-error', 'children'),
    Input('search-button', 'n_clicks'),
    State('search-input', 'value'),
    prevent_initial_call=True,
)
def search_topic(n_clicks, search_value):
    """Handle search bar submissions on landing page."""
    if not n_clicks or not search_value:
        raise dash.exceptions.PreventUpdate

    topic_key = (search_value or '').lower().strip()
    
    # If the topic is found, go to the subtopic selection page as before
    if topic_key in MOCK_DATA:
        return {'view': 'subtopic_selection', 'main_topic': topic_key, 'subtopic': None}, None
    
    # NEW BEHAVIOR: If the topic is NOT found, go directly to the dashboard
    # We use the search value as the main_topic and a special key for the subtopic
    else:
        return {'view': 'dashboard', 'main_topic': search_value, 'subtopic': 'custom_query'}, None

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'topic-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_main_topic(n_clicks):
    """Handle main topic button clicks."""
    ctx = dash.callback_context
    if not any(n_clicks) or not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    main_topic_key = button_id['index']
    return {'view': 'subtopic_selection', 'main_topic': main_topic_key, 'subtopic': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'subtopic-button', 'main_topic': ALL, 'subtopic_key': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_subtopic(n_clicks):
    """Handle subtopic button clicks."""
    ctx = dash.callback_context
    if not any(n_clicks) or not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    main_topic_key = button_id['main_topic']
    subtopic_key = button_id['subtopic_key']
    return {'view': 'dashboard', 'main_topic': main_topic_key, 'subtopic': subtopic_key}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-topics-button', 'n_clicks'),
    prevent_initial_call=True
)
def go_back_to_topics(n_clicks):
    """Handle 'Back to Topics' button click."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    return {'view': 'landing', 'main_topic': None, 'subtopic': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-subtopics-button', 'n_clicks'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def go_back_to_subtopics(n_clicks, current_state):
    """Handle 'Go Back to Subtopics' button click."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    main_topic = current_state.get('main_topic')
    return {'view': 'subtopic_selection', 'main_topic': main_topic, 'subtopic': None}

# This callback can be removed as there's no graph-click-output in the new layout
# Or kept if you add that component back into the dynamic dashboard
# @app.callback(...)

# ------------------------------------------------------------------
# 1.  BACKEND FETCHER  ––  edit however you like
# ------------------------------------------------------------------
def fetch_from_backend(path: str):
    """
    path = "radiation/dna_damage/summary"
    Return string, list or dict to inject into the JSON structure.
    Below are THREE example implementations – pick ONE (or write your own).
    """
    import os, json, pathlib, requests

    # -------  A.  local JSON file  ---------------------------------
    # file  backend.json  sitting next to app.py
    # {
    #   "radiation": {
    #     "dna_damage": {
    #       "summary": "text fetched from file",
    #       "experiments": [{"Organism":"Mice","Count":99}]
    #     }
    #   }
    # }
    backend_file = pathlib.Path("backend.json")
    if backend_file.exists():
        root = json.loads(backend_file.read_text())
        keys = path.split("/")
        for k in keys:
            root = root.get(k, {})
        return root

    # -------  B.  environment variable  -----------------------------
    env_key = path.replace("/", "_").upper()   # RADIATION_DNA_DAMAGE_SUMMARY
    return os.getenv(env_key, f"⚠️ no backend value for {path}")

    # -------  C.  remote REST endpoint  -----------------------------
    # url = f"https://your.api/nasa/{path}"
    # return requests.get(url, timeout=5).json()

    # fallback
    return f"⚠️ backend key {path} not found"

# ------------------------------------------------------------------
# 2.  JSON → PYTHON  (with backend injection + DataFrame conversion)
# ------------------------------------------------------------------
import pathlib, json, pandas as pd

def _load_dynamic_mock(json_path="mock_data.json"):
    raw = json.loads(pathlib.Path(json_path).read_text())

    def _walk(obj):
        if isinstance(obj, dict):
            # if we see {"backend": "some/path"}  ->  replace it
            if "backend" in obj and len(obj) == 1:
                return fetch_from_backend(obj["backend"])
            return {k: _walk(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_walk(item) for item in obj]
        return obj

    raw = _walk(raw)

    # convert experiments lists → DataFrame
    for main, cfg in raw.items():
        for sub, sub_cfg in cfg["subtopics"].items():
            sub_cfg["experiments"] = pd.DataFrame(sub_cfg["experiments"])
    return raw

# ------------------------------------------------------------------
# 3.  INITIAL LOAD  (same name your callbacks already use)
# ------------------------------------------------------------------
MOCK_DATA = _load_dynamic_mock()

# --- Run Application ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True,port=8502)