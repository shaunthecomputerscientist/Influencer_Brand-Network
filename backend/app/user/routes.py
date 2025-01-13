from flask import Blueprint, request, jsonify, current_app
from models.models import db, User, SocialLink, Notification
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from .utils import get_profile_data, search_influencers, get_profile_search_data, get_app_statistics
# from blueprints import user_bp
import json
from sqlalchemy.exc import SQLAlchemyError
from platformData.Instagram.fetcher import InstaloaderManager
from platformData.Youtube.fetcher import YouTubeDataFetcher
from services.Redis.cache_helpers import cache_data
from sqlalchemy import func

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard/<int:user_id>', methods=['GET'])
@jwt_required()
# @cache_data()
def user_dashboard(user_id):
    try:
        current_user = get_jwt_identity()
        role = current_user.get("role")  # Use .get() to avoid KeyError if key is missing
        
        # Fetch user profile data
        profile_data = get_profile_data(user_id=user_id)
        if not profile_data:
            return jsonify({"error": "Profile not found"}), 404
        
        # Logic to fetch the user's personalized dashboard based on role and user_id
        if role == 0:  # Influencer dashboard
            dashboard_data = get_app_statistics()
        elif role == 1:  # Influencer dashboard
            dashboard_data = f"Influencer Dashboard for User ID {user_id}"
        elif role == 2:  # Sponsor dashboard
            dashboard_data = f"Sponsor Dashboard for User ID {user_id}"
        else:
            return jsonify({"error": "Invalid role"}), 403

        return jsonify({"dashboard": dashboard_data, "profile_data": profile_data}), 200

    except Exception as e:
        print("ERRROEEEEEERRR",e)
        # Catch all other exceptions and return a generic error message
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Fetch user profile
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    print('user id:',user_id)
    try:
        profile_data=get_profile_data(user_id=user_id)
        print(profile_data)
        return jsonify({"message":'User Data Retrieved Successfully',"profile":profile_data}), 200
    
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Update user profile
@user_bp.route('/profile/update', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]
    data = request.form  # Changed to handle form data
    files = request.files  # Handle file uploads
    
    YOUTUBE_FETCHER = YouTubeDataFetcher(api_key=current_app.config['YOUTUBE_API_KEY'])
    INSTAGRAM_FETCHER = InstaloaderManager(accounts=current_app.config['INSTAGRAM_SCRAPING_ACCOUNTS'])


    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        role_map = {'influencer': 1, 'brand': 2}
        role = data.get('role')

        # Common fields
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.name = f"{data.get('first_name', user.name.split()[0])} {data.get('last_name', user.name.split()[1] if len(user.name.split()) > 1 else '')}"
        user.description = data.get('description', user.description)
        user.language = data.get('language', [])
        user.niche = data.get('niche', [])
        dob_str = data.get('dob', None)
        if dob_str:
            try:
                user.dob = datetime.strptime(dob_str+" 00:00:00", '%Y-%m-%d  %H:%M:%S')
            except ValueError:
                return jsonify({"message": "Invalid date format. Please use dd-mm-yyyy."}), 400

        # Handle profile image upload
        profile_image = files.get('profile_image')
        if profile_image:
            profile_image_upload_folder = current_app.config['PROFILE_IMAGE_UPLOAD_FOLDER']
            
            # Remove the old image if it exists
            if user.profile_image:
                old_image_path = os.path.join(current_app.root_path, user.profile_image)  # Correctly reference the path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save the new image
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(profile_image_upload_folder, filename)
            profile_image.save(profile_image_path)
            user.profile_image = os.path.join('static', 'uploads', 'profile_images', filename)

        # Role-based fields
        if role.lower() == 'influencer':
              # Store directly as JSON list
            user.gender = data.get('gender', user.gender)
          
              # Store directly as JSON list
            user.company_name = None
            user.industry = None
        elif role.lower() == 'brand':
            user.company_name = data.get('company_name', user.company_name)
            user.industry = data.get('industry', [])  # Store directly as JSON list
            # user.language = None
            user.gender = None
            # user.dob = None
            # user.niche = None

        db.session.commit()

        # Update social links if the role is influencer
        if role.lower() == 'influencer':
            platforms = json.loads(data.get('platforms', {}))
            print(platforms, '--------------------PLATFORMS--------------------------------------')
            for platform, link in platforms.items():

                existing_link = SocialLink.query.filter(
                    db.func.lower(SocialLink.platform) == platform.lower(),
                    SocialLink.user_id == user.id
                ).first()
                print(platform, link, user.id)
                print(existing_link)
                if existing_link:
                    existing_link.link = link
                else:
                    # SocialLink.query.filter_by(user_id=user.id).delete()
                    
                    if 'youtube' in platform.lower():
                        socialdata=YOUTUBE_FETCHER.fetch_limited_data(link)
                    elif 'instagram' in platform.lower():
                        socialdata=INSTAGRAM_FETCHER.run([link])[0]
                    else:
                        socialdata={}
                    
                    new_link = SocialLink(
                        user_id=user.id,
                        platform=platform,  # Convert platform to lowercase
                        link=link,
                        socialData=socialdata
                    )
                    print('Adding-----------------------',platform)
                    db.session.add(new_link)
                    db.session.commit()

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500










