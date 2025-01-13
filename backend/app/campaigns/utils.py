import os,json,time,datetime
from models.models import User, InfluencerCampaign, TaskProgress, AdminFlags, BlockedEntities
from datetime import datetime

def get_campaign_data(campaign):
    try:
        sponsor = User.query.filter(User.id == campaign.sponsor_id).first()
        adminflags = AdminFlags.query.filter_by(flagged_type='flag-campaign', flagged_id=campaign.id).first()
        blockedStatus = BlockedEntities.query.filter_by(entity_type='flag-campaign', entity_id=campaign.id).first()

        trackingMethods = {
            'influencerSocials' : True if campaign.trackInfluencerSocials else False,
            'brandSocials' : True if campaign.trackBrandSocials else False,
            'utmLinks' : True if campaign.trackUtmLinks else False
        }


        active_tracking_methods = []

        # Iterate over the dictionary and append the keys with value True to the list
        for key, value in trackingMethods.items():
            if value:
                active_tracking_methods.append(key)

        influencers_data = []
        for influencer in campaign.influencers:
            # Get the first InfluencerCampaign for the current influencer
            influencer_campaign = InfluencerCampaign.query.filter_by(influencer_id=influencer.influencer.id, campaign_id=campaign.id).first()
            print(influencer_campaign)

            # If influencer_campaign exists, retrieve relevant data
            if influencer_campaign:
                # print(influencer_campaign.post_tracking_metric)
                influencers_data.append(
                    {
                        "influencer_id": influencer.influencer.id,
                        "influencer_name": influencer.influencer.name,  # Assuming there's a name field
                        "status": influencer_campaign.status,  # Use status from InfluencerCampaign
                        "payment_amount": influencer_campaign.payment_amount,
                        "participation_date": influencer_campaign.participation_date.strftime('%Y-%m-%d %H:%M:%S') if influencer_campaign.participation_date else None,
                        "influencer_feedback": influencer_campaign.influencer_feedback,
                        "requested": influencer_campaign.requested,
                        "chat_request": influencer_campaign.chat_request,
                        "profile_image": influencer.influencer.profile_image,  # Add profile image here
                        "taskProgress" : influencer_campaign.task_progress,
                        "postrackingMetric": influencer_campaign.post_tracking_metric
                    }
                )

        # print(influencers_data)




        campaign_data = {
            "id": campaign.id,
            "name": campaign.name,
            "description": campaign.description,
            "start_date": campaign.start_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format as string
            "end_date": campaign.end_date.strftime('%Y-%m-%d %H:%M:%S'),      # Format as string
            "budget": campaign.budget,
            "sponsor_id": campaign.sponsor_id,
            "visibility": campaign.visibility,
            "goals": campaign.goals,
            "niches": campaign.niches if campaign.niches else [],  # Split if exists
            "created_date": campaign.created_date.strftime('%Y-%m-%d %H:%M:%S') if campaign.created_date else None,  # Handle None
            "status": campaign.status,
            "company_name":sponsor.company_name,
            "company_logo": sponsor.profile_image,
            "trackingMethods" : active_tracking_methods,
            "brandSocialLink" : campaign.brand_social,
            "brandTarget" : campaign.brand_target,
            "brandCurrent" : campaign.brand_current,
            "jsonCredentials" : campaign.ga4_credentials_json,
            "propertyId" : campaign.ga4_property_id,
            "ga4_base_url" : campaign.ga4_base_url,
            "isAffiliate" : campaign.isAffiliate,
            "progress" : campaign.calculate_progress,
            "tasks" : campaign.tasks,
            "guidelines" : campaign.guidelines,
            "influencers" : influencers_data,
            "acceptedInfluencers" : len(campaign.accepted_influencers_count),
            "appliedInfluencers" : len(campaign.applied_influencers),
            "influencersPerCampaign" : 5,
            "goalProgress" : campaign.goal_progress,
            "flagCount" : adminflags.flag_count if adminflags else None,
            "flagFeedback" : adminflags.feedback if adminflags else None,
            "isBlocked" : blockedStatus.is_blocked if blockedStatus else None,
            "reason" : blockedStatus.reason if blockedStatus else None



        }
        return campaign_data
    except Exception as e:
        return str(e)
    

