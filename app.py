import dash
from dash import dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_cytoscape as cyto
import json

# =========================================================================
# === GEMINI INTEGRATION SECTION ===
# =========================================================================
import tempfile
import os
import base64
from google import genai
from google.genai import types

# WARNING: Replace this with your actual key or use os.environ['GEMINI_API_KEY']
# Using a placeholder for security.
GEMINI_API_KEY = "AIzaSyA2f64amvhSBD26sDYgzJv6bgTQqlB_hNA" 
MODEL_NAME = 'gemini-2.5-flash'

# Initialize the Gemini Client
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "AIzaSyA2f64amvhSBD26sDYgzJv6bgTQqlC_hNA_REPLACE_ME":
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        client = None
        GEMINI_AVAILABLE = False
        print("WARNING: Gemini API Key not set. Document Analysis will be disabled.")
except Exception as e:
    client = None
    GEMINI_AVAILABLE = False
    print(f"Error initializing Gemini Client: {e}")

def get_pdf_summary_dash(base64_content, filename, summary_length, current_client):
    """
    Handles file decoding, upload to Gemini, summarization, and cleanup.
    Returns the summary text and a status message.
    """
    if not current_client or not base64_content:
        return "Gemini API is not configured or file content is missing.", "danger"

    content_type, content_string = base64_content.split(',')
    decoded = base64.b64decode(content_string)
    
    uploaded_file_part = None
    temp_file_path = None
    
    # 1. Save the uploaded file to a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(decoded)
            temp_file_path = tmp_file.name

        # 2. Upload the file to the Gemini File API
        uploaded_file_part = current_client.files.upload(
            file=temp_file_path, 
            config={'mime_type': 'application/pdf'}
        )
        
        system_instruction = (
            "You are an expert document summarization specialist. Your task is to provide a concise, "
            "accurate summary of the provided PDF document. Focus on key findings, main arguments, "
            "and conclusions. The user wants the output in Markdown format."
        )
        
        prompt = f"Summarize the uploaded PDF document named '{filename}' in a **{summary_length}** format. Return only the summary text, no conversational phrases."
        
        # 3. Generate content
        response = current_client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file_part, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2 
            )
        )
        summary = response.text
        status = "success"
        
    except Exception as e:
        summary = f"An error occurred during summarization: {e}"
        status = "danger"
        
    finally:
        # 4. Clean up
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            
        if uploaded_file_part:
            try:
                current_client.files.delete(name=uploaded_file_part.name)
            except Exception as e:
                # Log the file cleanup failure but don't halt the app
                print(f"Gemini file cleanup failed for {uploaded_file_part.name}: {e}")
            
    return summary, status
# =========================================================================


