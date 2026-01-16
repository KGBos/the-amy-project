import logging
import os

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available. Audio transcription will not function.")

logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    Handles audio transcription using the Whisper model.
    """
    def __init__(self, model_size: str = "base"):
        """
        Initializes the AudioTranscriber with a specified Whisper model size.

        Args:
            model_size: The size of the Whisper model to load (e.g., "tiny", "base", "small", "medium", "large").
                        "base" is a good balance for most uses.
        """
        self.model = None
        if WHISPER_AVAILABLE:
            try:
                logger.info(f"Loading Whisper model: {model_size}...")
                self.model = whisper.load_model(model_size)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model '{model_size}': {e}")
                self.model = None
        else:
            logger.warning("Whisper library not found. Audio transcription will be disabled.")

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribes an audio file to text.

        Args:
            audio_path: The path to the audio file.

        Returns:
            The transcribed text, or an empty string if transcription fails or Whisper is not available.
        """
        if not self.model:
            logger.warning("Whisper model not loaded. Cannot transcribe audio.")
            return ""

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return ""

        try:
            result = self.model.transcribe(audio_path)
            transcribed_text = result.get("text", "").strip()
            logger.info(f'Transcribed audio from {audio_path}: "{transcribed_text[:50]}..."')
            return transcribed_text
        except Exception as e:
            logger.error(f"Error during audio transcription from {audio_path}: {e}")
            return ""

# Example usage (for testing purposes, will be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    transcriber = AudioTranscriber("base")

    # This part would require an actual audio file to test fully
    # For now, it just demonstrates how it would be called.
    # audio_file_path = "path/to/your/audio.mp3"
    # if os.path.exists(audio_file_path):
    #     text = transcriber.transcribe_audio(audio_file_path)
    #     print(f"Transcription result: {text}")
    # else:
    #     print("Please provide a valid audio file path for testing.") 