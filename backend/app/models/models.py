from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy import Text
from sqlalchemy import PrimaryKeyConstraint, Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    # Common fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)  # Increased to 255
    password = db.Column(db.String(255), nullable=False)  # Increased to 255
    role = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)  # Increased to 255
    email = db.Column(db.String(255), unique=True, nullable=False)  # Increased to 255
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(255), nullable=True)  # Increased to 255
    profile_image = db.Column(db.String(512), nullable=True)  # Increased to 512
    description = db.Column(db.Text, nullable=True)  # Changed to Text for longer content
    niche = db.Column(db.JSON, nullable=True)  # JSON, compatible with SQLite and PostgreSQL
    language = db.Column(db.JSON, nullable=True)  # JSON, compatible with SQLite and PostgreSQL
    dob = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Influencer-specific fields
    gender = db.Column(db.String(20), nullable=True, default=None)  # Increased to 20
    phyllo_user_id = db.Column(db.String(255), unique=True, nullable=True)  # Increased to 255

    # Sponsor-specific fields
    company_name = db.Column(db.String(255), nullable=True)  # Increased to 255
    industry = db.Column(db.JSON, nullable=True)  # JSON, compatible with SQLite and PostgreSQL

    # Relationships
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)
    influencer_campaigns = db.relationship('InfluencerCampaign', back_populates='influencer', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"



class SocialLink(db.Model):
    __tablename__ = 'social_link'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(100), nullable=False)  # Name of the platform (e.g., Instagram, YouTube)
    link = db.Column(db.String(255), nullable=False)  # The social media link
    socialData = db.Column(JSON, nullable=False)

    user = db.relationship('User', backref=db.backref('social_links', lazy=True))

    def __repr__(self):
        return f"<SocialLink {self.platform} - {self.link}>"


class Campaign(db.Model):
    __tablename__ = 'campaign'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)  # Increased to 255
    description = db.Column(db.Text, nullable=True)  # Changed to Text for longer content
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    niches = db.Column(db.JSON, nullable=False)  # JSON, compatible with SQLite and PostgreSQL
    platforms = db.Column(db.JSON, nullable=False)  # JSON, compatible with SQLite and PostgreSQL
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(20), nullable=False)  # Increased to 20
    goals = db.Column(db.JSON, nullable=False)  # JSON, compatible with SQLite and PostgreSQL
    tasks = db.Column(db.JSON, nullable=True)  # JSON, compatible with SQLite and PostgreSQL
    guidelines = db.Column(db.Text, nullable=True)  # Changed to Text for longer content
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='inactive')  # Increased to 20

    # GA4 tracking details
    ga4_property_id = db.Column(db.String(255), nullable=True)  # Increased to 255
    ga4_credentials_json = db.Column(db.JSON, nullable=True)  # JSON, compatible with SQLite and PostgreSQL
    ga4_base_url = db.Column(db.String(512), nullable=True)  # Increased to 512

    # Tracking methods
    trackInfluencerSocials = db.Column(db.Boolean, default=False)
    trackUtmLinks = db.Column(db.Boolean, default=False)
    trackBrandSocials = db.Column(db.Boolean, default=False)
    isAffiliate = db.Column(db.Boolean, default=False)
    influencers_per_campaign = db.Column(db.Integer, default=10)

    brand_social = db.Column(db.String(255), nullable=True)  # Increased to 255
    brand_target = db.Column(db.Integer, default=10000)
    brand_current = db.Column(db.Integer, default=0)

    # Progress
    goal_progress = db.Column(db.Float, default=0.0)

    # Relationships
    influencers = db.relationship('InfluencerCampaign', back_populates='campaign', lazy=True)

    def __repr__(self):
        return f"<Campaign {self.name}>"

    @property
    def affiliate_enabled(self):
        return self.trackUtmLinks and self.isAffiliate

    @property
    def accepted_influencers_count(self):
        return [influencer for influencer in self.influencers if influencer.status == 'accepted']

    @property
    def applied_influencers(self):
        return [influencer for influencer in self.influencers if influencer.status in ['pending', 'accepted', 'rejected']]

    @property
    def calculate_progress(self):
        accepted_influencers = [
            influencer for influencer in self.influencers if influencer.status == 'accepted'
        ]
        if not accepted_influencers:
            return 0.0

        influencer_progress = [influencer.task_progress for influencer in accepted_influencers]
        avg_task_progress = sum(influencer_progress) / len(influencer_progress)
        self.progress = 0.5 * (avg_task_progress + self.goal_progress)
        return self.progress

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(JSON, nullable=True, default=[])
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_type = db.Column(db.String(255))  # Optional to specify if needed

    # Relationships
    campaign = db.relationship('Campaign', backref=db.backref('chats', lazy=True))
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref=db.backref('received_messages', lazy=True))

    def __repr__(self):
        return f"<Chat CampaignID={self.campaign_id}, SenderID={self.sender_id}, ReceiverID={self.receiver_id}>"
    



