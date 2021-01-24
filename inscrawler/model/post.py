from typing import Optional, List

from inscrawler.model.comment import Comment
from inscrawler.model.profile import Profile


class Post:
    id_: Optional[int]
    profile: Optional[Profile]
    url: Optional[str]
    url_imgs: Optional[List[str]]
    post_date: Optional[int]
    caption: Optional[str]
    likers: Optional[List[Profile]]
    comments: Optional[List[Comment]]
    last_visit: Optional[int]
    created_at: Optional[int]
    deleted: Optional[bool]

    def __init__(self, id_: Optional[int] = None,
                 profile: Optional[Profile] = None,
                 url: Optional[str] = None,
                 url_imgs: Optional[List[str]] = None,
                 post_date: Optional[int] = None,
                 caption: Optional[str] = None,
                 likers: Optional[List[Profile]] = None,
                 comments: Optional[List[Comment]] = None,
                 last_visit: Optional[int] = None,
                 created_at: Optional[int] = None,
                 deleted: Optional[bool] = None) -> None:
        self.id_ = id_
        self.profile = profile
        self.url = url
        self.url_imgs = url_imgs
        self.post_date = post_date
        self.caption = caption
        self.likers = likers
        self.comments = comments
        self.last_visit = last_visit
        self.created_at = created_at
        self.deleted = deleted
