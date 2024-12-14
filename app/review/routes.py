from flask import Flask, Blueprint, render_template, redirect, url_for, jsonify, session, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Session, Review, Book
from app.forms import ReviewForm

review_bp = Blueprint('review', __name__)


@review_bp.route('/add/<int:book_id>', methods=['GET', 'POST'])
@jwt_required()
def add_review(book_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.Login'))

    form = ReviewForm()
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
            flash('Review added successfully')
            return redirect(url_for('review.view_book_reviews', book_id=book_id))
        except Exception as e:
            flash(f'Review addition failed: {str(e)}')
            Session.rollback()

    return render_template('review.html', form=form)

@review_bp.route('/book/<int:book_id>', methods=['GET'])
@jwt_required()
def view_book_reviews(book_id):
    try:
        # Fetch the book and its reviews
        book = session.query(Book).filter_by(id=book_id).first()

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
        return jsonify(book_data)
    except Exception as e:
        flash(f"Error fetching book details: {str(e)}")
        return jsonify({"error": "Could not fetch book details"}), 500
    finally:
        session.close()

   
