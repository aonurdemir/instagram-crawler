from datetime import datetime
from typing import List

from peewee import fn

from inscrawler.model.profile import Profile
from inscrawler.persistence.data.following_data import create_or_update_following
from inscrawler.persistence.entity.profile_entity import ProfileEntity


def create_or_update_profile(profile: Profile):
    profile_entity_on_db: ProfileEntity = ProfileEntity.get_or_create(username=profile.username)[0]

    now = int(datetime.now().timestamp())
    if profile_entity_on_db.created_at is None:
        profile.created_at = now
    else:
        profile.created_at = profile_entity_on_db.created_at

    profile.last_visit = now

    profile.id_ = profile_entity_on_db.id
    profile_entity: ProfileEntity = to_entity(profile)

    profile_entity.save()

    for follower in profile.followers:
        create_or_update_following(follower, profile)

    for follower in profile.followings:
        create_or_update_following(profile, follower)


def get_or_create_profile(username: str) -> Profile:
    profile_entity: ProfileEntity = ProfileEntity.get_or_create(username=username)[0]
    return from_entity(profile_entity)


# Let A be a sorted list of profiles(by the last_visit column), sort a random number between 1 and the number of
# elements of the profile table, and then select the n_profile elements below the nth + 1 record
def get_profile_to_crawl(n_profile: int) -> List[Profile]:
    profile_entity_list: List[ProfileEntity] = ProfileEntity.select().order_by(ProfileEntity.last_visit.asc()).limit(
        n_profile).offset(fn.FLOOR(fn.RANDOM() * ProfileEntity.select().count()) + 1)

    return [from_entity(profile) for profile in profile_entity_list]


def to_entity(profile: Profile) -> ProfileEntity:
    return ProfileEntity(id=profile.id_,
                         username=profile.username,
                         name=profile.name,
                         description=profile.description,
                         n_followers=profile.n_followers,
                         n_following=profile.n_following,
                         n_posts=profile.n_posts,
                         photo_url=profile.photo_url,
                         last_visit=profile.last_visit,
                         created_at=profile.created_at,
                         deleted=profile.deleted,
                         visited=profile.visited)


def from_entity(profile_entity: ProfileEntity) -> Profile:
    return Profile(id_=profile_entity.id,
                   username=profile_entity.username,
                   name=profile_entity.name,
                   description=profile_entity.description,
                   n_followers=profile_entity.n_followers,
                   n_following=profile_entity.n_following,
                   n_posts=profile_entity.n_posts,
                   photo_url=profile_entity.photo_url,
                   last_visit=profile_entity.last_visit,
                   created_at=profile_entity.created_at,
                   deleted=profile_entity.deleted,
                   visited=profile_entity.visited)
