from typing import Optional

from inscrawler.model.profile import Profile


class Following:
    followed: Optional[Profile]
    follower: Optional[Profile]
    created_at: Optional[int]
    last_visit: Optional[int]
    deleted: Optional[bool]

    def __init__(self, followed: Optional[Profile],
                 follower: Optional[Profile],
                 created_at: Optional[int],
                 last_visit: Optional[int],
                 deleted: Optional[bool]) -> None:
        self.followed = followed
        self.follower = follower
        self.created_at = created_at
        self.last_visit = last_visit
        self.deleted = deleted
