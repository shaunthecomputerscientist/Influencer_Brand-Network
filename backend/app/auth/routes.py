from flask import Blueprint, request, jsonify, redirect, current_app, make_response
from models.models import db, User, SocialLink, BlockedEntities
from services.email_service.email_service import send_confirmation_email, send_verification_email, send_password_reset_email
from .utils import is_valid_email, validate_email, hash_password, check_password, create_jwt_token
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token
from jwt.exceptions import ExpiredSignatureError, DecodeError
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from .phyllo import get_user_data, phylloworkflow
import hmac
import hashlib
import requests
import json
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from platformData.Youtube.fetcher import YouTubeDataFetcher
from platformData.Instagram.fetcher import InstaloaderManager
# from app.blueprints import auth_bp
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/google/callback', methods=['GET'])
def google_callback():
    # Get the authorization code from the callback URL
    code = request.args.get('code')

    if not code:
        return jsonify({"message": "Authorization code not found"}), 400

    # Exchange the authorization code for an access token
    token_response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': os.environ.get('CLIENT_SECRET'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI')
    }).json()

    access_token = token_response.get('access_token')

    if not access_token:
        return jsonify({"message": "Failed to retrieve access token"}), 400

    # Get user info from Google
    user_info_response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', headers={
        'Authorization': f'Bearer {access_token}'
    }).json()

    email = user_info_response.get('email')
    first_name = user_info_response.get('given_name')
    last_name = user_info_response.get('family_name')
    print(email, first_name, last_name)

    if not email:
        return jsonify({"message": "Failed to retrieve email from Google"}), 400

    # Check if the user already exists in the database
    user = User.query.filter_by(email=email).first()

    if not user:
        # If the user does not exist, you can either return an error or ask them to sign up
        return jsonify({"message": "No account found for this email. Please sign up."}), 404

    # If user exists, create access and refresh tokens
    access_token = create_access_token(identity={"user_id": user.id, "username": user.username, "role": user.role})
    refresh_token = create_refresh_token(identity={"user_id": user.id, "username": user.username, "role": user.role})

    # Use make_response to set HttpOnly cookie
    response = make_response(jsonify({
        "message": "Logged in successfully with Google",
        "access_token": access_token
    }))
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=True,  # Use only over HTTPS in production
        samesite='Strict'  # Adjust this depending on your cross-site requirements
    )
    return response



