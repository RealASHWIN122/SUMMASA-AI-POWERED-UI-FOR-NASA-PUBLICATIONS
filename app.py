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

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', "AIzaSyA2f64amvhSBD26sDYgzJv6bgTQqlB_hNA") 
MODEL_NAME = 'gemini-1.5-flash'
try:
    if GEMINI_API_KEY != "AIzaSyA2f64amvhSBD26sDYgzJv6bgTQqlB_hNA":
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        client = None; GEMINI_AVAILABLE = False
        print("WARNING: Gemini API Key not set.")
except Exception as e:
    client = None; GEMINI_AVAILABLE = False
    print(f"Error initializing Gemini Client: {e}")

def get_pdf_summary_dash(file_path, filename, summary_length, current_client):
    """
    Handles file upload FROM A SERVER PATH to Gemini, summarization, and cleanup.
    """
    if not current_client or not file_path:
        return "Gemini API is not configured or file path is missing.", "danger"
    
    uploaded_file = None
    try:
        # 1. Upload the file to the Gemini File API directly from the path
        uploaded_file = current_client.files.upload(path=file_path, display_name=filename)
        
        system_instruction = "You are an expert document summarization specialist..."
        prompt = f"Summarize the uploaded PDF document named '{filename}' in a **{summary_length}** format..."
        
        # 2. Generate content
        model = current_client.models.get_model(f'models/{MODEL_NAME}')
        response = model.generate_content([uploaded_file, prompt], system_instruction=system_instruction)
        summary, status = response.text, "success"
        
    except Exception as e:
        summary, status = f"An error occurred during summarization: {e}", "danger"
        
    finally:
        # 3. Clean up the server's temporary file and the Gemini file
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            
        if uploaded_file:
            try:
                current_client.files.delete(name=uploaded_file.name)
            except Exception as e:
                print(f"Gemini file cleanup failed for {uploaded_file.name}: {e}")
            
    return summary, status
# =========================================================================

