from peewee import BigIntegerField, BooleanField, ForeignKeyField, CompositeKey

from inscrawler.persistence.entity.base_model import BaseModel
from inscrawler.persistence.entity.comment_entity import CommentEntity
from inscrawler.persistence.entity.profile_entity import ProfileEntity


# TODO create indexes
class LikeOnCommentEntity(BaseModel):
    profile = ForeignKeyField(ProfileEntity)
    comment = ForeignKeyField(CommentEntity)
    created_at = BigIntegerField(null=True)
    last_visit = BigIntegerField(null=True)
    deleted = BooleanField(null=True)

    class Meta:
        table_name = "like_on_comment"
        primary_key = CompositeKey('profile', 'comment')
