import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret_976527903112-mh2asun5r8bmhb892bafmoe9ev1uaiv8.apps.googleusercontent.com.json"

def setup_google():
    global youtube
    # initialize credentials
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console() # how can we make this auto load
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

def youtube(search_term, count = 1):
    request = youtube.search().list(
        part="snippet",
        maxResults=count,
        q=search_term
    )
    response = request.execute()
    
    return response

def youtube_video_info(video_id):
    request = youtube.videos().list(
        part="snippet, contentDetails",
        id=video_id
    )
    response = request.execute()

    return response