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
from typing import List

from tqdm import tqdm

from . import secret
from .browser import Browser
from .constants.html_selectors import PROFILE_NAME, PROFILE_DESCRIPTION, PROFILE_PUBLIC_ACCOUNT_PHOTO, \
	PROFILE_PRIVATE_ACCOUNT_PHOTO, PROFILE_STATISTICS, PROFILE_FOLLOWERS_ELEMENTS, FOLLOWERS_SCROLL_DOWN, \
	FOLLOWERS_LAST_PROFILE
from .exceptions import RetryException
from .fetch import fetch_caption
from .fetch import fetch_comments
from .fetch import fetch_datetime
from .fetch import fetch_details
from .fetch import fetch_imgs
from .fetch import fetch_likers
from .fetch import fetch_likes_plays
from .model.post import Post
from .model.profile import Profile
# from .persistence.data.profile_data import get_or_create_profile
from .utils import randmized_sleep
from .utils import retry


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

	def __init__(self, has_screen: bool = False):
		super(InsCrawler, self).__init__()
		self.browser = Browser(has_screen)
		self.page_height = 0

	def _dismiss_login_prompt(self):
		ele_login = self.browser.find_one(".Ls00D .Szr5J")
		if ele_login:
			ele_login.click()

	def login(self):
		browser = self.browser
		url = "%s/accounts/login/" % InsCrawler.URL
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

	def get_user_profile(self, username: str, follow_list_enabled: bool = False, follower_limit: int = 200) -> Profile:
		browser = self.browser
		url = "%s/%s/" % (InsCrawler.URL, username)
		browser.get(url)

		name: str = self.__get_profile_name()
		description: str = self.__get_profile_description()
		photo: str = self.__get_photo_url()

		statistics_elem = self.browser.find(PROFILE_STATISTICS)
		post_num_elem = statistics_elem[0]
		follower_elem = statistics_elem[1]
		following_elem = statistics_elem[2]

		post_num, follower_num, following_num = self.get_user_statistics(statistics_elem)

		followers = None
		followings = None
		if follow_list_enabled and follower_num <= follower_limit:
			follower_btn = follower_elem
			follower_btn.click()

			try:
				follower_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS, waittime=0.6))

				follower_elems[-1].location_once_scrolled_into_view
				sleep(0.6)

				follower_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS))
				last_follower = follower_elems[-1]
				username_last_check = last_follower.get_attribute("title")
				while follower_elems:
					# Scroll down
					self.browser.driver.execute_script(FOLLOWERS_SCROLL_DOWN)
					sleep(0.6)

					# Get last follower
					try:
						last_follower = browser.find_one(FOLLOWERS_LAST_PROFILE)
						current_username = last_follower.get_attribute("title")
					except AttributeError:
						break

					# Check if the last username of current iteration is the same as the previous iteration
					if current_username == username_last_check:
						break

					# Save last username of list
					username_last_check = current_username

				follower_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS, waittime=1))
				followers_username: List[str] = list([ele.get_attribute("title") for ele in follower_elems])
				# followers: List[Profile] = [get_or_create_profile(username) for username in followers_username]
				followers: List[Profile] = [Profile(username=username) for username in followers_username]

				close_btn = browser.find_one(".WaOAr button.wpO6b")
				close_btn.click()
			except Exception as e:
				print('Private profile')

			# statistics_elem = self.browser.find(PROFILE_STATISTICS)
			# following_elem = statistics_elem[2]
			# following_btn = following_elem
			# following_btn.click()
			#
			# try:
			#     following_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS, waittime=0.6))
			#
			#     following_elems[-1].location_once_scrolled_into_view
			#     sleep(0.6)
			#
			#     following_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS))
			#     last_followed = following_elems[-1]
			#     username_last_check = last_followed.get_attribute("title")
			#     while following_elems:
			#         # Scroll down
			#         self.browser.driver.execute_script(FOLLOWERS_SCROLL_DOWN)
			#         sleep(0.6)
			#
			#         # Get last followed
			#         try:
			#             last_followed = browser.find_one(FOLLOWERS_LAST_PROFILE)
			#             current_username = last_followed.get_attribute("title")
			#         except AttributeError:
			#             break
			#
			#         # Check if the last username of current iteration is the same as the previous iteration
			#         if current_username == username_last_check:
			#             break
			#
			#         # Save last username of list
			#         username_last_check = current_username
			#
			#     following_elems = list(browser.find(PROFILE_FOLLOWERS_ELEMENTS, waittime=1))
			#     followeds_username: List[str] = list([ele.get_attribute("title") for ele in following_elems])
			#
			#     followings: List[Profile] = [get_or_create_profile(username) for username in followeds_username]
			#
			#     close_btn = browser.find_one(".WaOAr button.wpO6b")
			#     close_btn.click()
			# except Exception as e:
			#     print('Private profile')

		return Profile(username=username, name=name, description=description, n_followers=follower_num,
		               n_following=following_num, n_posts=post_num, followers=followers, followings=followings,
		               photo_url=photo)

	def get_user_statistics(self, statistics) -> (int, int, int):
		post_num: int = int(statistics[0].text.replace(",", "").replace(".", ""))
		follower_num: int = int(statistics[1].get_attribute("title").replace(",", "").replace(".", ""))
		following_num: int = int(statistics[2].text.replace(",", "").replace(".", ""))
		return post_num, follower_num, following_num

	def __get_photo_url(self):
		try:
			photo = self.browser.find_one(PROFILE_PUBLIC_ACCOUNT_PHOTO).get_attribute("src")
		except AttributeError:
			try:
				photo = self.browser.find_one(PROFILE_PRIVATE_ACCOUNT_PHOTO).get_attribute("src")  # Private profile
			except AttributeError:
				photo = ''
		return photo

	def __get_profile_description(self):
		try:
			desc = self.browser.find_one(PROFILE_DESCRIPTION).text
		except AttributeError:
			desc = ''
		return desc

	def __get_profile_name(self):
		try:
			name = self.browser.find_one(PROFILE_NAME).text
		except AttributeError:
			name = ''
		return name

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

		# Return empty list for users without posts
		if ele_post is None:
			return list()

		ele_post.click()
		posts: List[Post] = []

		pbar = tqdm(total=num)
		pbar.set_description("fetching")
		cur_key = None

		# Fetching all posts
		for _ in range(num):
			dict_post = {}
			post: Post = Post()

			# Fetching post detail
			try:
				check_next_post(cur_key)

				# Fetching datetime and url as key
				ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
				cur_key = ele_a_datetime.get_attribute("href")
				post.url = cur_key
				fetch_datetime(browser, post)
				fetch_imgs(browser, post)
				fetch_likes_plays(browser, post)
				fetch_likers(browser, post)
				fetch_caption(browser, post)
				fetch_comments(browser, post)

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

			# self.log(json.dumps(post, ensure_ascii=False))

			posts.append(post)

			pbar.update(1)
			right_arrow = browser.find_one("._65Bje")
			if right_arrow:
				right_arrow.click()

		pbar.close()
		if posts:
			posts.sort(key=lambda post: post.post_date, reverse=True)

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

		user_profile = Profile(username=username)

		q = [user_profile]
		visited = {username}

		while q.__len__() > 0 and depth >= 0:
			q_length = q.__len__()

			fetched_profiles = []
			for i in range(0, q_length):
				popped_user_profile = q.pop(0)
				user_profile = self.get_user_profile(popped_user_profile.username, follow_list_enabled=True)
				fetched_profiles.append(user_profile)
			#fetch above without followers, then sort, filter, then fetch followers
			#also filter private ones
			sorted(fetched_profiles, key=lambda p: p.n_followers,reverse=True)
			fetched_profiles = fetched_profiles[:5]

			for pp in fetched_profiles:
				follower_profiles = pp.followers
				if follower_profiles:
					for profile in follower_profiles:
						if profile.username not in visited:
							q.append(profile)
							visited.add(profile.username)

			depth = depth - 1

		return
