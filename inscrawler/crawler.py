from __future__ import unicode_literals

import glob
import json
import os
import re
import sys
import time
import traceback
from builtins import open
from time import sleep
from datetime import datetime
import dateutil.parser

from tqdm import tqdm

from . import secret
from .browser import Browser
from .exceptions import RetryException
from .fetch import fetch_caption
from .fetch import fetch_comments
from .fetch import fetch_datetime
from .fetch import fetch_imgs
from .fetch import fetch_likers
from .fetch import fetch_likes_plays
from .fetch import fetch_details
from .utils import instagram_int
from .utils import randmized_sleep
from .utils import retry

from selenium import webdriver


class Logging(object):
    PREFIX = "instagram-crawler"

    def __init__(self):
        try:
            timestamp = int(time.time())
            self.cleanup(timestamp)
            self.logger = open("/tmp/%s-%s.log" %
                               (Logging.PREFIX, timestamp), "w")
            self.log_disable = False
        except Exception:
            self.log_disable = True

    def cleanup(self, timestamp):
        days = 86400 * 7
        days_ago_log = "/tmp/%s-%s.log" % (Logging.PREFIX, timestamp - days)
        for log in glob.glob("/tmp/instagram-crawler-*.log"):
            if log < days_ago_log:
                os.remove(log)

    def log(self, msg):
        if self.log_disable:
            return

        self.logger.write(msg + "\n")
        self.logger.flush()

    def __del__(self):
        if self.log_disable:
            return
        self.logger.close()


