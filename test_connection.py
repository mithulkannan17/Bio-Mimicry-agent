from google import genai
import os

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

def test_free_connection():
    print("...Connecting to Gemini via AI Studio (Free)...")
    
    # Initialize the client with your API Key
    client = genai.Client(api_key=MY_API_KEY)

    # Send a message
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents="Are you ready for my Bio-Mimicry Capstone?"
    )
    
    print("\n--- GEMINI SAYS ---")
    print(response.text)

if __name__ == "__main__":
    test_free_connection()