from apify_client import ApifyClient
import pandas as pd

# ── 🔑 CONFIGURATION & MULTI-TOKEN FALLBACK ───────────────────────────
APIFY_TOKENS = [
    "apify_api_ACgxAK0CRe49YvyIIB0buj4ld1hf933bunBt",
    "apify_api_vQO9QbL4Pmlbr2j3Wmw8UsUFNZ8NSd1zI6HG",
    "apify_api_ohHltIT0elCbFbec3VunMFatgUQJ1r2uNqzW"
]
# ──────────────────────────────────────────────────────────────────────

def scrape_tweets_apify(query: str, max_results: int = 10, use_toxic_lexicon: bool = False) -> pd.DataFrame:
    """
    Mengeruk data X via Apify Aktor (api-ninja/x-twitter-advanced-search).
    Mendukung multi-token fallback, penanganan pencarian fleksibel, dan ekstraksi data bertingkat.
    """
    # 1. Penyusunan Query Pencarian
    if use_toxic_lexicon:
        lexicon_toksik = "(tolol OR bodoh OR goblok OR benci OR munafik OR jelek OR parah OR cacat)"
        full_query = f"{query} {lexicon_toksik} lang:id"
    else:
        full_query = f"{query} lang:id -is:retweet"
    
    actor_limit = max(max_results * 2, 15)
    
    # 2. Parameter Resmi Aktor Apify
    run_input = {
        "query": full_query,
        "search_type": "Top",
        "numberOfTweets": actor_limit,
        "maxTweets": actor_limit
    }
    
    last_error = None
    
    # 3. Iterasi Token Fallback
    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue
            
        try:
            client = ApifyClient(token)
            print(f"\n[PROSES] Mengirim perintah ke Cloud Apify (Token: {token[:15]}...) untuk query: '{full_query}'...")
            
            run = client.actor("api-ninja/x-twitter-advanced-search").call(run_input=run_input)
            print("[PROSES] Data berhasil dipanen! Sedang mengunduh dataset...")
            records = []
            
            for item in client.dataset(run.default_dataset_id).iterate_items():
                # Ekstraksi Teks Hierarkis
                text_content = (
                    item.get('text') or 
                    item.get('fullText') or 
                    item.get('full_text') or 
                    (item.get('tweet', {}).get('full_text') if isinstance(item.get('tweet'), dict) else None)
                )
                
                if not text_content:
                    continue
                
                # Ekstraksi Username Hierarkis
                username_val = None
                user_obj = item.get('author') or item.get('user')
                if isinstance(user_obj, dict):
                    username_val = user_obj.get('username') or user_obj.get('screen_name') or user_obj.get('screenName')
                if not username_val:
                    username_val = item.get('username') or item.get('screen_name') or item.get('author_name') or "X_User"
                
                stats_obj = item.get('stats') or item or {}
                
                records.append({
                    'id': str(item.get('id') or item.get('tweet_id') or item.get('id_str', '')),
                    'text': str(text_content).strip(),
                    'created_at': str(item.get('date') or item.get('createdAt') or item.get('created_at') or ''),
                    'like_count': stats_obj.get('likes') or stats_obj.get('favorite_count') or 0,
                    'retweet_count': stats_obj.get('retweets') or stats_obj.get('retweet_count') or 0,
                    'reply_count': stats_obj.get('replies') or stats_obj.get('reply_count') or 0,
                    'username': username_val,
                    'label': None
                })
                
            df = pd.DataFrame(records)
            
            if not df.empty:
                df = df.drop_duplicates(subset=['text'])
                df = df[~df['text'].str.startswith('RT @', na=False)]
                return df.head(max_results)
                
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ Token {token[:15]}... mengalami kendala: {last_error}")
            
    print(f"❌ Seluruh token Apify gagal dieksekusi. Detail error terakhir: {last_error}")
    return pd.DataFrame()

# ── 🏎️ PENGUJIAN LOKAL (MOCK RUNNER) ───────────────────────────────────
if __name__ == "__main__":
    print("\n==================================================")
    print("🚀 TESTING REAL-TIME SCRAPER (API-NINJA ACTOR)")
    print("==================================================")
    df_hasil = scrape_tweets_apify(query="Gibran", max_results=5)
    if not df_hasil.empty:
        print(df_hasil[['username', 'created_at', 'text']].to_string())
    else:
        print("Dataset kosong.")
