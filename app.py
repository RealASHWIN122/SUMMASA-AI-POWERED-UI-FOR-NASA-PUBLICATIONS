import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_cytoscape as cyto
import json
import tempfile
import os
import base64
import atexit

# Scraper and Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# Make sure you have nslsl_scraper.py in the same directory
from nslsl_scraper import scrape_nslsl_search_results, download_nslsl_pdf

# Gemini Imports
from google import genai
from google.genai import types

# =========================================================================
# === WEB DRIVER & GEMINI MANAGEMENT ===
# =========================================================================
print("🚀 Initializing Selenium WebDriver...")
chrome_options = Options()
chrome_options.add_argument("--headless")
DRIVER = webdriver.Chrome(options=chrome_options)

def close_driver():
    print("🛑 Shutting down WebDriver.")
    DRIVER.quit()
atexit.register(close_driver)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "YOUR_API_KEY_HERE") 
MODEL_NAME = 'gemini-1.5-flash'
try:
    if GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        client = None; GEMINI_AVAILABLE = False
        print("WARNING: Gemini API Key not set.")
except Exception as e:
    client = None; GEMINI_AVAILABLE = False
    print(f"Error initializing Gemini Client: {e}")

def get_pdf_summary_dash(base64_content, filename, summary_length, current_client):
    if not current_client or not base64_content: return "Gemini API is not configured or file content is missing.", "danger"
    content_type, content_string = base64_content.split(',')
    decoded = base64.b64decode(content_string)
    uploaded_file = None
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(decoded)
            temp_file_path = tmp_file.name
        uploaded_file = current_client.files.upload(path=temp_file_path, display_name=filename)
        system_instruction = "You are an expert document summarization specialist..."
        prompt = f"Summarize the uploaded PDF document named '{filename}' in a **{summary_length}** format..."
        model = current_client.models.get_model(f'models/{MODEL_NAME}')
        response = model.generate_content([uploaded_file, prompt], system_instruction=system_instruction)
        summary, status = response.text, "success"
    except Exception as e:
        summary, status = f"An error occurred during summarization: {e}", "danger"
    finally:
        if temp_file_path and os.path.exists(temp_file_path): os.unlink(temp_file_path)
        if uploaded_file:
            try: current_client.files.delete(name=uploaded_file.name)
            except Exception as e: print(f"Gemini file cleanup failed for {uploaded_file.name}: {e}")
    return summary, status
# =========================================================================

# --- MOCK DATA ---
MOCK_DATA = {
    'physics': {
        'display_name': 'Physics', 'layout_group': 'sidebar', 'subtopics': {
            'classical_mechanics': {
                'title': 'Classical Mechanics', 'summary': "Classical mechanics deals with the motion of macroscopic objects...",
                'experiments': pd.DataFrame({"System": ["Pendulums", "Projectiles", "Planetary Orbits"], "Studies": [120, 85, 200]}),
                'knowledge_gaps': {"Three-Body Problem": 40, "Non-Inertial Frames": 30, "Chaotic Systems": 30},
                'actionable': { 'Mission Architects': "Utilize gravitational assist maneuvers...", 'Scientists': "Refine models for atmospheric drag...", 'Managers': "Allocate resources for better collision avoidance..." },
                'graph_elements': [ {'data': {'id': 'newton', 'label': "Newton's Laws"}}, {'data': {'id': 'motion', 'label': 'Equations of Motion'}}, {'data': {'source': 'newton', 'target': 'motion'}} ],
                'related_documents': [ {'title': 'NASA Reports: Basics of Space Flight', 'url': 'https://solarsystem.nasa.gov/basics/space-flight/'}, {'title': 'Orbital Mechanics - Glenn Research Center', 'url': 'https://www.nasa.gov/mission_pages/station/expeditions/expedition30/tryathome.html'} ]
            },
            'quantum_mechanics': { 'title': 'Quantum Mechanics', 'summary': "Summary for Quantum Mechanics...", 'experiments': pd.DataFrame(), 'knowledge_gaps': {}, 'actionable': {}, 'graph_elements': [] },
        }
    },
    'chemistry': {
        'display_name': 'Chemistry', 'layout_group': 'sidebar', 'subtopics': {
            'astrochemistry': { 'title': 'Astrochemistry', 'summary': "Astrochemistry is the study of molecules in the Universe...", 'experiments': pd.DataFrame(), 'knowledge_gaps': {}, 'actionable': {}, 'graph_elements': [] },
        }
    },
    'maths': {
        'display_name': 'Maths', 'layout_group': 'sidebar', 'subtopics': {
            'orbital_mechanics': { 'title': 'Orbital Mechanics', 'summary': "Also known as astrodynamics...", 'experiments': pd.DataFrame(), 'knowledge_gaps': {}, 'actionable': {}, 'graph_elements': [] },
        }
    },
    'science': {
        'display_name': 'Science', 'layout_group': 'sidebar', 'subtopics': {
            'exoplanetology': { 'title': 'Exoplanetology', 'summary': "The scientific field of exoplanets...", 'experiments': pd.DataFrame(), 'knowledge_gaps': {}, 'actionable': {}, 'graph_elements': [] },
        }
    },
    'doc_analysis': { 'display_name': 'Document Analysis (AI)', 'layout_group': 'main', 'default_subtopic': 'summarizer_mode' }
}

