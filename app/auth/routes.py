from flask import Flask, Blueprint, render_template, redirect, url_for, flash, make_response, session
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required    
from app.models import User, Session
from app.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

auth_bp = Blueprint('auth', __name__)

# This function will redirect the user to the login page
@limiter.limit("5 per minute")
@auth_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('auth.Login'))

# This function and route is for the user to login 
@auth_bp.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()

    # If the form is submitted and validated, the user will be redirected to the task page
    if form.validate_on_submit(): 
        user = Session.query(User).filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id

            # Create the access and refresh tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            response = make_response(redirect(url_for('book.add')))
            response.set_cookie('access_token_cookie', access_token, httponly=True)
            response.set_cookie('refresh_token_cookie', refresh_token, httponly=True)
            return response 
      # return jsonify(access_token=access_token, refresh_token=refresh_token)
    return render_template('login.html', form=form)

# This function and route is for the user to register
@limiter.limit("5 per minute")
@auth_bp.route('/register', methods=['GET', 'POST'])
def Register():
    form = RegisterForm()

    # If the form is submitted and validated, the user will be redirected to the login page
    if form.validate_on_submit():
        passcode = generate_password_hash(form.password.data)  
        user = User(username=form.username.data, password=passcode)
        Session.add(user)
        Session.commit()
        flash('User created successfully')
        return redirect(url_for('auth.Login'))
    else:
        Session.rollback()
        flash('User creation failed')
    return render_template('signup.html', form=form)

# This function and route is for the user to logout
@auth_bp.route('/logout', methods=['GET'])  
@jwt_required()
def Logout():

    response = make_response(redirect(url_for('auth.Login')))
    response.delete_cookie('access_token_cookie')  # Ensure you delete the correct cookie
    response.delete_cookie('refresh_token_cookie')  # Also delete the refresh token
    session.clear()
    return response