def get_campaign_task_data(campaign_id):
    try:
        # Query all relevant data with eager loading
        task_progress_entries = (TaskProgress.query
                                 .join(User, User.id == TaskProgress.influencer_id)
                                 .filter(TaskProgress.campaign_id == campaign_id)
                                 .all())

        # Organize by influencer for structured JSON
        influencers_data = {}
        
        for task in task_progress_entries:
            influencer_id = task.influencer_id
            
            # Initialize influencer entry if it doesn't exist
            if influencer_id not in influencers_data:
                influencers_data[influencer_id] = {
                    "influencer_id": influencer_id,
                    "influencer_name": task.influencer.name,
                    "tasks": []
                }
            
            # Append task data
            influencers_data[influencer_id]["tasks"].append({
                "task_id": task.task_id,
                "task_description": task.task_description,
                "status": task.status,
                "submitted_date": task.submitted_date.strftime('%Y-%m-%d %H:%M:%S') if task.submitted_date else None,
                "approved_date": task.approved_date.strftime('%Y-%m-%d %H:%M:%S') if task.approved_date else None,
                "feedback": task.feedback
            })
        
        # Convert to JSON-serializable structure
        task_data = {
            "campaign_id": campaign_id,
            "influencers": list(influencers_data.values())
        }
        
        return task_data
    except Exception as e:
        return {"error": str(e)}