# --- STYLES & APP INIT ---
APP_THEME = dbc.themes.CYBORG
CUSTOM_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
LOGO = "/assets/AI-image-summarizer-for-Journalists-Content-Creators.png"
CHART_TEMPLATE = 'plotly_dark'
app = dash.Dash(__name__, external_stylesheets=[APP_THEME, CUSTOM_CSS, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "NASA HELPER"

# --- REUSABLE COMPONENTS ---
def create_card(title, content, icon):
    if content is None: return None
    header = html.H5([html.I(className=f"bi {icon} me-2"), " ", title], className="card-title", style={'color': '#00bfff'})
    body = [header, html.Hr()]
    if isinstance(content, list): body.extend(content)
    else: body.append(content)
    return dbc.Card(dbc.CardBody(body), className="mb-4", style={'borderColor': '#00bfff', 'backgroundColor': '#1a2a44'})

# --- LAYOUT GENERATORS ---
def generate_summarizer_page_layout():
    """Generates the dedicated layout for the document summarizer feature."""
    gemini_ui_content = [
        html.P("Upload a PDF document to receive an AI-powered summary. This is ideal for quickly processing research papers, mission reports, or technical specifications.", className="lead"),
        dbc.Alert(
            "⚠️ Gemini API Key is not configured. Document Analysis is currently disabled. Please set your API key as an environment variable.", 
            color="warning", 
            is_open=not GEMINI_AVAILABLE
        ),
        dbc.Row([
            dbc.Col(dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select a PDF File', style={'color': '#ff8c00'})]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px 0', 'color': '#00bfff'
                },
                multiple=False,
                disabled=not GEMINI_AVAILABLE
            ), md=6),
            dbc.Col(dcc.Dropdown(
                id='summary-length-dropdown',
                options=[
                    {'label': 'Executive Summary (200 words)', 'value': 'executive summary (200 words)'},
                    {'label': '3 Concise Bullet Points', 'value': '3 concise bullet points'},
                    {'label': 'One Short Paragraph', 'value': 'one short paragraph'},
                    {'label': 'Detailed Report (500 words)', 'value': 'detailed report (500 words)'}
                ],
                value='executive summary (200 words)',
                clearable=False,
                style={'color': '#333'} 
            ), md=4),
            dbc.Col(dbc.Button(
                "Summarize Document", 
                id="summarize-button", 
                color="primary", 
                className="mt-3 w-100",
                disabled=not GEMINI_AVAILABLE,
                style={'backgroundColor': '#ff8c00', 'borderColor': '#ff8c00'}
            ), md=2)
        ], className="align-items-center"),
        
        html.Div(id='upload-filename-display', className="mb-3 text-white-50"),
        html.Div(id='summary-output-container', children=dbc.Alert("Upload a PDF and click 'Summarize Document' to see results.", color="info", className="mt-4")),
    ]
    
    return html.Div([
        dbc.Button("Back to Topics", id="back-to-topics-button", className="mb-3", color="light", outline=True),
        html.H3("Gemini AI Document Analysis", className="text-white mb-4"),
        create_card("On-Demand PDF Summarizer", gemini_ui_content, "bi-file-earmark-text-fill")
    ])

