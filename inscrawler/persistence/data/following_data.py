from datetime import datetime

import inscrawler.persistence.data.profile_data as profile_data
from inscrawler.model.profile import Profile
from inscrawler.persistence.entity import FollowingEntity, ProfileEntity


def create_or_update_following(follower: Profile, followed: Profile):
    follower_on_db: Profile = profile_data.get_or_create_profile(follower.username)
    followed_on_db: Profile = profile_data.get_or_create_profile(followed.username)

    follower_entity: ProfileEntity = profile_data.to_entity(follower_on_db)
    followed_entity: ProfileEntity = profile_data.to_entity(followed_on_db)

    following_on_db: FollowingEntity = \
        FollowingEntity.get_or_create(follower=follower_entity, followed=followed_entity)[0]

    now = int(datetime.now().timestamp())
    if following_on_db.created_at is None:
        following_on_db.created_at = now
    else:
        following_on_db.created_at = following_on_db.created_at

    following_on_db.last_visit = now

    following_on_db.save()
