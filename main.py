from fastapi import FastAPI
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3/search"

@app.get("/search")
def search_youtube(q: str):
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": 15,
        "key": YOUTUBE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()

# Assuming 'data' is a dictionary or JSON-like structure
    print(json.dumps(data, indent=2))
    results = []
    for item in data.get("items", []):
        results.append({
            "videoId": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
        })

    return {"results": results}
