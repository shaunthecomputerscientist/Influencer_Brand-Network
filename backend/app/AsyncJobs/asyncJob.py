from flask import request, jsonify, Response, send_file, make_response
from models.models import Campaign, Chat, InfluencerCampaign,User, TaskProgress,Notification, db
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, decode_token
# from main import socketio
from services.Redis.cache_helpers import cache_data, generate_cache_key
from operator import itemgetter
import json,os
from flask import render_template, url_for
import os
from campaigns.GA4Manager.ga4analytics import get_ga4_Report
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
from flask import url_for
# from asyncBP import trigger_bp
# from main import celery, app
# from campaigns.routes import campaigns_bp
from flask import Blueprint
# from intermediateimport import fetch_ga4_report_async

# Define the blueprint for async tasks
trigger_bp = Blueprint('triggerjobs', __name__)
from campaigns.GA4Manager.ga4analytics import get_ga4_Report
from io import BytesIO
from zipfile import ZipFile
import pandas as pd
from celery import shared_task




@shared_task
def fetch_ga4_report_async(campaign_id):
    from flask import current_app
    app = current_app
    with app.app_context():
        # Fetch the campaign by its ID
        campaign = Campaign.query.filter_by(id=campaign_id, trackUtmLinks=True, status='active').first()

        if not campaign:
            return "Campaign not found or is inactive."

        user = User.query.filter_by(id=campaign.sponsor_id).first()

        # Get GA4 report for this specific campaign
        data = get_ga4_Report(campaign.id)  # Get dataframe
        
        # Convert dataframe to CSV
        csv_buffer = BytesIO()
        data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Reset buffer
        
        # Save the CSV data
        file_name = f"{campaign.name}.csv"
        
        # Temporary directory setup
        temp_dir = os.path.join(os.getcwd(), "tmp")
        if not os.path.exists(temp_dir):  # Ensure the directory exists
            os.makedirs(temp_dir)

        # Save CSV to a file
        csv_path = os.path.join(temp_dir, file_name)
        with open(csv_path, 'wb') as f:
            f.write(csv_buffer.getvalue())

        return csv_path  # Return the file path






@trigger_bp.route('/ga4/export', methods=['POST'])
@jwt_required()
def trigger_ga4_export():
    sponsor = get_jwt_identity()
    campaign_id = request.json.get('campaign_id')  # Extract campaign_id from the request body
    if not campaign_id:
        return jsonify({"message": "Campaign ID is required."}), 400
    
    task = fetch_ga4_report_async.delay(campaign_id)  # Pass the campaign ID to the task
    return jsonify({"message": "Export started", "task_id": task.id}), 200


@trigger_bp.route('/ga4/export/<task_id>', methods=['GET'])
@jwt_required()
def download_ga4_export(task_id):
    from flask import current_app
    task_result = fetch_ga4_report_async.AsyncResult(task_id)

    if task_result.status == "SUCCESS":
        file_path = task_result.result
        print(file_path)

        # Send the CSV file to the client
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),  # Send the file with its original name
            mimetype='text/csv'
        )

        # Ensure the file is deleted after the response is sent
        try:
            os.remove(file_path)
        except OSError as e:
            current_app.logger.error(f"Error deleting file {file_path}: {e}")

        return response

    elif task_result.status == "PENDING":
        return jsonify({"message": "Export is still processing"}), 202

    elif task_result.status == "FAILURE":
        return jsonify({"message": "Export failed"}), 500

    else:
        return jsonify({"message": "Task status unknown"}), 400
