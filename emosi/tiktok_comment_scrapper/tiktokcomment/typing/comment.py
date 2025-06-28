import json

from datetime import datetime

from typing import Optional, List, Dict, Any

class Comment:
    def __init__(
        self: 'Comment',
        comment_id: str,
        username: str,

        comment: str,
        create_time: Any,
        total_reply: int,
        like_count: int,
        replies: Optional[List[Any]] = None
    ) -> None:
        self._comment_id: str = comment_id
        self._username: str = username

        self._comment: str = comment

        if isinstance(create_time, (int, float)):
            self._create_time: str = datetime.fromtimestamp(create_time).strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(create_time, str):
            self._create_time: str = create_time
        else:
            self._create_time: str = "1970-01-01T00:00:00"


        self._total_reply: int = total_reply
        self._like_count: int = like_count

        self._replies: List['Comment'] = [
            reply if isinstance(reply, Comment) else Comment(**reply)
            for reply in replies or []
        ]

    # ✅ Tambahkan properti akses langsung
    @property
    def comment_id(self) -> str:
        return self._comment_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def create_time(self) -> str:
        return self._create_time

    @property
    def total_reply(self) -> int:
        return self._total_reply

    @property
    def like_count(self) -> int:
        return self._like_count

    @property
    def replies(self) -> List['Comment']:
        return self._replies

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            'comment_id': self._comment_id,
            'username': self._username,

            'comment': self._comment,
            'create_time': self._create_time,
            
            'total_reply': self._total_reply,
            'like_count': self._like_count,
            'replies': [reply.dict for reply in self._replies]
        }

    @property
    def json(self) -> str:
        return json.dumps(self.dict, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return self.json
