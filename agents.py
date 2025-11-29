import os
from google import genai
from google.genai import types

# ==========================================
# SECURE AUTHENTICATION
# ==========================================
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

# Get the key
MY_API_KEY = get_api_key()

if not MY_API_KEY:
    print("🚨 Error: API Key not found.")
    print("Please ensure you have created '.streamlit/secrets.toml' with your key.")
    exit()

# Initialize Client
client = genai.Client(api_key=MY_API_KEY)

# ==========================================
# AGENT 1: THE EVOLUTIONARY BIOLOGIST
# ==========================================
def ask_biologist(user_problem):
    print(f"\n...Biologist is researching: '{user_problem}'...")

    # Define the tool (Google Search)
    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )

    # Define the System Instruction
    sys_instruction = """
    You are an expert Evolutionary Biologist.
    When asked about a problem, search for biological organisms that solve it.
    Focus on MECHANISM and FUNCTION.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_problem,
        config=types.GenerateContentConfig(
            tools=[google_search_tool], 
            system_instruction=sys_instruction,
            temperature=0.4
        )
    )

    return response.text

# ==========================================
# TEST
# ==========================================
if __name__ == "__main__":
    problem = "How can I filter water efficiently without clogging?"
    result = ask_biologist(problem)
    
    print("\n--- BIOLOGIST REPORT ---")
    print(result)