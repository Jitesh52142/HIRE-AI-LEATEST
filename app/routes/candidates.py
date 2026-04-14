from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.utils.gsheets import fetch_google_sheet_data
from app import mongo

candidates_bp = Blueprint('candidates', __name__)

# --- Google Sheet URLs ---
# It's better to store these in config, but for simplicity, we'll define them here.
SHEET_URL_INSIGHTS = "https://docs.google.com/spreadsheets/d/12xDq4BvuXsoRTUHcuuD_y9xHDNEaylS43bzehemy_wA/edit?gid=1831348468"
SHEET_URL_HISTORY_1 = "https://docs.google.com/spreadsheets/d/12xDq4BvuXsoRTUHcuuD_y9xHDNEaylS43bzehemy_wA/edit?gid=0"
SHEET_URL_RESPONSE = "https://docs.google.com/spreadsheets/d/1UIfB60ao9-vIJEaqIUHQW6wlEMEXBYlkE8NLOQvnNUg/edit?gid=1586095684"

@candidates_bp.route('/candidate-insights')
@login_required
def candidate_insights():
    # Demo data from Google Sheets has been disabled per user request
    # To restore dynamic fetching from MongoDB in the future, fetch from mongo.db.form_submissions or similar.
    candidates = []
            
    return render_template('candidates/insights.html', candidates=candidates)

@candidates_bp.route('/history')
@login_required
def history():
    # Demo data pulling has been disabled
    history1 = []
    history2 = []
        
    return render_template('candidates/history.html', history1=history1, history2=history2)

@candidates_bp.route('/response-score/<email>')
@login_required
def response_score(email):
    df = fetch_google_sheet_data(SHEET_URL_RESPONSE)
    candidate_data = None
    columns = []

    if df.empty:
        flash(f'Could not fetch response score data for {email}.', 'danger')
    else:
        # Find the row matching the email
        candidate_row = df[df['email'].str.lower() == email.lower()]
        if not candidate_row.empty:
            candidate_data = candidate_row.to_dict('records')[0]
            columns = df.columns.tolist()
            # Save to MongoDB
            mongo.db.response_scores_cache.update_one(
                {'email': email},
                {'$set': candidate_data},
                upsert=True
            )
        else:
            flash(f'No response score data found for candidate with email: {email}', 'warning')
            
    return render_template('candidates/response_score.html', candidate=candidate_data, email=email, columns=columns)