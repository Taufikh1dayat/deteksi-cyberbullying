from apify_client import ApifyClient
import pandas as pd
from datetime import datetime
from .config import APIFY_TOKENS

def scrape_tiktok(video_url: str, max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk komentar video TikTok via Apify SDK menggunakan Aktor gratis:
    'clockworks/tiktok-comments-scraper'.
    """
    clean_url = video_url.strip()
    
    # Parameter hemat kuota gratisan:
    run_input = {
        "postURLs": [clean_url],
        "commentsPerPost": max_results,
        "maxRepliesPerComment": 0  # Mengabaikan balasan anak agar hemat waktu & komputasi
    }
    
    last_error = None
    
    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue
            
        try:
            client = ApifyClient(token)
            print(f"\n[PROSES TIKTOK] Menghubungi Aktor 'clockworks/tiktok-comments-scraper' (Token: {token[:12]}...)...")
            
            run = client.actor("clockworks/tiktok-comments-scraper").call(run_input=run_input)
            records = []
            
            for item in client.dataset(run.default_dataset_id).iterate_items():
                text_content = (
                    item.get('text') or 
                    item.get('commentText') or 
                    item.get('comment')
                )
                
                if not text_content:
                    continue
                
                # Ekstraksi username pemberi komentar
                username_val = (
                    item.get('uniqueId') or 
                    item.get('authorPinTitle') or 
                    item.get('user', {}).get('uniqueId') if isinstance(item.get('user'), dict) else None
                ) or "TikTok_User"
                
                # Konversi timestamp UNIX jika ada
                raw_time = item.get('createTime') or item.get('createdAt')
                if isinstance(raw_time, (int, float)):
                    try:
                        created_str = datetime.fromtimestamp(raw_time).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        created_str = str(raw_time)
                else:
                    created_str = str(raw_time or '')
                
                like_count = item.get('diggCount') or item.get('likes') or item.get('likeCount') or 0
                
                records.append({
                    'platform': 'TikTok',
                    'id': str(item.get('cid') or item.get('id') or item.get('commentId', '')),
                    'text': str(text_content).strip(),
                    'created_at': created_str,
                    'like_count': int(like_count),
                    'retweet_count': 0,
                    'reply_count': item.get('replyCommentTotal') or 0,
                    'username': username_val,
                    'label': None
                })
                
            df = pd.DataFrame(records)
            
            if not df.empty:
                df = df.drop_duplicates(subset=['text'])
                print(f"[BERHASIL TIKTOK] Memanen {len(df)} komentar video TikTok!")
                return df.head(max_results)
                
        except Exception as e:
            last_error = str(e)
            print(f"[WARN TIKTOK] Token {token[:12]}... kendala: {last_error}")
            
    print(f"[ERROR TIKTOK] Seluruh token Apify gagal: {last_error}")
    return pd.DataFrame()