def populate_campaign_fields(campaign, data, update=False):
    # Parse date strings into datetime objects
    if update:
        campaign.start_date = datetime.strptime(data.get('start_date', campaign.start_date.strftime('%Y-%m-%d')) + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
        campaign.end_date = datetime.strptime(data.get('end_date', campaign.end_date.strftime('%Y-%m-%d')) + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
    else:
        campaign.start_date = datetime.strptime(data.get('start_date', None) + ' 00:00:00',"%Y-%m-%d %H:%M:%S")
        campaign.end_date = datetime.strptime(data.get('end_date', None) + ' 00:00:00',"%Y-%m-%d %H:%M:%S")

    
    campaign.name = data.get('name', campaign.name)
    campaign.description = data.get('description', campaign.description)
    campaign.budget = data.get('budget', campaign.budget)
    campaign.visibility = data.get('visibility', campaign.visibility)
    campaign.goals = data.get('goals', campaign.goals)
    campaign.niches = data.get('niches', campaign.niches)
    campaign.platforms = data.get('platforms', campaign.platforms)
    campaign.tasks = data.get('tasks', campaign.tasks)
    campaign.guidelines = data.get('guidelines', campaign.guidelines)


    
    # Tracking options
    track_influencer_socials = 'influencerSocials' in data.get('trackingMethods', [])
    track_brand_socials = 'brandSocials' in data.get('trackingMethods', [])
    track_utm_links = 'utmLinks' in data.get('trackingMethods', [])
    
    campaign.trackInfluencerSocials = track_influencer_socials
    campaign.trackBrandSocials = track_brand_socials
    campaign.trackUtmLinks = track_utm_links
    campaign.brand_social = data.get('brandSocialLink', campaign.brand_social) if track_brand_socials else campaign.brand_social
    campaign.brand_target = data.get('brandTarget' , campaign.brand_target) if track_brand_socials else campaign.brand_target
    campaign.ga4_property_id = data.get('propertyId', campaign.ga4_property_id) if track_utm_links else campaign.ga4_property_id
    campaign.ga4_base_url = data.get('ga4_base_url',campaign.ga4_base_url) if track_utm_links else campaign.ga4_base_url
    campaign.ga4_credentials_json = data.get('jsonCredentials', campaign.ga4_credentials_json) if track_utm_links else campaign.ga4_credentials_json
    campaign.isAffiliate = data.get('isAffiliate', campaign.isAffiliate) if track_utm_links else campaign.isAffiliate
    # if not data.get('status', campaign.status):

    #     # Determine campaign status
    #     if campaign.start_date < datetime.utcnow() <= campaign.end_date:
    #         campaign.status = 'active'
    #     else:
    #         campaign.status = 'inactive'
    if data.get('status', campaign.status):
        campaign.status = data.get('status', campaign.status)




import uuid

def generate_unique_message_id(campaign_id, sender_id, timestamp):
    """
    Generate a unique ID for a chat message.

    Parameters:
    - campaign_id (int): ID of the campaign
    - sender_id (int): ID of the sender
    - timestamp (datetime): Timestamp of the message

    Returns:
    - str: A unique ID for the message
    """
    # Generate a unique identifier using UUID and combine it with other details
    return f"{campaign_id}-{sender_id}-{int(timestamp.timestamp())}-{uuid.uuid4().hex[:8]}"









def calculate_goal_progress(campaign):
        """
        Calculate the goal progress for the campaign.
        - Influencer progress (weighted 0.7)
        - Brand progress (weighted 0.5)
        """
        # Calculate influencer progress for accepted influencers
        accepted_influencers = [
            influencer for influencer in campaign.influencers if influencer.status == 'accepted'
        ]

        if not accepted_influencers:
            return 0.0  # No accepted influencers, goal progress is 0%

        influencer_progresses = []

        for influencer in accepted_influencers:
            influencer_progress = []
            platform_progress = []
            # Loop through each platform for the influencer
            if not influencer.post_tracking_metric:
                influencer.post_tracking_metric={}
            for platform, posts in influencer.post_tracking_metric.items():
                
                # print(influencer.post_tracking_metric)
                for post in posts:
                # Loop through each link (post) within a platform
                    for link, metrics in post.items():
                        if 'likes_obtained' in metrics['metrics'] and 'likes_target' in metrics['metrics']:
                            # Calculate like progress if likes data is available
                            like_progress = (int(metrics['metrics']['likes_obtained'])/ int(metrics['metrics']['likes_target'])) * 100
                            platform_progress.append(like_progress)
                        elif 'views_obtained' in metrics['metrics'] and 'views_target' in metrics['metrics']:
                            # Calculate view progress if views data is available
                            view_progress = (int(metrics['metrics']['views_obtained']) / int(metrics['metrics']['views_target'])) * 100
                            platform_progress.append(view_progress)

                # Calculate average progress for all posts in the platform
                if platform_progress:
                    print('platform progress', platform_progress)
                    influencer_progress.append(sum(platform_progress) / len(platform_progress))
                    print(influencer_progress)

            # Average across all platforms for this influencer
            if influencer_progress:
                influencer_goal_progress = sum(influencer_progress) / len(influencer_progress)
            else:
                influencer_goal_progress = 0  # If no progress, set to 0

            influencer_progresses.append(influencer_goal_progress)
            print(influencer_progresses)

        # Calculate the average influencer goal progress
        average_influencer_progress = sum(influencer_progresses) / len(influencer_progresses) if influencer_progresses else 0
        if average_influencer_progress>100:
            average_influencer_progress=100

        # Weight the influencer progress (0.7 weight)
        weighted_influencer_progress = (average_influencer_progress/100) * 0.7
        print(weighted_influencer_progress)

        # Calculate the brand progress
        brand_progress = (campaign.brand_current / campaign.brand_target) * 100 if campaign.brand_target else 0
        if brand_progress>100:
            brand_progress=100
        weighted_brand_progress = (brand_progress/100) * 0.3

        print(weighted_brand_progress)

        # Calculate the final goal progress for the campaign
        final_goal_progress = weighted_influencer_progress + weighted_brand_progress
        # print(final_goal_progress)

        return final_goal_progress