class InsCrawler(Logging):
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, has_screen=False):
        super(InsCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0        

    def _dismiss_login_prompt(self):
        ele_login = self.browser.find_one(".Ls00D .Szr5J")
        if ele_login:
            ele_login.click()

    def login(self):
        browser = self.browser
        url = "%s/accounts/login/" % (InsCrawler.URL)
        browser.get(url)
        u_input = browser.find_one('input[name="username"]')
        u_input.send_keys(secret.username)
        p_input = browser.find_one('input[name="password"]')
        p_input.send_keys(secret.password)

        login_btn = browser.find_one(".L3NKy")
        login_btn.click()

        @retry()
        def check_login():
            if browser.find_one('input[name="username"]'):
                raise RetryException()

        check_login()

    def get_user_profile(self, username, follow_list_enabled=False):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)

        try:
            name = browser.find_one(".rhpdm").text
        except AttributeError:
            name = ''
        
        try:
            desc = browser.find_one(".-vDIg > span").text
        except AttributeError:
            desc = ''

        try:
            photo = browser.find_one("._6q-tv").get_attribute("src")
        except AttributeError:
            try:
                photo = browser.find_one(".be6sR").get_attribute("src") #Private profile
            except AttributeError:
                photo = ''

        statistics = browser.find(".g47SY")

        post_num = statistics[0].text.replace(",", "")
        follower_num = statistics[1].get_attribute("title").replace(",", "")
        following_num = statistics[2].text.replace(",", "")

        followers = None
        if follow_list_enabled:
            follower_btn = statistics[1]
            follower_btn.click()

            follower_elems_css_selector = ".RnEpo.Yx5HN .isgrP .PZuss .FPmhX"
            try:
                follower_elems = list(browser.find(follower_elems_css_selector, waittime=0.6))

                username_last_check = None
                current_username = None

                follower_elems[-1].location_once_scrolled_into_view
                sleep(0.6)

                follower_elems = list(browser.find(follower_elems_css_selector))
                last_follower = follower_elems[-1]
                username_last_check = last_follower.get_attribute("title")
                while follower_elems:
                    # Scroll down
                    script = "document.querySelector(\".isgrP\").scrollTo(0, document.querySelector(\".isgrP\").scrollHeight);"
                    self.browser.driver.execute_script(script)
                    sleep(0.6)

                    # Get last username
                    last_profile = browser.find_one(".wo9IH:last-child .enpQJ a")
                    try:
                        current_username = last_profile.get_attribute("title")
                    except AttributeError:
                        break

                    # Check if the last username of current iteration is the same as the previous iteration
                    if current_username == username_last_check:
                        break

                    # Save last username of list
                    username_last_check = current_username

                follower_elems = list(browser.find(follower_elems_css_selector, waittime=1))
                followers = list([ele.get_attribute("title") for ele in follower_elems])

                close_btn = browser.find_one("button.wpO6b")
                close_btn.click()
            except:
                print('Private profile')


        return_obj = {
            "name": name,
            "desc": desc,
            "photo_url": photo,
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num
        }

        if followers is not None:
            return_obj['followers'] = followers

        return return_obj

    def get_user_profile_from_script_shared_data(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        source = browser.driver.page_source
        p = re.compile(
            r"window._sharedData = (?P<json>.*?);</script>", re.DOTALL)
        json_data = re.search(p, source).group("json")
        data = json.loads(json_data)

        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        return {
            "name": user_data["full_name"],
            "desc": user_data["biography"],
            "photo_url": user_data["profile_pic_url_hd"],
            "post_num": user_data["edge_owner_to_timeline_media"]["count"],
            "follower_num": user_data["edge_followed_by"]["count"],
            "following_num": user_data["edge_follow"]["count"],
            "website": user_data["external_url"],
        }

    def get_user_posts(self, username, number=None, detail=False):
        user_profile = self.get_user_profile(username)
        print(user_profile)
        if not number:
            number = instagram_int(user_profile["post_num"])

        self._dismiss_login_prompt()

        if detail:
            return self._get_posts_full(username, number)
        else:
            return self._get_posts(number)

    def get_latest_posts_by_tag(self, tag, num):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self._get_posts(num)

    def auto_like(self, tag="", maximum=1000):
        self.login()
        browser = self.browser
        if tag:
            url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        else:
            url = "%s/explore/" % (InsCrawler.URL)
        self.browser.get(url)

        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()

        for _ in range(maximum):
            heart = browser.find_one(
                ".dCJp8 .glyphsSpriteHeart__outline__24__grey_9")
            if heart:
                heart.click()
                randmized_sleep(2)

            left_arrow = browser.find_one(".HBoOv")
            if left_arrow:
                left_arrow.click()
                randmized_sleep(2)
            else:
                break

    def _get_posts_full(self, username, num):
        @retry()
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")

            # It takes time to load the post for some users with slow network
            if ele_a_datetime is None:
                raise RetryException()

            next_key = ele_a_datetime.get_attribute("href")
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        browser.implicitly_wait(1)
        browser.scroll_down()
        ele_post = browser.find_one(".v1Nh3 a")

        #Return empty list for users without posts
        if ele_post is None:
            return list()

        ele_post.click()
        dict_posts = {}

        pbar = tqdm(total=num)
        pbar.set_description("fetching")
        cur_key = None


        # Fetching all posts
        for _ in range(num):
            dict_post = {}

            # Fetching post detail
            try:
                check_next_post(cur_key)

                # Fetching datetime and url as key
                ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
                cur_key = ele_a_datetime.get_attribute("href")
                dict_post["key"] = cur_key
                fetch_datetime(browser, dict_post)
                fetch_imgs(browser, dict_post)
                fetch_likes_plays(browser, dict_post)
                fetch_likers(browser, dict_post)
                fetch_caption(browser, dict_post)
                fetch_comments(browser, dict_post)

            except RetryException:
                sys.stderr.write(
                    "\x1b[1;31m" +
                    "Failed to fetch the post: " +
                    cur_key or 'URL not fetched' +
                    "\x1b[0m" +
                    "\n"
                )
                break

            except Exception:
                sys.stderr.write(
                    "\x1b[1;31m" +
                    "Failed to fetch the post: " +
                    cur_key if isinstance(cur_key, str) else 'URL not fetched' +
                                                               "\x1b[0m" +
                                                               "\n"
                )
                traceback.print_exc()

            self.log(json.dumps(dict_post, ensure_ascii=False))
            dict_posts[browser.current_url] = dict_post

            pbar.update(1)
            right_arrow = browser.find_one("._65Bje")
            if right_arrow:
                right_arrow.click()

        pbar.close()
        posts = list(dict_posts.values())
        if posts:
            posts.sort(key=lambda post: post["datetime"], reverse=True)

        return posts

    def _get_posts(self, num):
        """
            To get posts, we have to click on the load more
            button and make the browser call post api.
        """
        TIMEOUT = 600
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a")
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in key_set:
                    dict_post = {"key": key}
                    ele_img = browser.find_one(".KL4Bh img", ele)
                    dict_post["caption"] = ele_img.get_attribute("alt")
                    dict_post["img_url"] = ele_img.get_attribute("src")

                    fetch_details(browser, dict_post)

                    key_set.add(key)
                    posts.append(dict_post)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                pbar.set_description("Wait for %s sec" % (wait_time))
                sleep(wait_time)
                pbar.set_description("fetching")

                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        pbar.set_description("fetching")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        pbar.close()
        print("Done. Fetched %s posts." % (min(len(posts), num)))
        return posts[:num]

    def get_network_by_username(self, username, depth):

        TIMEOUT = 600
        browser = self.browser

        notif_modal = browser.find_one(".pbNvD")  # turn on notif modal
        if notif_modal:
            browser.find_one(".HoLwm").click()  # not now button

        user_profiles = []
        q = [username]

        while q.__len__() > 0 and depth > 0:
            q_length = q.__len__()
            for i in range(0, q_length):
                randmized_sleep(2)
                popped_username = q.pop(0)
                user_profile = self.get_user_profile(popped_username)
                user_profiles.append(user_profile)

                is_private = browser.find_one(".rkEop")
                if is_private:
                    user_profile['private'] = True
                    continue

                followers_link = browser.find(".k9GMp a")[0]
                followers_link.click()
                followers_li_items = browser.find(".jSC57 li")

                follower_usernames = []
                for li in followers_li_items:
                    title = li.find_element_by_class_name("FPmhX").get_attribute("title")
                    follower_usernames.append(title)
                    q.append(title)

                user_profile['followers'] = follower_usernames

            depth = depth - 1


