from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import time
import requests

load_dotenv()  # take environment variables from .env.

API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = "client_secret.json"

def get_livestream_details(youtube, video_id):
    request = youtube.videos().list(
        part="liveStreamingDetails",
        id=video_id
    )
    response = request.execute()

    live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']
    
    return live_chat_id

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_console()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


# def send_chat(messages):

#     print('test')
#     url = "http://localhost:3000/api/return_chat"
#     res = requests.post(url, json=messages)

#     print(f"SENT MESSAGES with Response: {res}")


import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('airadio-393111-firebase-adminsdk-fsps5-db0ae1456e.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

ENV="lofigirl"

def send_chat(messages):
    doc_ref = db.collection(f'{ENV}_chatMessages').document()
    doc_ref.set({
        f'messages': messages,
    })


def get_chat_messages(service, live_chat_id):
    page_token = None
    while True:
        try:
            results = service.liveChatMessages().list(
                liveChatId=live_chat_id,
                part='id, snippet',
                pageToken=page_token,
            ).execute()

            messages = []

            for item in results['items']:
                author = item['snippet']['authorChannelId']
                message = item['snippet']['displayMessage']
                messages.append(message)
                print(f'{author}: {message}')


                if message[:5] == '!vote':
                    print('VOTE DETECTED')

            
            page_token = results.get('nextPageToken')

            send_chat(messages)

            time.sleep(5)  # As per YouTube API rate limits.
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
            break

if __name__ == "__main__":
    video_id = 'jfKfPfyJRdk'
    live_chat_id = get_livestream_details(youtube, video_id)
    print(f"Live chat ID: {live_chat_id}")

    service = get_authenticated_service()

    get_chat_messages(service, live_chat_id)
