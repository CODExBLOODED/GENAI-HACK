import os
import pathlib
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud import vision
from google.cloud import genai
from typing import Sequence

# Grant permission for Cloud API
credential_path = r"C:\Users\{your_username}\AppData\Roaming\gcloud\application_default_credentials.json"
os.environ["YOUR_API_KEY"]=credential_path

SPEECH_FILE = "/Resources/speech.wav"

VISION_FILE =  "/Resources/vision.jpeg"

def image_to_uri():
    with open(VISION_FILE, "rb") as image_file:
        content = image_file.read()
    return content

def analyze_image_from_uri(
    feature_types: Sequence
) -> vision.AnnotateImageResponse:
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_to_uri())
    features = [vision.Feature(type_=feature_type) for feature_type in feature_types]
    request = vision.AnnotateImageRequest(image=image, features=features)
    response = client.annotate_image(request=request)
    return response

def object_detect():
    features = [vision.Feature.Type.OBJECT_LOCALIZATION]
    response = analyze_image_from_uri(features)
    lst = [obj.name.lower() for obj in response.localized_object_annotations]
    return ', '.join(set(lst))

def text_detect():
    features = [vision.Feature.Type.TEXT_DETECTION]
    response = analyze_image_from_uri(features)
    lst = [annotation.description.lower() for annotation in response.text_annotations]
    return ', '.join(lst)

def text_to_speech(text_input: str):
    client_tts = texttospeech.TextToSpeechClient()
    synthesis_in = texttospeech.SynthesisInput(text=text_input)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client_tts.synthesize_speech(
    input=synthesis_in, voice=voice, audio_config=audio_config
    )
    return response.audio_content

def prompt(user_prompt):
    model = genai.GenerativeModel('gemini-pro-vision')

    picture = [{
        'mime_type': 'image/png',
        'data': pathlib.Path(VISION_FILE).read_bytes()
    }]

    response = model.generate_content(
        model="gemini-pro-vision",
        content=[user_prompt, picture]
    )
    return text_to_speech(response.text)

def speech_to_prompt():
    """Streams transcription of the given audio file."""
    client = speech.SpeechClient()

    with open(SPEECH_FILE, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        if result is not None:
            print(f"Transcript: {result.alternatives[0].transcript}")

    return prompt(response)        
