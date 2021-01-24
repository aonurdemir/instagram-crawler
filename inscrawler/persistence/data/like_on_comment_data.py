from datetime import datetime

from inscrawler.model.comment import Comment
from inscrawler.model.post import Post
from inscrawler.model.profile import Profile
from inscrawler.persistence.entity import LikeOnCommentEntity
import inscrawler.persistence.data.comment_data as comment_data
import inscrawler.persistence.data.profile_data as profile_data


def create_or_update_like_on_comment(comment: Comment, post: Post, profile: Profile):
    like_on_comment_entity_on_db: LikeOnCommentEntity = \
        LikeOnCommentEntity.get_or_create(comment=comment_data.to_entity(comment, post),
                                          profile=profile_data.to_entity(profile))[0]

    now = int(datetime.now().timestamp())
    if like_on_comment_entity_on_db.created_at is None:
        like_on_comment_entity_on_db.created_at = now
    else:
        like_on_comment_entity_on_db.created_at = like_on_comment_entity_on_db.created_at

    like_on_comment_entity_on_db.last_visit = now

    like_on_comment_entity_on_db.save()
