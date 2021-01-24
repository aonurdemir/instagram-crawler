from inscrawler.persistence.entity import *
from inscrawler.persistence.entity.base_model import psql_db
from inscrawler.persistence.entity.comment_entity import CommentEntity
from inscrawler.persistence.entity.following_entity import FollowingEntity
from inscrawler.persistence.entity.like_on_comment_entity import LikeOnCommentEntity
from inscrawler.persistence.entity.like_on_post_entity import LikeOnPostEntity
from inscrawler.persistence.entity.post_entity import PostEntity
from inscrawler.persistence.entity.profile_entity import ProfileEntity


def reset_db():
    psql_db.drop_tables(
        [ProfileEntity, PostEntity, CommentEntity, LikeOnPostEntity, LikeOnCommentEntity, FollowingEntity],
        cascade=True)

    ProfileEntity.create_table()
    PostEntity.create_table()
    CommentEntity.create_table()
    LikeOnPostEntity.create_table()
    LikeOnCommentEntity.create_table()
    FollowingEntity.create_table()

# Uncomment to re-create tables
# reset_db()
