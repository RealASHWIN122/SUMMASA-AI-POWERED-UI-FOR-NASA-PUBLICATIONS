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
# Updated MOCK_DATA to include subtopics
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
            'countermeasures': {
                'title': 'Radiation Countermeasures',
                'summary': "Research into radiation countermeasures is exploring both passive shielding and active biological interventions. Promising avenues include pharmaceutical radioprotectants and gene editing techniques. The challenge lies in developing solutions effective against the broad spectrum of cosmic radiation.",
                'experiments': pd.DataFrame({
                    "Organism": ["Mice", "Human Cells", "Yeast"],
                    "Count": [10, 15, 7],
                }),
                'knowledge_gaps': {"Drug Efficacy": 45, "Combined Stressors": 30, "Long-Term Safety": 25},
                'actionable': {
                    'Mission Architects': "Integrate multi-layered shielding. Design habitats to allow crew members to shelter during solar events.",
                    'Scientists': "Identify and validate biomarkers for early radiation exposure and response. Develop broad-spectrum radioprotectants.",
                    'Managers': "Fund international collaborations to pool data on radiation biology and countermeasure testing."
                },
                'graph_elements': [
                    {'data': {'id': 'rad', 'label': 'Radiation Exposure'}, 'position': {'x': 100, 'y': 100}},
                    {'data': {'id': 'shield', 'label': 'Shielding'}, 'position': {'x': 250, 'y': 50}},
                    {'data': {'id': 'pharm', 'label': 'Radioprotectants'}, 'position': {'x': 250, 'y': 150}},
                    {'data': {'id': 'biorep', 'label': 'Biological Repair'}, 'position': {'x': 400, 'y': 100}},
                    {'data': {'id': 'health', 'label': 'Crew Health'}, 'position': {'x': 550, 'y': 100}},
                    {'data': {'source': 'rad', 'target': 'shield'}, 'classes': 'edge'},
                    {'data': {'source': 'rad', 'target': 'pharm'}, 'classes': 'edge'},
                    {'data': {'source': 'shield', 'target': 'health'}, 'classes': 'edge'},
                    {'data': {'source': 'pharm', 'target': 'health'}, 'classes': 'edge'},
                    {'data': {'source': 'rad', 'target': 'biorep'}, 'classes': 'edge'},
                    {'data': {'source': 'biorep', 'target': 'health'}, 'classes': 'edge'},
                ]
            }
        },
        'default_subtopic': 'dna_damage'
    },
    'sleep': {
        'display_name': 'Sleep',
        'subtopics': {
            'circadian_rhythms': {
                'title': 'Circadian Rhythms in Space',
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
            'cognitive_performance': {
                'title': 'Cognitive Performance & Sleep',
                'summary': "Reduced sleep quality in space directly impacts crew cognitive function, affecting decision-making and reaction times. Studies highlight the importance of understanding the links between sleep architecture changes and neurobehavioral performance metrics for mission success.",
                'experiments': pd.DataFrame({
                    "Organism": ["Humans"],
                    "Count": [18],
                }),
                'knowledge_gaps': {"Performance Metrics": 40, "Individual Variability": 35, "Long-Term Effects": 25},
                'actionable': {
                    'Mission Architects': "Implement cognitive testing protocols throughout missions. Ensure adequate time for crew rest and recovery.",
                    'Scientists': "Develop more sensitive and space-appropriate cognitive assessment tools. Research the role of specific sleep stages on cognitive repair.",
                    'Managers': "Invest in psychological support programs and tools to manage stress and improve mental well-being for better sleep."
                },
                'graph_elements': [
                    {'data': {'id': 'sleep_qual', 'label': 'Sleep Quality'}, 'position': {'x': 100, 'y': 100}},
                    {'data': {'id': 'cognition', 'label': 'Cognitive Function'}, 'position': {'x': 250, 'y': 100}},
                    {'data': {'id': 'decision', 'label': 'Decision Making'}, 'position': {'x': 400, 'y': 50}},
                    {'data': {'id': 'reaction', 'label': 'Reaction Time'}, 'position': {'x': 400, 'y': 150}},
                    {'data': {'id': 'mission_succ', 'label': 'Mission Success'}, 'position': {'x': 550, 'y': 100}},
                    {'data': {'source': 'sleep_qual', 'target': 'cognition'}, 'classes': 'edge'},
                    {'data': {'source': 'cognition', 'target': 'decision'}, 'classes': 'edge'},
                    {'data': {'source': 'cognition', 'target': 'reaction'}, 'classes': 'edge'},
                    {'data': {'source': 'decision', 'target': 'mission_succ'}, 'classes': 'edge'},
                    {'data': {'source': 'reaction', 'target': 'mission_succ'}, 'classes': 'edge'},
                ]
            }
        },
        'default_subtopic': 'circadian_rhythms'
    },
    'plants': {
        'display_name': 'Plants',
        'subtopics': {
            'crop_cultivation': {
                'title': 'Space Crop Cultivation',
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
                    {'data': {'id': 'nutrients', 'label': 'Nutrients Uptake'}, 'position': {'x': 400, 'y': 150}},
                    {'data': {'id': 'led', 'label': 'LED Lighting'}, 'position': {'x': 400, 'y': 50}},
                    {'data': {'id': 'yield', 'label': 'Crop Yield'}, 'position': {'x': 550, 'y': 100}},
                    {'data': {'id': 'missions', 'label': 'Mission Self-Sufficiency'}, 'position': {'x': 700, 'y': 100}},
                    {'data': {'source': 'microg', 'target': 'roots'}, 'classes': 'edge'},
                    {'data': {'source': 'roots', 'target': 'nutrients'}, 'classes': 'edge'},
                    {'data': {'source': 'nutrients', 'target': 'yield'}, 'classes': 'edge'},
                    {'data': {'source': 'led', 'target': 'yield'}, 'classes': 'edge'},
                    {'data': {'source': 'yield', 'target': 'missions'}, 'classes': 'edge'},
                ]
            },
            'plant_stress_response': {
                'title': 'Plant Stress Response in Space',
                'summary': "Plants in space face unique stressors including microgravity, altered light, and radiation. Understanding their molecular and physiological responses is key to developing robust crop systems. Research indicates changes in gene expression related to cell wall modification and hormone signaling.",
                'experiments': pd.DataFrame({
                    "Organism": ["Arabidopsis", "Wheat"],
                    "Count": [20, 10],
                }),
                'knowledge_gaps': {"Gene Regulation": 40, "Epigenetics": 30, "Long-Term Adaptation": 30},
                'actionable': {
                    'Mission Architects': "Consider environmental control systems that can mitigate stress for plants, e.g., optimized CO2 levels.",
                    'Scientists': "Investigate genetic modifications to enhance plant resilience to spaceflight stressors. Focus on stress-responsive pathways.",
                    'Managers': "Fund automated phenotyping systems for in-situ monitoring of plant health and stress indicators."
                },
                'graph_elements': [
                    {'data': {'id': 'microg', 'label': 'Microgravity'}, 'position': {'x': 100, 'y': 100}},
                    {'data': {'id': 'stress', 'label': 'Plant Stress'}, 'position': {'x': 250, 'y': 100}},
                    {'data': {'id': 'gene_exp', 'label': 'Gene Expression Change'}, 'position': {'x': 400, 'y': 50}},
                    {'data': {'id': 'hormones', 'label': 'Hormone Signaling'}, 'position': {'x': 400, 'y': 150}},
                    {'data': {'id': 'resilience', 'label': 'Plant Resilience'}, 'position': {'x': 550, 'y': 100}},
                    {'data': {'source': 'microg', 'target': 'stress'}, 'classes': 'edge'},
                    {'data': {'source': 'stress', 'target': 'gene_exp'}, 'classes': 'edge'},
                    {'data': {'source': 'stress', 'target': 'hormones'}, 'classes': 'edge'},
                    {'data': {'source': 'gene_exp', 'target': 'resilience'}, 'classes': 'edge'},
                    {'data': {'source': 'hormones', 'target': 'resilience'}, 'classes': 'edge'},
                ]
            }
        },
        'default_subtopic': 'crop_cultivation'
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
                topic_data['display_name'], # Use display_name
                id={'type': 'topic-button', 'index': topic_key},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #ff8c00, #ff5722)', 'borderColor': '#ff8c00', 'minWidth': '150px'}
            ) for topic_key, topic_data in MOCK_DATA.items() # Iterate through MOCK_DATA
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

