from flask import Flask, Blueprint, render_template, redirect, url_for, jsonify, session, flash, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Session, Review, Book
from app.forms import ReviewForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["5 per minute"])

review_bp = Blueprint('review', __name__)

# This function and route is for the user to add a review
@limiter.limit("5 per minute")
@review_bp.route('/add/<int:book_id>', methods=['GET', 'POST'])
@jwt_required()
def add_review(book_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.Login'))

    form = ReviewForm()
    book = Session.query(Book).get(book_id)  # Fetch the book object
    if not book:
        flash("Book not found.")
        return redirect(url_for('review.view_book_reviews', book_id=book_id))
    if form.validate_on_submit():
        try:
            # Create a new review for the specific book
            new_review = Review(
                content=form.content.data,
                user_id=session['user_id'],  # Get the user ID from the session
                book_id=book_id  # Associate the review with the specific book
            )
            Session.add(new_review)
            Session.commit()
            current_app.logger.info(f"Review added for book {book.title}")
            return redirect(url_for('review.view_book_reviews', book_id=book.id))
        except Exception as e:
            flash(f'Review addition failed: {str(e)}')
            Session.rollback()

    return render_template('review.html', form=form, book=book)

# This function and route is for the user to view the reviews of a book
@review_bp.route('/view/<int:book_id>', methods=['GET'])
@jwt_required()
def view_book_reviews(book_id):
    user_id = get_jwt_identity()
    try:
        Session.rollback()
        # Fetch the book and its reviews
        book = Session.query(Book).filter_by(id=book_id).first()

        if not book:
            flash("Book not found")
            return jsonify({"error": "Book not found"}), 404

        # Format the response
        book_data = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "reviews": [{"id": review.id, "content": review.content} for review in book.reviews]
        }
        current_app.logger.info(f"Book reviews fetched for book {book.title}")
        return jsonify(book_data)
    except Exception as e:
        current_app.logger.error(f"Failed to fetch book details: {str(e)}")
        return jsonify({"error": "Could not fetch book details"}), 500
    finally:
        Session.close()

   
