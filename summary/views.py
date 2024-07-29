from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from google.cloud import speech
from googleapiclient.discovery import build
import requests
from google.cloud import speech
from googleapiclient.discovery import build



@api_view(['POST'])
def process_youtube_url(request):
    youtube_url = request.data.get('url')
    transcript = get_youtube_transcript(youtube_url)
    if not transcript:
        transcript = convert_audio_to_text(youtube_url)
    summary = summarize_text(transcript)
    return Response({'summary': summary})


def convert_audio_to_text(url):
    client = speech.SpeechClient()

    # Download audio from YouTube
    audio_content = download_youtube_audio(url)
    
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US'
    )
    
    response = client.recognize(config=config, audio=audio)
    
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    return transcript

def download_youtube_audio(url):
    import youtube_dl

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': '/tmp/%(id)s.%(ext)s'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict.get("id", None)
        ydl.download([url])

    file_path = f'/tmp/{video_id}.wav'
    with open(file_path, 'rb') as f:
        audio_content = f.read()
    
    return audio_content


def summarize_text(text):
    from gensim.summarization import summarize
    try:
        return summarize(text)
    except ValueError:
        return text  # Return original text if summary fails


def get_youtube_transcript(url):
    youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY')
    video_id = extract_video_id(url)
    captions = youtube.captions().list(part='snippet', videoId=video_id).execute()
    
    for item in captions['items']:
        if item['snippet']['language'] == 'en':
            caption_id = item['id']
            transcript = youtube.captions().download(id=caption_id).execute()
            return transcript.decode('utf-8')
    return None

def extract_video_id(url):
    import re
    pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)')
    match = pattern.match(url)
    return match.group(1) if match else None

