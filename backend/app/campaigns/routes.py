from flask import Blueprint, request, jsonify, current_app, Response, send_file
from models.models import Campaign, Chat, InfluencerCampaign,User, TaskProgress,Notification, db
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, decode_token
from .utils import get_campaign_data, populate_campaign_fields, generate_unique_message_id, calculate_goal_progress
from datetime import datetime, timedelta
from .GA4Manager.ga4analytics import generate_utm_links_wrapper, get_ga4_Report, aggregate_data
from sqlalchemy import and_, or_
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import func
from flask_socketio import SocketIO, emit, join_room, leave_room
# from main import socketio
from flask_sse import sse
from services.Redis.cache_helpers import cache_data, generate_cache_key
from operator import itemgetter
import json,os

campaigns_bp = Blueprint('campaigns', __name__)

# ------------------- Campaign Routes ----------------------

# Create a new campaign (Protected)
@campaigns_bp.route('/create', methods=['POST'])
@jwt_required()  # Protecting route
def create_campaign():
    data = request.json
    user_id = get_jwt_identity()  # Get the user ID from JWT token
    try:
        new_campaign = Campaign(
            sponsor_id=user_id['user_id'],  # Using the authenticated user as the sponsor
            created_date=datetime.utcnow()
        )
        print('before operation')
        populate_campaign_fields(new_campaign, data)
        
        db.session.add(new_campaign)
        db.session.commit()
        return jsonify({'message': 'Campaign created successfully!', 'newCampaign':get_campaign_data(new_campaign)}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


# Get all campaigns (Protected)
@campaigns_bp.route('/all/<int:user_id>', methods=['GET'])
@jwt_required()  # Protecting route
@cache_data()
def get_all_campaigns(user_id):
# Get user identity from JWT token
    user_identity = get_jwt_identity()
    user_role = user_identity["role"]
    user_id = user_identity["user_id"]
    # print('user Role',user_role)

    campaigns = []

    if user_role == 2:
        # Fetch campaigns created by the brand
        brand_campaigns = Campaign.query.filter_by(sponsor_id=user_id).limit(50).all()
        # print(brand_campaigns)
        
        # Fetch 50 random campaigns excluding the brand's own campaigns
        random_campaigns = (Campaign.query
                            .filter(Campaign.sponsor_id != user_id)
                            .order_by(func.random())
                            .limit(50)
                            .all())

        # Combine both lists, ensuring the brand's campaigns come first
        campaigns = brand_campaigns + random_campaigns

    elif user_role == 1 or user_role==0:
        # Fetch campaigns the influencer is associated with
        influencer_campaigns = (db.session.query(Campaign)
                                .join(InfluencerCampaign, Campaign.id == InfluencerCampaign.campaign_id)
                                .filter(InfluencerCampaign.influencer_id == user_id)
                                .all())

        # Fetch 50 random campaigns for influencers
        # random_campaigns = (Campaign.query
        #                     .order_by(func.random())
        #                     .limit(50)
        #                     .all()) with the random campaigns
        campaigns = influencer_campaigns

    else:
        # If role is not brand or influencer, return unauthorized
        return jsonify({"error": "Unauthorized access"}), 403

    # Format campaigns using get_campaign_data
    campaign_data = [get_campaign_data(campaign) for campaign in campaigns]

    # print(campaign_data)
    
    return jsonify({'campaigns':campaign_data}), 200


def get_campaign_filters(data):
    filters = []

    if 'brandName' in data and data['brandName']:
        filters.append(User.company_name.ilike(f"%{data['brandName'].strip()}%"))
    if 'campaignName' in data and data['campaignName']:
        filters.append(Campaign.name.ilike(f"%{data['campaignName'].strip()}%"))
    if 'budget' in data and data['budget']:
        filters.append(Campaign.budget <= int(data['budget']))
    if 'status' in data and data['status']:
        filters.append(Campaign.status == data['status'].strip())
    if 'startDate' in data and data['startDate']:
        filters.append(Campaign.start_date >= data['startDate'])
    if 'endDate' in data and data['endDate']:
        filters.append(Campaign.end_date <= data['endDate'])
    if 'niche' in data and data['niche']:
        # Use a JSON query to check if any of the niches match
        niche_filters = [Campaign.niches.like(f'%"{niche}"%') for niche in data['niche']]
        filters.append(or_(*niche_filters))
    filters.append(Campaign.visibility == 'public')  # Always include visibility filter

    return filters


@campaigns_bp.route('/search', methods=['POST'])
@jwt_required()
def search_campaigns():
    data = request.json
    print(data)

    # Generate filters
    filters = get_campaign_filters(data)
    print("Generated filters:", filters)

    # Fetch campaigns using `and_` to combine filters
    query = Campaign.query.join(User).filter(and_(*filters))
    print("Generated SQL Query:", str(query))

    campaigns = query.all()
    
    # Convert campaigns to JSON-compatible format
    campaign_data = [get_campaign_data(campaign) for campaign in campaigns]
    print("Matching Campaigns:", campaign_data)
    return jsonify({'campaigns': campaign_data})


# @campaigns_bp.route('/search', methods=['POST'])
# @jwt_required()
# def search_campaigns():
#     data = request.json
#     filters = []
#     print(data)

#     filters = get_campaign_filters(data)
#     # Fetch campaigns based on filters
#     campaigns = Campaign.query.join(User).filter(and_(*filters)).all()
#     # print(campaigns, filters, Campaign.query.filter(Campaign.budget<=123456))
#     campaign_data = [get_campaign_data(campaign) for campaign in campaigns]  # Assuming to_dict method exists
#     print(campaign_data)
#     return jsonify({'campaigns': campaign_data})


# Get campaign by ID (Protected)
@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()  # Protecting route
def get_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    print(campaign)
    if datetime.now() > campaign.end_date:
        campaign.status = 'inactive'  # Update status to 'inactive'
        db.session.commit()  # Commit the change to the database
    if campaign.status=='active':
        goal_progress = calculate_goal_progress(campaign)
        campaign.goal_progress = goal_progress
        db.session.commit()


    return jsonify(get_campaign_data(campaign)), 200


@campaigns_bp.route('brandCampaigns/all', methods=['GET'])
@jwt_required()  # Protecting route
def getFreshBrandcampaign():
    identity=get_jwt_identity()
    sponsor_id=identity['user_id']
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
    
    campaign_data = [get_campaign_data(campaign) for campaign in campaigns]

    # print(campaign_data)
    
    return jsonify({'campaigns':campaign_data}), 200

# Update campaign (Protected)
@campaigns_bp.route('/update/<int:campaign_id>', methods=['PUT'])
@jwt_required()  # Protecting route
def update_campaign(campaign_id):
    data = request.json
    campaign = Campaign.query.get_or_404(campaign_id)
    user_id = get_jwt_identity()  # Ensure that only the campaign's sponsor can update it

    # Check if the current user is the sponsor of the campaign
    if campaign.sponsor_id != user_id['user_id']:
        return jsonify({'error': 'Unauthorized access to update campaign'}), 403

    try:
        # Update campaign fields
        populate_campaign_fields(campaign, data)

        # Set campaign status based on start and end dates
        if campaign.start_date <= datetime.utcnow() <= campaign.end_date:
            campaign.status = 'active'
        else:
            campaign.status = 'inactive'
            campaign.progress = 1

        # Fetch all accepted influencers for the campaign
        accepted_influencers = InfluencerCampaign.query.filter_by(
            campaign_id=campaign_id, status='accepted'
        ).all()

        if len(accepted_influencers) > 0:
            # Delete existing TaskProgress records for the campaign
            TaskProgress.query.filter_by(campaign_id=campaign_id).delete()

            # Create TaskProgress entries for each accepted influencer
            campaign_tasks = campaign.tasks or []  # Get tasks from the campaign
            for request_entry in accepted_influencers:
                influencer_id = request_entry.influencer_id

                for task in campaign_tasks:
                    task_id = task.get("id")
                    task_description = task.get("description", "No description provided")
                    new_task_progress = TaskProgress(
                        influencer_id=influencer_id,
                        campaign_id=campaign_id,
                        task_id=task_id,
                        task_description=task_description,
                    )
                    db.session.add(new_task_progress)

        # Commit the changes
        db.session.commit()
        return jsonify({'message': 'Campaign updated successfully and tasks refreshed for accepted influencers!'}), 200
    except Exception as e:
        # Rollback if there’s an error
        db.session.rollback()
        return jsonify({'error': str(e)}), 400





# Delete campaign (Protected)
@campaigns_bp.route('/delete/<int:campaign_id>', methods=['DELETE'])
@jwt_required()  # Protecting route
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    user = get_jwt_identity()  # Ensure that only the campaign's sponsor can delete it

    # Check if the current user is the sponsor of the campaign
    if campaign.sponsor_id != user['user_id']:
        return jsonify({'error': 'Unauthorized access to delete campaign'}), 403
    
    try:

        cache_key = generate_cache_key(f"campaigns/all/{user['user_id']}")
        
        # Delete the campaign from the database
        db.session.delete(campaign)
        db.session.commit()

        # Invalidate the cache by deleting the cache key
        redis_client = current_app.config['REDIS_CLIENT']
        redis_client.delete(cache_key)
        return jsonify({'message': 'Campaign deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@campaigns_bp.route('/start/<int:campaign_id>',methods=['PUT'])
@jwt_required()
def startCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    user = get_jwt_identity()
    if campaign.sponsor_id != user['user_id']:
        return jsonify({'error': 'Unauthorized access to start campaign'}), 403
    try:
        campaign.status = 'active'
        campaign.progress = 0
        db.session.commit()
        return jsonify({'message': 'Campaign started successfully!', 'campaign': get_campaign_data(campaign=campaign)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@campaigns_bp.route('/end/<int:campaign_id>',methods=['PUT'])
@jwt_required()
def endCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    user = get_jwt_identity()
    if campaign.sponsor_id != user['user_id']:
        return jsonify({'error': 'Unauthorized access to end campaign'}), 403
    try:
        campaign.status = 'inactive'
        db.session.commit()
        goal_progress = calculate_goal_progress(campaign)
        campaign.goal_progress = goal_progress
        db.session.commit()
        return jsonify({'message': 'Campaign halted successfully!', 'campaign': get_campaign_data(campaign=campaign)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400



# fetch influencers who sent campaign requests to join ones associated with the campaign in some way.
@campaigns_bp.route('/<int:campaign_id>/requests', methods=['GET'])
@jwt_required()
def get_campaign_requests(campaign_id):
    user = get_jwt_identity()
    
    # Fetch all influencer campaign requests for the specified campaign
    campaign_requests = InfluencerCampaign.query.filter_by(campaign_id=campaign_id).all()

    if not campaign_requests:
        return jsonify({"message": "No requests found for this campaign."}), 404

    # Serialize the data to return
    requests_data = [
        {
            "id": request.id,
            "influencer_id": request.influencer_id,
            "campaign_id": request.campaign_id,
            "status": request.status,
            "payment_amount": request.payment_amount,
            "participation_date": request.participation_date,
            "influencer_feedback": request.influencer_feedback,
            "requested": request.requested,
            "chat_request": request.chat_request,
        }
        for request in campaign_requests
    ]

    return jsonify({"requests": requests_data}), 200


# join request for a campaign by influencer
@campaigns_bp.route('/<int:campaign_id>/join-request', methods=['POST'])
@jwt_required()
def request_to_join_campaign(campaign_id):
    influencer = get_jwt_identity()
    
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    if len(campaign.accepted_influencers_count) >= 5:
        return jsonify({'error': 'Maximum limit of 5 influencers reached for this campaign.'}), 400

    # Ensure the influencer hasn’t already requested or joined this campaign
    existing_request = InfluencerCampaign.query.filter_by(influencer_id=influencer['user_id'], campaign_id=campaign_id).first()
    if existing_request and existing_request.status in ['pending', 'accepted', 'rejected']:
        return jsonify({'error': 'Request already exists or you have joined this campaign'}), 400
    elif existing_request:
        # Update the existing request to 'pending' status if it was previously canceled or needs to be updated
        existing_request.status = 'pending'
        existing_request.influencer_id = influencer['user_id']
        existing_request.campaign_id = campaign_id
        existing_request.requested = True
        db.session.commit()

    elif not existing_request:
        try:
            new_request = InfluencerCampaign(
                influencer_id=influencer['user_id'],
                campaign_id=campaign_id,
                status='pending',
                requested=True
            )
            db.session.add(new_request)
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # Create a new notification for the campaign sponsor
    try:
        new_notification = Notification(
            category='campaign',
            role=1,  # Influencer sending the request
            sender_id=influencer['user_id'],
            receiver_role=2,  # Sponsor receiving the notification
            receiver_id=campaign.sponsor_id,
            campaign_id=campaign_id,
            message=f"{influencer['username']} has requested to join your campaign '{campaign.name}'",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(new_notification)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': 'Failed to create notification: ' + str(e)}), 500

    return jsonify({'message': 'Join request sent successfully and notification created!'}), 201



# campaigns respond to join requests

@campaigns_bp.route('/join-request/<int:influencer_id>/respond/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def respond_to_join_request(influencer_id, campaign_id):
    data = request.json
    user = get_jwt_identity()
    request_entry = InfluencerCampaign.query.filter_by(influencer_id=influencer_id, campaign_id=campaign_id).first()
    
    # Ensure the responder is the campaign sponsor
    if not request_entry or request_entry.campaign.sponsor_id != user['user_id']:
        return jsonify({'error': 'Unauthorized access to respond to join request'}), 403

    try:
        status = data.get('status')
        feedback = data.get('influencer_feedback', None)
        
        if status not in ['accepted', 'rejected', 'pending']:
            return jsonify({'error': 'Invalid status. Use "accepted", "rejected", or "pending".'}), 400

        # Update the join request status
        request_entry.status = status
        request_entry.influencer_feedback = feedback

        # Handle accepted status: assign tasks
        if status == 'accepted':
            # Retrieve campaign tasks from the campaign associated with the request
            campaign_tasks = request_entry.campaign.tasks or []

            # Check if TaskProgress entries already exist for the influencer and campaign
            existing_tasks = TaskProgress.query.filter_by(
                influencer_id=influencer_id,
                campaign_id=request_entry.campaign_id
            ).count()

            # If TaskProgress entries do not exist, create new entries for each campaign task
            if existing_tasks == 0:
                for task in campaign_tasks:
                    task_id = task.get("id")
                    task_description = task.get("description", "No description provided")
                    new_task_progress = TaskProgress(
                        influencer_id=influencer_id,
                        campaign_id=request_entry.campaign_id,
                        task_id=task_id,
                        task_description=task_description,
                    )
                    db.session.add(new_task_progress)

            # Set notification message for acceptance
            notification_message = f"Your request to join the campaign '{request_entry.campaign.name}' has been accepted."

        # Handle rejected status: delete tasks
        elif status == 'rejected':
            # Delete all TaskProgress entries related to this influencer and campaign
            TaskProgress.query.filter_by(
                influencer_id=influencer_id,
                campaign_id=request_entry.campaign_id
            ).delete()

            # Set notification message for rejection
            notification_message = f"Your request to join the campaign '{request_entry.campaign.name}' has been rejected."

        # Create a notification based on the status
        new_notification = Notification(
            category='campaign',
            role=2,  # Sponsor role
            sender_id=user['user_id'],
            receiver_role=1,  # Influencer role
            receiver_id=influencer_id,
            campaign_id=campaign_id,
            message=notification_message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(new_notification)

        db.session.commit()
        return jsonify({'message': f'Join request {status.lower()} successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    

@campaigns_bp.route('/<int:campaign_id>/chat/request', methods=['POST'])
@jwt_required()
def send_chat_request(campaign_id):
    user = get_jwt_identity()
    influencer_id = user['user_id']  # Assuming the user is an influencer

    # Check if the influencer is part of the campaign
    influencer_campaign = InfluencerCampaign.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()

    # If not present, create a new InfluencerCampaign object
    if not influencer_campaign:
        influencer_campaign = InfluencerCampaign(
            influencer_id=influencer_id,
            campaign_id=campaign_id,
            chat_request='pending'  # Indicate that a chat request is sent
        )
        db.session.add(influencer_campaign)
    else:
        # If present, update the chat_request status to 'pending'
        if influencer_campaign.chat_request != "pending":
            influencer_campaign.chat_request = "pending"  # Update the status
        else:
            return jsonify({'error': 'Chat request already sent or responded to.'}), 400

    # Retrieve the campaign and its sponsor information
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found.'}), 404
    
    sponsor_id = campaign.sponsor_id

    # Create a notification for the sponsor about the chat request
    notification_message = f"{user['username']} has requested to initiate a chat for the campaign '{campaign.name}'."
    new_notification = Notification(
        category='chat_request',
        role=1,  # Influencer role
        sender_id=influencer_id,
        receiver_role=2,  # Sponsor role
        receiver_id=sponsor_id,
        campaign_id=campaign_id,
        message=notification_message,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.session.add(new_notification)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': 'Chat request sent successfully!'}), 200


@campaigns_bp.route('/<int:campaign_id>/chat/request/<int:influencer_id>', methods=['POST'])
@jwt_required()
def update_chat_request(campaign_id, influencer_id):
    user = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)

    # Ensure only the sponsor can update the chat request status
    if user['user_id'] != campaign.sponsor_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    new_status = data.get('status')  # Expected values: 'accepted' or 'rejected'

    # Validate the new_status value
    if new_status not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status. Use "accepted" or "rejected".'}), 400

    # Update the chat_request field for the influencer in the InfluencerCampaign table
    influencer_campaign = InfluencerCampaign.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if not influencer_campaign:
        return jsonify({'error': 'Influencer not found for this campaign'}), 404

    # Update the chat request status
    influencer_campaign.chat_request = new_status

    # Create a notification for the influencer based on the new status
    notification_message = (
        f"Your chat request for the campaign '{campaign.name}' has been {new_status}."
    )
    new_notification = Notification(
        category='campaign',
        role=2,  # Sponsor role
        sender_id=user['user_id'],
        receiver_role=1,  # Influencer role
        receiver_id=influencer_id,
        campaign_id=campaign_id,
        message=notification_message,
        is_read=False,
        created_at=datetime.utcnow()
    )
    db.session.add(new_notification)

    # Commit the changes to the database
    db.session.commit()

    return jsonify({'message': f'Chat request {new_status} successfully!'}), 200



# campaign-influencer messages
@campaigns_bp.route('/<int:campaign_id>/chat/send-message', methods=['POST'])
@jwt_required()
def send_chat_message(campaign_id):
    user = get_jwt_identity()
    data = request.get_json()
    message_content = data.get('content')
    influencer_id = data.get('influencer_id')  # Retrieve influencer ID from the request data

    # Check if the campaign exists
    campaign = Campaign.query.get_or_404(campaign_id)

    # Determine sender and receiver IDs based on the user's role
    if user['user_id'] == campaign.sponsor_id:
        sender_id = campaign.sponsor_id
        if not influencer_id or not InfluencerCampaign.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first():
            return jsonify({'error': 'Invalid or unauthorized influencer for this campaign'}), 400
        receiver_id = influencer_id
    else:
        sender_id = user['user_id']
        if not InfluencerCampaign.query.filter_by(campaign_id=campaign_id, influencer_id=sender_id).first():
            return jsonify({'error': 'Unauthorized access to this campaign'}), 403
        receiver_id = campaign.sponsor_id

    # Generate a unique ID for the message
    timestamp = datetime.utcnow()
    message_id = generate_unique_message_id(campaign_id, sender_id, timestamp)

    # Check if a chat already exists for this sender and receiver
    existing_chat = Chat.query.filter_by(campaign_id=campaign_id, sender_id=sender_id, receiver_id=receiver_id).first()
    if existing_chat:
        # Append the new message to the existing chat's message list
        new_message_entry = {
            'id': message_id,
            'content': message_content,
            'timestamp': timestamp.isoformat(),
            'sender_type': 'sponsor' if sender_id == campaign.sponsor_id else 'influencer'
        }
        # existing_chat.message.append(new_message_entry)
        existing_chat.message = existing_chat.message + [new_message_entry]
        # print(existing_chat.message,type(existing_chat.message))
    else:
        # Create a new chat with the first message
        new_message_entry = {
            'id': message_id,
            'content': message_content,
            'timestamp': timestamp.isoformat(),
            'sender_type': 'sponsor' if sender_id == campaign.sponsor_id else 'influencer'
        }
        new_chat = Chat(
            campaign_id=campaign_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=[new_message_entry]  # Initialize with the first message
        )
        db.session.add(new_chat)

    db.session.commit()
    return jsonify({'message': 'Message sent successfully'}), 201


# fetching chat messages associted with an influencer and sponsor within a campaign
@campaigns_bp.route('/<int:campaign_id>/chat/messages', methods=['GET'])
@jwt_required()
def get_chat_messages(campaign_id):
    user = get_jwt_identity()
    
    # Fetch all chat rows for the given campaign and user
    chats = Chat.query.filter(
        Chat.campaign_id == campaign_id,
        db.or_(
            Chat.sender_id == user['user_id'],
            Chat.receiver_id == user['user_id']
        )
    ).all()

    if not chats:
        return jsonify({'error': 'No chat found for this user in the specified campaign'}), 404

    # Structure the messages for each chat entry
    structured_messages = []
    for chat in chats:
        structured_messages = structured_messages + chat.message

    # Sort all messages by timestamp
    sorted_messages = sorted(structured_messages, key=itemgetter('timestamp'))

    return jsonify({'messages': sorted_messages}), 200


def get_current_user():
    identity = get_jwt_identity()
    user_id = identity['user_id']
    role = identity['role']
    return user_id, role

# 1. Fetch Tasks - For Influencer or Campaign Owner
@campaigns_bp.route('/<int:campaign_id>/tasks', methods=['GET'])
@jwt_required()
def get_campaign_task_data(campaign_id):
    try:
        user_id, role = get_current_user()
        
        if role == 1:  # Influencer
            # Get only the tasks for this influencer in the campaign
            task_progress_entries = TaskProgress.query.filter_by(campaign_id=campaign_id, influencer_id=user_id).all()
        else:
            # Campaign owner or other authorized user sees all tasks for the campaign
            task_progress_entries = (TaskProgress.query
                                     .join(User, User.id == TaskProgress.influencer_id)
                                     .filter(TaskProgress.campaign_id == campaign_id)
                                     .all())
            
            print(task_progress_entries)

        # Organize by influencer for structured JSON response
        influencers_data = {}
        for task in task_progress_entries:
            influencer_id = task.influencer_id
            if influencer_id not in influencers_data:
                influencers_data[influencer_id] = {
                    "influencer_id": influencer_id,
                    "influencer_name": task.influencer.name,
                    "tasks": []
                }

            influencers_data[influencer_id]["tasks"].append({
                "task_id": task.task_id,
                "task_description": task.task_description,
                "status": task.status,
                "submitted_date": task.submitted_date.strftime('%Y-%m-%d %H:%M:%S') if task.submitted_date else None,
                "approved_date": task.approved_date.strftime('%Y-%m-%d %H:%M:%S') if task.approved_date else None,
                "feedback": task.feedback
            })

        task_data = {
            "campaign_id": campaign_id,
            "influencers": list(influencers_data.values())
        }

        print(task_data)
        return jsonify(task_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Mark Task as Completed - For Influencer
@campaigns_bp.route('/tasks/<int:task_id>/mark-completed/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def mark_task_as_completed(task_id, campaign_id):
    try:
        user_id, role = get_current_user()
        
        if role != 1:  # Only influencers can mark tasks as completed
            return jsonify({"error": "Only influencers can mark tasks as completed"}), 403

        task = TaskProgress.query.filter_by(campaign_id=campaign_id,task_id=task_id, influencer_id=user_id).first()
        if not task:
            return jsonify({"error": "Task not found or not associated with the influencer"}), 404

        task.status = 'pending'
        task.submitted_date = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Task marked as completed and submitted for approval"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Approve or Reject Task - For Campaign Owner
@campaigns_bp.route('<int:campaign_id>/tasks/<int:task_id>/approve-reject', methods=['POST'])
@jwt_required()
def approve_reject_task(campaign_id, task_id):
    try:
        user_id, role = get_current_user()
        print(request.json)
        action = request.json.get('status')
        feedback = request.json.get('feedback')
        influencer_id = request.json.get('influencerId')
        campaign = Campaign.query.get_or_404(campaign_id)

        # Only allow campaign owners (non-influencers) to approve/reject tasks
        if role == 1:
            return jsonify({"error": "Only campaign owners can approve or reject tasks"}), 403

        # Retrieve the specific task and verify authorization
        task = TaskProgress.query.filter_by(
            influencer_id=influencer_id,
            task_id=task_id,
            campaign_id=campaign_id
        ).first()
        
        if not task:
            return jsonify({"error": "Task not found or not authorized to approve/reject"}), 404

        # Update task status and feedback
        if action in ['accepted', 'rejected']:
            task.status = action
            if action == 'accepted':
                task.approved_date = datetime.utcnow()
            if feedback:
                task.feedback = feedback
        else:
            return jsonify({"error": "Invalid action"}), 400

        # Retrieve all tasks for this influencer and campaign
        tasks = TaskProgress.query.filter_by(influencer_id=influencer_id, campaign_id=campaign_id).all()
        total_tasks_count = len(tasks)

        # Calculate the count of accepted and rejected tasks
        accepted_tasks_count = sum(1 for t in tasks if t.status == 'accepted')

        # Update InfluencerCampaign task progress
        influencer_campaigns = InfluencerCampaign.query.filter_by(
            campaign_id=campaign_id,
            influencer_id=influencer_id
        ).first()
        progress_fraction = accepted_tasks_count/total_tasks_count
        if influencer_campaigns:
            influencer_campaigns.task_progress = progress_fraction
            influencer_campaigns.payment_amount = progress_fraction*campaign.budget if progress_fraction<0.7 else campaign.budget
        

        print(influencer_campaigns.task_progress)
        # Commit changes to the database
        db.session.commit()
        
        return jsonify({
            "message": f"Task has been {action}",
            "feedback": task.feedback,
            "task_progress": influencer_campaigns.task_progress if influencer_campaigns else "N/A"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/update/payment/<int:campaign_id>/<int:influencer_id>', methods=['PUT'])
@jwt_required()
def updatePayments(campaign_id, influencer_id):
    data = request.json
    paymentamount = data.get('payment_amount')
    influencer_campaign = InfluencerCampaign.query.filter_by(campaign_id=campaign_id,influencer_id=influencer_id).first()
    try:
        influencer_campaign.payment_amount = int(paymentamount)
        db.session.commit()
        return jsonify({'message':'amount updated for the influencer'}) , 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



#----------------------------------------------------------------------------------------------------------------------------#
#GA4 API ENDPOINTS

@campaigns_bp.route('/<int:campaign_id>/generate/links/<int:influencer_id>', methods=['GET'])
@jwt_required()
def getUtmLinks(campaign_id, influencer_id):
    try:
        utmLinks = generate_utm_links_wrapper(campaignId=campaign_id, influencerId=influencer_id)
        influencer_campaign = InfluencerCampaign.query.filter_by(campaign_id=campaign_id,influencer_id=influencer_id).first()
        influencer_campaign.utm_links = utmLinks
        db.session.commit()

        return jsonify({'utmLinks':utmLinks}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@campaigns_bp.route('/<int:campaign_id>/ga4DataApi', methods=['GET'])
@jwt_required()
@cache_data()
def getGa4Data(campaign_id):
    try:
        influencer_campaign_list = InfluencerCampaign.query.filter_by(campaign_id=campaign_id,status='accepted').all()
        influencer_ids = [influencer.influencer_id for influencer in influencer_campaign_list]
        df = get_ga4_Report(campaignId=campaign_id)
        aggregated_influencer_data, influencer_data, aggregated_external_data, external_data = aggregate_data(df,influencer_ids=influencer_ids)

        response = {
            "aggregated_influencer_data": aggregated_influencer_data.to_dict(orient="records"),
            "raw_influencer_data": influencer_data.to_dict(orient="records"),
            "aggregated_external_data": aggregated_external_data.to_dict(orient="records"),
            "raw_external_data": external_data.to_dict(orient="records"),
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#----------------------ASYNC JOB--------------------------------------------------#























# notification
@campaigns_bp.route('/<int:campaign_id>/influencers/<int:influencer_id>/requests', methods=['POST'])
@jwt_required()  # Ensure the request is authenticated
@cache_data()
def send_campaign_request_to_influencer(campaign_id, influencer_id):
    print(campaign_id, influencer_id)
    
    # Fetch campaign
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({"message": "Campaign not found"}), 404
    
    # Fetch influencer
    influencer = User.query.get(influencer_id)
    if not influencer:
        return jsonify({"message": "Influencer not found"}), 404

    # Check for an existing notification
    existing_notification = Notification.query.filter_by(
        category='campaign',
        role=2,  # Sponsor role
        sender_id=campaign.sponsor_id,
        receiver_role=1,  # Influencer role
        receiver_id=influencer_id,
        campaign_id=campaign_id
    ).first()
    
    # If a notification exists, check its timestamp
    if existing_notification:
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        if existing_notification.created_at >= two_days_ago:
            return jsonify({"message": "Request already exists and was sent within the last 2 days"}), 409
        else:
            # Update the timestamp of the existing notification
            existing_notification.created_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                "message": "Existing notification timestamp updated",
                "campaign_id": campaign_id,
                "influencer_id": influencer_id,
                "notification_id": existing_notification.id
            }), 200
    
    # Create a new notification if none exists
    notification_message = f"You have a new campaign request from {campaign.sponsor.company_name}."
    new_notification = Notification(
        category='campaign',
        role=2,  # Role of the sender (Sponsor)
        sender_id=campaign.sponsor_id,
        receiver_role=1,  # Role of the receiver (Influencer)
        receiver_id=influencer_id,
        campaign_id=campaign_id,
        message=notification_message,
        created_at=datetime.utcnow()
    )

    db.session.add(new_notification)
    db.session.commit()

    return jsonify({
        "message": "Request sent successfully to influencer",
        "campaign_id": campaign_id,
        "influencer_id": influencer_id,
        "notification_id": new_notification.id
    }), 201