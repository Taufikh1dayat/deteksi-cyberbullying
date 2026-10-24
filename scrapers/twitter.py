from apify_client import ApifyClient
import pandas as pd
from .config import APIFY_TOKENS

def scrape_twitter(query: str, max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk data X (Twitter) via Apify SDK menggunakan Aktor API-Ninja (api-ninja/x-twitter-advanced-search).
    """
    full_query = query.strip()
    actor_limit = max(max_results, 20)
    
    run_input = {
        "query": full_query,
        "search_type": "Latest",
        "numberOfTweets": actor_limit
    }
    
    last_error = None
    
    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue
            
        try:
            client = ApifyClient(token)
            print(f"\n[PROSES X] Menghubungi Aktor 'api-ninja/x-twitter-advanced-search' (Token: {token[:12]}...) untuk query: '{full_query}'...")
            
            run = client.actor("api-ninja/x-twitter-advanced-search").call(run_input=run_input)
            records = []
            
            for item in client.dataset(run.default_dataset_id).iterate_items():
                text_content = (
                    item.get('text') or 
                    item.get('full_text') or 
                    item.get('fullText') or 
                    (item.get('tweet', {}).get('full_text') if isinstance(item.get('tweet'), dict) else None)
                )
                
                if not text_content:
                    continue
                
                username_val = None
                user_info = item.get('user_info') or item.get('user') or item.get('author')
                if isinstance(user_info, dict):
                    username_val = user_info.get('screen_name') or user_info.get('username') or user_info.get('name')
                if not username_val:
                    username_val = item.get('username') or item.get('screen_name') or item.get('author_name') or "X_User"
                
                stats_obj = item.get('stats') or item or {}
                
                records.append({
                    'platform': 'Twitter / X',
                    'id': str(item.get('tweet_id') or item.get('id') or item.get('id_str', '')),
                    'text': str(text_content).strip(),
                    'created_at': str(item.get('created_at') or item.get('createdAt') or item.get('date') or ''),
                    'like_count': stats_obj.get('favorites') or stats_obj.get('favorite_count') or stats_obj.get('likes') or 0,
                    'retweet_count': stats_obj.get('retweets') or stats_obj.get('retweet_count') or 0,
                    'reply_count': stats_obj.get('replies') or stats_obj.get('reply_count') or 0,
                    'username': username_val,
                    'label': None
                })
                
            df = pd.DataFrame(records)
            
            if not df.empty:
                df = df.drop_duplicates(subset=['text'])
                df = df[~df['text'].str.startswith('RT @', na=False)]
                
                # Urutkan tanggal dari yang paling baru
                df['created_at_dt'] = pd.to_datetime(df['created_at'], errors='coerce')
                df = df.sort_values(by='created_at_dt', ascending=False)
                df = df.drop(columns=['created_at_dt'], errors='ignore')
                
                print(f"[BERHASIL X] Memanen {len(df)} tweet real-time!")
                return df.head(max_results)
                
        except Exception as e:
            last_error = str(e)
            print(f"[WARN X] Token {token[:12]}... kendala: {last_error}")
            
    print(f"[ERROR X] Seluruh token Apify gagal: {last_error}")
    return pd.DataFrame()
