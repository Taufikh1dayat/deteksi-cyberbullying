from apify_client import ApifyClient
import pandas as pd
from datetime import datetime
from .config import APIFY_TOKENS

def _parse_instagram_item(item: dict) -> dict:
    """Ekstraksi satu data komentar Instagram ke skema terpadu."""
    text_content = (
        item.get('text') or
        item.get('commentText') or
        item.get('caption')
    )
    if not text_content:
        return None

    # Ekstraksi username pemberi komentar
    owner_info = item.get('owner') or item.get('user') or {}
    username_val = (
        item.get('ownerUsername') or
        (owner_info.get('username') if isinstance(owner_info, dict) else None) or
        item.get('username') or
        "IG_User"
    )

    # Format timestamp
    raw_time = item.get('timestamp') or item.get('createdAt') or item.get('date') or ''
    created_str = str(raw_time)
    if 'T' in created_str:
        created_str = created_str.replace('T', ' ').split('.')[0].replace('Z', '')
    elif isinstance(raw_time, (int, float)):
        try:
            created_str = datetime.fromtimestamp(raw_time).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            created_str = str(raw_time)

    like_count = item.get('likesCount') or item.get('likes') or item.get('like_count') or 0

    return {
        'platform': 'Instagram',
        'id': str(item.get('id') or item.get('pk') or ''),
        'text': str(text_content).strip(),
        'created_at': created_str,
        'like_count': int(like_count),
        'retweet_count': 0,
        'reply_count': int(item.get('repliesCount') or item.get('reply_count') or 0),
        'username': str(username_val),
        'label': None
    }


def scrape_instagram(target: str, max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk komentar postingan atau Reels Instagram via Apify SDK
    menggunakan aktor resmi: 'apify/instagram-comment-scraper'.
    """
    clean_url = target.strip()
    if not clean_url:
        return pd.DataFrame()

    # Normalisasi URL jika belum ada protokol
    if not clean_url.startswith("http"):
        clean_url = f"https://{clean_url}"

    run_input = {
        "directUrls": [clean_url],
        "resultsLimit": max_results
    }

    last_error = None

    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue

        try:
            client = ApifyClient(token)
            print(f"\n[PROSES INSTAGRAM] Menghubungi Aktor 'apify/instagram-comment-scraper' (Token: {token[:12]}...) untuk URL: '{clean_url}'...")

            run = client.actor("apify/instagram-comment-scraper").call(run_input=run_input)
            records = []

            for item in client.dataset(run.default_dataset_id).iterate_items():
                rec = _parse_instagram_item(item)
                if rec:
                    records.append(rec)

            df = pd.DataFrame(records)

            if not df.empty:
                df = df.drop_duplicates(subset=['text'])
                print(f"[BERHASIL INSTAGRAM] Memanen {len(df)} komentar Instagram!")
                return df.head(max_results)

        except Exception as e:
            last_error = str(e)
            print(f"[WARN INSTAGRAM] Token {token[:12]}... kendala: {last_error}")

    print(f"[ERROR INSTAGRAM] Seluruh token Apify gagal: {last_error}")
    return pd.DataFrame()