# Delete user profile
@user_bp.route('/profile/delete', methods=['DELETE'])
@jwt_required()
def delete_profile():
    current_user = get_jwt_identity()
    user_id = current_user["user_id"]

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500
    


@user_bp.route('/userProfile/<int:user_id>', methods=['GET'])
@jwt_required()
@cache_data(expiration=3)
def getUserProfileById(user_id):
    """
    Retrieve a user profile by user ID.
    """
    try:
        # Query the user by ID
        print(user_id)
        user = User.query.get(user_id)

        # If user is not found, return 404
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Use the helper function to process the user object
        user_profile = get_profile_data(user_id)

        # Return the processed profile data as a JSON response
        return jsonify(user_profile), 200

    except SQLAlchemyError as e:
        return jsonify({"message": str(e)}), 500
    


@user_bp.route('/influencers/search', methods=['POST'])
@jwt_required()
def search_influencers_route():
    filters = request.json  # Using request.json to get the data from the body
    # Extract filters from JSON payload as before
    print(filters)
    influencers = search_influencers(
        name=filters.get('name'),
        username=filters.get('username'),
        location=filters.get('location'),
        gender=filters.get('gender'),
        niches=filters.get('niches'),
        languages=filters.get('languages'),
        followers_min=filters.get('followers_min'),
        followers_max=filters.get('followers_max'),
        engagement_min=filters.get('engagement_min'),
        engagement_max=filters.get('engagement_max'),
        platforms=filters.get('platform'),
    )

    # Format the results using get_profile_data
    influencer_data = [get_profile_search_data(influencer.id) for influencer in influencers]
    return jsonify(influencer_data), 200


@user_bp.route('/influencers', methods=['GET'])
@jwt_required()
def initial_influencer_data():
    user = get_jwt_identity()

    if user['role']==1:
        user_id = user['user_id']
        user = User.query.filter_by(id = user_id).first()
        influencers = search_influencers(niches=user.niche, location=user.location)
        influencer_data = [get_profile_search_data(influencer.id) for influencer in influencers]
    return jsonify(influencer_data), 200



#notifications

@user_bp.route('/notification/<int:user_id>', methods=['GET'])
@jwt_required()
@cache_data(expiration=timedelta(minutes=10))
def get_recent_notifications(user_id):
    user = get_jwt_identity()
    receiver_id = user['user_id']
    ten_days_ago = datetime.utcnow() - timedelta(days=10)

    # Query notifications from the last 30 days for the specific user
    notifications = Notification.query.filter(
        Notification.receiver_id == receiver_id,
        Notification.created_at >= ten_days_ago
    ).order_by(Notification.created_at.desc()).all()

    # Serialize notifications
    notifications_list = [{
        'id': n.id,
        'category': n.category,
        'role': n.role,
        'sender_id': n.sender_id,
        'receiver_role': n.receiver_role,
        'receiver_id': n.receiver_id,
        'campaign_id': n.campaign_id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications]

    print(notifications_list, 'list')

    return jsonify(notifications_list), 200

@user_bp.route('/notification/read', methods=['PUT'])
@jwt_required()
def mark_notifications_as_read():
    user = get_jwt_identity()
    receiver_id = user['user_id']
    notification_ids = request.json.get('notification_ids', [])

    # Update specified notifications as read for the user
    updated_count = Notification.query.filter(
        Notification.receiver_id == receiver_id,
        Notification.id.in_(notification_ids),
        Notification.is_read == False
    ).update({"is_read": True}, synchronize_session='fetch')

    db.session.commit()

    return jsonify({'message': f'{updated_count} notifications marked as read.'}), 200
