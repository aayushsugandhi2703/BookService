from flask import Flask, Blueprint, render_template, redirect, url_for, jsonify, session, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Session, Book, User
from app.forms import BookForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import lru_cache

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

book_bp = Blueprint('book', __name__)

@limiter.limit("5 per minute")
@book_bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add():
    user_id = get_jwt_identity()
    user = Session.query(User).get(user_id)
    
    if not user:
        current_app.logger.warning("Unauthorized user attempted to add a book.")
        return redirect(url_for('auth.Login'))
    
    form = BookForm()
    if form.validate_on_submit():
        try:
            new_book = Book(title=form.title.data,
                            description=form.description.data,
                            user_id=user_id)
            Session.add(new_book)
            Session.commit()
            current_app.logger.info(f"Book added by {user.username}: {user_id} : {new_book.title}")
            flash("Book added successfully!", "success")
            return redirect(url_for('book.get_books'))  # Redirect to a list view or home
        except Exception as e:
            Session.rollback()
            current_app.logger.error(f"Failed to add book for user {user.username}: {str(e)}")
            flash("An error occurred while adding the book. Please try again.", "error")
    
    return render_template('book.html', form=form)

@lru_cache(maxsize=50)
@book_bp.route('/display', methods=['GET'])
@jwt_required()
def get_books():
    user_id = get_jwt_identity()
    
    # Rollback if there's any uncommitted session state (though it's not usually necessary here)
    Session.rollback()
    
    view_books = Session.query(Book).filter_by(user_id=user_id).all()
    view_books_json = [{'id': view_book.id, 'title': view_book.title, 'description': view_book.description} for view_book in view_books]
    
    return jsonify(view_books_json)

@book_bp.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    if 'user_id' in session:
        user_id = session['user_id']
    delete_book = Session.query(Book).filter_by(user_id=user_id).filter_by(id=id).first()
    Session.delete(delete_book)
    Session.commit()
    current_app.logger.info(f"Book deleted by user {user_id}: {delete_book.title}")
    return redirect(url_for('book.get_books'))