# --- Mock Data (MODIFIED for Doc Analysis Button) --------------------------------------------
# --- Mock Data (MODIFIED for new buttons and layout) ---------------------
# --- Mock Data (MODIFIED with all subtopics) ---------------------
MOCK_DATA = {
    # --- Physics (Already done) ---
    'physics': {
        'display_name': 'Physics',
        'layout_group': 'sidebar',
        'subtopics': {
            'classical_mechanics': {
    'title': 'Classical Mechanics',
    'summary': "Classical mechanics deals with the motion of macroscopic objects...",
    # ... (keep all the existing keys like experiments, knowledge_gaps, etc.)
    
    # --- UPDATE THIS LIST ---
    'related_documents': [
            {'title': 'NASA Technical Reports: Basics of Space Flight', 'url': 'https://solarsystem.nasa.gov/basics/space-flight/'},
            {'title': 'Introduction to Orbital Mechanics - Glenn Research Center', 'url': 'https://www.nasa.gov/mission_pages/station/expeditions/expedition30/tryathome.html'}
            

        
      
    ]
    # ------------------------------------
},
            'quantum_mechanics': {
                'title': 'Quantum Mechanics',
                'summary': "Summary for Quantum Mechanics goes here.",
                'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
                'knowledge_gaps': {"Awaiting Analysis": 100},
                'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
                'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
            },
            'thermodynamics': {
                'title': 'Thermodynamics',
                'summary': "Summary for Thermodynamics goes here.",
                'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
                'knowledge_gaps': {"Awaiting Analysis": 100},
                'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
                'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
            }
        }
    },
    
    # --- NEW: Chemistry ---
    'chemistry': {
        'display_name': 'Chemistry',
        'layout_group': 'sidebar',
        'subtopics': {
            'astrochemistry': {
                'title': 'Astrochemistry',
                'summary': "Astrochemistry is the study of the abundance and reactions of molecules in the Universe, and their interaction with radiation. It's crucial for understanding the formation of stars, planets, and potentially life.",
                'experiments': pd.DataFrame({
                    "Method": ["Radio Telescopes", "Space Probes", "Lab Simulations"],
                    "Detections": [150, 45, 90]
                }),
                'knowledge_gaps': {"Prebiotic Molecules": 50, "Isotopic Ratios": 30, "Reaction Pathways": 20},
                'actionable': {
                    'Mission Architects': "Equip probes with advanced spectrometers to analyze molecular clouds and planetary atmospheres.",
                    'Scientists': "Model chemical reactions in low-temperature, low-pressure environments to replicate interstellar conditions.",
                    'Managers': "Support interdisciplinary projects combining astronomy, chemistry, and biology."
                },
                'graph_elements': [
                    {'data': {'id': 'clouds', 'label': 'Interstellar Clouds'}},
                    {'data': {'id': 'molecules', 'label': 'Simple Molecules'}},
                    {'data': {'id': 'organics', 'label': 'Complex Organics'}},
                    {'data': {'id': 'life', 'label': 'Origin of Life?'}},
                    {'data': {'source': 'clouds', 'target': 'molecules'}},
                    {'data': {'source': 'molecules', 'target': 'organics'}},
                    {'data': {'source': 'organics', 'target': 'life'}},
                ]
            },
            'propellants': {
                'title': 'Propellant Chemistry',
                'summary': "The study of chemical propellants is vital for launch vehicles and spacecraft. Research focuses on increasing specific impulse (Isp), stability, and storability of fuels and oxidizers, including cryogenics and hypergolic compounds.",
                'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
                'knowledge_gaps': {"Awaiting Analysis": 100},
                'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
                'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
            }
        }
    },

    # --- NEW: Maths ---
    'maths': {
        'display_name': 'Maths',
        'layout_group': 'sidebar',
        'subtopics': {
            'orbital_mechanics': {
                'title': 'Orbital Mechanics',
                'summary': "Also known as astrodynamics, this is the application of ballistics and celestial mechanics to the practical problems concerning the motion of rockets and other spacecraft. It allows for the calculation of trajectories, planetary flybys, and orbital maneuvers.",
                'experiments': pd.DataFrame({
                    "Application": ["Satellite Deployment", "Interplanetary Travel", "Debris Tracking"],
                    "Missions": [1000, 50, 200]
                }),
                'knowledge_gaps': {"Low-Thrust Optimization": 45, "N-Body Problem": 35, "Chaotic Systems": 20},
                'actionable': {
                    'Mission Architects': "Design fuel-efficient trajectories using principles like Hohmann transfers and gravitational assists.",
                    'Scientists': "Develop robust algorithms to solve the n-body problem for stable multi-satellite constellations.",
                    'Managers': "Invest in collision avoidance systems based on predictive orbital modeling."
                },
                'graph_elements': [
                    {'data': {'id': 'kepler', 'label': "Kepler's Laws"}},
                    {'data': {'id': 'trajectory', 'label': 'Trajectory Calculation'}},
                    {'data': {'id': 'hohmann', 'label': 'Hohmann Transfer'}},
                    {'data': {'id': 'success', 'label': 'Mission Success'}},
                    {'data': {'source': 'kepler', 'target': 'trajectory'}},
                    {'data': {'source': 'trajectory', 'target': 'hohmann'}},
                    {'data': {'source': 'hohmann', 'target': 'success'}},
                ]
            },
            'signal_processing': {
                'title': 'Signal Processing',
                'summary': "Mathematical techniques are essential for cleaning, decoding, and interpreting data transmitted from spacecraft over vast distances. This includes Fourier analysis, error correction codes, and image compression algorithms.",
                'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
                'knowledge_gaps': {"Awaiting Analysis": 100},
                'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
                'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
            }
        }
    },

    # --- NEW: Science ---
    'science': {
        'display_name': 'Science',
        'layout_group': 'sidebar',
        'subtopics': {
            'exoplanetology': {
                'title': 'Exoplanetology',
                'summary': "The scientific field dedicated to the discovery and study of exoplanets (planets outside our Solar System). Key methods include transit photometry and radial velocity, with the ultimate goal of finding habitable worlds.",
                'experiments': pd.DataFrame({
                    "Mission": ["Kepler", "TESS", "JWST"],
                    "Discoveries": [2662, 250, 50]
                }),
                'knowledge_gaps': {"Biosignatures": 60, "Planet Formation": 25, "Rogue Planets": 15},
                'actionable': {
                    'Mission Architects': "Design next-generation telescopes with coronagraphs to directly image exoplanets and analyze their atmospheres.",
                    'Scientists': "Develop machine learning models to sift through telescope data and identify potential transit signals.",
                    'Managers': "Prioritize long-term funding for missions capable of atmospheric characterization of Earth-like exoplanets."
                },
                'graph_elements': [
                    {'data': {'id': 'star', 'label': 'Distant Star'}},
                    {'data': {'id': 'transit', 'label': 'Transit Method'}},
                    {'data': {'id': 'planet', 'label': 'Exoplanet Detected'}},
                    {'data': {'id': 'atmosphere', 'label': 'Atmosphere Analysis'}},
                    {'data': {'id': 'habitability', 'label': 'Habitability?'}},
                    {'data': {'source': 'star', 'target': 'transit'}},
                    {'data': {'source': 'transit', 'target': 'planet'}},
                    {'data': {'source': 'planet', 'target': 'atmosphere'}},
                    {'data': {'source': 'atmosphere', 'target': 'habitability'}},
                ]
            },
            'planetary_geology': {
                'title': 'Planetary Geology',
                'summary': "This discipline, also known as astrogeology, studies the geology of celestial bodies such as planets, moons, asteroids, and comets. It helps us understand the formation and evolution of our solar system.",
                'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
                'knowledge_gaps': {"Awaiting Analysis": 100},
                'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
                'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
            }
        }
    },
    
    # --- Main Button ---
    'doc_analysis': {
        'display_name': 'Document Analysis (AI)',
        'layout_group': 'main', 
        'default_subtopic': 'summarizer_mode' 
    }
}

