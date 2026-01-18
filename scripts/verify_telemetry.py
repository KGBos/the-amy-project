"""
Verification Script for Observability
Checks if the Freeplay plugin loads correctly when API key is present.
"""
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load Env
from dotenv import load_dotenv
load_dotenv()

from amy.core.telemetry import get_telemetry_plugins

def main():
    print("Checking Telemetry Configuration...")
    print(f"FREEPLAY_API_KEY present: {'Yes' if os.environ.get('FREEPLAY_API_KEY') else 'No'}")
    
    plugins = get_telemetry_plugins()
    print(f"Loaded Plugins: {len(plugins)}")
    
    found_freeplay = False
    for p in plugins:
        name = p.__class__.__name__
        print(f" - {name}")
        if "FreeplayObservabilityPlugin" in name:
            found_freeplay = True
            
    if found_freeplay:
        print("\nSUCCESS: Freeplay Plugin is active!")
    else:
        print("\nWARNING: Freeplay Plugin NOT loaded (Check API Key).")

if __name__ == "__main__":
    main()
