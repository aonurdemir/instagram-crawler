from peewee import AutoField, TextField, BigIntegerField, BooleanField, ForeignKeyField

from inscrawler.persistence.entity.base_model import BaseModel
from inscrawler.persistence.entity.profile_entity import ProfileEntity


# TODO create indexes
class PostEntity(BaseModel):
    id = AutoField(null=False)
    profile = ForeignKeyField(ProfileEntity, null=True)
    url = TextField(null=True)
    url_imgs = TextField(null=True)
    post_date = BigIntegerField(null=True)
    caption = TextField(null=True)
    last_visit = BigIntegerField(null=True)
    created_at = BigIntegerField(null=True)
    deleted = BooleanField(null=True)

    class Meta:
        table_name = 'post'
