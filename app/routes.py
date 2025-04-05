from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from app import db
from app.models import Campaign, Contact, ContactGroup, CampaignContact
from app.whatsapp import send_whatsapp_message
from app.ai_service import generate_message
import traceback

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Log the full error traceback
        current_app.logger.error(f"Error in index route: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        # Return a more informative error page
        return render_template('error.html', error=str(e)), 500

@main.route('/dashboard')
@login_required
def dashboard():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', campaigns=campaigns)

@main.route('/contacts')
@login_required
def contacts():
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    groups = ContactGroup.query.filter_by(user_id=current_user.id).all()
    return render_template('contacts.html', contacts=contacts, groups=groups)

@main.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('main.contacts'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('main.contacts'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload CSV or Excel file.', 'error')
        return redirect(url_for('main.contacts'))
    
    try:
        # Create contact group if name provided
        group = None
        group_name = request.form.get('group_name')
        if group_name:
            group = ContactGroup(
                name=group_name,
                user_id=current_user.id
            )
            db.session.add(group)
            db.session.commit()
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['name', 'phone']
        if not all(col in df.columns for col in required_columns):
            flash('File must contain columns: name, phone', 'error')
            return redirect(url_for('main.contacts'))
        
        # Import contacts
        for _, row in df.iterrows():
            contact = Contact(
                name=row['name'],
                phone=row['phone'],
                email=row.get('email'),
                user_id=current_user.id,
                group_id=group.id if group else None
            )
            db.session.add(contact)
        
        db.session.commit()
        flash('Contacts imported successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing contacts: {str(e)}', 'error')
    
    return redirect(url_for('main.contacts'))

@main.route('/contacts/create', methods=['GET', 'POST'])
@login_required
def create_contact():
    if request.method == 'POST':
        try:
            contact = Contact(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form.get('email'),
                user_id=current_user.id,
                group_id=request.form.get('group_id')
            )
            db.session.add(contact)
            db.session.commit()
            flash('Contact created successfully', 'success')
            return redirect(url_for('main.contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating contact: {str(e)}', 'error')
    
    groups = ContactGroup.query.filter_by(user_id=current_user.id).all()
    return render_template('contact_form.html', groups=groups)

@main.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.contacts'))
    
    if request.method == 'POST':
        try:
            contact.name = request.form['name']
            contact.phone = request.form['phone']
            contact.email = request.form.get('email')
            contact.group_id = request.form.get('group_id')
            db.session.commit()
            flash('Contact updated successfully', 'success')
            return redirect(url_for('main.contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating contact: {str(e)}', 'error')
    
    groups = ContactGroup.query.filter_by(user_id=current_user.id).all()
    return render_template('contact_form.html', contact=contact, groups=groups)

@main.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.contacts'))
    
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting contact: {str(e)}', 'error')
    
    return redirect(url_for('main.contacts'))

@main.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        try:
            group = ContactGroup(
                name=request.form['name'],
                description=request.form.get('description'),
                user_id=current_user.id
            )
            db.session.add(group)
            db.session.commit()
            flash('Group created successfully', 'success')
            return redirect(url_for('main.contacts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating group: {str(e)}', 'error')
    
    return render_template('group_form.html')

@main.route('/campaigns/new', methods=['GET', 'POST'])
@login_required
def new_campaign():
    if request.method == 'POST':
        try:
            campaign = Campaign(
                name=request.form['name'],
                description=request.form.get('description'),
                message_template=request.form.get('message_template'),
                schedule=datetime.strptime(request.form['schedule'], '%Y-%m-%dT%H:%M') if request.form.get('schedule') else None,
                user_id=current_user.id
            )
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating campaign: {str(e)}', 'error')
    
    return render_template('campaign_form.html')

@main.route('/api/generate-message', methods=['POST'])
@login_required
def generate_campaign_message():
    try:
        data = request.get_json()
        message = generate_message(data.get('prompt', ''))
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main.route('/api/send-message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    contact_id = data.get('contact_id')
    message_content = data.get('message')
    
    try:
        result = send_whatsapp_message(contact_id, message_content)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400 
    
