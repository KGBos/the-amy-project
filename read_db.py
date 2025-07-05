import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import json # Added this line

# Load environment variables from the .env file in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Get the absolute path to the project's root directory
project_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_root, "instance", "amy_memory.db")
db_url = f"sqlite:///{db_path}"

print(f"Connecting to database: {db_url}")

try:
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the 'events' table
    # Note: The 'content' column stores JSON strings, so we'll just print the raw string
    # The 'author' column stores who sent the message (user or model)
    result = session.execute(text("SELECT author, content FROM events ORDER BY timestamp ASC"))

    print("\n--- Conversation History from amy_memory.db ---")
    for row in result:
        author = row[0]
        content_json = row[1] # This is a JSON string
        
        # Attempt to parse content if it's a JSON string and extract text
        try:
            content_dict = json.loads(content_json)
            text_content = ""
            if 'parts' in content_dict:
                for part in content_dict['parts']:
                    if 'text' in part:
                        text_content += part['text']
            print(f"{author.upper()}: {text_content}")
        except json.JSONDecodeError:
            print(f"{author.upper()}: (Raw Content) {content_json}")

    print("-------------------------------------------")

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'session' in locals() and session:
        session.close()
    if 'engine' in locals() and engine:
        engine.dispose()