# --- MOCK DATA ---
MOCK_DATA = {
    # --- Physics ---
    'physics': {
        'display_name': 'Physics', 'layout_group': 'sidebar', 'subtopics': {
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
    """Creates the detailed dashboard view, with tabs and a modal for abstracts."""
    if main_topic_key == 'doc_analysis' and subtopic_key == 'summarizer_mode':
        return generate_summarizer_page_layout()

    data = {}
    is_custom_query = subtopic_key == 'custom_query'

    if is_custom_query:
        data = {
            'title': f"Search Results for: {main_topic_key.title()}",
            'summary': f"Showing live results for your query: '{main_topic_key}'. Click a title in the 'Scraped Documents' card for options."
        }
    elif main_topic_key in MOCK_DATA and subtopic_key in MOCK_DATA[main_topic_key].get('subtopics', {}):
        data = MOCK_DATA[main_topic_key]['subtopics'][subtopic_key]
    else:
        return dbc.Alert("Error: Data for this topic could not be found.", color="danger")

    # --- Create all dashboard cards ---
    summary_card = create_card("AI-Powered Summary", dcc.Markdown(data.get('summary', '')), "bi-robot")
    knowledge_graph = create_card("Knowledge Graph", cyto.Cytoscape(id='knowledge-graph', layout={'name': 'cose'}, style={'width': '100%', 'height': '400px'}, elements=data.get('graph_elements', [])), "bi-diagram-3-fill")
    
    experiments_df = data.get('experiments')
    bar_chart = create_card("Data Distribution", dcc.Graph(figure=px.bar(experiments_df, x=experiments_df.columns[0], y=experiments_df.columns[1], template=CHART_TEMPLATE)), "bi-bar-chart-line-fill") if experiments_df is not None and not experiments_df.empty else None

    # --- Scraped Documents Card ---
    scraped_documents_card = None
    if scraped_results and scraped_results.get('documents'):
        doc_items = [dbc.ListGroupItem([dbc.Row([dbc.Col(doc["title"], width=8), dbc.Col(dbc.ButtonGroup([dbc.Button("Abstract", id={'type': 'abstract-button', 'index': i}, size="sm", color="info", outline=True), dbc.Button("Download", id={'type': 'download-button', 'index': i}, size="sm", color="success", outline=True)]), width=4, className="d-flex justify-content-end")], align="center")]) for i, doc in enumerate(scraped_results['documents'])]
        scraped_content = [
            html.P("View an abstract or download the PDF.", className="small"),
            dbc.ListGroup(doc_items, flush=True, style={'maxHeight': '400px', 'overflowY': 'auto'}),
            html.Div(id='download-status-container', className="mt-2")
        ]
        scraped_documents_card = create_card("Scraped Documents", scraped_content, "bi-card-list")

    # --- Create the content for the Document Analysis tab ---
    research_links_section = None
    related_docs_list = data.get('related_documents', [])
    if related_docs_list:
        research_links_section = html.Div([
            html.H5("Related Research Papers", className="mt-4"),
            dbc.ListGroup([dbc.ListGroupItem(html.A(doc['title'], href=doc['url'], target="_blank")) for doc in related_docs_list], flush=True)
        ])

    doc_analysis_tab_content = html.Div([
        html.P("Upload a PDF document to get an on-demand summary related to space research.", className="lead"),
        dbc.Row([
            dbc.Col(dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select a PDF File')]), style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px', 'color': '#00bfff'}, multiple=False), md=6),
            dbc.Col(dcc.Dropdown(id='summary-length-dropdown', options=[{'label': 'Executive Summary (200 words)', 'value': 'executive summary (200 words)'}, {'label': '3 Concise Bullet Points', 'value': '3 concise bullet points'}], value='executive summary (200 words)', clearable=False, style={'color': '#333'}), md=4),
            dbc.Col(dbc.Button("Summarize Document", id="summarize-button", color="primary", className="mt-3", disabled=not GEMINI_AVAILABLE), md=2)
        ]),
        html.Div(id='upload-filename-display', className="mb-3 text-white-50"),
        html.Div(id='summary-output-container', children=dbc.Alert("Upload a PDF and click 'Summarize Document' to see results.", color="info", className="mt-4")),
        html.Hr(),
        research_links_section if research_links_section else ""
    ])

    back_button_id = "back-to-subtopics-button" if not is_custom_query else "back-to-topics-button"
    back_button_text = "Go Back to Subtopics" if not is_custom_query else "Back to Home"

    abstract_modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Document Abstract")),
        dbc.ModalBody(dcc.Loading(id="abstract-content")),
    ], id="abstract-modal", size="lg", is_open=False)

    # --- ### FINAL LAYOUT WITH TABS RESTORED ### ---
    return html.Div([
        abstract_modal,
        dbc.Button(back_button_text, id=back_button_id, className="mb-3", color="light", outline=True),
        html.H3(f"{data.get('title', 'Dashboard')}", className="text-white mb-4"),
        
        dbc.Tabs([
            # -- Tab 1: Topic Dashboard --
            dbc.Tab(
                label="Topic Dashboard",
                children=html.Div([
                    dbc.Row([
                        dbc.Col(summary_card, width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(knowledge_graph, md=7),
                        # Place the bar chart and scraped results on the right
                        dbc.Col([bar_chart, scraped_documents_card], md=5)
                    ])
                ])
            ),
            # -- Tab 2: Document Analysis --
            dbc.Tab(
                label="Document Analysis (Gemini)",
                children=doc_analysis_tab_content
            )
        ])
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
    [Output('app-state', 'data', allow_duplicate=True), 
     Output('upload-filename-display', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'), State('app-state', 'data'),
    prevent_initial_call=True
)
def save_uploaded_file(list_of_contents, list_of_names, current_state):
    """Saves the uploaded file to a temp location on the SERVER and stores the path."""
    if list_of_contents is None:
        raise dash.exceptions.PreventUpdate

    # Decode the base64 string
    content_type, content_string = list_of_contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Create a temporary file and save the content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(decoded)
        temp_file_path = tmp_file.name # Get the path to the temporary file

    # Store the FILENAME and the temporary file PATH in the app state
    current_state['uploaded_filename'] = list_of_names
    current_state['temp_file_path'] = temp_file_path # Instead of 'uploaded_data'
    
    return current_state, html.P(f"File ready: **{list_of_names}**", className="text-success")

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
    Output('abstract-modal', 'is_open'),
    Output('abstract-content', 'children'),
    Input({'type': 'abstract-button', 'index': ALL}, 'n_clicks'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def show_abstract(n_clicks, app_state):
    if not ctx.triggered_id or not any(n_clicks):
        raise dash.exceptions.PreventUpdate

    # Get the index of the button that was clicked
    button_index = ctx.triggered_id['index']
    
    # Find the corresponding document URL
    scraped_data = app_state.get('scraped_results', {}).get('full_data', [])
    if button_index >= len(scraped_data):
        return True, "Error: Document index out of range."

    selected_doc_url = scraped_data[button_index]["url"]
    
    # Use your new scraper function to get the abstract
    print(f"📄 Scraping abstract for: {selected_doc_url}")
    abstract_text = get_abstract_for_doc(driver=DRIVER, doc_url=selected_doc_url)
    
    # Open the modal and display the text
    return True, dcc.Markdown(abstract_text)
@app.callback(
    Output('download-status-container', 'children'),
    Input({'type': 'download-button', 'index': ALL}, 'n_clicks'),
    State('app-state', 'data'),
    prevent_initial_call=True
)
def handle_pdf_download(n_clicks, app_state):
    if not ctx.triggered_id or not any(n_clicks):
        raise dash.exceptions.PreventUpdate

    button_index = ctx.triggered_id['index']
    scraped_data = app_state.get('scraped_results', {}).get('full_data', [])
    
    if button_index >= len(scraped_data):
        return dbc.Alert("Error: Document index out of range.", color="danger")
        
    selected_doc = scraped_data[button_index]
    
    pdf_path = download_nslsl_pdf(driver=DRIVER, doc_url=selected_doc["url"])
    
    if pdf_path:
        return dbc.Alert(f"Success! Saved to: {os.path.abspath(pdf_path)}", color="success", duration=10000)
    else:
        return dbc.Alert(f"Download failed for '{selected_doc['title']}'.", color="danger", duration=10000)
if __name__ == '__main__':
    app.run(debug=True)