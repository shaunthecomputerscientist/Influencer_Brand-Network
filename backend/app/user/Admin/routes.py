from flask import Blueprint, request, jsonify, current_app
from models.models import db, User, SocialLink, Notification, BlockedEntities, AdminFlags, Campaign
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from ..utils import get_profile_data, search_influencers, get_profile_search_data
# from blueprints import user_bp
import json
from sqlalchemy.exc import SQLAlchemyError
from platformData.Instagram.fetcher import InstaloaderManager
from platformData.Youtube.fetcher import YouTubeDataFetcher
from services.Redis.cache_helpers import cache_data

admin_bp = Blueprint('admin',__name__)


@admin_bp.route('/influencers/<int:influencer_id>/flags', methods=['POST'])
@jwt_required()
def increase_flag(influencer_id):
    try:
        # Get admin ID from JWT token
        admindata = get_jwt_identity()
        admin_id = admindata['user_id']

        # Get feedback from request data
        data = request.get_json()
        feedback = data.get('feedback', '')  # feedback should be a string

        # Fetch influencer
        influencer = User.query.get(influencer_id)
        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        # Check or create an AdminFlag entry
        admin_flag = AdminFlags.query.filter_by(
            flagged_id=influencer_id, flagged_type='influencer'
        ).first()

        if not admin_flag:
            admin_flag = AdminFlags(
                admin_id=admin_id,
                flagged_id=influencer_id,
                flagged_type='influencer',
                flag_count=0,
                feedback=''  # Initialize feedback as an empty string
            )
            db.session.add(admin_flag)

        # Increment the flag count
        admin_flag.flag_count += 1

        # Update feedback based on the flag count
        feedback_message = f"You have been flagged for the {admin_flag.flag_count} time for this reason: {feedback}"
        admin_flag.feedback = feedback_message  # Update feedback with the new message

        # Check if the influencer should be blocked
        blocked_entity = BlockedEntities.query.filter_by(
            entity_type='influencer', entity_id=influencer_id
        ).first()

        if admin_flag.flag_count >= 3:  # Replace `3` with your desired threshold
            if not blocked_entity or not blocked_entity.is_blocked:
                # Block influencer
                if not blocked_entity:
                    blocked_entity = BlockedEntities(
                        entity_type='influencer',
                        entity_id=influencer_id,
                        reason=f"Flag count exceeded threshold: {admin_flag.flag_count}",
                        is_blocked=True
                    )
                    db.session.add(blocked_entity)
                else:
                    blocked_entity.is_blocked = True
                    blocked_entity.reason = f"Flag count exceeded threshold: {admin_flag.flag_count}"
                    blocked_entity.updated_at = datetime.utcnow()

                # Send block notification
                notification_message = (
                    f"You have been flagged for the following reason: {feedback}. "
                    "Your account has been blocked due to excessive flags."
                )
                new_notification = Notification(
                    category='flag',
                    role=0,  # Admin role
                    sender_id=admin_id,
                    receiver_role=1,  # Influencer role
                    receiver_id=influencer_id,
                    message=notification_message,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_notification)
        else:
            # Send warning notification
            notification_message = f"You have been flagged for the following reason: {feedback}."
            new_notification = Notification(
                category='flag',
                role=0,  # Admin role
                sender_id=admin_id,
                receiver_role=1,  # Influencer role
                receiver_id=influencer_id,
                message=notification_message,
                created_at=datetime.utcnow()
            )
            db.session.add(new_notification)
        
        print(new_notification)
        db.session.commit()

        return jsonify({
            "message": "Flag added successfully",
            "flag_count": admin_flag.flag_count,
            "notification_id": new_notification.id
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@admin_bp.route('/influencers/<int:influencer_id>/flags', methods=['DELETE'])
@jwt_required()
def decrease_flag(influencer_id):
    try:
        # Get admin ID from JWT token
        admindata = get_jwt_identity()
        admin_id = admindata['user_id']

        # Fetch influencer
        influencer = User.query.get(influencer_id)
        if not influencer:
            return jsonify({"message": "Influencer not found"}), 404

        # Check for existing AdminFlag entry
        admin_flag = AdminFlags.query.filter_by(
            flagged_id=influencer_id, flagged_type='influencer'
        ).first()

        if not admin_flag or admin_flag.flag_count <= 0:
            return jsonify({"message": "No flags to remove for this influencer"}), 400

        # Decrease the flag count
        admin_flag.flag_count -= 1

        # Update feedback with the decreased flag count
        feedback_message = f"You have been flagged for the {admin_flag.flag_count} time for this reason: {admin_flag.feedback}"
        admin_flag.feedback = feedback_message  # Update feedback to reflect the new count

        # Check if influencer is currently blocked
        blocked_entity = BlockedEntities.query.filter_by(
            entity_type='influencer', entity_id=influencer_id
        ).first()

        if blocked_entity and blocked_entity.is_blocked and admin_flag.flag_count < 3:
            # Unblock influencer if flag count falls below threshold
            blocked_entity.is_blocked = False
            blocked_entity.reason = "Flag count dropped below threshold"
            blocked_entity.updated_at = datetime.utcnow()

            # Send unblock notification
            notification_message = (
                "A flag on your account has been removed by admin. Your account is now unblocked."
            )
            new_notification = Notification(
                category='flag',
                role=0,  # Admin role
                sender_id=admin_id,
                receiver_role=1,  # Influencer role
                receiver_id=influencer_id,
                message=notification_message,
                created_at=datetime.utcnow()
            )
            db.session.add(new_notification)
        else:
            # Send notification about flag removal
            notification_message = "A flag on your account has been removed by admin."
            new_notification = Notification(
                category='flag',
                role=0,  # Admin role
                sender_id=admin_id,
                receiver_role=1,  # Influencer role
                receiver_id=influencer_id,
                message=notification_message,
                created_at=datetime.utcnow()
            )
            db.session.add(new_notification)

        db.session.commit()

        return jsonify({
            "message": "Flag removed successfully",
            "flag_count": admin_flag.flag_count,
            "notification_id": new_notification.id
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500



@admin_bp.route('/campaigns/<int:campaign_id>/flags', methods=['POST'])
@jwt_required()
def increase_campaign_flag(campaign_id):
    try:
        # Get admin ID from JWT token
        admindata = get_jwt_identity()
        admin_id = admindata['user_id']

        # Get feedback from request data
        data = request.get_json()
        feedback = data.get('feedback', '')

        # Fetch campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404

        # Check or create an AdminFlag entry
        admin_flag = AdminFlags.query.filter_by(
            flagged_id=campaign_id, flagged_type='flag-campaign'
        ).first()

        if not admin_flag:
            admin_flag = AdminFlags(
                admin_id=admin_id,
                flagged_id=campaign_id,
                flagged_type='flag-campaign',
                flag_count=0,
                feedback=''  # Initialize feedback as a string, not a list
            )
            db.session.add(admin_flag)

        # Increment flag count and replace feedback
        admin_flag.flag_count += 1
        admin_flag.feedback = f"Your campaign has been flagged for {admin_flag.flag_count} time for this reason: {feedback}"

        # Check if the campaign should be blocked
        if admin_flag.flag_count >= 3:  # Replace `3` with your desired threshold
            # Add entry to BlockedEntities
            blocked_entity = BlockedEntities.query.filter_by(
                entity_type='flag-campaign', entity_id=campaign_id, is_blocked=False
            ).first()

            if not blocked_entity:
                blocked_entity = BlockedEntities(
                    entity_type='flag-campaign',
                    entity_id=campaign_id,
                    reason=f"Flag count exceeded threshold: {admin_flag.flag_count}",
                    is_blocked=True
                )
               
                db.session.add(blocked_entity)
            else:
                blocked_entity.is_blocked=True
                blocked_entity.reason=f"Flag count exceeded threshold: {admin_flag.flag_count}"
                blocked_entity.updated_at = datetime.utcnow()
                print("MARKING CAMPAIGN AS BLOCKED")
            

            db.session.commit()


            # Update campaign status to 'inactive'
            campaign.status = 'inactive'

        # Create a notification for the sponsor
        notification_message = f"Your campaign '{campaign.name}' has been flagged for the following reason: {feedback}."
        if admin_flag.flag_count >= 3:
            notification_message += f"Your campaign {campaign.name} has been blocked due to excessive flags."

        new_notification = Notification(
            category='flag-campaign',
            role=0,  # Admin role
            sender_id=admin_id,
            receiver_role=2,  # Sponsor role
            receiver_id=campaign.sponsor_id,
            campaign_id=campaign_id,
            message=notification_message,
            created_at=datetime.utcnow()
        )
        db.session.add(new_notification)

        db.session.commit()

        return jsonify({
            "message": "Flag added successfully",
            "flag_count": admin_flag.flag_count,
            "notification_id": new_notification.id
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@admin_bp.route('/campaigns/<int:campaign_id>/flags', methods=['DELETE'])
@jwt_required()
def decrease_campaign_flag(campaign_id):
    try:
        # Get admin ID from JWT token
        admindata = get_jwt_identity()
        admin_id = admindata['user_id']

        # Fetch campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({"message": "Campaign not found"}), 404

        # Check for existing AdminFlag entry
        admin_flag = AdminFlags.query.filter_by(
            flagged_id=campaign_id, flagged_type='flag-campaign'
        ).first()

        if not admin_flag or admin_flag.flag_count <= 0:
            return jsonify({"message": "No flags to remove for this campaign"}), 400

        # Decrease flag count and update feedback
        admin_flag.flag_count -= 1
        admin_flag.feedback = f"You have been flagged for the {admin_flag.flag_count} time for this reason: {admin_flag.feedback}"

        # Check if the campaign is currently blocked
        blocked_entity = BlockedEntities.query.filter_by(
            entity_type='flag-campaign', entity_id=campaign_id
        ).first()

        if blocked_entity and blocked_entity.is_blocked and admin_flag.flag_count < 3:
            # Unblock campaign if flag count falls below threshold
            blocked_entity.is_blocked = False
            blocked_entity.reason = "Flag count dropped below threshold"
            blocked_entity.updated_at = datetime.utcnow()

            # Send unblock notification
            notification_message = f"A flag on your campaign has been removed. Your campaign {campaign.name} is now unblocked."
            new_notification = Notification(
                category='flag-campaign',
                role=0,  # Admin role
                sender_id=admin_id,
                receiver_role=2,  # Sponsor role
                receiver_id=campaign.sponsor_id,
                campaign_id=campaign_id,
                message=notification_message,
                created_at=datetime.utcnow()
            )
            db.session.add(new_notification)
        else:
            # Send notification about flag removal
            notification_message = f"A flag on your campaign {campaign.name} has been removed."
            new_notification = Notification(
                category='flag-campaign',
                role=0,  # Admin role
                sender_id=admin_id,
                receiver_role=2,  # Sponsor role
                receiver_id=campaign.sponsor_id,
                message=notification_message,
                campaign_id=campaign_id,
                created_at=datetime.utcnow()
            )
            db.session.add(new_notification)

        db.session.commit()

        return jsonify({
            "message": "Flag removed successfully",
            "flag_count": admin_flag.flag_count,
            "notification_id": new_notification.id
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