# --- Styles & Theming (Unchanged) -----------------------------------------------------------
# --- Styles & Theming (Unchanged) -----------------------------------------------------------
APP_THEME = dbc.themes.CYBORG
CUSTOM_CSS = "https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
# The final, correct line
LOGO = "/assets/AI-image-summarizer-for-Journalists-Content-Creators.png"
CHART_TEMPLATE = 'plotly_dark'
# --- App Initialization (Unchanged) ---------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[APP_THEME, CUSTOM_CSS, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "NASA HELPER"

# --- Reusable Components (Unchanged) -------------------------------------------------------
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

# --- NEW: Dedicated Summarizer Layout Function ---
def generate_summarizer_page_layout():
    """Generates the dedicated layout for the document summarizer feature (NO TABS)."""
    # Gemini Document Analysis Content block
    gemini_ui_content = [
        html.P("Upload a PDF document to receive an AI-powered summary. This is ideal for quickly processing research papers, mission reports, or technical specifications.", className="lead"),
        dbc.Alert(
            "⚠️ Gemini API Key is not configured. Document Analysis is currently disabled. Please set your API key in the script.", 
            color="warning", 
            is_open=not GEMINI_AVAILABLE
        ) if not GEMINI_AVAILABLE else None,
        
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
                className="mt-3",
                disabled=not GEMINI_AVAILABLE,
                style={'backgroundColor': '#ff8c00', 'borderColor': '#ff8c00'}
            ), md=2)
        ], className="align-items-center"),
        
        html.Div(id='upload-filename-display', className="mb-3 text-white-50"),
        html.Div(id='summary-output-container', children=dbc.Alert("Upload a PDF and click 'Summarize Document' to see results.", color="info", className="mt-4")),
    ]
    
    return html.Div([
        # Button to go back to the landing page
        dbc.Button("Back to Topics", id="back-to-topics-button", className="mb-3", color="light", outline=True),
        html.H3("Gemini AI Document Analysis", className="text-white mb-4"),
        
        # The main card containing the Gemini UI
        create_card("On-Demand PDF Summarizer", gemini_ui_content, "bi-file-earmark-text-fill")
    ])

