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
    # --- Physics ---
    'physics': {
        'display_name': 'Physics',
        'layout_group': 'sidebar',
        'subtopics': {
            'classical_mechanics': {
                'title': 'Classical Mechanics',
                'summary': "Classical mechanics deals with the motion of macroscopic objects, from projectiles to parts of machinery, and astronomical objects. It's foundational to understanding forces like gravity and momentum as described by Newton's Laws of Motion.",
                'experiments': pd.DataFrame({"Object Type": ["Satellites", "Projectiles", "Planetary Orbits", "Robotic Arms"], "Studies": [25, 18, 15, 11]}),
                'knowledge_gaps': {"Orbital Decay": 40, "N-Body Problem": 35, "Material Stress": 25},
                'actionable': {
                    'Mission Architects': "Utilize gravitational assists for interplanetary missions to conserve fuel.",
                    'Scientists': "Investigate the long-term stability of orbits in multi-body systems.",
                    'Managers': "Fund development of predictive models for space debris trajectories."
                },
                'graph_elements': [{'data': {'id': 'newton', 'label': "Newton's Laws"}}, {'data': {'id': 'gravity', 'label': 'Gravity'}}, {'data': {'id': 'orbits', 'label': 'Planetary Orbits'}}, {'data': {'id': 'propulsion', 'label': 'Propulsion Systems'}}, {'data': {'source': 'newton', 'target': 'gravity'}}, {'data': {'source': 'gravity', 'target': 'orbits'}}, {'data': {'source': 'orbits', 'target': 'propulsion'}}],
                'related_documents': [
                    {'title': 'NASA Technical Reports: Basics of Space Flight', 'url': 'https://solarsystem.nasa.gov/basics/space-flight/'},
                    {'title': 'Introduction to Orbital Mechanics - Glenn Research Center', 'url': 'https://www.nasa.gov/mission_pages/station/expeditions/expedition30/tryathome.html'},
                    {'title': 'JPL Publication: Trajectory Design and Optimization', 'url': 'https://descanso.jpl.nasa.gov/monograph/series1/Descanso1_all.pdf'}
                ]
            },
            'quantum_mechanics': {
                'title': 'Quantum Mechanics',
                'summary': "Quantum mechanics governs the behavior of matter and light on the atomic and subatomic scale. Its applications in space include ultra-precise atomic clocks for navigation, quantum sensors, and future quantum communication networks.",
                'experiments': pd.DataFrame({"Application": ["Atomic Clocks", "Quantum Sensing", "Quantum Communication"], "Missions": [30, 8, 3]}),
                'knowledge_gaps': {"Decoherence in Space": 50, "Entanglement Distribution": 40, "Quantum Computing": 10},
                'actionable': {'Mission Architects': "Integrate next-gen atomic clocks for improved GPS and deep space navigation.", 'Scientists': "Develop quantum sensors for detecting gravitational waves and dark matter.", 'Managers': "Invest in foundational research for secure space-to-ground quantum communication."},
                'graph_elements': [{'data': {'id': 'qm', 'label': 'Quantum Mechanics'}}, {'data': {'id': 'clock', 'label': 'Atomic Clocks'}}, {'data': {'id': 'comm', 'label': 'Quantum Communication'}}, {'data': {'source': 'qm', 'target': 'clock'}}, {'data': {'source': 'qm', 'target': 'comm'}}],
                'related_documents': [
                    {'title': 'Quantum Technology for Space Applications', 'url': 'https://ntrs.nasa.gov/citations/20205008215'},
                    {'title': 'NASA\'s Quantum Computing Laboratory', 'url': 'https://www.nas.nasa.gov/quantum/'}
                ]
            },
            'thermodynamics': {
                'title': 'Thermodynamics',
                'summary': "Thermodynamics in space applications deals with heat management, power generation, and engine efficiency. This includes designing thermal protection systems for re-entry and powering deep space probes with Radioisotope Thermoelectric Generators (RTGs).",
                'experiments': pd.DataFrame({"System": ["Heat Shields", "RTGs", "Cryocoolers"], "Applications": [40, 27, 15]}),
                'knowledge_gaps': {"High-Temp Materials": 45, "Power Efficiency": 35, "Cryogenic Storage": 20},
                'actionable': {'Mission Architects': "Design missions like the Parker Solar Probe with robust thermal shielding.", 'Scientists': "Research more efficient thermoelectric materials for next-generation RTGs.", 'Managers': "Fund research into mitigating boil-off of cryogenic propellants for long-duration missions."},
                'graph_elements': [{'data': {'id': 'thermo', 'label': 'Thermodynamics'}}, {'data': {'id': 'heat', 'label': 'Heat Management'}}, {'data': {'id': 'power', 'label': 'Power Generation'}}, {'data': {'source': 'thermo', 'target': 'heat'}}, {'data': {'source': 'thermo', 'target': 'power'}}],
                'related_documents': [
                    {'title': 'A Heat Shield for Touching the Sun - NASA', 'url': 'https://www.nasa.gov/feature/goddard/2018/a-heat-shield-for-touching-the-sun'},
                    {'title': 'What Is a Radioisotope Thermoelectric Generator?', 'url': 'https://www.nasa.gov/directorates/spacetech/game_changing_development/what_is_a_radioisotope_thermoelectric_generator'}
                ]
            }
        }
    },
    # --- Chemistry ---
    'chemistry': {
        'display_name': 'Chemistry',
        'layout_group': 'sidebar',
        'subtopics': {
            'astrochemistry': {
                'title': 'Astrochemistry',
                'summary': "Astrochemistry is the study of molecules in the Universe and their reactions. It is crucial for understanding the formation of stars, planets, and the potential for life beyond Earth.",
                'experiments': pd.DataFrame({"Method": ["Radio Telescopes", "Space Probes", "Lab Simulations"], "Detections": [150, 45, 90]}),
                'knowledge_gaps': {"Prebiotic Molecules": 50, "Isotopic Ratios": 30, "Reaction Pathways": 20},
                'actionable': {'Mission Architects': "Equip probes with advanced spectrometers.", 'Scientists': "Model chemical reactions in interstellar conditions.", 'Managers': "Support interdisciplinary projects combining astronomy and chemistry."},
                'graph_elements': [{'data': {'id': 'clouds', 'label': 'Interstellar Clouds'}}, {'data': {'id': 'molecules', 'label': 'Simple Molecules'}}, {'data': {'id': 'organics', 'label': 'Complex Organics'}}, {'data': {'id': 'life', 'label': 'Origin of Life?'}}, {'data': {'source': 'clouds', 'target': 'molecules'}}, {'data': {'source': 'molecules', 'target': 'organics'}}, {'data': {'source': 'organics', 'target': 'life'}}],
                'related_documents': [
                    {'title': 'NASA’s Cosmic Ice Lab Helps Uncover the Chemistry of the Universe', 'url': 'https://www.nasa.gov/goddard/2023/feature/nasa-s-cosmic-ice-lab-helps-uncover-the-chemistry-of-the-universe'},
                    {'title': 'Webb Sees Ingredients for Life in Early Universe', 'url': 'https://www.nasa.gov/missions/webb/webb-sees-ingredients-for-life-in-early-universe/'}
                ]
            },
            'propellants': {
                'title': 'Propellant Chemistry',
                'summary': "The study of chemical propellants is vital for launch vehicles and spacecraft. Research focuses on increasing efficiency (specific impulse), stability, and storability of fuels and oxidizers.",
                'experiments': pd.DataFrame({"Type": ["Cryogenic", "Hypergolic", "Solid"], "Use Cases": [22, 18, 35]}),
                'knowledge_gaps': {"Methane Engines": 40, "Green Propellants": 35, "Long-term Storage": 25},
                'actionable': {'Mission Architects': "Select propellant types based on mission duration and thrust requirements.", 'Scientists': "Develop catalysts for more efficient green propellants to replace toxic hypergolics.", 'Managers': "Invest in infrastructure for in-situ resource utilization (e.g., creating methane on Mars)."},
                'graph_elements': [{'data': {'id': 'prop', 'label': 'Propellants'}}, {'data': {'id': 'launch', 'label': 'Launch'}}, {'data': {'id': 'maneuver', 'label': 'In-Space Maneuvers'}}, {'data': {'source': 'prop', 'target': 'launch'}}, {'data': {'source': 'prop', 'target': 'maneuver'}}],
                'related_documents': [
                    {'title': 'The Chemistry of Space Propulsion - ACS', 'url': 'https://www.acs.org/education/resources/highschool/chemmatters/past-issues/2018-2019/december-2018/space-propulsion.html'},
                    {'title': 'NASA is Turning to Greener Rocket Propellants', 'url': 'https://www.nasa.gov/nasa-is-turning-to-greener-rocket-propellants/'}
                ]
            }
        }
    },
    # --- Maths ---
    'maths': {
        'display_name': 'Maths',
        'layout_group': 'sidebar',
        'subtopics': {
            'orbital_mechanics': {
                'title': 'Orbital Mechanics',
                'summary': "Also known as astrodynamics, this is the application of ballistics and celestial mechanics to the practical problems concerning the motion of rockets and other spacecraft.",
                'experiments': pd.DataFrame({"Application": ["Satellite Deployment", "Interplanetary Travel", "Debris Tracking"], "Missions": [1000, 50, 200]}),
                'knowledge_gaps': {"Low-Thrust Optimization": 45, "N-Body Problem": 35, "Chaotic Systems": 20},
                'actionable': {'Mission Architects': "Design fuel-efficient trajectories using Hohmann transfers.", 'Scientists': "Develop algorithms to solve the n-body problem for constellations.", 'Managers': "Invest in collision avoidance systems."},
                'graph_elements': [{'data': {'id': 'kepler', 'label': "Kepler's Laws"}}, {'data': {'id': 'trajectory', 'label': 'Trajectory Calculation'}}, {'data': {'id': 'hohmann', 'label': 'Hohmann Transfer'}}, {'data': {'id': 'success', 'label': 'Mission Success'}}, {'data': {'source': 'kepler', 'target': 'trajectory'}}, {'data': {'source': 'trajectory', 'target': 'hohmann'}}, {'data': {'source': 'hohmann', 'target': 'success'}}],
                 'related_documents': [
                    {'title': 'What Is an Orbit? - NASA', 'url': 'https://www.nasa.gov/audience/forstudents/5-8/features/nasa-knows/what-is-orbit-58.html'},
                    {'title': 'Space Mathematics - A Resource for Teachers', 'url': 'https://www.nasa.gov/wp-content/uploads/2015/06/space_math_viii.pdf'}
                ]
            },
            'signal_processing': {
                'title': 'Signal Processing',
                'summary': "Mathematical techniques are essential for cleaning, decoding, and interpreting data transmitted from spacecraft over vast distances. This includes Fourier analysis, error correction codes, and image compression.",
                'experiments': pd.DataFrame({"Technique": ["Error Correction", "Image Compression", "Noise Filtering"], "Applications": [50, 45, 60]}),
                'knowledge_gaps': {"High-Bandwidth Comms": 55, "Data Compression Ratios": 30, "AI in Signal ID": 15},
                'actionable': {'Mission Architects': "Design communication systems with appropriate redundancy and error correction.", 'Scientists': "Create novel compression algorithms to maximize data return from deep space.", 'Managers': "Upgrade the Deep Space Network with more powerful signal processing hardware."},
                'graph_elements': [{'data': {'id': 'signal', 'label': 'Raw Signal'}}, {'data': {'id': 'filter', 'label': 'Noise Filtering'}}, {'data': {'id': 'decode', 'label': 'Decoding'}}, {'data': {'id': 'data', 'label': 'Usable Data'}}, {'data': {'source': 'signal', 'target': 'filter'}}, {'data': {'source': 'filter', 'target': 'decode'}}, {'data': {'source': 'decode', 'target': 'data'}}],
                 'related_documents': [
                    {'title': 'Deep Space Network (DSN) - NASA', 'url': 'https://www.nasa.gov/directorates/heo/scan/services/networks/deep_space_network/'},
                    {'title': 'How NASA Communicates with Faraway Spacecraft', 'url': 'https://www.jpl.nasa.gov/edu/news/2020/4/1/how-nasa-communicates-with-faraway-spacecraft/'}
                ]
            }
        }
    },
    # --- Science ---
    'science': {
        'display_name': 'Science',
        'layout_group': 'sidebar',
        'subtopics': {
            'exoplanetology': {
                'title': 'Exoplanetology',
                'summary': "The scientific field dedicated to the discovery and study of exoplanets. Key methods include transit photometry and radial velocity, with the ultimate goal of finding habitable worlds.",
                'experiments': pd.DataFrame({"Mission": ["Kepler", "TESS", "JWST"], "Discoveries": [2662, 250, 50]}),
                'knowledge_gaps': {"Biosignatures": 60, "Planet Formation": 25, "Rogue Planets": 15},
                'actionable': {'Mission Architects': "Design next-generation telescopes with coronagraphs to directly image exoplanets.", 'Scientists': "Develop machine learning models to identify potential transit signals.", 'Managers': "Prioritize funding for missions capable of atmospheric characterization."},
                'graph_elements': [{'data': {'id': 'star', 'label': 'Distant Star'}}, {'data': {'id': 'transit', 'label': 'Transit Method'}}, {'data': {'id': 'planet', 'label': 'Exoplanet Detected'}}, {'data': {'id': 'atmosphere', 'label': 'Atmosphere Analysis'}}, {'data': {'id': 'habitability', 'label': 'Habitability?'}}, {'data': {'source': 'star', 'target': 'transit'}}, {'data': {'source': 'transit', 'target': 'planet'}}, {'data': {'source': 'planet', 'target': 'atmosphere'}}, {'data': {'source': 'atmosphere', 'target': 'habitability'}}],
                 'related_documents': [
                    {'title': 'NASA Exoplanet Exploration Program', 'url': 'https://exoplanets.nasa.gov/'},
                    {'title': 'How Do We Find Exoplanets? - Hubblesite', 'url': 'https://hubblesite.org/contents/articles/how-do-we-find-exoplanets'}
                ]
            },
            'planetary_geology': {
                'title': 'Planetary Geology',
                'summary': "This discipline, also known as astrogeology, studies the geology of celestial bodies such as planets, moons, asteroids, and comets to understand the formation and evolution of our solar system.",
                'experiments': pd.DataFrame({"Target": ["Mars (Rovers)", "Moon (Apollo)", "Asteroids (OSIRIS-REx)"], "Missions": [5, 6, 1]}),
                'knowledge_gaps': {"Cryovolcanism": 40, "Planetary Core Dynamics": 35, "Early Solar System History": 25},
                'actionable': {'Mission Architects': "Design rovers and landers with drills and seismometers.", 'Scientists': "Analyze returned samples to date geological events.", 'Managers': "Fund sample return missions to diverse celestial bodies like asteroids and comets."},
                'graph_elements': [{'data': {'id': 'planet', 'label': 'Planet/Moon'}}, {'data': {'id': 'surface', 'label': 'Surface Features'}}, {'data': {'id': 'interior', 'label': 'Interior Structure'}}, {'data': {'id': 'history', 'label': 'Geological History'}}, {'data': {'source': 'planet', 'target': 'surface'}}, {'data': {'source': 'planet', 'target': 'interior'}}, {'data': {'source': 'surface', 'target': 'history'}}],
                 'related_documents': [
                    {'title': 'Planetary Geology - NASA Science', 'url': 'https://science.nasa.gov/planetary-science/geology/'},
                    {'title': 'Mars Science Laboratory (Curiosity Rover)', 'url': 'https://mars.nasa.gov/msl/home/'}
                ]
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
    
    if main_topic_key == 'doc_analysis' and subtopic_key == 'summarizer_mode':
        return generate_summarizer_page_layout()

    # --- Standard Topic/Query Handling ---
    data = {}
    if subtopic_key == 'custom_query':
        data = {
            'title': f"On-Demand Analysis for: {main_topic_key.title()}",
            'summary': "This is a custom query. A backend model would generate a summary here...",
            'experiments': pd.DataFrame({"Category": ["N/A"], "Count": [0]}),
            'knowledge_gaps': {"Awaiting Analysis": 100},
            'actionable': {'Mission Architects': "N/A", 'Scientists': "N/A", 'Managers': "N/A"},
            'graph_elements': [{'data': {'id': 'placeholder', 'label': 'Coming Soon'}}]
        }
    elif main_topic_key in MOCK_DATA and subtopic_key in MOCK_DATA[main_topic_key].get('subtopics', {}):
        data = MOCK_DATA[main_topic_key]['subtopics'][subtopic_key]
    else:
        return dbc.Alert("Error: Data for this topic could not be found.", color="danger")

    # --- ### ROBUST COMPONENT GENERATION (with corrections) ### ---
    
    summary_text = data.get('summary', 'No summary available for this topic.')
    summary_card = create_card("AI-Powered Summary", dcc.Markdown(summary_text), "bi-robot")

    graph_elements = data.get('graph_elements', [])
    # CORRECTED: Added the icon argument "bi-diagram-3-fill"
    knowledge_graph = create_card(
        "Knowledge Graph", 
        cyto.Cytoscape(id='knowledge-graph', layout={'name': 'cose'}, style={'width': '100%', 'height': '400px'}, elements=graph_elements, stylesheet=[{'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#00bfff', 'color': 'white'}}, {'selector': 'edge', 'style': {'line-color': '#4e5d78', 'width': 2}}]),
        "bi-diagram-3-fill" 
    )

    experiments_df = data.get('experiments', pd.DataFrame({'Category': ['No Data'], 'Count': [0]}))
    # CORRECTED: Added the icon argument "bi-bar-chart-line-fill"
    bar_chart = create_card(
        "Data Distribution", 
        dcc.Graph(figure=px.bar(experiments_df, x=experiments_df.columns[0], y=experiments_df.columns[1], template=CHART_TEMPLATE)),
        "bi-bar-chart-line-fill"
    )

    gaps_data = data.get('knowledge_gaps', {'No Data': 100})
    # CORRECTED: Added the icon argument "bi-pie-chart-fill"
    pie_chart = create_card(
        "Areas of Study", 
        dcc.Graph(figure=px.pie(names=list(gaps_data.keys()), values=list(gaps_data.values()), template=CHART_TEMPLATE, hole=0.4)),
        "bi-pie-chart-fill"
    )

    actionable_data = data.get('actionable', {})
    # CORRECTED: Added the icon argument "bi-lightbulb-fill"
    actionable_insights = create_card(
        "Actionable Insights", 
        [dbc.Tabs([
            dbc.Tab(dcc.Markdown(actionable_data.get('Mission Architects', 'N/A')), label="Architects"),
            dbc.Tab(dcc.Markdown(actionable_data.get('Scientists', 'N/A')), label="Scientists"),
            dbc.Tab(dcc.Markdown(actionable_data.get('Managers', 'N/A')), label="Managers")
        ])],
        "bi-lightbulb-fill"
    )
    
    research_links_section = None
    related_docs_list = data.get('related_documents', [])
    if related_docs_list:
        research_links_section = html.Div([
            html.H5("Related Research Papers", className="mt-4"),
            dbc.ListGroup(
                [dbc.ListGroupItem(html.A(doc['title'], href=doc['url'], target="_blank")) for doc in related_docs_list],
                flush=True
            )
        ])

    doc_analysis_tab_content = html.Div([
        html.P("Upload a PDF document to get an on-demand summary related to space research.", className="lead"),
        dbc.Alert("⚠️ Gemini API Key is not configured...", color="warning", is_open=not GEMINI_AVAILABLE) if not GEMINI_AVAILABLE else None,
        dbc.Row([
            dbc.Col(dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select a PDF File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px', 'color': '#00bfff'}, multiple=False), md=6),
            dbc.Col(dcc.Dropdown(id='summary-length-dropdown', options=[{'label': 'Executive Summary (200 words)', 'value': 'executive summary (200 words)'}, {'label': '3 Concise Bullet Points', 'value': '3 concise bullet points'}, {'label': 'One Short Paragraph', 'value': 'one short paragraph'}, {'label': 'Detailed Report (500 words)', 'value': 'detailed report (500 words)'}], value='executive summary (200 words)', clearable=False, style={'color': '#333'}), md=4),
            dbc.Col(dbc.Button("Summarize Document", id="summarize-button", color="primary", className="mt-3", disabled=not GEMINI_AVAILABLE), md=2)
        ]),
        html.Div(id='upload-filename-display', className="mb-3 text-white-50"),
        html.Div(id='summary-output-container', children=dbc.Alert("Upload a PDF and click 'Summarize Document' to see results.", color="info", className="mt-4")),
        html.Hr(),
        research_links_section if research_links_section else ""
    ])
    
    back_button_id = "back-to-subtopics-button" if subtopic_key != 'custom_query' else "back-to-topics-button"
    back_button_text = "Go Back to Subtopics" if subtopic_key != 'custom_query' else "Back to Home"

    return html.Div([
        dbc.Button(back_button_text, id=back_button_id, className="mb-3", color="light", outline=True),
        html.H3(f"Dashboard for: {data.get('title', main_topic_key.replace('_', ' ').title())}", className="text-white mb-4"),
        
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
                label="Document Analysis", 
                children=doc_analysis_tab_content
            ),
        ]),
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