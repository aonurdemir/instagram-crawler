from inscrawler.persistence.data.comment_data import get_comments_by_post

# try:
# comments = get_comments_by_post(1)
# for comment in comments:
#     print(comment.author)

# print(get_comments_by_post(1))
# except CommentEntity.DoesNotExist:
#     print("Não existe")


# from inscrawler.persistence.data.comment_data import get_by_author_and_date
# from inscrawler.persistence.entity import CommentEntity, PostEntity, ProfileEntity
#
# profile = ProfileEntity.create(username="fulano", name="fulano", )
# post = PostEntity.create(url="url", profile_id=profile.id)
#
# CommentEntity.create(post_id=post.id, author_id=profile.id, comment="comment", comment_date=5)
#
# try:
#     print(get_by_author_and_date(1, 1))
# except CommentEntity.DoesNotExist:
#     print("Não existe")
