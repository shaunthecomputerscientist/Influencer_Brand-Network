from flask import Blueprint, request, jsonify, current_app
from models.models import db, User, SocialLink, AdminFlags, BlockedEntities, Campaign, InfluencerCampaign
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from sqlalchemy import and_, func, cast, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import joinedload


def get_profile_data(user_id):
    try:
        campaign_payments=[]
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        if user.role==1:

            socialLinks=SocialLink.query.filter_by(user_id=user.id).all()
            social_platforms = {}
            for social_link in socialLinks:
                # print(social_link)
                platform = social_link.platform.lower()
                # Each platform has a list of link data
                if platform not in social_platforms.keys():
                    social_platforms[platform.lower()] = {
                    "link": social_link.link,
                    "socialData": social_link.socialData  # Include any additional JSON data if present
                }
                    
            influencer_campaigns = InfluencerCampaign.query.filter_by(influencer_id=user_id).all()
            campaign_payments = [{'campaignId':ic.campaign_id, 'campaignName':ic.campaign.name,'status': ic.campaign.status, 'paymentAmount':ic.payment_amount} for ic in influencer_campaigns]
                    
            # print(social_platforms)

        
        adminflags = AdminFlags.query.filter_by(flagged_type='influencer',flagged_id=user_id).first()
        blockedStatus = BlockedEntities.query.filter_by(entity_type='influencer', entity_id=user_id).first()
        # print(adminflags,blockedStatus)

        # print('UPDATED PROFILE DATA -----------------------', user.language, user.location, user.dob)
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.name.split()[0] if user.name else None,
            "last_name": user.name.split()[1] if user.name and len(user.name.split()) > 1 else None,
            "role": 'admin' if user.role == 0 else 'influencer' if user.role == 1 else 'brand' if user.role == 2 else 'unknown',
            
            # Split language only if it exists, otherwise assign an empty list
            "language": user.language.split(",") if user.language else [],
            
            "gender": user.gender,
            "dob": user.dob,
            
            # Split niche only if it exists, otherwise assign an empty list
            "niche": user.niche.split(",") if user.niche else [],
            
            "company_name": user.company_name,
            
            # Split industry only if it exists, otherwise assign an empty list
            "industry": user.industry.split(",") if user.industry else [],
            
            # For platforms, handle social links safely
            "platforms": {social_link.platform: social_link.link for social_link in user.social_links} if user.social_links else {},
            
            "location": user.location,
            'phyllo_user_id': user.phyllo_user_id,
            'registered_on':user.registered_on,
            "profile_image": user.profile_image,
            "description" : user.description,
            "socialData" : social_platforms if user.role==1 else None,
            "flagCount" : adminflags.flag_count if adminflags else None,
            "flagFeedback" : adminflags.feedback if adminflags else None,
            "isBlocked" : blockedStatus.is_blocked if blockedStatus else None,
            "reason" : blockedStatus.reason if blockedStatus else None,
            'campaignPayments' : campaign_payments or []

        }
        # print(profile_data)
        # print('current profile details', profile_data)
        print(profile_data)
        return profile_data
    except Exception as e:
        print(e)
        return e

from sqlalchemy import asc, desc

