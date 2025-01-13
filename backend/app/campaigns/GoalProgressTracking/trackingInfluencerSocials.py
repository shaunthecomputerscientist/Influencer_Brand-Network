from flask import Blueprint, request, jsonify, current_app, Response
from models.models import Campaign, Chat, InfluencerCampaign,User, TaskProgress,Notification, db, SocialLink
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, decode_token
from ..utils import get_campaign_data, populate_campaign_fields, generate_unique_message_id
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import func
from flask_socketio import SocketIO, emit, join_room, leave_room
# from main import socketio
from flask_sse import sse
from services.Redis.cache_helpers import cache_data, generate_cache_key
from operator import itemgetter
from platformData.Instagram.fetcher import InstaloaderManager
from platformData.Youtube.fetcher import YouTubeDataFetcher
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified



campaigns_tracking_bp = Blueprint('campaign/tracking', __name__)

@campaigns_tracking_bp.route("/<int:campaign_id>/influencer/post-media", methods=["POST"])
@jwt_required()
def create_post_metrics(campaign_id):
    try:
        # Parse incoming data
        data = request.json
        user = get_jwt_identity()
        influencer_id = user['user_id']
        posts = data.get("platformLinks", [])  # List of {'platform': 'url'}

        YOUTUBE_FETCHER = YouTubeDataFetcher(api_key=current_app.config['YOUTUBE_API_KEY'])
        INSTAGRAM_FETCHER = InstaloaderManager(accounts=current_app.config['INSTAGRAM_SCRAPING_ACCOUNTS'])

        # Validate required fields
        if not influencer_id or not campaign_id or not posts:
            return jsonify({"error": "Missing required fields"}), 400

        # Fetch the InfluencerCampaign instance
        campaign_entry = db.session.query(InfluencerCampaign).filter_by(
            influencer_id=influencer_id,
            campaign_id=campaign_id
        ).first()

        if not campaign_entry:
            return jsonify({"error": "InfluencerCampaign not found"}), 404

        # Initialize metrics
        metrics = campaign_entry.post_tracking_metric or {}

        # Supported platforms
        supported_platforms = current_app.config['PLATFORMS']

        # Process each post
        for post in posts:
            platform = post.get("platform")
            url = (post.get("url")).strip()

            if platform not in supported_platforms:
                return jsonify({"error": f"Platform '{platform}' is not supported"}), 400
            if platform.lower() not in metrics.keys():
                metrics[platform.lower()] = []

            # Fetch platform-specific metrics and add to the JSON structure
            if platform.lower() == "instagram":
                instagram_metrics = INSTAGRAM_FETCHER.fetch_post_details_by_shortcode(url)
                new_metrics = decide_instagram_metrics(instagram_metrics, influencer_id, platform)

                # Check if the URL exists in the platform's metrics
                existing_entry = next((element for element in metrics[platform.lower()] if url in element), None)

                if not existing_entry:
                    # Add new entry if URL is not found
                    metrics[platform.lower()].append({
                        url: {
                            "data": instagram_metrics,
                            "metrics": new_metrics
                        }
                    })
                else:
                    # Update existing entry
                    existing_entry[url]["data"] = instagram_metrics
                    existing_metrics = existing_entry[url]["metrics"]

                    # Update obtained likes or views but keep target values unchanged
                    if "likes_obtained" in new_metrics:
                        existing_metrics["likes_obtained"] = new_metrics["likes_obtained"]
                    if "views_obtained" in new_metrics:
                        existing_metrics["views_obtained"] = new_metrics["views_obtained"]

            elif platform.lower() == "youtube":
                video_id = YOUTUBE_FETCHER.get_video_id_from_link(url)
                youtube_metrics = YOUTUBE_FETCHER.fetch_video_details(video_id)

                # Check if the URL exists in the platform's metrics
                existing_entry = next((element for element in metrics[platform.lower()] if url in element), None)

                if not existing_entry:
                    # Add new entry if URL is not found
                    metrics[platform.lower()].append({
                        url: {
                            "data": youtube_metrics,
                            "metrics": {
                                "views_obtained": youtube_metrics.get("views"),
                                "views_target": calculate_target_views(influencer_id, platform)
                            }
                        }
                    })
                else:
                    # Update existing entry
                    existing_entry[url]["data"] = youtube_metrics
                    existing_metrics = existing_entry[url]["metrics"]

                    # Update obtained views but keep target views unchanged
                    existing_metrics["views_obtained"] = youtube_metrics.get("views")

        # Update the InfluencerCampaign entry
        campaign_entry.post_tracking_metric = metrics
        flag_modified(campaign_entry, "post_tracking_metric")
        print(campaign_entry.post_tracking_metric)
        db.session.commit()

        return jsonify({"message": "Post metrics updated successfully", "metrics": metrics}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        current_app.logger.error(f"Error in update_post_metrics: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def calculate_target_views(influencer_id, platform):
    platform_lower = platform.lower()
    social_link = SocialLink.query.filter(
        SocialLink.user_id == influencer_id,
        func.lower(SocialLink.platform) == platform_lower
    ).first()
    print(social_link.socialData.keys(),'-------------------------------------------------------------------------------------')
    if 'statistics' in social_link.socialData.keys():
        views = int(2 * social_link.socialData['statistics']['followers'])
        targetValue = views +  views * int(social_link.socialData['statistics']['engagement']//100)
    else:
        views = int(2 * social_link.socialData['followers'])
        targetValue = views +  views * int(social_link.socialData['engagement']//100)
    return targetValue

def calculate_target_likes(influencer_id, platform):
    platform_lower = platform.lower()
    social_link = SocialLink.query.filter(
        SocialLink.user_id == influencer_id,
        func.lower(SocialLink.platform) == platform_lower
    ).first()
    print(social_link.socialData)
    if 'statistics' in social_link.socialData.keys():
        print('hello')
        likes = int(0.5 * social_link.socialData['statistics']['followers'])
        targetValue = likes + int(likes * (social_link.socialData['statistics']['engagement']/100))
    else:

        likes = int(0.5 * social_link.socialData['followers'])
        targetValue = likes + int(likes * (social_link.socialData['engagement']/100))
    # print('--------------------------------------------------------',targetValue)
    return targetValue
def decide_instagram_metrics(postData, influencerId, platform):
    views = postData['views']
    print(type(views),views)
    likes = postData['likes']
    if views==0:
        return {"likes_obtained": likes, 'likes_target':calculate_target_likes(influencer_id=influencerId,platform=platform)}
    else:
        return {"views_obtained": postData["views"],
                "views_target": calculate_target_views(influencerId, platform)}
    

@campaigns_tracking_bp.route("/<int:campaign_id>/updatepostmetrics", methods=["POST"])
@jwt_required()
def update_post_metrics(campaign_id):
    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"error": "Campaign not found"}), 404

        # Get influencer campaigns associated with the campaign
        influencer_campaigns = InfluencerCampaign.query.filter_by(
            campaign_id=campaign_id, status="accepted"
        ).all()

        if not influencer_campaigns:
            return jsonify({"error": "No influencers associated with this campaign"}), 404

        # Initialize fetchers
        YOUTUBE_FETCHER = YouTubeDataFetcher(api_key=current_app.config['YOUTUBE_API_KEY'])
        INSTAGRAM_FETCHER = InstaloaderManager(accounts=current_app.config['INSTAGRAM_SCRAPING_ACCOUNTS'])

        def determine_platform(url):
            """Helper function to determine the platform from the URL."""
            if "youtube.com" in url or "youtu.be" in url:
                return "youtube"
            elif "instagram.com" in url:
                return "instagram"
            return None

        def update_post_data(platform, url, metrics):
            """Helper function to fetch and update post data for a specific platform and URL."""
            if platform == "instagram":
                instagram_metrics = INSTAGRAM_FETCHER.fetch_post_details_by_shortcode(url)
                if not instagram_metrics:
                    return

                existing_entry = next((item for item in metrics if url in item), None)
                if existing_entry:
                    existing_entry[url]["data"] = instagram_metrics
                    if 'likes_obtained' in existing_entry[url]["metrics"]:

                        existing_entry[url]["metrics"]["likes_obtained"] = instagram_metrics.get("likes")

                    else:
                        existing_entry[url]["metrics"]["views_obtained"] = instagram_metrics.get("views", 0)

            elif platform == "youtube":
                video_id = YOUTUBE_FETCHER.get_video_id_from_link(url)
                youtube_metrics = YOUTUBE_FETCHER.fetch_video_details(video_id)
                if not youtube_metrics:
                    return

                existing_entry = next((item for item in metrics if url in item), None)
                if existing_entry:
                    existing_entry[url]["data"] = youtube_metrics
                    existing_entry[url]["metrics"]["views_obtained"] = youtube_metrics.get("views")

        # Iterate over each influencer campaign
        for influencer_campaign in influencer_campaigns:
            metrics = influencer_campaign.post_tracking_metric or {}

            for platform, posts in metrics.items():
                for post_entry in posts:
                    for url in post_entry:
                        platform = determine_platform(url)
                        if platform:
                            update_post_data(platform, url, posts)

            # Update influencer campaign in the database
            influencer_campaign.post_tracking_metric = metrics
            flag_modified(influencer_campaign, "post_tracking_metric")
            db.session.commit()

        return jsonify({"message": "Post metrics updated successfully"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        current_app.logger.error(f"Error in update_post_metrics: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def determine_platform(url):
        """Helper function to determine the platform from the URL."""
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube"
        elif "instagram.com" in url:
            return "instagram"
        return None




@campaigns_tracking_bp.route('/<int:campaign_id>/brandSocials/metric', methods=['GET'])
@jwt_required()
def get_brand_socials_metric(campaign_id):
    YOUTUBE_FETCHER = YouTubeDataFetcher(api_key=current_app.config['YOUTUBE_API_KEY'])
    INSTAGRAM_FETCHER = InstaloaderManager(accounts=current_app.config['INSTAGRAM_SCRAPING_ACCOUNTS'])


    try:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"error": "Campaign not found"}), 404
        
        platform = determine_platform(campaign.brand_social)

        if platform == 'instagram':
            instagram_metrics = INSTAGRAM_FETCHER.run([campaign.brand_social])[0]
            followers = instagram_metrics.get('followers',0)
            metadata = instagram_metrics

        elif platform == 'youtube':
            youtube_metrics = YOUTUBE_FETCHER.fetch_limited_data(campaign.brand_social)
            followers = youtube_metrics['statistics']['followers']
            metadata = youtube_metrics['statistics']

        campaign.brand_current = followers
        db.session.commit()

        return jsonify({'message':'brandSocials metric retrieved successfully', 'followers':followers, 'metadata':metadata}), 200


        
        

    except Exception as e:
        current_app.logger.error(f"Error in update_post_metrics: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500






@campaigns_tracking_bp.route("/<int:campaign_id>/influencer/delete-post-tracking", methods=["DELETE"])
@jwt_required()
def delete_post_tracking(campaign_id):
    """
    Deletes an entry from the post_tracking_metric for a given influencer, campaign, link, and platform.
    
    Request Payload:
    - influencer_id: The ID of the influencer
    - campaign_id: The ID of the campaign
    - link: The URL/link to be deleted
    
    - platform: The platform associated with the link (e.g., 'youtube', 'instagram')

    Returns:
    - 200: Success message if the entry is removed
    - 400: Error message if something goes wrong
    """
    try:
        # Parse request data
        data = request.json
        influencer = get_jwt_identity()
        influencer_id = influencer['user_id']
        link = data.get('link')
        platform = data.get('platform', '').lower()

        if not influencer_id or not campaign_id or not link or not platform:
            return jsonify({"error": "Missing required fields: influencer_id, campaign_id, link, platform"}), 400

        # Fetch the InfluencerCampaign record
        influencer_campaign = InfluencerCampaign.query.filter_by(
            campaign_id=campaign_id,
            influencer_id=influencer_id
        ).first()

        if not influencer_campaign:
            return jsonify({"error": "InfluencerCampaign not found"}), 404

        # Get the post_tracking_metric and ensure it's a dictionary
        post_tracking_metric = influencer_campaign.post_tracking_metric or {}

        if platform not in post_tracking_metric:
            return jsonify({"error": f"Platform '{platform}' not found in post_tracking_metric"}), 404

        # Find and remove the entry by link
        updated_metrics = [
            entry for entry in post_tracking_metric[platform]
            if link not in entry
        ]
        print(len(updated_metrics))

        if len(updated_metrics) == len(post_tracking_metric[platform]):
            return jsonify({"error": f"Link '{link}' not found under platform '{platform}'"}), 404

        # Update the metrics in the database
        post_tracking_metric[platform] = updated_metrics
        flag_modified(influencer_campaign, "post_tracking_metric")
        influencer_campaign.post_tracking_metric = post_tracking_metric
        db.session.commit()

        return jsonify({"message": "Entry successfully deleted", "updated_metrics": post_tracking_metric}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500







# @campaigns_tracking_bp.route('/cccR',methods=['GET'])