def generate_subtopic_layout(main_topic_key):
    """Generates the layout for selecting subtopics for a given main topic."""
    if main_topic_key not in MOCK_DATA or 'subtopics' not in MOCK_DATA[main_topic_key]:
        return dbc.Alert("Error: Subtopics not found for this main topic.", color="danger")

    main_topic_data = MOCK_DATA[main_topic_key]
    subtopic_buttons = []
    for sub_key, sub_data in main_topic_data['subtopics'].items():
        subtopic_buttons.append(
            dbc.Button(
                sub_data['title'], # Use the title for the subtopic button
                id={'type': 'subtopic-button', 'main_topic': main_topic_key, 'subtopic_key': sub_key},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #6a5acd, #483d8b)', 'borderColor': '#6a5acd', 'minWidth': '200px'}
            )
        )

    return dbc.Container(
        [
            dbc.Row(dbc.Col(dbc.Button("Back to Topics", id="back-to-topics-button", className="mb-4", color="light", outline=True))),
            html.H2(f"Select a Subtopic for {main_topic_data['display_name']}", className="text-center text-white mb-5"),
            html.Div(subtopic_buttons, className="d-flex justify-content-center flex-wrap mb-4"),
            # Add a placeholder for subtopic search/error if desired later
        ],
        fluid=True,
        className="py-5 text-center d-flex flex-column justify-content-center",
        style={
            'background': 'radial-gradient(circle, rgba(13,23,42,1) 0%, rgba(0,0,0,1) 100%)',
            'minHeight': 'calc(100vh - 56px)'
        }
    )


