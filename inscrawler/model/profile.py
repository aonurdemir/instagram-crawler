from typing import Optional, List


class Profile:
    id_: Optional[int]
    username: Optional[str]
    name: Optional[str]
    description: Optional[str]
    n_followers: Optional[int]
    n_following: Optional[int]
    n_posts: Optional[int]
    followers: Optional[List['Profile']]
    followings: Optional[List['Profile']]
    photo_url: Optional[str]
    last_visit: Optional[int]
    created_at: Optional[int]
    deleted: Optional[bool]
    visited: Optional[bool]

    def __init__(self, id_: Optional[int] = None,
                 username: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 n_followers: Optional[int] = None,
                 n_following: Optional[int] = None,
                 n_posts: Optional[int] = None,
                 followers: Optional[List['Profile']] = None,
                 followings: Optional[List['Profile']] = None,
                 photo_url: Optional[str] = None,
                 last_visit: Optional[int] = None,
                 created_at: Optional[int] = None,
                 deleted: Optional[bool] = None,
                 visited: Optional[bool] = None) -> None:
        self.id_ = id_
        self.username = username
        self.name = name
        self.description = description
        self.n_followers = n_followers
        self.n_following = n_following
        self.followers = followers
        self.followings = followings
        self.n_posts = n_posts
        self.photo_url = photo_url
        self.last_visit = last_visit
        self.created_at = created_at
        self.deleted = deleted
        self.visited = visited
