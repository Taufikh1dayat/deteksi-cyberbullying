from apify_client import ApifyClient
import pandas as pd

# ── 🔑 CONFIGURATION ──────────────────────────────────────────────────
# Menggunakan token resmi Azz Personal (Pastikan berakhiran angka 0)
APIFY_TOKEN = "apify_api_50ZAtK7h0wDuY7KcsnVggZadCa7fN31Qws9O"
# ──────────────────────────────────────────────────────────────────────

def scrape_tweets_apify(query: str, max_results: int = 10) -> pd.DataFrame:
    """
    Mengeruk data X via Aktor API-NINJA.
    Menggunakan kombinasi mode 'Top' + filter 'since' untuk menembus firewall anonim X
    dan membatasi data agar hanya memuat tahun 2024 ke atas.
    """
    # 1. Inisialisasi koneksi ke SDK Apify Client
    client = ApifyClient(APIFY_TOKEN)
    
    # 2. Query Expansion: Menyuntikkan Leksikon Kata Kebencian/Bullying
    lexicon_toksik = "(tolol OR bodoh OR goblok OR benci OR munafik OR jelek OR parah OR cacat)"
    
    # 3. Time Framing: Memaksa X memblokir data purba (Hanya mengambil data 2024 s.d 2026)
    full_query = f"{query} {lexicon_toksik} lang:id since:2024-01-01"
    
    # 4. Penebalan kuota data kontainer untuk cadangan setelah filter lokal
    actor_limit = max(max_results * 2, 20)
    
    # 5. Struktur parameter resmi yang divalidasi oleh skema JSON Apify Ninja
    run_input = {
        "query": full_query,
        "search_type": "Top",          # Jalur aman untuk kueri kompleks tanpa login
        "numberOfTweets": actor_limit 
    }
    
    try:
        print(f"\n[PROSES] Mengirim perintah ke Cloud Apify untuk keyword: '{full_query}'...")
        # Mengeksekusi kontainer docker aktor di server cloud Apify
        run = client.actor("api-ninja/x-twitter-advanced-search").call(run_input=run_input)
        
        print("[PROSES] Data berhasil dipanen! Sedang mengunduh dataset ke lokal...")
        records = []
        
        # 6. Melakukan iterasi dan ekstraksi objek JSON bertingkat hasil scraping
        for item in client.dataset(run.default_dataset_id).iterate_items():
            # Ekstraksi konten teks utama
            text_content = item.get('text') or item.get('fullText') or item.get('full_text')
            
            # Ekstraksi nama pengguna (Super Hunter bertingkat)
            username_val = None
            user_obj = item.get('author') or item.get('user')
            if isinstance(user_obj, dict):
                username_val = user_obj.get('username') or user_obj.get('screen_name') or user_obj.get('screenName')
            if not username_val:
                username_val = item.get('username') or item.get('screen_name') or item.get('author_name')
            
            # Ekstraksi metrik interaksi (Engagement Metrics)
            stats_obj = item.get('stats') or item or {}
            
            # Memasukkan data bersih ke dalam daftar records
            records.append({
                'id': str(item.get('id') or item.get('tweet_id') or item.get('id_str', '')),
                'text': text_content,
                'created_at': item.get('date') or item.get('createdAt') or item.get('created_at'),
                'like_count': stats_obj.get('likes') or stats_obj.get('favorite_count') or 0,
                'retweet_count': stats_obj.get('retweets') or stats_obj.get('retweet_count') or 0,
                'reply_count': stats_obj.get('replies') or stats_obj.get('reply_count') or 0,
                'username': username_val if username_val else "X_User",
                'label': None  # Disiapkan untuk proses pemodelan SVM / Naive Bayes
            })
            
        # Mengubah list data menjadi objek Pandas DataFrame
        df = pd.DataFrame(records)
        
        # 7. Pembersihan dan Pemotongan Data secara Lokal (Pandas Layer)
        if not df.empty:
            # Membuang data duplikasi/retweet murni agar model ML tidak bias
            df = df[~df['text'].str.startswith('RT @', na=False)]
            # Memotong baris sesuai request jumlah slider dari antarmuka Streamlit
            df = df.head(max_results)
            
        return df
        
    except Exception as e:
        # Menampilkan pesan log asli ke terminal jika terjadi crash di server cloud
        print(f"❌ Terjadi kendala saat scraping via Apify: {str(e)}")
        return pd.DataFrame()

# ── 🏎️ PENGUJIAN LOKAL (MOCK RUNNER) ───────────────────────────────────
if __name__ == "__main__":
    print("\n==================================================")
    print("🚀 TESTING REAL-TIME SCRAPER (API-NINJA ACTOR)")
    print("==================================================")
    df_hasil = scrape_tweets_apify(query="Gibran", max_results=5)
    if not df_hasil.empty:
        print(df_hasil[['username', 'created_at', 'text']].to_string())