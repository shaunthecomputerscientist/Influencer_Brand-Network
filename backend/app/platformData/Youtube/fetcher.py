from googleapiclient.discovery import build
import re, math



class YouTubeDataFetcher:
    def __init__(self, api_key):
        """
        Initialize the YouTube API client and store the API key.
        :param api_key: Your YouTube API key.
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_channel_data(self, channel_username):
        """
        Fetch channel data like statistics and upload playlist.
        :param channel_username: The YouTube channel's username.
        :return: Channel data (if found) or None.
        """
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                forUsername=channel_username
            )
            response = request.execute()

            if 'items' not in response:
                print("Channel not found.")
                return None

            return response['items'][0]
        except Exception as e:
            print(f"Error fetching channel data: {str(e)}")
            return None

    def get_recent_videos(self, channel_data, max_results=10):
        """
        Fetch recent videos from the channel's uploads playlist.
        :param channel_data: The channel data dictionary.
        :param max_results: Maximum number of recent videos to retrieve.
        :return: List of video data (id, title, description).
        """
        try:
            uploads_playlist_id = channel_data['contentDetails']['relatedPlaylists']['uploads']
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            response = request.execute()

            video_data = [
                {
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description']
                }
                for item in response['items']
            ]
            return video_data
        except Exception as e:
            print(f"Error fetching recent videos: {str(e)}")
            return []

    def get_video_comments(self, video_id, max_results=100):
        """
        Fetch top-level comments from a video.
        :param video_id: The video ID to fetch comments for.
        :param max_results: Maximum number of comments to retrieve.
        :return: List of comments.
        """
        comments = []
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            )
            response = request.execute()

            comments = [item['snippet']['topLevelComment']['snippet']['textOriginal'] for item in response['items']]
        except Exception as e:
            print(f"Error fetching comments for video {video_id}: {str(e)}")

        return comments

    def get_video_id_from_query(self, query, max_results=1):
        """
        Search for a YouTube video by query and return its video ID.
        :param query: The search query (e.g., video title).
        :param max_results: Maximum number of results to return (default: 1).
        :return: List of video IDs.
        """
        try:
            request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=max_results
            )
            response = request.execute()

            video_ids = [item['id']['videoId'] for item in response['items']]
            return video_ids
        except Exception as e:
            print(f"Error searching video by query: {str(e)}")
            return []

    def get_video_id_from_link(self, link):
        """
        Extract the video ID from a YouTube URL.
        :param link: YouTube video link (e.g., https://youtu.be/79zE7E8k03c).
        :return: The video ID.
        """
        try:
            video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', link)
            if video_id:
                return video_id.group(1)
            else:
                print("Invalid YouTube link format.")
                return None
        except Exception as e:
            print(f"Error extracting video ID from link: {str(e)}")
            return None

    def fetch_video_details(self, video_id):
        """
        Fetch video metadata, statistics, and caption details for a given video ID.
        :param video_id: The video ID.
        :return: Dictionary with video details (metadata, statistics, captions).
        """
        try:
            video_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()

            if not video_response['items']:
                return f"Video with ID {video_id} not found."

            video_data = video_response['items'][0]
            snippet = video_data['snippet']
            statistics = video_data['statistics']


            # Extract relevant data
            details = {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'publish_date': snippet.get('publishedAt'),
                'category_id': snippet.get('categoryId'),
                'tags': snippet.get('tags', []),
                'thumbnails': snippet.get('thumbnails', {}),
                'views': statistics.get('viewCount'),
                'likes': statistics.get('likeCount'),
                'dislikes': statistics.get('dislikeCount', 'N/A'),
                'comments': statistics.get('commentCount')
            }

            # Fetch captions (if available)
            captions_response = self.youtube.captions().list(part="snippet", videoId=video_id).execute()
            details['captions'] = [
                {
                    'language': item['snippet']['language'],
                    'name': item['snippet']['name']
                }
                for item in captions_response.get('items', [])
            ]

            return details
        except Exception as e:
            print(f"Error fetching video details: {str(e)}")
            return None

    def fetch_limited_data(self, channel_username_or_url):
        """
        Fetch detailed channel data including channel ID, etag, snippet, statistics, status, topic details, and thumbnails.

        :param channel_username_or_url: The username or URL of the YouTube channel.
        :return: A dictionary with detailed channel data or a dictionary with None values in case of an error.
        """

        # Predefine the default response dictionary
        default_response = {
            'channel_id': None,
            'etag': None,
            'title': None,
            'description': None,
            'default_thumbnail': None,
            'statistics': {
                'followers': None,
                'view_count': None,
                'video_count': None,
                'engagement': None
            },
            'topic_details': {
                'topic_ids': None,
                'topic_categories': None
            },
            'status': {
                'privacy_status': None,
                'is_linked': None,
                'long_uploads_status': None,
                'made_for_kids': None
            }
        }

        # Check if the input is a URL
        if re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/', channel_username_or_url):
            # Attempt to extract the channel name from the URL
            match = re.search(r'(?:/c/|/channel/|/user/|/@)([^/?]+)', channel_username_or_url)
            if match:
                channel_username = match.group(1)
                print(channel_username,'------------------Channel USERNAME---------------------------------------------------')
            else:
                print("Invalid YouTube channel link format.")
                return default_response
        else:
            channel_username = channel_username_or_url  # Treat as a direct username

        try:
            # Attempt to fetch channel by handle/username
            request = self.youtube.channels().list(
                part='snippet,statistics,status,topicDetails,localizations',
                forHandle=channel_username
            )
            response = request.execute()

            # If no channel is found, fall back to searching by name
            if not response['items']:
                print(f"Channel with username '{channel_username}' not found. Falling back to search API.")
                search_request = self.youtube.search().list(
                    part="snippet",
                    q=channel_username,
                    type="channel",
                    maxResults=1
                )
                search_response = search_request.execute()

                # If no channel is found through search either, return default dict
                if not search_response['items']:
                    print(f"Channel with name '{channel_username}' not found in search results.")
                    return default_response

                # Extract channel ID from search response
                channel_id = search_response['items'][0]['id']['channelId']

                # Fetch channel details using the channel ID
                channel_request = self.youtube.channels().list(
                    part='snippet,statistics,status,topicDetails',
                    id=channel_id
                )
                response = channel_request.execute()

            # If channel data is found, extract all relevant fields
            channel_data = response['items'][0]
            channel_id = channel_data['id']
            etag = channel_data['etag']
            snippet = channel_data['snippet']
            statistics = channel_data.get('statistics', {})
            status = channel_data.get('status', {})
            topic_details = channel_data.get('topicDetails', {})
            thumbnails = snippet.get('thumbnails', {}).get('high', {}).get('url', None)

            # Prepare a response with detailed fields
            engagement_rate, _ = 0, 0
            if statistics.get('subscriberCount', None) and statistics.get('viewCount', None) and statistics.get('videoCount', None):
                engagement_rate, _ = self.engagement(
                    int(statistics['subscriberCount']),
                    int(statistics['viewCount']),
                    int(statistics['videoCount'])
                )

            detailed_data = {
                'channel_id': channel_id,
                'etag': etag,
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'default_thumbnail': thumbnails,
                'statistics': {
                    'followers': statistics.get('subscriberCount', None),
                    'view_count': statistics.get('viewCount', None),
                    'media_count': statistics.get('videoCount', None),
                    'engagement': engagement_rate
                },
                'topic_details': {
                    'topic_ids': topic_details.get('topicIds', []),
                    'topic_categories': topic_details.get('topicCategories', [])
                },
                'status': {
                    'privacy_status': status.get('privacyStatus', None),
                    'is_linked': status.get('isLinked', None),
                    'long_uploads_status': status.get('longUploadsStatus', None),
                    'made_for_kids': status.get('madeForKids', None)
                }
            }

            print(detailed_data)

            return detailed_data

        except Exception as e:
            # Return the predefined default dictionary in case of an error
            print(f"An error occurred: {e}")
            return default_response

        

    def engagement(self,subscriber_count, view_count, video_count, k=1, x0=1):
        if subscriber_count <= 0 or video_count <= 0:
            return 0  # Avoid division by zero

        # Calculate the ratio of views to subscribers
        view_subscriber_ratio = view_count / subscriber_count
        
        # Sigmoid function application
        sigmoid_engagement = 1 / (1 + math.exp(-k * (view_subscriber_ratio - x0)))
        
        # Scale to percentage and calculate per video
        engagement_rate = sigmoid_engagement * 100
        average_engagement_per_video = engagement_rate / video_count
        
        return engagement_rate, average_engagement_per_video




# youtube_data_fetcher =YouTubeDataFetcher(api_key = 'AIzaSyAOWVaQYixdqdn8EiKdF_l1hv9nSGbcj7c')
# l=[]
# usernames = ['TechnicalGuruji', 'MumbikerNikhil', 'ashishchanchlanivines', 'TheAmitBhadana', 'TechnicalGuruji', 'Bhuvan_Bam', 'round2hell', 'aayuandpihushow', 'iamharshbeniwal']
# for username in usernames:
#     # print(youtube_data_fetcher.fetch_limited_data(username))
#     l.append(youtube_data_fetcher.fetch_limited_data(username))
# # youtube_data_fetcher.fetch_limited_data('brightsideofmaths')