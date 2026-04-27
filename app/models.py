from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    contacts = db.relationship('Contact', backref='user', lazy=True)
    contact_groups = db.relationship('ContactGroup', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    message_template = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, paused
    schedule = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_contacts = db.relationship('CampaignContact', backref='campaign', lazy=True)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('contact_group.id'))
    campaign_contacts = db.relationship('CampaignContact', backref='contact', lazy=True)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

class ContactGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contacts = db.relationship('Contact', backref='group', lazy=True)

    def __repr__(self):
        return f'<ContactGroup {self.name}>'

class CampaignContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    def __repr__(self):
        return f'<CampaignContact {self.campaign_id}:{self.contact_id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    sent_messages = db.relationship('SentMessage', backref='message', lazy=True)

class SentMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    provider_message_id = db.Column(db.String(100))

# Association table for campaign-contacts many-to-many relationship
campaign_contacts = db.Table('campaign_contacts',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'), primary_key=True)
) 