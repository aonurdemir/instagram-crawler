from datetime import datetime

import inscrawler.persistence.data.comment_data as comment_data
import inscrawler.persistence.data.like_on_post_data as like_on_post_data
import inscrawler.persistence.data.profile_data as profile_data
from inscrawler.model.post import Post
from inscrawler.persistence.entity.post_entity import PostEntity


def save_post(post: Post):
    post_on_db: PostEntity = PostEntity.get_or_create(url=post.url)[0]

    now = int(datetime.now().timestamp())
    if post_on_db.created_at is None:
        post.created_at = now
    else:
        post.created_at = post_on_db.created_at

    post.last_visit = now

    post.id_ = post_on_db.id
    post_entity: PostEntity = to_entity(post)

    post_entity.save()

    if post.comments is not None:
        for comment in post.comments:
            comment_data.create_or_update_comment(comment, post)

    if post.likers is not None:
        for profile in post.likers:
            like_on_post_data.create_or_update_like_on_post(post, profile)


def get_or_create_post(url: str) -> Post:
    return from_entity(PostEntity.get_or_create(url=url)[0])


def from_entity(post_entity: PostEntity) -> Post:
    return Post(id_=post_entity.id,
                profile=post_entity.profile,
                url=post_entity.url,
                url_imgs=post_entity.url_imgs,
                post_date=post_entity.post_date,
                caption=post_entity.caption,
                last_visit=post_entity.last_visit,
                created_at=post_entity.created_at,
                deleted=post_entity.deleted)


def to_entity(post: Post) -> PostEntity:
    return PostEntity(id=post.id_,
                      profile=profile_data.to_entity(post.profile),
                      url=post.url,
                      url_imgs=post.url_imgs,
                      post_date=post.post_date,
                      caption=post.caption,
                      last_visit=post.last_visit,
                      created_at=post.created_at,
                      deleted=post.deleted)
