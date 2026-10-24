import pandas as pd
from .twitter import scrape_twitter
from .tiktok import scrape_tiktok

def scrape_data(platform: str, target: str, max_results: int = 10) -> pd.DataFrame:
    """
    Dispatcher tunggal untuk mengeruk data dari berbagai platform media sosial
    dengan skema DataFrame yang seragam dan standar.
    """
    platform_key = platform.lower().strip()
    
    if "tiktok" in platform_key:
        return scrape_tiktok(video_url=target, max_results=max_results)
    elif "twitter" in platform_key or "x" in platform_key:
        return scrape_twitter(query=target, max_results=max_results)
    else:
        # Default fallback ke Twitter jika platform tidak dikenali
        return scrape_twitter(query=target, max_results=max_results)
