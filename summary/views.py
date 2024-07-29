from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from google.cloud import speech
from googleapiclient.discovery import build
import requests
import logging
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import yt_dlp as youtube_dl

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\aksha\Downloads\yt-api-430715-4df37fba2c72.json"  # Replace with actual path

@api_view(['POST'])
def process_youtube_url(request):
    youtube_url = request.data.get('url')
    logger.debug(f"Processing URL: {youtube_url}")
    transcript = get_youtube_transcript(youtube_url)
    if not transcript:
        transcript = convert_audio_to_text(youtube_url)
    summary = summarize_text(transcript)
    return Response({'summary': summary})

def convert_audio_to_text(url):
    client = speech.SpeechClient()

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
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)

    return " ".join(str(sentence) for sentence in summary)

def get_youtube_transcript(url):
    youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY') 
    video_id = extract_video_id(url)
    logger.debug(f"Extracted video ID: {video_id}")
    try:
        captions = youtube.captions().list(part='snippet', videoId=video_id).execute()
        logger.debug(f"Captions list response: {captions}")
        
        for item in captions['items']:
            if item['snippet']['language'] == 'en':
                caption_id = item['id']
                logger.debug(f"Found English caption with ID: {caption_id}")
                transcript = youtube.captions().download(id=caption_id).execute()
                return transcript.decode('utf-8')
    except Exception as e:
        logger.error(f"Error fetching captions: {e}")
    return None

def extract_video_id(url):
    import re
    pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)')
    match = pattern.match(url)
    return match.group(1) if match else None
