from google.adk.tools import FunctionTool

@FunctionTool
def send_sms(phone_number: str, message: str) -> str:
    """
    Sends an SMS message to a given phone number.

    Args:
        phone_number: The recipient's phone number in E.164 format.
        message: The content of the text message.

    Returns:
        A string confirming the message was sent, e.g., 'SMS sent successfully.'
    """
    # TODO: Implement this using an SMS service like Twilio.
    print(f"--- TOOL: Sending SMS to {phone_number}: '{message}' ---")
    raise NotImplementedError("Connect this tool to an SMS API like Twilio.")

@FunctionTool
def make_phone_call(phone_number: str, message_to_speak: str) -> str:
    """
    Makes a phone call and speaks a message using text-to-speech.

    Args:
        phone_number: The phone number to call in E.164 format.
        message_to_speak: The message to be converted to speech and spoken on the call.

    Returns:
        A string confirming the call was initiated, e.g., 'Call initiated successfully.'
    """
    # TODO: Implement this using a voice service like Twilio.
    print(f"--- TOOL: Calling {phone_number} to say: '{message_to_speak}' ---")
    raise NotImplementedError("Connect this tool to a Voice API like Twilio.")

@FunctionTool
def send_media(recipient: str, media_url: str, caption: str) -> str:
    """
    Sends media (image, video, etc.) to a recipient via a messaging platform.

    Args:
        recipient: The identifier for the recipient (e.g., phone number or user ID).
        media_url: The public URL of the media to send.
        caption: A text caption to send with the media.

    Returns:
        A string confirming the media was sent.
    """
    # TODO: Implement this using a service like Telegram Bot API or Twilio MMS.
    print(f"--- TOOL: Sending media from {media_url} to {recipient} with caption: '{caption}' ---")
    raise NotImplementedError("Connect this tool to a messaging API.")
