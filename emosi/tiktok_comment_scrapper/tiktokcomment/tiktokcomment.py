import jmespath
from typing import Any, Dict, Iterator, Optional, List
from requests import Session, Response
from loguru import logger

from datetime import datetime

from .typing import Comments, Comment


class TiktokComment:
    BASE_URL = 'https://www.tiktok.com'
    API_URL = f'{BASE_URL}/api'

    def __init__(self):
        self.__session = Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        })

    def __parse_comment(self, data: Dict[str, Any]) -> Comment:
        extracted = jmespath.search("""
        {
            comment_id: cid,
            username: user.unique_id,
            comment: text,
            create_time: create_time,
            total_reply: reply_comment_total,
            like_count: digg_count
        }""", data) or {}

        # Log debugging untuk memastikan komentar terbaca
        if extracted.get("username") and extracted.get("create_time"):
            try:
                readable_time = datetime.fromtimestamp(int(extracted["create_time"])).strftime("%Y-%m-%dT%H:%M:%S")
                logger.debug(f"Komentar dari @{extracted['username']} di {readable_time}")
            except Exception:
                logger.debug(f"Komentar dari @{extracted['username']} (waktu tidak valid)")

        return Comment(
            **extracted,
            replies=list(self.get_all_replies(extracted.get('comment_id'), 3)) if extracted.get('total_reply') else []
        )

    def get_all_replies(self, comment_id: str, max_pages: int) -> Iterator[Comment]:
        page = 1
        while page <= max_pages:
            for reply in self.get_replies(comment_id, page):
                yield reply

            page += 1

    def get_replies(self, comment_id: str, page: int = 1) -> List[Comment]:
        response = self.__session.get(
            f'{self.API_URL}/comment/list/reply/',
            params={
                'aid': 1988,
                'comment_id': comment_id,
                'item_id': self.aweme_id,
                'count': 50,
                'cursor': (page - 1) * 50
            }
        )

        try:
            return [self.__parse_comment(r) for r in response.json().get('comments', [])]
        except Exception as e:
            logger.warning(f"Gagal parse reply: {e}")
            return []

    def get_all_comments(self, aweme_id: str, max_pages: int = 10) -> Comments:
        self.aweme_id = aweme_id
        page = 1

        # Ambil halaman pertama komentar
        response = self.__session.get(
            f'{self.API_URL}/comment/list/',
            params={
                'aid': 1988,
                'aweme_id': aweme_id,
                'count': 50,
                'cursor': 0
            }
        )

        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Gagal parsing komentar: {e}")
            return Comments("-", f"https://www.tiktok.com/video/{aweme_id}", 0, [], 0)

        raw_comments = data.get("comments", [])
        all_comments = [self.__parse_comment(c) for c in raw_comments]

        # Fallback caption dan url
        caption = "-"
        video_url = f"https://www.tiktok.com/video/{aweme_id}"
        like_count = 0

        if raw_comments:
            share_info = raw_comments[0].get("share_info", {})
            caption = share_info.get("title", caption)
            video_url = share_info.get("url", video_url)

        # Loop komentar berikutnya
        while data.get("has_more", 0) and page < max_pages:
            page += 1
            logger.debug(f"➡️ Mengambil halaman komentar ke-{page}")

            response = self.__session.get(
                f'{self.API_URL}/comment/list/',
                params={
                    'aid': 1988,
                    'aweme_id': aweme_id,
                    'count': 50,
                    'cursor': (page - 1) * 50
                }
            )

            try:
                data = response.json()
                raw_comments = data.get("comments", [])
                new_comments = [self.__parse_comment(c) for c in raw_comments]
                all_comments.extend(new_comments)
            except Exception as e:
                logger.warning(f"Gagal parsing halaman ke-{page}: {e}")
                break

        logger.success(f"✅ Total komentar terkumpul: {len(all_comments)}")

        return Comments(
            caption=caption,
            video_url=video_url,
            like_count=like_count,
            comments=all_comments,
            has_more=0
        )

    def __call__(self, aweme_id: str) -> Comments:
        return self.get_all_comments(aweme_id)
