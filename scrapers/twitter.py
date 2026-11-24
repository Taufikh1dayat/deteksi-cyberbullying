from apify_client import ApifyClient
import pandas as pd
from .config import APIFY_TOKENS

def _parse_apidojo_item(item: dict) -> dict:
    """Ekstraksi item dari apidojo/tweet-scraper ke format standar."""
    text_content = item.get('text') or item.get('full_text') or item.get('fullText')
    if not text_content:
        return None
        
    author = item.get('author') or {}
    username_val = author.get('userName') or author.get('name') or item.get('username') or "X_User"
    
    return {
        'platform': 'Twitter / X',
        'id': str(item.get('id') or item.get('id_str', '')),
        'text': str(text_content).strip(),
        'created_at': str(item.get('createdAt') or item.get('created_at') or ''),
        'like_count': int(item.get('likeCount') or item.get('favorite_count') or 0),
        'retweet_count': int(item.get('retweetCount') or item.get('retweet_count') or 0),
        'reply_count': int(item.get('replyCount') or item.get('reply_count') or 0),
        'username': str(username_val),
        'label': None
    }

def _parse_apininja_item(item: dict) -> dict:
    """Ekstraksi item dari api-ninja/x-twitter-advanced-search ke format standar."""
    text_content = (
        item.get('text') or 
        item.get('full_text') or 
        item.get('fullText') or 
        (item.get('tweet', {}).get('full_text') if isinstance(item.get('tweet'), dict) else None)
    )
    if not text_content:
        return None
        
    username_val = None
    user_info = item.get('user_info') or item.get('user') or item.get('author')
    if isinstance(user_info, dict):
        username_val = user_info.get('screen_name') or user_info.get('username') or user_info.get('name')
    if not username_val:
        username_val = item.get('username') or item.get('screen_name') or "X_User"
        
    stats_obj = item.get('stats') or item or {}
    return {
        'platform': 'Twitter / X',
        'id': str(item.get('tweet_id') or item.get('id') or item.get('id_str', '')),
        'text': str(text_content).strip(),
        'created_at': str(item.get('created_at') or item.get('createdAt') or item.get('date') or ''),
        'like_count': int(stats_obj.get('favorites') or stats_obj.get('favorite_count') or stats_obj.get('likes') or 0),
        'retweet_count': int(stats_obj.get('retweets') or stats_obj.get('retweet_count') or 0),
        'reply_count': int(stats_obj.get('replyCount') or stats_obj.get('replies') or 0),
        'username': str(username_val),
        'label': None
    }

def scrape_twitter(query: str, max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk data Twitter / X via Apify SDK.
    Menggunakan apidojo/tweet-scraper sebagai aktor utama lintas seluruh token,
    dengan fallback otomatis ke api-ninja jika seluruh token apidojo habis.
    """
    full_query = query.strip()
    if not full_query:
        return pd.DataFrame()
        
    target_limit = min(max(max_results, 5), 10) # Free plan batas optimal 10 items
    
    # ── TAHAP 1: Coba apidojo/tweet-scraper ke setiap token yang tersedia ──
    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue
            
        try:
            client = ApifyClient(token)
            print(f"\n[PROSES X] Menghubungi 'apidojo/tweet-scraper' (Token: {token[:12]}...) query: '{full_query}'...")
            run_input = {
                "searchTerms": [full_query],
                "maxItems": target_limit
            }
            run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
            records = []
            for item in client.dataset(run.default_dataset_id).iterate_items():
                parsed = _parse_apidojo_item(item)
                if parsed:
                    records.append(parsed)
                    
            if records:
                df = pd.DataFrame(records).drop_duplicates(subset=['text'])
                df = df[~df['text'].str.startswith('RT @', na=False)]
                print(f"[BERHASIL X] Memanen {len(df)} tweet real-time dari apidojo/tweet-scraper!")
                return df.head(max_results)
            else:
                print(f"[INFO X] Token {token[:12]}... mengembalikan 0 tweet (kemungkinan kuota run aktor habis).")
        except Exception as e:
            print(f"[WARN X] Token {token[:12]}... kendala apidojo: {e}")

    # ── TAHAP 2: Fallback ke api-ninja/x-twitter-advanced-search jika tahap 1 gagal ──
    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue
        try:
            client = ApifyClient(token)
            print(f"[PROSES X] Menghubungi fallback 'api-ninja/x-twitter-advanced-search' (Token: {token[:12]}...)...")
            run_input = {
                "query": full_query,
                "search_type": "Latest",
                "numberOfTweets": max(target_limit, 20)
            }
            run = client.actor("api-ninja/x-twitter-advanced-search").call(run_input=run_input)
            records = []
            for item in client.dataset(run.default_dataset_id).iterate_items():
                parsed = _parse_apininja_item(item)
                if parsed:
                    records.append(parsed)
                    
            if records:
                df = pd.DataFrame(records).drop_duplicates(subset=['text'])
                df = df[~df['text'].str.startswith('RT @', na=False)]
                print(f"[BERHASIL X] Memanen {len(df)} tweet dari api-ninja!")
                return df.head(max_results)
        except Exception as e:
            print(f"[WARN X] api-ninja kendala: {e}")

    print("[ERROR X] Seluruh aktor dan token Apify tidak menghasilkan tweet.")
    return pd.DataFrame()