# --- Layout Generators ---------------------------------------------------------
def generate_landing_layout():
    """Creates the initial screen with a horizontal button bar above the title."""
    
    # 1. Create the horizontal bar of buttons from MOCK_DATA
    # This now includes all buttons that were previously in the sidebar
    horizontal_buttons = html.Div(
        [
            dbc.Button(
                data['display_name'],
                id={'type': 'topic-button', 'index': key},
                className="m-2", # Adds margin around each button
                color="secondary"
            ) for key, data in MOCK_DATA.items() if data.get('layout_group') == 'sidebar'
        ],
        className="d-flex justify-content-center flex-wrap mb-4" # Centers the buttons
    )

    # 2. Create the main "Document Analysis" button
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
    
    # 3. Assemble the final layout
    hero_section = dbc.Container(
        [
            # --- BUTTON BAR GOES HERE, ABOVE EVERYTHING ELSE ---
            horizontal_buttons, 
            
            html.H1("Welcome to D0C0SUM", className="display-1 fw-bold text-White text-center"),
            html.P("A hacky bois initiative for summarize", className="text-center text-white-50 fs-4 mb-5"),
            
            main_buttons, # The Document Analysis button
            
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

def generate_dashboard_layout(main_topic_key, subtopic_key):
    """Creates the detailed dashboard view for a selected topic or a custom query."""
    
    # *** CORE LOGIC FIX: Check for the dedicated summarizer flow and return the custom layout ***
    if main_topic_key == 'doc_analysis' and subtopic_key == 'summarizer_mode':
        return generate_summarizer_page_layout()
    # *****************************************************************************************

    # --- Standard Topic/Query Handling ---
    data = {}
    
    # CASE 1: Handle a custom query that is not in MOCK_DAT
    data = {
            'title': f"On-Demand Analysis for: {subtopic_key.title()}",
            'summary': "This is a custom query. In a real application, a backend model would generate a summary here based on the search term.",
            'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
            'knowledge_gaps': {"Awaiting Analysis": 100},
            'actionable': {
                'Mission Architects': "No pre-defined actions for this custom query.",
                'Scientists': "Further research is required based on this query.",
                'Managers': "Evaluate the potential of this new research area."
            },
            'graph_elements': [
                {'data': {'id': 'query', 'label': subtopic_key.title()}},
                {'data': {'id': 'placeholder', 'label': 'Analysis Pending...'}},
                {'data': {'source': 'query', 'target': 'placeholder'}, 'classes': 'edge'},
            ]
        }
   

    # --- Standard Dashboard Components ---
    graph_config = {'staticPlot': True}
    summary_card = create_card("AI-Powered Summary", dcc.Markdown(data['summary']), "bi-robot")
    knowledge_graph = create_card("Knowledge Graph", cyto.Cytoscape(
        id='knowledge-graph',
        layout={'name': 'cose'}, 
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
    
    # --- Gemini Document Analysis Tab Content (Reused in the main dashboard) ---
    doc_analysis_tab_content = html.Div([
        html.P("Upload a PDF document to get an on-demand summary related to space research.", className="lead"),
        dbc.Alert(
            "⚠️ Gemini API Key is not configured. Document Analysis is currently disabled.", 
            color="warning", 
            is_open=not GEMINI_AVAILABLE
        ) if not GEMINI_AVAILABLE else None,
        
        dbc.Row([
            dbc.Col(dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select a PDF File')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px', 'color': '#00bfff'
                },
                multiple=False
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
                className="mt-3",
                disabled=not GEMINI_AVAILABLE
            ), md=2)
        ]),
        html.Div(id='upload-filename-display', className="mb-3 text-white-50"),
        html.Div(id='summary-output-container', children=dbc.Alert("Upload a PDF and click 'Summarize Document' to see results.", color="info", className="mt-4")),
    ])
    
    # --- Dashboard Layout Structure with Tabs ---
    back_button_id = "back-to-subtopics-button" if subtopic_key != 'custom_query' else "back-to-topics-button"
    back_button_text = "Go Back to Subtopics" if subtopic_key != 'custom_query' else "Back to Home"

    return html.Div([
        dbc.Button(back_button_text, id=back_button_id, className="mb-3", color="light", outline=True),
        html.H3(f"{data['title']}", className="text-white mb-4"),
        
        # This is the standard view with the two tabs
        dbc.Tabs([
            dbc.Tab(
                label="Topic Dashboard", 
                children=html.Div([
                    dbc.Row([dbc.Col(summary_card, md=12)]),
                    dbc.Row([dbc.Col(knowledge_graph, md=7), dbc.Col([bar_chart, pie_chart], md=5)]),
                    dbc.Row([dbc.Col(actionable_insights, md=12)])
                ])
            ),
            dbc.Tab(
                label="Document Analysis ", 
                children=doc_analysis_tab_content
            ),
        ], className="mb-4", active_tab="tab-0") 
    ])


# --- Main App Layout (Unchanged) ------------------------------------------------------------
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
    dcc.Store(id='app-state', data={'view': 'landing', 'main_topic': None, 'subtopic': None, 'uploaded_data': None, 'uploaded_filename': None}),
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

# --- Dash/Gemini Integration Callbacks (UNMOVED: IDs are global) ---

@app.callback(
    [Output('app-state', 'data', allow_duplicate=True),
     Output('upload-filename-display', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def save_uploaded_file(list_of_contents, list_of_names, current_state):
    """Saves the uploaded file's content and name to the dcc.Store."""
    if list_of_contents is None:
        raise dash.exceptions.PreventUpdate

    uploaded_data = list_of_contents
    uploaded_filename = list_of_names
    
    current_state['uploaded_data'] = uploaded_data
    current_state['uploaded_filename'] = uploaded_filename
    
    return current_state, html.P(f"File ready for summarization: **{uploaded_filename}**", className="text-success")

@app.callback(
    Output('summary-output-container', 'children'),
    Input('summarize-button', 'n_clicks'),
    State('app-state', 'data'),
    State('summary-length-dropdown', 'value'),
    prevent_initial_call=True
)
def generate_summary_from_upload(n_clicks, app_state, summary_length):
    """Triggers the Gemini summarization and displays the result."""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    
    if not GEMINI_AVAILABLE:
        return dbc.Alert("Error: Gemini API is not configured.", color="danger")

    uploaded_data = app_state.get('uploaded_data')
    uploaded_filename = app_state.get('uploaded_filename')
    
    if not uploaded_data:
        return dbc.Alert("Please upload a PDF file first.", color="warning")

    # Call the core Gemini function
    summary, status = get_pdf_summary_dash(uploaded_data, uploaded_filename, summary_length, client)
    
    return create_card(
        f"Gemini Summary: {uploaded_filename}", 
        dcc.Markdown(summary), 
        "bi-file-earmark-text-fill"
    ) if status == 'success' else dbc.Alert(summary, color=status)


# --- Navigation Callbacks (Adjusted for 'doc_analysis' flow) ---

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
    
    if topic_key in MOCK_DATA:
        if 'subtopics' not in MOCK_DATA[topic_key]:
            # Directly navigate non-subtopic entries (like 'doc_analysis') to their dashboard state
            subtopic_key = MOCK_DATA[topic_key]['default_subtopic']
            return {'view': 'dashboard', 'main_topic': topic_key, 'subtopic': subtopic_key}, None
            
        return {'view': 'subtopic_selection', 'main_topic': topic_key, 'subtopic': None}, None
    
    else:
        return {'view': 'dashboard', 'main_topic': search_value, 'subtopic': 'custom_query'}, None

@app.callback(
    Output('app-state', 'data', allow_duplicate=True),
    Input({'type': 'topic-button', 'index': ALL}, 'n_clicks'),
    Input('logo-home-link', 'n_clicks'),
    Input('home-nav-link', 'n_clicks'),
    prevent_initial_call=True
)
def select_main_topic(n_clicks_list, logo_clicks, home_nav_clicks):
    """Handle main topic button clicks and home/logo navigation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    if trigger_id in ('logo-home-link.n_clicks', 'home-nav-link.n_clicks'):
         return {'view': 'landing', 'main_topic': None, 'subtopic': None}
         
    if 'topic-button' in trigger_id:
        button_id = json.loads(trigger_id.split('.')[0])
        main_topic_key = button_id['index']

        # SPECIAL HANDLING: If the topic has no subtopics (like 'doc_analysis'), go straight to dashboard
        if main_topic_key in MOCK_DATA and 'subtopics' not in MOCK_DATA[main_topic_key]:
            subtopic_key = MOCK_DATA[main_topic_key]['default_subtopic']
            return {'view': 'dashboard', 'main_topic': main_topic_key, 'subtopic': subtopic_key}
            
        return {'view': 'subtopic_selection', 'main_topic': main_topic_key, 'subtopic': None}
        
    raise dash.exceptions.PreventUpdate


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

# --- Run Application (FIXED: app.run_server -> app.run) -------------------------------------
if __name__ == '__main__':
    app.run(debug=True)