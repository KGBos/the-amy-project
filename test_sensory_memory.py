import os
import sys
import logging
import soundfile as sf
import numpy as np
import asyncio
import shutil # Import shutil for rmtree

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.amy_agent.memory_service import AmyMemoryService

# Configure logging to see info messages from our components
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

def clean_ltm_data(vector_db_path: str = "instance/vector_db") -> None:
    """
    Deletes the LTM JSON data to ensure a clean state for testing.
    """
    # Construct the absolute path from the project root
    project_root = os.path.abspath(os.path.dirname(__file__))
    ltm_dir_to_clean = os.path.join(project_root, vector_db_path)

    logger.info(f"DEBUG: Expected LTM data directory for cleanup: {ltm_dir_to_clean}") # Added debug print

    if os.path.exists(ltm_dir_to_clean) and os.path.isdir(ltm_dir_to_clean):
        shutil.rmtree(ltm_dir_to_clean)
        logger.info(f"Cleaned LTM data by removing directory: {ltm_dir_to_clean}")
    else:
        logger.info(f"LTM data directory not found, no cleanup needed: {ltm_dir_to_clean}")

def create_dummy_audio_file(file_path: str, duration_seconds: int = 1, samplerate: int = 16000) -> None:
    """
    Creates a dummy audio file for testing purposes.
    """
    frequency = 440  # A4 note
    t = np.linspace(0, duration_seconds, int(samplerate * duration_seconds), False)
    amplitude = np.sin(2 * np.pi * frequency * t)
    sf.write(file_path, amplitude, samplerate)
    logger.info(f"Created dummy audio file at: {file_path}")

def test_audio_transcription_integration(audio_file_path: str):
    """
    Tests the integration of audio transcription within AmyMemoryService.
    """
    print("\n🧪 Testing Audio Transcription Integration (Basic)... ")
    
    if not os.path.exists(audio_file_path):
        logger.warning(f"Audio file '{audio_file_path}' not found. Creating a dummy one for the test.")
        create_dummy_audio_file(audio_file_path)
        
    try:
        # Initialize AmyMemoryService
        memory_service = AmyMemoryService()
        
        user_id = "test_user"
        session_id = "test_session_audio"
        role = "user"
        content = "This is a fallback text if audio transcription fails."
        
        logger.info(f"Calling add_message with audio_path: {audio_file_path}")
        memory_service.add_message(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            audio_path=audio_file_path
        )
        
        print("\n✅ Audio transcription integration test triggered. Check logs above for transcription success/failure.")
        
    except Exception as e:
        logger.error(f"Error during audio transcription integration test: {e}")
        print(f"❌ Audio transcription integration test failed due to an error.")

async def test_end_to_end_sensory_memory(audio_file_path: str):
    """
    Tests the end-to-end flow of sensory memory (audio transcription) through STM and LTM.
    """
    print("\n🧪 Testing End-to-End Sensory Memory Flow (Transcription -> STM -> LTM)...")

    if not os.path.exists(audio_file_path):
        logger.warning(f"Audio file '{audio_file_path}' not found. Creating a dummy one for the test.")
        create_dummy_audio_file(audio_file_path)

    try:
        memory_service = AmyMemoryService()
        user_id = "e2e_test_user"
        session_id = "e2e_test_session_audio"
        initial_content = "This is a dummy message if transcription fails."

        logger.info(f"Adding audio message via add_message with path: {audio_file_path}")
        memory_service.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=initial_content,
            audio_path=audio_file_path
        )

        # --- Verify STM storage ---
        logger.info("Verifying STM content...")
        stm_context = memory_service.get_context(user_id=user_id, session_id=session_id)
        # The transcribed content will be the actual content in STM, so we need to know what to expect.
        # Based on previous runs, it's "Brave warrior, you've come far, but the dark fore..."
        expected_transcription_start = "Brave warrior, you've come far, but the dark fore"
        
        assert expected_transcription_start in stm_context, \
            f"❌ Transcribed audio not found in STM context. Expected to find '{expected_transcription_start}' in '{stm_context}'"
        logger.info("✅ Transcribed audio successfully found in STM.")

        # --- Verify LTM storage (via search) ---
        logger.info("Verifying LTM content via search...")
        # Use a query related to the transcribed content to search LTM
        ltm_search_query = "brave warrior"
        ltm_results = await memory_service.search_memory(app_name="test_app", user_id=user_id, query=ltm_search_query)
        
        found_in_ltm = False
        if ltm_results and "memories" in ltm_results:
            for mem in ltm_results["memories"]:
                logger.debug(f"DEBUG TEST: Type of mem: {type(mem)}, Content of mem: {mem}")
                if expected_transcription_start in mem.get("text", ""):
                    found_in_ltm = True

        assert found_in_ltm, \
            f"❌ Transcribed audio not found in LTM search results for query '{ltm_search_query}'"
        logger.info("✅ Transcribed audio successfully found in LTM via search.")

        print("\n✅ End-to-End Sensory Memory Flow test passed successfully!")

    except AssertionError as ae:
        logger.error(f"Assertion Error during end-to-end test: {ae}")
        print(f"❌ End-to-End Sensory Memory Flow test failed: {ae}")
    except Exception as e:
        logger.error(f"Error during end-to-end sensory memory test: {e}")
        print(f"❌ End-to-End Sensory Memory Flow test failed due to an unexpected error.")

if __name__ == "__main__":
    user_provided_audio_file = "ElevenLabs_2025-07-06T01_34_30_Adam_pre_sp100_s50_sb75_se0_m2.mp3" # Using the exact filename you provided
    
    # Clean up LTM data before running tests
    clean_ltm_data()
    
    # Run the basic transcription integration test
    test_audio_transcription_integration(user_provided_audio_file)

    # Run the end-to-end sensory memory test
    asyncio.run(test_end_to_end_sensory_memory(user_provided_audio_file)) 