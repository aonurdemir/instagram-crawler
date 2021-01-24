# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import argparse
import json
import logging
import sys
from io import open
from typing import List

from inscrawler import InsCrawler
from inscrawler.model.post import Post
from inscrawler.model.profile import Profile
#from inscrawler.persistence.data.post_data import save_post
# from inscrawler.persistence.data.profile_data import get_or_create_profile, create_or_update_profile, \
#     get_profile_to_crawl
from inscrawler.settings import override_settings, settings
from inscrawler.settings import prepare_override_settings


def usage():
    return """
        python crawler.py posts -u cal_foodie -n 100 -o ./output
        python crawler.py posts_full -u cal_foodie -n 100 -o ./output
        python crawler.py profile -u cal_foodie -o ./output
        python crawler.py profile_script -u cal_foodie -o ./output
        python crawler.py hashtag -t taiwan -o ./output
        python crawler.py network -u onurdemir -d 2 -o ./output

        The default number for fetching posts via hashtag is 100.
    """


def get_posts_by_user(username, number, detail, debug, ins_crawler=None):
    if ins_crawler is None:
        ins_crawler = InsCrawler(has_screen=debug)
        ins_crawler.login()
    return ins_crawler.get_user_posts(username, number, detail)


def get_profile(username, debug=False, follow_list_enabled=False):
    ins_crawler = InsCrawler(has_screen=debug)
    ins_crawler.login()
    return ins_crawler.get_user_profile(username, follow_list_enabled)


def get_profile_from_script(username):
    ins_cralwer = InsCrawler()
    return ins_cralwer.get_user_profile_from_script_shared_data(username)


def get_posts_by_hashtag(tag, number, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_latest_posts_by_tag(tag, number)


def get_network_by_username(username, depth, debug):
    ins_crawler = InsCrawler(has_screen=debug)
    return ins_crawler.get_network_by_username(username, depth)


def arg_required(args, fields=[]):
    for field in fields:
        if not getattr(args, field):
            parser.print_help()
            sys.exit()


def output(data, filepath):
    out = json.dumps(data, ensure_ascii=False)
    if filepath:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(out)
    else:
        print(out)


def get_post_full(username, number=None, debug=False, ins_crawler=None):
    posts: List[Post] = get_posts_by_user(username, number, True, debug, ins_crawler)

    # profile: Profile = get_or_create_profile(username)

    for post in posts:
        post.profile = profile
        # save_post(post)

    return posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Instagram Crawler", usage=usage())
    parser.add_argument(
        "mode", help="options: [posts, posts_full, profile, profile_script, hashtag, crawler, network]"
    )
    parser.add_argument("-n", "--number", type=int,
                        help="number of returned posts")
    parser.add_argument("-u", "--username", help="instagram's username")
    parser.add_argument("-t", "--tag", help="instagram's tag name")
    parser.add_argument("-o", "--output", help="output file name(json format)")
    parser.add_argument("-d", "--depth", type=int, help="depth of the network")
    parser.add_argument("--debug", action="store_true")

    prepare_override_settings(parser)

    args = parser.parse_args()

    override_settings(args)

    logger = logging.getLogger(__name__)

    if args.mode in ["posts", "posts_full"]:
        arg_required("username")
        posts = get_post_full(args.username, args.number, args.debug)

        # output(posts, args.output, )

    elif args.mode == "profile":
        arg_required("username")

        ins_crawler = InsCrawler(has_screen=args.debug)
        ins_crawler.login()
        profile = ins_crawler.get_user_profile(args.username, True)

        #create_or_update_profile(profile)

    elif args.mode == "profile_script":
        arg_required("username")
        # output(get_profile_from_script(args.username), args.output)
    elif args.mode == "hashtag":
        arg_required("tag")
        # output(
        #     get_posts_by_hashtag(
        #         args.tag, args.number or 100, args.debug), args.output
        # )
    elif args.mode == "crawler":
        settings = settings()
        setattr(settings, 'fetch_comments', True)
        setattr(settings, 'fetch_likers', True)

        override_settings(settings)

        ins_crawler = InsCrawler(has_screen=args.debug)
        ins_crawler.login()

        # while True:
        #     profiles_to_crawl: List[Profile] = get_profile_to_crawl(10)
        #     for profile_to_crawl in profiles_to_crawl:
        #         profile = ins_crawler.get_user_profile(profile_to_crawl.username, True)
        #         create_or_update_profile(profile)
        #
        #         get_post_full(profile.username, profile.n_posts, args.debug, ins_crawler)
    elif args.mode == "network":
        arg_required("username")
        arg_required("depth")
        output(get_network_by_username(args.username, args.depth or 3, args.debug), args.output)
    else:
        usage()
