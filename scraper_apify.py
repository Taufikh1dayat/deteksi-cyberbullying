"""
Jembatan kompatibilitas (Backward-Compatibility Bridge).
Seluruh modul scraper sekarang telah dirapikan ke dalam paket folder 'scrapers/'.
"""
from scrapers.config import APIFY_TOKENS
from scrapers.twitter import scrape_twitter as scrape_tweets_apify
from scrapers.tiktok import scrape_tiktok
from scrapers.manager import scrape_data

__all__ = ["APIFY_TOKENS", "scrape_tweets_apify", "scrape_tiktok", "scrape_data"]

if __name__ == "__main__":
    print("\n==================================================")
    print("[TESTING] SCRAPER PACKAGE MODULE CHECK")
    print("==================================================")
    print("Modul scrapers berhasil dimuat.")
