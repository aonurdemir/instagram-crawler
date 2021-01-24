from peewee import AutoField, TextField, IntegerField, BigIntegerField, BooleanField

from inscrawler.persistence.entity.base_model import BaseModel


# TODO create indexes
class ProfileEntity(BaseModel):
    id = AutoField(null=False)
    username = TextField(null=False, unique=True)
    name = TextField(null=True)
    description = TextField(null=True)
    n_followers = IntegerField(null=True)
    n_following = IntegerField(null=True)
    n_posts = IntegerField(null=True)
    photo_url = TextField(null=True)
    last_visit = BigIntegerField(null=True)
    created_at = BigIntegerField(null=True)
    deleted = BooleanField(null=True)
    visited = BooleanField(null=True)

    class Meta:
        table_name = 'profile'