def generate_dashboard_layout(main_topic_key, subtopic_key):
    """Creates the detailed dashboard view for a selected main topic and subtopic."""
    if main_topic_key not in MOCK_DATA or subtopic_key not in MOCK_DATA[main_topic_key]['subtopics']:
        return dbc.Alert("Error: Subtopic data not found.", color="danger")
    
    data = MOCK_DATA[main_topic_key]['subtopics'][subtopic_key]
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
        userPanningEnabled=False,
        userZoomingEnabled=False,
        boxSelectionEnabled=False,
        autoungrabify=True, # Prevents nodes from being grabbed
        autounselectify=True
    ), "bi-diagram-3-fill")

    fig_bar = px.bar(
        data['experiments'], x='Organism', y='Count',
        title=f'Experiments by Organism for "{data["title"]}"',
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
        dbc.Button("Go Back to Subtopics", id="back-to-subtopics-button", className="mb-3", color="light", outline=True),
        html.H3(f"{data['title']} Details", className="text-white mb-4"), # Added subtopic title
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
    dcc.Store(id='app-state', data={'view': 'landing', 'main_topic': None, 'subtopic': None}), # Updated app-state
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
        # Removed p-4 here, as generate_subtopic_layout now handles its own container
        return generate_subtopic_layout(main_topic) 
    elif view == 'dashboard':
        return html.Div(generate_dashboard_layout(main_topic, subtopic), className="p-4") 
    return html.Div("404 - Page not found")

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Output('search-error', 'children'), # Keep search-error for landing page
    Input('search-button', 'n_clicks'),
    State('search-input', 'value'),
    prevent_initial_call=True,
)
def search_topic(n_clicks, search_value):
    """Handle search bar submissions on landing page."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    topic_key = (search_value or '').lower().strip()
    
    # Check if the search matches a main topic, then go to subtopic selection
    if topic_key in MOCK_DATA:
        return {'view': 'subtopic_selection', 'main_topic': topic_key, 'subtopic': None}, None
    
    # Optionally, check if it matches a subtopic and jump directly to dashboard
    # This requires iterating through all subtopics, which can be complex.
    # For now, we'll only allow main topic search to simplify.
    
    error_msg = f"Topic '{search_value}' not found. Please try one of the main topics or select a button."
    return dash.no_update, dbc.Alert(error_msg, color="danger", dismissable=True, className="mt-3")

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'topic-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_main_topic(n_clicks):
    """Handle main topic button clicks to switch to the subtopic selection view."""
    ctx = dash.callback_context
    if not any(n_clicks) or not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    button_id_str = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id_str)
    main_topic_key = button_id['index']
    
    # Now, navigate to the subtopic selection view
    return {'view': 'subtopic_selection', 'main_topic': main_topic_key, 'subtopic': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'subtopic-button', 'main_topic': ALL, 'subtopic_key': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_subtopic(n_clicks):
    """Handle subtopic button clicks to switch to the detailed dashboard view."""
    ctx = dash.callback_context
    if not any(n_clicks) or not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id_str = ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id_str)
    
    main_topic_key = button_id['main_topic']
    subtopic_key = button_id['subtopic_key']
    
    # Navigate to the dashboard view with both main topic and subtopic
    return {'view': 'dashboard', 'main_topic': main_topic_key, 'subtopic': subtopic_key}


@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-topics-button', 'n_clicks'),
    prevent_initial_call=True
)
def go_back_to_topics(n_clicks):
    """Handle 'Back to Topics' button click to return to the landing page."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    return {'view': 'landing', 'main_topic': None, 'subtopic': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-subtopics-button', 'n_clicks'),
    State('app-state', 'data'), # Need current app state to know the main topic
    prevent_initial_call=True
)
def go_back_to_subtopics(n_clicks, current_state):
    """Handle 'Go Back to Subtopics' button click to return to subtopic selection."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    main_topic = current_state.get('main_topic')
    return {'view': 'subtopic_selection', 'main_topic': main_topic, 'subtopic': None}


@app.callback(
    Output('graph-click-output', 'children'),
    Input('knowledge-graph', 'tapNodeData'),
    prevent_initial_call=True
)
def display_tap_node_data(data):
    if data:
        return f"You clicked on node: **{data['label']}**. In a real app, this would trigger a new search or display detailed publication data related to this topic."
    return "Click a node to see details."


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
    app.run(debug=True)