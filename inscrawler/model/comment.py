from typing import Optional, List

from inscrawler.model.profile import Profile


class Comment:
    id_: Optional[int]
    # post: Optional[Post]
    author: Optional[Profile]
    comment: Optional[str]
    likers: Optional[List[Profile]]
    created_at: Optional[int]
    last_visit: Optional[int]
    comment_date: Optional[int]
    deleted: Optional[bool]

    def __init__(self, id_: Optional[int] = None,
                 # post: Optional[Post] = None,
                 author: Optional[Profile] = None,
                 comment: Optional[str] = None,
                 likers: Optional[List[Profile]] = None,
                 created_at: Optional[int] = None,
                 last_visit: Optional[int] = None,
                 comment_date: Optional[int] = None,
                 deleted: Optional[bool] = None) -> None:
        self.id_ = id_
        # self.post = post
        self.author = author
        self.comment = comment
        self.created_at = created_at
        self.likers = likers
        self.last_visit = last_visit
        self.comment_date = comment_date
        self.deleted = deleted
