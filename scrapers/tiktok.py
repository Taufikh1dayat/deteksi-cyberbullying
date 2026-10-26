from apify_client import ApifyClient
import pandas as pd
from datetime import datetime
from .config import APIFY_TOKENS

def _parse_tiktok_item(item: dict) -> dict:
    """Ekstraksi satu data TikTok (komentar atau post/caption) ke skema terpadu."""
    text_content = (
        item.get('text') or
        item.get('commentText') or
        item.get('comment') or
        item.get('desc')
    )
    if not text_content:
        return None

    # Ekstraksi username
    user_info = item.get('user') or item.get('author') or item.get('authorMeta') or {}
    username_val = (
        item.get('uniqueId') or
        item.get('authorPinTitle') or
        (user_info.get('uniqueId') if isinstance(user_info, dict) else None) or
        (user_info.get('name') if isinstance(user_info, dict) else None) or
        item.get('author_name') or
        "TikTok_User"
    )

    # Konversi timestamp UNIX jika ada
    raw_time = item.get('createTime') or item.get('createdAt')
    if isinstance(raw_time, (int, float)):
        try:
            created_str = datetime.fromtimestamp(raw_time).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            created_str = str(raw_time)
    else:
        created_str = str(raw_time or '')

    like_count = (
        item.get('diggCount') or
        item.get('likes') or
        item.get('likeCount') or
        item.get('digg_count') or
        0
    )

    return {
        'platform': 'TikTok',
        'id': str(item.get('cid') or item.get('id') or item.get('commentId', '')),
        'text': str(text_content).strip(),
        'created_at': created_str,
        'like_count': int(like_count),
        'retweet_count': 0,
        'reply_count': int(item.get('replyCommentTotal') or item.get('reply_count') or 0),
        'username': str(username_val),
        'label': None
    }


def scrape_tiktok(target: str = "", video_url: str = "", max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk data TikTok via Apify SDK.
    - Jika URL video: menggunakan 'clockworks/tiktok-comments-scraper' untuk menarik komentar video tersebut.
    - Jika Kata Kunci / Profil: menggunakan 'clockworks/tiktok-scraper' dengan limit dinamis (minimal 20 data).
    """
    input_str = (target or video_url).strip()
    if not input_str:
        return pd.DataFrame()

    is_url = "tiktok.com" in input_str or input_str.startswith("http")
    actor_limit = max(max_results, 20)
    last_error = None

    for token in APIFY_TOKENS:
        if not token or "apify_api_" not in token:
            continue

        try:
            client = ApifyClient(token)

            if is_url:
                actor_id = "clockworks/tiktok-comments-scraper"
                run_input = {
                    "postURLs": [input_str],
                    "commentsPerPost": actor_limit,
                    "maxRepliesPerComment": 0
                }
                mode_desc = f"URL Video: '{input_str}'"
            elif input_str.startswith("@"):
                actor_id = "clockworks/tiktok-scraper"
                run_input = {
                    "profiles": [input_str.lstrip("@")],
                    "resultsPerPage": actor_limit,
                    "shouldDownloadComments": True,
                    "commentsPerPost": 10
                }
                mode_desc = f"Profil TikTok: '{input_str}'"
            else:
                actor_id = "clockworks/tiktok-scraper"
                run_input = {
                    "searchQueries": [input_str],
                    "resultsPerPage": actor_limit,
                    "shouldDownloadComments": True,
                    "commentsPerPost": 10
                }
                mode_desc = f"Kata Kunci: '{input_str}'"

            print(f"\n[PROSES TIKTOK] Menghubungi Aktor '{actor_id}' (Token: {token[:12]}...) target: {mode_desc}...")
            run = client.actor(actor_id).call(run_input=run_input)
            records = []

            for item in client.dataset(run.default_dataset_id).iterate_items():
                # 1. Cek jika item menyertakan daftar komentar di dalamnya
                nested = item.get('comments')
                if isinstance(nested, list) and len(nested) > 0:
                    for c in nested:
                        rec = _parse_tiktok_item(c)
                        if rec:
                            records.append(rec)

                # 2. Cek item utama (caption/konten)
                rec = _parse_tiktok_item(item)
                if rec:
                    records.append(rec)

            df = pd.DataFrame(records)

            if not df.empty:
                df = df.drop_duplicates(subset=['text'])
                print(f"[BERHASIL TIKTOK] Memanen {len(df)} data TikTok untuk {mode_desc}!")
                return df.head(max_results)

        except Exception as e:
            last_error = str(e)
            print(f"[WARN TIKTOK] Token {token[:12]}... kendala: {last_error}")

    print(f"[ERROR TIKTOK] Seluruh token Apify gagal: {last_error}")
    return pd.DataFrame()
