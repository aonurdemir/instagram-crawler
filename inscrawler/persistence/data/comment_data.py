from datetime import datetime
from typing import Optional, List

import inscrawler.persistence.data.post_data as post_data
import inscrawler.persistence.data.profile_data as profile_data
from inscrawler.model.comment import Comment
from inscrawler.model.post import Post
from inscrawler.persistence.data.like_on_comment_data import create_or_update_like_on_comment
from inscrawler.persistence.entity import CommentEntity


def get_by_id(comment_id: int):
    return from_entity(CommentEntity.get_by_id(comment_id))


def get_by_author_and_date(author_id: int, comment_date: int) -> Optional[Comment]:
    try:
        comment_entity: CommentEntity = CommentEntity.get(CommentEntity.author == author_id,
                                                          CommentEntity.comment_date == comment_date)
    except CommentEntity.DoesNotExist:
        return None

    return from_entity(comment_entity)


def create_or_update_comment(comment: Comment, post: Post):
    comment_on_db: CommentEntity = \
        CommentEntity.get_or_create(post=post_data.to_entity(post), author=profile_data.to_entity(comment.author),
                                    comment_date=comment.comment_date)[0]

    now = int(datetime.now().timestamp())
    if comment_on_db.created_at is None:
        comment.created_at = now
    else:
        comment.created_at = comment_on_db.created_at

    comment.last_visit = now

    comment.id_ = comment_on_db.id
    comment_entity: CommentEntity = to_entity(comment, post)

    comment_entity.save()

    for comment_liker in comment.likers:
        create_or_update_like_on_comment(comment, post, comment_liker)


def get_comments_by_post(post_id: int) -> List[Comment]:
    comment_entity_list: List[CommentEntity] = CommentEntity.select().where(CommentEntity.post == post_id)
    return_list = []
    for comment_entity in comment_entity_list:
        return_list.append(from_entity(comment_entity))

    return return_list


def create(comment: Comment, post: Post):
    CommentEntity.insert(to_entity(comment, post))


def to_entity(comment: Comment, post: Post) -> CommentEntity:
    return CommentEntity(id=comment.id_,
                         post=post_data.to_entity(post),
                         author=profile_data.to_entity(comment.author),
                         comment=comment.comment,
                         last_visit=comment.last_visit,
                         comment_date=comment.comment_date,
                         deleted=comment.deleted
                         )


def from_entity(comment_entity: CommentEntity) -> Comment:
    return Comment(id_=comment_entity.id,
                   # post=comment_entity.post,
                   author=comment_entity.author,
                   comment=comment_entity.comment,
                   last_visit=comment_entity.last_visit,
                   comment_date=comment_entity.comment_date,
                   deleted=comment_entity.deleted
                   )
