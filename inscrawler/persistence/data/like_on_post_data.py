from datetime import datetime

import inscrawler.persistence.data.post_data as post_data
import inscrawler.persistence.data.profile_data as profile_data
from inscrawler.model.post import Post
from inscrawler.model.profile import Profile
from inscrawler.persistence.entity import LikeOnPostEntity


def create_or_update_like_on_post(post: Post, profile: Profile):
    like_on_post_entity_on_db: LikeOnPostEntity = \
        LikeOnPostEntity.get_or_create(post=post_data.to_entity(post), profile=profile_data.to_entity(profile))[0]

    now = int(datetime.now().timestamp())
    if like_on_post_entity_on_db.created_at is None:
        like_on_post_entity_on_db.created_at = now
    else:
        like_on_post_entity_on_db.created_at = like_on_post_entity_on_db.created_at

    like_on_post_entity_on_db.last_visit = now

    like_on_post_entity_on_db.save()