def search_influencers(name=None, username=None, location=None, gender=None, niches=None, languages=None, 
                       followers_min=None, followers_max=None, engagement_min=None, engagement_max=None, 
                       platforms=None, order_by_field='name', order_direction='asc'):
    query = db.session.query(User).outerjoin(SocialLink).filter(User.role == 1)  # Only influencers

    # Name and Username filtering
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))

    # Location, Gender, and Language filtering
    if location:
        query = query.filter(User.location.ilike(f"%{location}%"))
    if gender:
        query = query.filter(User.gender == gender)
    if languages:
        query = query.filter(
            or_(
                User.language.ilike(f"%{lang}%") for lang in languages
            )
        )

    # Niche filtering if any niches are provided
    if niches:
        query = query.filter(or_(User.niche.ilike(f"%{niche}%") for niche in niches))

    # Social Link filtering based on platform and social metrics
    if platforms or followers_min is not None or followers_max is not None or engagement_min is not None or engagement_max is not None:
        platform_conditions = []

        if platforms:
            platform_conditions.append(or_(SocialLink.platform.ilike(f"%{platform}%") for platform in platforms))

        if followers_min is not None:
            platform_conditions.append(cast(SocialLink.socialData['followers'], db.Integer) >= followers_min)
        if followers_max is not None:
            platform_conditions.append(cast(SocialLink.socialData['followers'], db.Integer) <= followers_max)

        if engagement_min is not None:
            platform_conditions.append(cast(SocialLink.socialData['engagement'], db.Float) >= engagement_min)
        if engagement_max is not None:
            platform_conditions.append(cast(SocialLink.socialData['engagement'], db.Float) <= engagement_max)

        query = query.filter(and_(*platform_conditions))

    # sorting
    if order_by_field:
        column = getattr(User, order_by_field, None)
        if column:
            if order_direction == 'desc':
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))

    return query.all()


def get_profile_search_data(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        
        if user.role==1:

            socialLinks=SocialLink.query.filter_by(user_id=user.id).all()
            social_platforms = {}
            for social_link in socialLinks:
                # print(social_link)
                platform = social_link.platform.lower()
                # Each platform has a list of link data
                if platform not in social_platforms.keys():
                    social_platforms[platform.lower()] = {
                    "link": social_link.link,
                    "socialData": social_link.socialData  # Include any additional JSON data if present
                }
                    
            # print(social_platforms)

        profile_data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "location": user.location,
            "gender": user.gender,
            "niche": user.niche.split(",") if user.niche else [],
            "language": user.language.split(",") if user.language else [],
            "platforms": social_platforms,
            "socialData" : social_platforms if user.role==1 else None,
            "profile_image" : user.profile_image

        }

        return profile_data
    except Exception as e:
        return {"error": str(e)}
    

def get_app_statistics():
    """
    Fetches app statistics including user counts, campaign details, and flagged/blocked entities.
    Returns:
        JSON: Statistics of the application.
    """
    try:
        # Number of influencers (role 1)
        num_influencers = db.session.query(func.count(User.id)).filter(User.role == 1).scalar()

        # Number of brands/businesses (role 2)
        num_brands = db.session.query(func.count(User.id)).filter(User.role == 2).scalar()

        # Total number of campaigns
        num_campaigns = db.session.query(func.count(Campaign.id)).scalar()

        # Number of active campaigns
        num_active_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.status == 'active').scalar()

        # Number of blocked users
        num_blocked_users = db.session.query(func.count(BlockedEntities.id)).filter(BlockedEntities.is_blocked == True).scalar()

        # List of currently flagged users (flag_count > 0)
        flagged_users = db.session.query(AdminFlags.flagged_id).filter(AdminFlags.flag_count > 0).all()
        flagged_user_objects = [User.query.filter_by(id=flag.flagged_id).first() for flag in flagged_users]
        flagged_users = [(user.name, user.role, user.id) for user in flagged_user_objects]  # Extract IDs from query result

        # Additional statistics (optional)
        total_users = db.session.query(func.count(User.id)).scalar()
        num_social_links = db.session.query(func.count(SocialLink.id)).scalar()

        # Compile statistics into a dictionary
        statistics = {
            "num_influencers": num_influencers,
            "num_brands": num_brands,
            "num_campaigns": num_campaigns,
            "num_active_campaigns": num_active_campaigns,
            "num_blocked_users": num_blocked_users,
            "flagged_user_ids": flagged_users,
            "additional_statistics": {
                "total_users": total_users,
                "num_social_links": num_social_links
            }
        }
        print(statistics)

        # Return as JSON
        return statistics

    except Exception as e:
        # Handle exceptions and return an error response
        return e