# Update InfluencerCampaign model with request status
class InfluencerCampaign(db.Model):
    __tablename__ = 'influencer_campaigns'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    status = db.Column(db.String(255), default="null")  # Track request status: Pending, Accepted, Rejected for joining campaign
    payment_amount = db.Column(db.Float, nullable=True)
    participation_date = db.Column(db.DateTime)
    influencer_feedback = db.Column(db.Text, nullable=True)
    requested = db.Column(db.Boolean, nullable=False, default=True)
    task_progress = db.Column(db.Float, default=0.0)  # Progress of task as a percentage

    utm_links = db.Column(JSON, nullable=True, default=[])  # Store generated UTM links as a JSON object

    post_tracking_metric = db.Column(JSON, nullable=True, default={})

    chat_request = db.Column(db.String(20), default="null")  # Status: 'Pending', 'Accepted', 'Rejected' for chatting with sponsor


    # Relationships
    campaign = db.relationship('Campaign', back_populates='influencers')
    influencer = db.relationship('User', back_populates='influencer_campaigns')

    def __repr__(self):
        return f"<InfluencerCampaign CampaignID={self.campaign_id}, InfluencerID={self.influencer_id}>"



class TaskProgress(db.Model):
    __tablename__ = 'task_progress'
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    task_id = db.Column(db.String(100), nullable=False)  # Unique identifier for the task within the campaign
    task_description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(255), default='null')  # Task status: 'pending', 'completed', 'accepted', 'rejected'
    submitted_date = db.Column(db.DateTime, nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text, nullable=True)  # Optional feedback from the sponsor on task completion
    
    # Relationships
    influencer = db.relationship('User', backref='task_progress', lazy=True)
    campaign = db.relationship('Campaign', backref='task_progress', lazy=True)

    def __repr__(self):
        return f"<TaskProgress InfluencerID={self.influencer_id}, CampaignID={self.campaign_id}, TaskID={self.task_id}, Status={self.status}>"



class Notification(db.Model):
    __tablename__ = 'notification'

    # Columns
    id = db.Column(db.Integer, primary_key=True)  # Retain the single-column primary key for uniqueness
    category = db.Column(db.String(255), default='campaign')  # Notification category, e.g., 'campaign'
    role = db.Column(db.Integer, nullable=False)  # 1 - Influencer, 2 - Sponsor (Role of the sender)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User ID of sender
    receiver_role = db.Column(db.Integer, nullable=False)  # 1 - Influencer, 2 - Sponsor (Role of the receiver)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User ID of receiver
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=True)  # Optional link to campaign
    message = db.Column(db.String(255), nullable=False)  # Notification message content
    is_read = db.Column(db.Boolean, default=False)  # Track if the notification has been read
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_notifications')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_notifications')
    campaign = db.relationship('Campaign', backref='notifications')

    # Composite Primary Key
    # __table_args__ = (
    #     ('category', 'role', 'sender_id', 'receiver_role', 'receiver_id', name='notification_pk'),
    # )

    def __repr__(self):
        return f"<Notification {self.message} to User {self.receiver_id}>"



class AdminFlags(db.Model):
    __tablename__ = 'admin_flags'
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    flagged_type = Column(String(255), CheckConstraint("flagged_type IN ('influencer', 'flag-campaign')"), nullable=False)
    flagged_id = Column(Integer, nullable=False)
    flag_count = Column(Integer, default=1)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class BlockedEntities(db.Model):
    __tablename__ = 'blocked_entities'
    id = Column(Integer, primary_key=True)
    entity_type = Column(String(255), CheckConstraint("entity_type IN ('influencer', 'flag-campaign')"), nullable=False)
    entity_id = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_blocked = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "reason": self.reason,
            "blocked_at": self.blocked_at,
            "updated_at": self.updated_at,
            "is_blocked": self.is_blocked
        }


class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plan'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    platform_support = db.Column(JSON, nullable=False, default=[])
    influencers_per_campaign = db.Column(db.Integer, nullable=False, default=5)
    analytics_report = db.Column(db.String(100), nullable=False)
    ai_influencer_discovery_limit = db.Column(db.Integer, nullable=False, default=0)

    # Backref for UserSubscription
    user_subscriptions = db.relationship('UserSubscription', backref=db.backref('subscription_plan', lazy=True))

    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"



class UserSubscription(db.Model):
    __tablename__ = 'user_subscription'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_user_subscription_user_id'),
        nullable=False
    )
    subscription_plan_id = db.Column(
        db.Integer,
        db.ForeignKey('subscription_plan.id', name='fk_user_subscription_subscription_plan_id'),
        nullable=False
    )
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Enforce unique constraint with a name
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_subscription_user_id'),
    )

    def __repr__(self):
        return f"<UserSubscription User {self.user_id} - Plan {self.subscription_plan_id}>"


class PerformanceAnalytics(db.Model):
    """Analytics tracking performance metrics for campaigns and influencers."""
    __tablename__ = 'performance_analytics'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    impressions = db.Column(db.Integer, nullable=True)  # How many views the campaign got
    clicks = db.Column(db.Integer, nullable=True)  # Number of clicks or interactions
    conversions = db.Column(db.Integer, nullable=True)  # Number of people who acted (purchase, sign up)
    reach = db.Column(db.Integer, nullable=True)  # Number of people reached
    engagement_rate = db.Column(db.Float, nullable=True)  # Engagement rate from influencer
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PerformanceAnalytics Campaign: {self.campaign_id}, Influencer: {self.influencer_id}>"

class BrandInfluencer(db.Model):
    """Many-to-many relationship between Brands (Sponsors) and Influencers."""
    __tablename__ = 'brand_influencer'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    relationship_start = db.Column(db.DateTime, default=datetime.utcnow)
    relationship_end = db.Column(db.DateTime, nullable=True)  # Can be null for ongoing relationships
    
    def __repr__(self):
        return f"<BrandInfluencer Sponsor: {self.sponsor_id}, Influencer: {self.influencer_id}>"


