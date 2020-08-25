from peewee import BigIntegerField, BooleanField, ForeignKeyField, CompositeKey

from inscrawler.persistence.entity.base_model import BaseModel
from inscrawler.persistence.entity.profile_entity import ProfileEntity


# TODO create indexes
class FollowingEntity(BaseModel):
    followed = ForeignKeyField(ProfileEntity)
    follower = ForeignKeyField(ProfileEntity)
    created_at = BigIntegerField()
    last_visit = BigIntegerField()
    deleted = BooleanField()

    class Meta:
        primary_key = CompositeKey('followed', 'follower')
        table_name = 'following'