def generate_landing_layout():
    """Creates the initial screen."""
    horizontal_buttons = html.Div(
        [
            dbc.Button(
                data['display_name'],
                id={'type': 'topic-button', 'index': key},
                className="m-2",
                color="secondary"
            ) for key, data in MOCK_DATA.items() if data.get('layout_group') == 'sidebar'
        ],
        className="d-flex justify-content-center flex-wrap mb-4"
    )

    main_buttons = html.Div(
        [
            dbc.Button(
                data['display_name'],
                id={'type': 'topic-button', 'index': key},
                size="lg",
                className="m-3",
                style={'background': 'linear-gradient(90deg, #00bfff, #483d8b)', 'borderColor': '#00bfff', 'minWidth': '150px'}
            ) for key, data in MOCK_DATA.items() if data.get('layout_group') == 'main'
        ],
        className="d-flex justify-content-center flex-wrap mb-4"
    )
    
    hero_section = dbc.Container(
        [
            horizontal_buttons, 
            html.H1("Welcome to D0C0SUM", className="display-1 fw-bold text-white text-center"),
            html.P("A hacky bois initiative for summarize", className="text-center text-white-50 fs-4 mb-5"),
            main_buttons,
            dbc.InputGroup(
                [
                    dbc.Input(id="search-input", placeholder="Search for any topic...", type="text"),
                    dbc.Button(html.I(className="bi bi-search"), id="search-button", color="primary", style={'backgroundColor': '#00bfff', 'borderColor': '#00bfff'}),
                ],
                className="mb-3 w-75 mx-auto",
            ),
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

def generate_dashboard_layout(main_topic_key, subtopic_key, scraped_results=None):
    """Creates the detailed dashboard view, with placeholder cards and the scraped list."""
    if main_topic_key == 'doc_analysis' and subtopic_key == 'summarizer_mode':
        return generate_summarizer_page_layout()

    data = {}
    is_custom_query = subtopic_key == 'custom_query'

    if is_custom_query:
        # Use placeholder data for the main dashboard cards
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
    elif main_topic_key in MOCK_DATA and subtopic_key in MOCK_DATA[main_topic_key].get('subtopics', {}):
        # Data from our pre-defined MOCK_DATA
        data = MOCK_DATA[main_topic_key]['subtopics'][subtopic_key]
    else:
        return dbc.Alert("Error: Data for this topic could not be found.", color="danger")

    # --- Create ALL dashboard cards, using placeholder data if needed ---
    summary_card = create_card("AI-Powered Summary", dcc.Markdown(data.get('summary', '')), "bi-robot")
    
    knowledge_graph = create_card("Knowledge Graph", cyto.Cytoscape(
        id='knowledge-graph', layout={'name': 'cose'}, style={'width': '100%', 'height': '400px'},
        elements=data.get('graph_elements', []),
    ), "bi-diagram-3-fill")

    experiments_df = data.get('experiments')
    if experiments_df is not None and not experiments_df.empty:
        fig_bar = px.bar(
            experiments_df, x=experiments_df.columns[0], y=experiments_df.columns[1],
            title='Data Distribution', template=CHART_TEMPLATE, color_discrete_sequence=['#ff69b4']
        )
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        bar_chart = create_card("Data Distribution", dcc.Graph(figure=fig_bar, config={'staticPlot': True}, style={'height': '350px'}), "bi-bar-chart-line-fill")
    else:
        bar_chart = create_card("Data Distribution", "No experimental data available.", "bi-bar-chart-line-fill")
        
    # --- Scraped Documents Card ---
    scraped_documents_card = None
    if scraped_results and scraped_results.get('documents'):
        doc_items = [
            dbc.ListGroupItem(
                doc["title"], id={'type': 'doc-title-button', 'index': doc["title"]},
                action=True, className="text-white bg-dark"
            ) for doc in scraped_results['documents']
        ]
        scraped_content = [
            html.P("Click a title to download its PDF.", className="small"),
            dbc.ListGroup(doc_items, flush=True, style={'maxHeight': '400px', 'overflowY': 'auto'}),
            html.Div(id='download-status-container', className="mt-2")
        ]
        scraped_documents_card = create_card("Scraped Documents", scraped_content, "bi-card-list")

    back_button_id = "back-to-subtopics-button" if not is_custom_query else "back-to-topics-button"
    back_button_text = "Go Back to Subtopics" if not is_custom_query else "Back to Home"

    # --- Assemble final layout ---
    return html.Div([
        dbc.Button(back_button_text, id=back_button_id, className="mb-3", color="light", outline=True),
        html.H3(f"{data.get('title', 'Dashboard')}", className="text-white mb-4"),
        dbc.Row([
            dbc.Col([
                summary_card,
                knowledge_graph,
            ], md=7),
            dbc.Col([
                bar_chart,
                scraped_documents_card, # Add the scraped documents card to the right column
            ], md=5)
        ]),
    ])

# --- MAIN APP LAYOUT & ROUTER ---
header = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row(
                [dbc.Col(html.Img(src=LOGO, height="40px")), dbc.Col(dbc.NavbarBrand("NASA DOCOSUM", className="ms-2 text-white"))],
                align="center", className="g-0",
            ),
            id="logo-home-link",
            href="#", style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Home", id="home-nav-link", href="#", active="exact", style={'color': '#ff8c00'})),
        ], className="ms-auto", navbar=True)
    ]),
    color="#0d172a", dark=True, sticky="top"
)

