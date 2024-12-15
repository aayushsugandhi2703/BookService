from flask import Flask, Blueprint, render_template, redirect, url_for, jsonify, session, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Session, Book
from app.forms import BookForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

book_bp = Blueprint('book', __name__)

@limiter.limit("5 per minute")
@book_bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.Login'))
    
    form = BookForm()
    if form.validate_on_submit():
            try:
                new_book = Book(title=form.title.data,
                                description=form.description.data,
                                user_id=session['user_id']
                                )
                Session.add(new_book)
                Session.commit()
                flash('book added successfully')
                return redirect(url_for('book.get_books'))
            except Exception as e:
                flash(f'book addition failed: {str(e)}')
                Session.rollback()
    return render_template('book.html', form=form)

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
    flash('Book deleted successfully')
    return redirect(url_for('book.get_books'))