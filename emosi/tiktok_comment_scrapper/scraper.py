import os
import re
import json
from loguru import logger
from tiktok_comment_scrapper.tiktokcomment.tiktokcomment import TiktokComment

def extract_video_id(url: str) -> str:
    """
    Mengambil aweme_id dari URL video TikTok.
    """
    match = re.search(r'/video/(\d+)', url)
    return match.group(1) if match else url # fallback: input langsung ID

def scrape_tiktok_comments(video_url: str, output_path: str = None) -> str:
    """
    Fungsi utama untuk scraping komentar TikTok.
    - video_url: URL lengkap video TikTok (atau hanya ID).
    - output_path: path penyimpanan file hasil dalam format JSON.
    """
    video_id = extract_video_id(video_url)
    scraper = TiktokComment()

    try:
        comments_obj = scraper(video_id)
    except Exception as e:
        logger.error(f"❌ Gagal scraping komentar: {e}")
        raise

    if not output_path:
        output_path = f"emosi/output/comments_{video_id}.json"

    # Buat folder jika belum ada
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(comments_obj.dict, f, ensure_ascii=False, indent=2)
        logger.success(f"✅ File komentar tersimpan di: {output_path}")
    except Exception as e:
        logger.error(f"❌ Gagal menyimpan file komentar: {e}")
        raise


    return output_path