app.layout = html.Div([
    dcc.Store(id='app-state', data={'view': 'landing', 'main_topic': None, 'subtopic': None, 'uploaded_data': None, 'uploaded_filename': None, 'scraped_results': None}),
    header,
    dcc.Loading(id="loading-spinner", type="circle", children=html.Div(id="page-content"))
])

@app.callback(Output('page-content', 'children'), Input('app-state', 'data'))
def router(data):
    """Main router to switch between views."""
    view = data.get('view')
    if view == 'landing': return generate_landing_layout()
    elif view == 'subtopic_selection': return generate_subtopic_layout(data.get('main_topic'))
    elif view == 'dashboard':
        return html.Div(generate_dashboard_layout(
            data.get('main_topic'), 
            data.get('subtopic'), 
            data.get('scraped_results')
        ), className="p-4")
    return html.Div("404 - Page not found")

# --- CALLBACKS ---
@app.callback(
    [Output('app-state', 'data', allow_duplicate=True), Output('upload-filename-display', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'), State('app-state', 'data'),
    prevent_initial_call=True
)
def save_uploaded_file(list_of_contents, list_of_names, current_state):
    if list_of_contents is None: raise dash.exceptions.PreventUpdate
    current_state['uploaded_data'] = list_of_contents
    current_state['uploaded_filename'] = list_of_names
    return current_state, html.P(f"File ready: **{list_of_names}**", className="text-success")

@app.callback(
    Output('summary-output-container', 'children'),
    Input('summarize-button', 'n_clicks'),
    State('app-state', 'data'), State('summary-length-dropdown', 'value'),
    prevent_initial_call=True
)
def generate_summary_from_upload(n_clicks, app_state, summary_length):
    if not n_clicks: raise dash.exceptions.PreventUpdate
    if not GEMINI_AVAILABLE: return dbc.Alert("Error: Gemini API is not configured.", color="danger")
    uploaded_data = app_state.get('uploaded_data')
    uploaded_filename = app_state.get('uploaded_filename')
    if not uploaded_data: return dbc.Alert("Please upload a PDF file first.", color="warning")
    summary, status = get_pdf_summary_dash(uploaded_data, uploaded_filename, summary_length, client)
    return create_card(f"Gemini Summary: {uploaded_filename}", dcc.Markdown(summary), "bi-file-earmark-text-fill") if status == 'success' else dbc.Alert(summary, color=status)

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Output('search-error', 'children'),
    Input('search-button', 'n_clicks'),
    State('search-input', 'value'), State('app-state', 'data'),
    prevent_initial_call=True,
)
def search_topic(n_clicks, search_value, current_state):
    """Handle search bar submissions, now with live scraping."""
    if not n_clicks or not search_value:
        raise dash.exceptions.PreventUpdate
    
    topic_key = (search_value or '').lower().strip()
    if topic_key in MOCK_DATA:
        if 'subtopics' not in MOCK_DATA[topic_key]:
            subtopic_key = MOCK_DATA[topic_key]['default_subtopic']
            current_state.update({'view': 'dashboard', 'main_topic': topic_key, 'subtopic': subtopic_key, 'scraped_results': None})
            return current_state, None
        current_state.update({'view': 'subtopic_selection', 'main_topic': topic_key, 'subtopic': None, 'scraped_results': None})
        return current_state, None
    else:
        print(f"🔍 Custom search triggered for: {search_value}")
        results = scrape_nslsl_search_results(DRIVER, search_value)
        
        current_state['scraped_results'] = {'documents': results, 'full_data': results} if results else None
        current_state['view'] = 'dashboard'
        current_state['main_topic'] = search_value
        current_state['subtopic'] = 'custom_query'
        return current_state, None

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'topic-button', 'index': ALL}, 'n_clicks'),
    Input('logo-home-link', 'n_clicks'), Input('home-nav-link', 'n_clicks'),
    prevent_initial_call=True
)
def select_main_topic(n_clicks_list, logo_clicks, home_nav_clicks):
    triggered_id = ctx.triggered_id
    if not triggered_id: raise dash.exceptions.PreventUpdate
    
    if isinstance(triggered_id, str) and triggered_id in ('logo-home-link', 'home-nav-link'):
        return {'view': 'landing', 'main_topic': None, 'subtopic': None, 'scraped_results': None}
    elif isinstance(triggered_id, dict) and triggered_id.get('type') == 'topic-button':
        main_topic_key = triggered_id['index']
        if 'subtopics' not in MOCK_DATA.get(main_topic_key, {}):
            subtopic_key = MOCK_DATA[main_topic_key]['default_subtopic']
            return {'view': 'dashboard', 'main_topic': main_topic_key, 'subtopic': subtopic_key, 'scraped_results': None}
        return {'view': 'subtopic_selection', 'main_topic': main_topic_key, 'subtopic': None, 'scraped_results': None}
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'subtopic-button', 'main_topic': ALL, 'subtopic_key': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def select_subtopic(n_clicks):
    if not ctx.triggered_id: raise dash.exceptions.PreventUpdate
    button_id = ctx.triggered_id
    return {'view': 'dashboard', 'main_topic': button_id['main_topic'], 'subtopic': button_id['subtopic_key'], 'scraped_results': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-topics-button', 'n_clicks'),
    prevent_initial_call=True
)
def go_back_to_topics(n_clicks):
    if not n_clicks: raise dash.exceptions.PreventUpdate
    return {'view': 'landing', 'main_topic': None, 'subtopic': None, 'scraped_results': None}

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input('back-to-subtopics-button', 'n_clicks'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def go_back_to_subtopics(n_clicks, current_state):
    if not n_clicks: raise dash.exceptions.PreventUpdate
    return {'view': 'subtopic_selection', 'main_topic': current_state.get('main_topic'), 'subtopic': None, 'scraped_results': None}

@app.callback(
    Output('download-status-container', 'children'),
    Input({'type': 'doc-title-button', 'index': ALL}, 'n_clicks'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def handle_document_click(n_clicks, app_state):
    if not ctx.triggered_id or not any(n_clicks): raise dash.exceptions.PreventUpdate
    clicked_doc_title = ctx.triggered_id['index']
    scraped_data = app_state.get('scraped_results', {}).get('full_data', [])
    selected_doc = next((doc for doc in scraped_data if doc["title"] == clicked_doc_title), None)
    if not selected_doc: return dbc.Alert(f"Error: Document '{clicked_doc_title}' not found.", color="danger")
    
    pdf_path = download_nslsl_pdf(driver=DRIVER, doc_url=selected_doc["url"])
    
    if pdf_path: return dbc.Alert(f"Success! Saved to: {os.path.abspath(pdf_path)}", color="success", duration=10000)
    else: return dbc.Alert(f"Download failed for '{clicked_doc_title}'.", color="danger", duration=10000)

if __name__ == '__main__':
    app.run(debug=True)