@auth_bp.route('/getsdktoken', methods=['POST'])
def get_sdk_token():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    platformName = data.get('platformName',None)

    if not firstname or not lastname:
        return jsonify({"message": "Firstname and lastname are required"}), 400

    try:
        print(firstname,lastname)
        user_id, sdk_token, platform_id = phylloworkflow(firstname, lastname, platformName=platformName)
        return jsonify({"user_id": user_id, "sdk_token": sdk_token, "platform_id" : platform_id}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500


@auth_bp.route('/signup', methods=['POST'])
def signup():
    profile_image_upload_folder = current_app.config['PROFILE_IMAGE_UPLOAD_FOLDER']
    

    YOUTUBE_FETCHER = YouTubeDataFetcher(api_key=current_app.config['YOUTUBE_API_KEY'])
    INSTAGRAM_FETCHER = InstaloaderManager(accounts=current_app.config['INSTAGRAM_SCRAPING_ACCOUNTS'])


    role_map = {'influencer': 1, 'brand': 2}
    data = request.form
    files = request.files
    print(data)
    print(files, files.get('profile_image'))

    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    language = data.get('language', [])  # Expecting a list of languages
    gender = data.get('gender')
    dob = datetime.strptime(data.get('dob')+" 00:00:00", "%Y-%m-%d %H:%M:%S") if role == 'influencer' else None
    niche = data.get('niche', [])  # Expecting a list of niches
    platforms = json.loads(data.get('platforms', {}))  # Expecting a dict like {'platform': 'link'}
    company_name = data.get('company_name')
    industry = data.get('industry', [])  # Expecting a list of industries
    location = data.get('location',None)
    phyllo_user_id = data.get('phyllo_user_id') if role == 'influencer' else None
    description = data.get('description','')
    # print(username,first_name,last_name,email,password,role,language, gender, dob, niche, platforms, company_name,industry,location, phyllo_user_id, description )

    print(get_user_data(phyllo_user_id))

    if role.lower() not in ['influencer', 'brand']:
        return jsonify({"message": "Invalid role"}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    hashed_password = hash_password(password)

    try:
        # Create the new user instance
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role_map[role],
            language=language,
            gender=gender if role == 'influencer' else None,
            dob=dob,
            niche=niche,
            company_name=company_name if role == 'brand' else None,
            industry=industry if role == 'brand' else None,
            registered_on=datetime.utcnow(),
            name=f"{first_name} {last_name}",
            phyllo_user_id=phyllo_user_id,
            location = location,
            description=description
        )

        # Save profile image if uploaded
        profile_image = files.get('profile_image')
        if profile_image:
            # Define a folder to save images

            # Secure the filename and save the image
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(profile_image_upload_folder, filename)
            print(profile_image_path)
            profile_image.save(profile_image_path)
            new_user.profile_image = os.path.join('static','uploads','profile_images',filename)  # Assuming you have a field in User model for image path

        # Add user to the session
        db.session.add(new_user)
        db.session.commit()  # Commit to generate the new_user.id


        # Add social links for influencers if provided
        if role.lower() == 'influencer' and platforms:
            for platform, link in platforms.items():
                if 'youtube' in platform.lower():
                    socialdata=YOUTUBE_FETCHER.fetch_limited_data(link)
                elif 'instagram' in platform.lower():
                    socialdata=INSTAGRAM_FETCHER.run([link])[0]
                else:
                    socialdata={}
                    

                social_link = SocialLink(user_id=new_user.id, platform=platform, link=link, socialData = socialdata)
                db.session.add(social_link)

        db.session.commit()  # Commit all changes to the database

        # Send confirmation email
        send_confirmation_email(email, f"{first_name} {last_name}")
        return jsonify({'message': 'Signup Successful'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

####################################################################################################################
# User Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not check_password(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    blockedEntity = BlockedEntities.query.filter_by(entity_type='influencer', entity_id=user.id).first()
    if blockedEntity:
        if blockedEntity.is_blocked:
            return jsonify({'message': 'Your account has been blocked by admin. Contact Customer Support.'}), 401

    access_token = create_access_token(identity={"user_id": user.id, "username": user.username, "role": user.role})
    refresh_token = create_refresh_token(identity={"user_id": user.id, "username": user.username, "role": user.role})

    # Use make_response to set HttpOnly cookie
    response = make_response(jsonify({
        "message": "Logged in successfully", 
        "access_token": access_token
    }))
    response.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=True,  # Use only over HTTPS in production
        samesite='Strict'  # Adjust this depending on your cross-site requirements
    )
    return response
# Admin Login
# @auth_bp.route('/admin_login', methods=['POST'])
# def admin_login():
    data = request.get_json()
    org_password = data.get('org_password')

    # Admin-specific password check
    admin_password = os.environ.get('ORG_ADMIN_PASSWORD', "")
    if org_password != admin_password:
        return jsonify({"message": "Invalid admin password"}), 401

    access_token = create_access_token(identity={"role": 0})  # Role 0 is for Admin
    refresh_token = create_refresh_token(identity={"role": 0})

    return jsonify({
        "message": "Admin logged in successfully", 
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# Refresh Token Endpoint
@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        return jsonify({"message": "Refresh token is missing"}), 401

    try:
        identity = decode_token(refresh_token)["sub"]
        new_access_token = create_access_token(identity=identity)
        return jsonify({
            "access_token": new_access_token
        }), 200
    except ExpiredSignatureError:
        return jsonify({"message": "Refresh token has expired"}), 401
    except DecodeError:
        return jsonify({"message": "Invalid refresh token"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred"}), 500






@auth_bp.route('/logout', methods=['POST'])
def logout():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return jsonify({"message": "No active session"}), 401

    try:
        identity = decode_token(refresh_token)["sub"]
        response = jsonify({"message": "Logout successful"})
        response.delete_cookie('refresh_token')  # Clear cookie
        return response, 200
    except ExpiredSignatureError:
        return jsonify({"message": "Session already expired"}), 401
    except DecodeError:
        return jsonify({"message": "Invalid refresh token"}), 401

##################################################################################################################################################################################
@auth_bp.route('/check-username/<string:username>', methods=['GET'])
def check_username_availability(username):
    print('inside check')
    try:
        user = User.query.filter_by(username=username).first()
        print(user)
        if user:
            return jsonify({"available": False, "message": "Username already taken"}), 200
        return jsonify({"available": True, "message": "Username is available"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500
@auth_bp.route('/check-email/<string:email>', methods=['GET'])
def check_email_availability(email):
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"available": False, "message": "Email already taken"}), 200
        elif not validate_email(email=email):
            return jsonify({"available": False, "message": "Invalid email. Not registered with smtp server."}), 200
        return jsonify({"available": True, "message": "Email is available"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500



@auth_bp.route('signup/options', methods=['GET'])
def get_options():
    # Hardcoded options for languages, niches, platforms, and industries
    options = {
        "languages":current_app.config['LANGUAGES'],
        "niches": current_app.config['NICHES'],
        "platforms": current_app.config['PLATFORMS'],
        "industries": current_app.config['INDUSTRIES'],
        "goals": current_app.config['GOALS'],
        'gender': current_app.config['GENDER'],
        "locations": {
            "countries": []
        }
    }

    # Load the countries data from the JSON file
    countries_data_path = os.path.join(current_app.root_path,'services','data_utils','country.json')
    print(countries_data_path)

    try:
        with open(countries_data_path, 'r', encoding='utf-8') as f:
            countries_data = json.load(f)
        # Create a list of country names and states
        countries_list = [{"name": country["name"], "states": country["states"]} for country in countries_data['countries']]

        # Update the locations key in options with countries list
        options["locations"]["countries"] = countries_list

    except Exception as e:
        print(f"Error reading countries data: {e}")
        return jsonify({"error": "Failed to read countries data"}), 500

    return jsonify(options), 200  # Return the complete options including locations


###################################################################################################################################
# FORGOT PASSWORD


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        token = create_reset_token(user)  # Create a function to generate the token
        print(os.environ.get('FRONTEND_URL'))
        
        # Get the base URL and add the path with token
        frontend_url = os.environ.get('FRONTEND_URL')
        reset_link = f"{frontend_url.rstrip('/')}/reset-password?token={token}"  # Ensure a single slash
        
        send_password_reset_email(email, reset_link, name=user.name)  # Send email with reset link
        return jsonify({"message": "Check your email for a password reset link."}), 200
    
    return jsonify({"message": "Email not found."}), 404

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('password')
    user = verify_reset_token(token)  # Create a function to verify the token
    if user:
        user.password = hash_password(new_password)  # Hash the password before saving
        db.session.commit()
        return jsonify({"message": "Your password has been updated."}), 200
    return jsonify({"message": "Invalid or expired token."}), 400

serializer = Serializer(os.environ.get('SECRET_KEY'))

def create_reset_token(user, expiration=3600):
    return serializer.dumps({'user_id': user.id}, salt='password-reset-salt')

def verify_reset_token(token):
    try:
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=3600)['user_id']
    except Exception:
        return None
    return User.query.get(user_id)
