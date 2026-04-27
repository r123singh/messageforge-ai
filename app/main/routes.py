from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Campaign, Contact, ContactGroup, CampaignContact
from app.extensions import db #, limiter
import logging
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
        return render_template('error.html'), 500

@main.route('/dashboard')
@login_required
# @limiter.limit("100 per hour")
def dashboard():
    try:
        campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
        total_contacts = Contact.query.filter_by(user_id=current_user.id).count()
        active_campaigns = Campaign.query.filter_by(user_id=current_user.id, status='active').count()
        
        return render_template('dashboard.html',
                             campaigns=campaigns,
                             total_campaigns=len(campaigns),
                             total_contacts=total_contacts,
                             active_campaigns=active_campaigns)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        flash('Error loading dashboard. Please try again.', 'error')
        return render_template('error.html'), 500

@main.route('/campaign/new', methods=['GET', 'POST'])
@login_required
# @limiter.limit("20 per hour")
def new_campaign():
    try:
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            message = request.form.get('message', '').strip()
            schedule = request.form.get('schedule')

            if not all([name, message]):
                flash('Campaign name and message are required.', 'error')
                return render_template('campaign_form.html')

            campaign = Campaign(
                name=name,
                description=description,
                message=message,
                schedule=datetime.strptime(schedule, '%Y-%m-%dT%H:%M') if schedule else None,
                user_id=current_user.id
            )
            
            db.session.add(campaign)
            db.session.commit()
            
            flash('Campaign created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        return render_template('campaign_form.html')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in new campaign route: {str(e)}")
        flash('Error creating campaign. Please try again.', 'error')
        return render_template('error.html'), 500

@main.route('/campaign/<int:id>/edit', methods=['GET', 'POST'])
@login_required
# @limiter.limit("20 per hour")
def edit_campaign(id):
    try:
        campaign = Campaign.query.get_or_404(id)
        
        if campaign.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.dashboard'))

        if request.method == 'POST':
            campaign.name = request.form.get('name', '').strip()
            campaign.description = request.form.get('description', '').strip()
            campaign.message = request.form.get('message', '').strip()
            schedule = request.form.get('schedule')
            
            if schedule:
                campaign.schedule = datetime.strptime(schedule, '%Y-%m-%dT%H:%M')
            
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        return render_template('campaign_form.html', campaign=campaign)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in edit campaign route: {str(e)}")
        flash('Error updating campaign. Please try again.', 'error')
        return render_template('error.html'), 500

@main.route('/campaign/<int:id>/delete', methods=['POST'])
@login_required
# @limiter.limit("10 per hour")
def delete_campaign(id):
    try:
        campaign = Campaign.query.get_or_404(id)
        
        if campaign.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.dashboard'))
            
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete campaign route: {str(e)}")
        flash('Error deleting campaign. Please try again.', 'error')
        
    return redirect(url_for('main.dashboard'))

@main.route('/contacts')
@login_required
# @limiter.limit("100 per hour")
def contacts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        contacts = Contact.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page)
        groups = ContactGroup.query.filter_by(user_id=current_user.id).all()
        return render_template('contacts.html', contacts=contacts, groups=groups)
    except Exception as e:
        logger.error(f"Error in contacts route: {str(e)}")
        flash('Error loading contacts. Please try again.', 'error')
        return render_template('error.html'), 500

@main.route('/contacts/import', methods=['POST'])
@login_required
# @limiter.limit("5 per hour")
def import_contacts():
    try:
        if 'file' not in request.files:
            flash('No file uploaded.', 'error')
            return redirect(url_for('main.contacts'))
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('main.contacts'))
            
        if not file.filename.endswith(('.csv', '.xlsx')):
            flash('Invalid file format. Please upload CSV or Excel file.', 'error')
            return redirect(url_for('main.contacts'))
            
        filename = secure_filename(file.filename)
        filepath = os.path.join('/tmp', filename)
        file.save(filepath)
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
                
            required_columns = ['name', 'phone']
            if not all(col in df.columns for col in required_columns):
                flash('File must contain name and phone columns.', 'error')
                return redirect(url_for('main.contacts'))
                
            for _, row in df.iterrows():
                contact = Contact(
                    name=row['name'].strip(),
                    phone=str(row['phone']).strip(),
                    user_id=current_user.id
                )
                db.session.add(contact)
                
            db.session.commit()
            flash(f'Successfully imported {len(df)} contacts!', 'success')
            
        finally:
            os.remove(filepath)
            
        return redirect(url_for('main.contacts'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in import contacts route: {str(e)}")
        flash('Error importing contacts. Please check your file and try again.', 'error')
        return redirect(url_for('main.contacts'))

@main.route('/api/generate-message', methods=['POST'])
@login_required
# @limiter.limit("10 per minute")
def generate_message():
    try:
        description = request.json.get('description', '')
        if not description:
            return jsonify({'error': 'Description is required'}), 400
            
        # TODO: Implement AI message generation
        # For now, return a placeholder message
        message = f"Thank you for your interest in our {description}. We'll be in touch soon!"
        
        return jsonify({'message': message})
    except Exception as e:
        logger.error(f"Error in generate message route: {str(e)}")
        return jsonify({'error': 'Error generating message'}), 500 