from typing import Optional

from inscrawler.model.comment import Comment
from inscrawler.model.profile import Profile


class LikeOnComment:
    profile: Optional[Profile]
    comment: Optional[Comment]
    created_at: Optional[int]
    last_visit: Optional[int]
    deleted: Optional[bool]

    def __init__(self, profile: Optional[Profile],
                 comment: Optional[Comment],
                 created_at: Optional[int],
                 last_visit: Optional[int],
                 deleted: Optional[bool]) -> None:
        self.profile = profile
        self.comment = comment
        self.created_at = created_at
        self.last_visit = last_visit
        self.deleted = deleted
