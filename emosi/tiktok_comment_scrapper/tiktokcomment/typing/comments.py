import json

from typing import List, Any, Dict

from .comment import Comment

class Comments:
    def __init__(
        self: 'Comments',
        caption: str,
        video_url: str,
        like_count: int,
        comments: List[Comment],
        has_more: bool  # ✅ ganti dari int ke bool
    ) -> None:
        self._caption = caption or "-"
        self._video_url = video_url
        self._like_count = like_count or 0
        self._comments = comments or []
        self._has_more = has_more

    @property
    def caption(self) -> str:
        return self._caption

    @property
    def video_url(self) -> str:
        return self._video_url

    @property
    def like_count(self) -> int:
        return self._like_count

    @property
    def comments(self) -> List[Comment]:
        return self._comments

    @property
    def has_more(self) -> bool:
        return self._has_more

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            'caption': self._caption,
            'video_url': self._video_url,
            'like_count': self._like_count,
            'comments': [comment.dict for comment in self._comments],
            'has_more': self._has_more
        }

    @property
    def json(self) -> str:
        return json.dumps(self.dict, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return self.json
