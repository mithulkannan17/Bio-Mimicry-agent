import streamlit as st
from google import genai
from google.genai import types
import urllib.parse # <--- New import for the URL hack
import os

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Bio-Mimicry Engine", page_icon="🌿", layout="wide")

# TODO: Paste your API Key here!
def get_api_key():
    """
    Securely retrieves the API key.
    Priority 1: Environment Variable (Deployment)
    Priority 2: Local Secrets File (Development)
    """
    # 1. Check standard environment variable
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
        
    # 2. If not found, try to read from the local .streamlit/secrets.toml file
    # (This simple parser works without installing extra libraries)
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            for line in f:
                if "GEMINI_API_KEY" in line:
                    # Extract the key between the quotes
                    return line.split('"')[1]
    except FileNotFoundError:
        pass
        
    return None

MY_API_KEY = get_api_key()

# Initialize Client
client = genai.Client(api_key=MY_API_KEY)

# ==========================================
# 2. AGENT FUNCTIONS (Backend)
# ==========================================
def run_biologist(problem):
    """Agent 1: Researches nature"""
    search_tool = types.Tool(google_search=types.GoogleSearch())
    
    sys_instruction = """
    You are an expert Evolutionary Biologist.
    User Input: A human engineering problem.
    Goal: Find a specific organism in nature that has solved this problem.
    Rules: Use Google Search to find REAL biological examples. Focus on MECHANISM.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=problem,
        config=types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction=sys_instruction,
            temperature=0.0
        )
    )
    return response.text

def run_engineer(bio_data, problem):
    """Agent 2: Designs the product"""
    code_tool = types.Tool(code_execution={}) 
    
    sys_instruction = """
    You are a Senior Bionics Engineer.
    Input: Biological data.
    Goal: Invent a human technology product based on that biology.
    Rules: Translate biology to mechanics. Use Code Execution to calculate a spec.
    """
    
    prompt = f"Problem: {problem}\nBiology Found: {bio_data}\nDesign a product and calculate a spec."
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[code_tool],
            system_instruction=sys_instruction
        )
    )
    return response.text

def run_illustrator_prompt(proposal):
    """Agent 3: Writes the text prompt"""
    sys_instruction = """
    You are an AI Art Director.
    Goal: Write a short, vivid prompt for an image generator.
    Rules: Start with 'Hyper-realistic product render of...'. 
    Keep it under 20 words for best results.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Create image prompt for: {proposal}",
        config=types.GenerateContentConfig(system_instruction=sys_instruction)
    )
    return response.text

# ==========================================
# 3. THE HACK (External Image API)
# ==========================================
def get_image_url(prompt_text):
    """
    Constructs a URL for the Pollinations.ai API with quality-improving parameters.
    """
    # 1. Clean the main prompt to make it URL-safe
    clean_prompt = urllib.parse.quote(prompt_text)
    
    # 2. Define a negative prompt to avoid bad quality
    # We tell it to avoid blurriness, low resolution, and pixelation.
    negative_prompt = urllib.parse.quote("blurry, low quality, pixelated, distorted, grainy")
    
    # 3. Construct the final magic URL
    # We use a landscape aspect ratio (768x512) and add the negative prompt parameter (&n=...)
    return f"https://image.pollinations.ai/prompt/{clean_prompt}?width=768&height=512&nologo=true&n={negative_prompt}"
    

# ==========================================
# 4. THE WEB UI (Frontend)
# ==========================================
st.title("🌿 Bio-Mimicry Innovation Engine")
st.markdown("### *3.8 billion years of R&D, available on demand.*")

col1, col2 = st.columns([1, 2])

with col1:
    # st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/DNA_structure_and_bases_PL.png", caption="Nature's Database")
    st.info("System Status: **ONLINE**")

with col2:
    user_problem = st.text_input(
        "Enter an engineering challenge:",
    )
    
    start_btn = st.button("🧬 Evolve Solution", type="primary")

if start_btn:
    
    # Create a container for the results
    result_container = st.container()
    
    with st.status("Running Evolutionary Pipeline...", expanded=True) as status:
        
        # --- PHASE 1: BIOLOGY ---
        status.write("🔍 **Biologist Agent** is querying the natural world...")
        bio_result = run_biologist(user_problem)
        st.success("Biological Mechanism Found")
        
        # --- PHASE 2: ENGINEERING ---
        status.write("⚙️ **Engineer Agent** is designing schematics...")
        eng_result = run_engineer(bio_result, user_problem)
        st.success("Prototype Computed")
        
        # --- PHASE 3: VISUALIZATION ---
        status.write("🎨 **Illustrator Agent** is rendering concept art...")
        art_prompt = run_illustrator_prompt(eng_result)
        
        # USE THE HACK
        image_url = get_image_url(art_prompt)
        
        status.update(label="Innovation Complete!", state="complete", expanded=False)

    # Display Results Beautifully
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📸 Visual Prototype", "🛠️ Engineering Specs", "🧬 Biological Source"])
    
    with tab1:
        st.subheader("Generative Concept Render")
        # We use the URL directly - it generates on the fly!
        st.image(image_url, caption=f"Prompt: {art_prompt}", use_container_width=True)
        
    with tab2:
        st.subheader("Technical Proposal")
        st.markdown(eng_result)
        
    with tab3:
        st.subheader("Research Data")
        st.markdown(bio_result)