import pandas as pd
from .twitter import scrape_twitter
from .tiktok import scrape_tiktok
from .instagram import scrape_instagram

def scrape_data(platform: str, target: str, max_results: int = 10) -> pd.DataFrame:
    """
    Dispatcher tunggal untuk mengeruk data dari berbagai platform media sosial
    (Twitter/X, TikTok, Instagram) dengan skema DataFrame yang seragam dan standar.
    """
    platform_key = platform.lower().strip()

    if "tiktok" in platform_key:
        return scrape_tiktok(target=target, max_results=max_results)
    elif "instagram" in platform_key or "ig" in platform_key:
        return scrape_instagram(target=target, max_results=max_results)
    elif "twitter" in platform_key or "x" in platform_key:
        return scrape_twitter(query=target, max_results=max_results)
    else:
        return scrape_twitter(query=target, max_results=max_results)
