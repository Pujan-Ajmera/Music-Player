from fastapi import FastAPI
import requests
import json
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"


# Helper: convert ISO 8601 duration to mm:ss
def format_duration(iso):
    import isodate
    try:
        duration = isodate.parse_duration(iso)
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    except:
        return "0:00"


# Helper: views formatting
def format_views(n):
    n = int(n)
    if n >= 1_000_000:
        return f"{n//1_000_000}M views"
    elif n >= 1_000:
        return f"{n//1_000}K views"
    return f"{n} views"


@app.get("/search")
def search_youtube(q: str):
    # 1) Search API — get video IDs
    params = {
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": 15,
        "key": YOUTUBE_API_KEY
    }

    search_response = requests.get(SEARCH_URL, params=params).json()
    items = search_response.get("items", [])

    video_ids = [item["id"]["videoId"] for item in items]
    if not video_ids:
        return {"results": []}

    # 2) Details API — get duration, views, date
    params_details = {
        "part": "contentDetails,statistics,snippet",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    details_response = requests.get(DETAILS_URL, params=params_details).json()
    details_map = {item["id"]: item for item in details_response.get("items", [])}

    results = []
    for item in items:
        vid = item["id"]["videoId"]
        details = details_map.get(vid, {})

        duration_iso = details.get("contentDetails", {}).get("duration", "PT0S")
        duration = format_duration(duration_iso)

        views = details.get("statistics", {}).get("viewCount", "0")
        views = format_views(views)

        published_at = item["snippet"].get("publishedAt", "")

        results.append({
            "videoId": vid,
            "title": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            "channelTitle": item["snippet"]["channelTitle"],
            "duration": duration,
            "views": views,
            "publishedAt": published_at
        })

    return {"results": results}
