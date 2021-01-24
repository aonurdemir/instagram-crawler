from typing import Optional

from inscrawler.model.post import Post
from inscrawler.model.profile import Profile


class LikeOnPost:
    profile: Optional[Profile]
    post: Optional[Post]
    created_at: Optional[int]
    last_visit: Optional[int]
    deleted: Optional[bool]

    def __init__(self, profile: Optional[Profile],
                 post: Optional[Post],
                 created_at: Optional[int],
                 last_visit: Optional[int],
                 deleted: Optional[bool]) -> None:
        self.profile = profile
        self.post = post
        self.created_at = created_at
        self.last_visit = last_visit
        self.deleted = deleted
