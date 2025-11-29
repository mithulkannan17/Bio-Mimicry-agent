from google import genai
from google.genai import types
import os

# ==========================================
# CONFIGURATION
# ==========================================
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

client = genai.Client(api_key=MY_API_KEY)

# ==========================================
# AGENT 1: THE BIOLOGIST (Researcher)
# ==========================================
def run_biologist_agent(user_problem):
    print(f"\n[1/3] Biologist Agent is researching: '{user_problem}'...")
    print("      (Consulting Google Search for 3.8 billion years of data...)")

    search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    sys_instruction = """
    You are an expert Evolutionary Biologist.
    User Input: A human engineering problem.
    Your Goal: Find a specific organism in nature that has solved this problem.
    RULES:
    1. Use Google Search to find REAL biological examples.
    2. Focus on the MECHANISM (how it works).
    3. Output Format: Organism Name, Function, and Mechanism.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_problem,
        config=types.GenerateContentConfig(
            tools=[search_tool], 
            system_instruction=sys_instruction,
            temperature=0.0
        )
    )
    return response.text

# ==========================================
# AGENT 2: THE ENGINEER (Builder)
# ==========================================
def run_engineer_agent(biological_data, original_problem):
    print(f"\n[2/3] Engineer Agent is designing a solution...")
    
    code_tool = types.Tool(
        code_execution={} 
    )

    sys_instruction = """
    You are a Senior Bionics Engineer.
    Input: Biological data about an organism.
    Your Goal: Invent a human technology product based on that biology.
    RULES:
    1. Translate 'cells/tissues' into 'materials/alloys/polymers'.
    2. Give the product a cool name.
    3. You MUST use the Code Execution tool to calculate a rough spec (e.g. weight, tensile strength) to prove feasibility.
    """

    prompt = f"""
    The User wanted to solve: "{original_problem}"
    The Biologist found: {biological_data}
    
    Design a product and calculate one specification using Python.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[code_tool],
            system_instruction=sys_instruction
        )
    )
    return response.text

# ==========================================
# AGENT 3: THE ILLUSTRATOR (Visualizer)
# ==========================================
def run_illustrator_agent(engineering_proposal):
    print(f"\n[3/3] Illustrator Agent is imagining the product...")
    
    sys_instruction = """
    You are a professional AI Art Director.
    Input: A technical product description.
    Your Goal: Write a highly detailed text-to-image prompt for a generator like Midjourney or Imagen.
    
    RULES:
    1. Focus on lighting, texture, and camera angle.
    2. Do NOT write chatty text. Output ONLY the prompt string.
    3. Start with: "Hyper-realistic product render of..."
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Create an image prompt for this product: {engineering_proposal}",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruction
        )
    )
    return response.text

# ==========================================
# THE ORCHESTRATOR
# ==========================================
def main():
    print("--- BIO-MIMICRY INNOVATION ENGINE INITIALIZED ---")
    
    user_problem = input("\nWhat engineering problem do you want to solve? ")
    if not user_problem: user_problem = "A helmet that prevents concussions"

    # Step 1: Biology
    bio_result = run_biologist_agent(user_problem)
    print(f"\n--- BIOLOGIST REPORT ---\n{bio_result}")
    
    # Step 2: Engineering
    eng_result = run_engineer_agent(bio_result, user_problem)
    print(f"\n--- ENGINEERING PROPOSAL ---\n{eng_result}")
    
    # Step 3: Illustration
    art_prompt = run_illustrator_agent(eng_result)
    print(f"\n--- IMAGE GENERATION PROMPT ---\n{art_prompt}")
    
    print("\n[System] Session Complete.")

if __name__ == "__main__":
    main()