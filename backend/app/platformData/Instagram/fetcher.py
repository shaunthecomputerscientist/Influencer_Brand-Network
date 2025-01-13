import instaloader
import os
import re
import random
import time
import json
import numpy as np

class InstaloaderManager:
    def __init__(self, accounts, session_flag=1):
        self.accounts = accounts
        self.loader = instaloader.Instaloader()
        self.logged_in_accounts = []
        self.session_flag = session_flag

    def _get_session_file(self, username):
        return f"{username}.session"

    def login(self, username, password):
        session_file = self._get_session_file(username)
        if self.session_flag == 1 and os.path.exists(session_file):
            try:
                self.loader.load_session_from_file(username)
                if username not in self.logged_in_accounts:
                    self.logged_in_accounts.append(username)
                print(f"Loaded session for {username}.")
            except Exception as e:
                print(f"Error loading session for {username}: {str(e)}")
        else:
            try:
                self.loader.login(username, password)
                self.loader.save_session_to_file(username)
                self.logged_in_accounts.append(username)
                print(f"Logged in and saved session for {username}.")
            except instaloader.exceptions.BadCredentialsException:
                print(f"Login failed for {username}. Check your credentials.")
            except Exception as e:
                print(f"An error occurred while logging in: {str(e)}")

    def choose_random_account(self):
        if not self.logged_in_accounts:
            raise Exception("No logged-in accounts available.")
        self.current_account = random.choice(self.logged_in_accounts)
        print(f"Selected account: {self.current_account}")

    def extract_shortcode(self, url):
        match = re.search(r'instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    def fetch_post_details_by_shortcode(self, post_url):
        if not hasattr(self, 'current_account'):
            for account in self.accounts:
                self.login(account['username'], account['password'])
            self.choose_random_account()

        shortcode = self.extract_shortcode(post_url)
        if not shortcode:
            print("Invalid URL format.")
            return None

        try:
            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            post_details = {
                "shortcode": post.shortcode,
                "comments": [comment.text for comment in post.get_comments()],
                "likes": post.likes,
                "views": post.video_view_count if post.is_video else 0,
                "caption": post.caption or "",
                "timestamp": post.date_utc.strftime("%Y-%m-%d %H:%M:%S")
            }
            return post_details

        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Post with shortcode '{shortcode}' not found.")
            return None
        except Exception as e:
            print(f"Error fetching post details: {str(e)}")
            return None

    def fetch_recent_posts_and_comments(self, target_username, num_posts=5):
        if not hasattr(self, 'current_account'):
            self.choose_random_account()

        try:
            profile = instaloader.Profile.from_username(self.loader.context, target_username)
            post_data = {}

            for post in profile.get_posts():
                if len(post_data) >= num_posts:
                    break

                post_data[post.shortcode] = {
                    "shortcode": post.shortcode,
                    "comments": [comment.text for comment in post.get_comments()],
                    "likes": post.likes,
                    "views": post.video_view_count if post.is_video else 0,
                    "caption": post.caption or "",
                    "timestamp": post.date.strftime("%Y-%m-%d %H:%M:%S")
                }

            return post_data

        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile '{target_username}' not found.")
            return {}
        except Exception as e:
            print(f"Error fetching posts for {target_username}: {str(e)}")
            return {}

    def run(self, target_usernames):
        for account in self.accounts:
            self.login(account['username'], account['password'])

        self.choose_random_account()
        extracted_usernames = self.extract_usernames(target_usernames)
        user_data = self.extract_user_data(extracted_usernames)
        for data in user_data:
            print(f"data: {json.dumps(data, indent=4)}")
        return user_data


        

    def extract_usernames(self, input_data):
        extracted_usernames = []
        for item in input_data:
            if "instagram.com" in item:
                match = re.search(r'instagram\.com/([^/?]+)', item)
                if match:
                    extracted_usernames.append(match.group(1))
            else:
                extracted_usernames.append(item)


        return extracted_usernames

    def extract_user_data(self, target_usernames):
        user_data_list = []
        for username in target_usernames:
            time.sleep(5)  # to avoid rate limiting
            data = self.fetch_user_data(username)
            if data:
                user_data_list.append(data)
        return user_data_list

    def fetch_user_data(self, username):
        if not hasattr(self, 'current_account'):
            self.choose_random_account()

        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            engagement_rate = self.calculate_normalized_engagement({'followers': profile.followers,
                'following': profile.followees,
                'media_count': profile.mediacount}) * 100
            return {
                'id': profile.userid,
                'username': profile.username,
                'followers': profile.followers,
                'following': profile.followees,
                'engagement': engagement_rate,
                'media_count': profile.mediacount,
                'bio': profile.biography,
                'image_link': profile.profile_pic_url,
                'is_private': profile.is_private,
                'is_verified': profile.is_verified
            }
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile '{username}' not found.")
            return {}
        except Exception as e:
            print(f"Error fetching data for {username}: {str(e)}")
            return e

    def normalize(self,value, min_value, max_value):
        # Avoid division by zero
        return (value - min_value) / (max_value - min_value) if max_value > min_value else 0

    def determine_dynamic_max(self, value, thresholds):
        """
        Determine dynamic max value based on input thresholds.
        thresholds: List of tuples in the form (threshold_value, max_value)
        """
        for threshold, max_value in thresholds:
            if value <= threshold:
                return max_value
        return thresholds[-1][1]  # Default to the largest max_value if above all thresholds

    def calculate_normalized_engagement(self,profile_data, 
                                        follower_min=100, following_min=0, media_count_min=0,
                                        follower_weight=0.5, following_weight=0.3, media_count_weight=0.2):
        
        # Set dynamic max values based on value thresholds
        follower_thresholds = [(1000, 1000),(10000, 10000),(100_000, 100_000), (10_000_000, 10_000_000), (1_000_000_000, 1_000_000_000), (10_000_000_000, 10_000_000_000)]
        following_thresholds = [(1000, 1000),(10000, 10000),(100_000, 100_000), (10_000_000, 10_000_000), (1_000_000_000, 1_000_000_000), (10_000_000_000, 10_000_000_000)]
        media_count_thresholds = [(1000, 1000),(10000, 10000),(100_000, 100_000), (10_000_000, 10_000_000), (1_000_000_000, 1_000_000_000), (10_000_000_000, 10_000_000_000)]

        # Determine max values based on thresholds
        follower_max = self.determine_dynamic_max(profile_data['followers'], follower_thresholds)
        following_max = self.determine_dynamic_max(profile_data['following'], following_thresholds)
        media_count_max = self.determine_dynamic_max(profile_data['media_count'], media_count_thresholds)

        # Normalize each metric
        followers_normalized = self.normalize(profile_data['followers'], follower_min, follower_max)
        following_normalized = self.normalize(profile_data['following'], following_min, following_max)
        media_count_normalized = self.normalize(profile_data['media_count'], media_count_min, media_count_max)
        
        # Combine normalized metrics with specified weights
        combined_score = (follower_weight * followers_normalized +
                        following_weight * following_normalized +
                        media_count_weight * media_count_normalized)
            
        # Apply sigmoid function for smoother scaling between 0 and 1
        # engagement_score = 1 / (1 + np.exp(-12 * (combined_score - 0.5)))  # Adjust sigmoid steepness if needed

        return combined_score