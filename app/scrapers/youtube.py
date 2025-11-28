from datetime import datetime, timedelta, timezone
from typing import List, Optional
import os
import feedparser
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.proxies import WebshareProxyConfig


class Transcript(BaseModel):
    text: str


class ChannelVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None


class YouTubeScraper:
    def __init__(self):
        proxy_config = None
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")
        
        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(     #optional proxy, YouTube often rate-limits requests or blocks them from certain regions. 
                proxy_username=proxy_username,
                proxy_password=proxy_password
            )
        
        self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config) # Python library that allows you to fetch subtitles/transcripts from YouTube videos without using the YouTube API key.
    
    #===================================================================================
    #get the RSS feed URL from Channel_ID
    #===================================================================================
    def _get_rss_url(self, channel_id: str) -> str:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
    #===================================================================================
    #extract video_id from the URL
    #===================================================================================
    def _extract_video_id(self, video_url: str) -> str:
        if "youtube.com/watch?v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
        if "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[1].split("?")[0]
        if "youtu.be/" in video_url:
            return video_url.split("youtu.be/")[1].split("?")[0]
        return video_url

    #===================================================================================
    #gets transcript from video_id
    #===================================================================================
    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        try:
            transcript = self.transcript_api.fetch(video_id)  
            text = " ".join([snippet.text for snippet in transcript.snippets])  # you join all the "text" to form a transcript.
            return Transcript(text=text)   # pydantic model returned.
        except (TranscriptsDisabled, NoTranscriptFound):  # handles the exception to avoid code crash.
            return None
        except Exception:
            return None

    #===================================================================================
    # Parses the Channel, for the latest(24hrs) Videos, returns ChannelVideo object
    #===================================================================================
    def get_latest_videos(self, channel_id: str, hours: int = 24) -> list[ChannelVideo]:
        feed = feedparser.parse(self._get_rss_url(channel_id))  # uses FeedParser lib to parse through the RSS feed of the "CHANNEL_ID"
        if not feed.entries:
            return []
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)  # only the last 24hrs.
        videos = []
        
        for entry in feed.entries:
            if "/shorts/" in entry.link:   #ignore the youtube Shorts
                continue
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) # This line converts the RSS timestamp (published_parsed) into a timezone-aware UTC datetime object..
            if published_time >= cutoff_time:
                video_id = self._extract_video_id(entry.link)  #extract the video id from the link
                videos.append(ChannelVideo(
                    title=entry.title,
                    url=entry.link,
                    video_id=video_id,
                    published_at=published_time,
                    description=entry.get("summary", "")
                ))
        
        return videos

    #===================================================================================
    #Scraped Videos into Transcipts
    def scrape_channel(self, channel_id: str, hours: int = 150) -> list[ChannelVideo]:
        videos = self.get_latest_videos(channel_id, hours)
        result = []
        for video in videos:
            transcript = self.get_transcript(video.video_id)
            #IMPORTANT - Pydantic feature (.model_copy)
            result.append(video.model_copy(update={"transcript": transcript.text if transcript else None})) # in our earlier model we didnt have "transcript", we created a copy of our pydantic model, [video.transcript = None | result.transcript = "..."]
        return result   # a updated pydantic model (with "transcript" added)
    
    
    
if __name__ == "__main__":
    scraper = YouTubeScraper()
    transcript: Transcript = scraper.get_transcript("jqd6_bbjhS8")
    print(transcript.text)
    channel_videos: List[ChannelVideo] = scraper.scrape_channel("UCn8ujwUInbJkBhffxqAPBVQ", hours=200)
    
