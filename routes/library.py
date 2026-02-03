from flask import Blueprint, render_template, request
from models import ScamReport

library_bp = Blueprint('library', __name__)

@library_bp.route('/library')
def index():
    page = request.args.get('page', 1, type=int)
    # Get all articles, newest first
    pagination = ScamReport.query.order_by(ScamReport.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('library.html', articles=pagination.items, pagination=pagination)

@library_bp.route('/library/<int:article_id>')
def detail(article_id):
    article = ScamReport.query.get_or_404(article_id)
    # Get recent articles for sidebar
    recent_articles = ScamReport.query.order_by(ScamReport.created_at.desc()).limit(5).all()
    return render_template('library_detail.html', article=article, recent_articles=recent_articles)
