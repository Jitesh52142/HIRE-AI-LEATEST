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
    df = fetch_google_sheet_data(SHEET_URL_INSIGHTS)
    if df.empty:
        flash('Could not fetch candidate insights data. The sheet might be private or unavailable.', 'danger')
        candidates = []
    else:
        candidates = df.to_dict('records')
        # Optionally, save to MongoDB for logging/caching
        if candidates:
            mongo.db.candidate_insights_cache.delete_many({})
            mongo.db.candidate_insights_cache.insert_many(candidates)
            
    return render_template('candidates/insights.html', candidates=candidates)

@candidates_bp.route('/history')
@login_required
def history():
    # Fetch from both sheets
    df1 = fetch_google_sheet_data(SHEET_URL_HISTORY_1)
    df2 = fetch_google_sheet_data(SHEET_URL_INSIGHTS) # The second history source is the insights sheet

    if df1.empty or df2.empty:
        flash('Could not fetch full history data. One or more sheets may be unavailable.', 'warning')

    history1 = df1.to_dict('records')
    history2 = df2.to_dict('records')

    # Optionally, save to MongoDB
    if history1:
        mongo.db.history1_cache.delete_many({})
        mongo.db.history1_cache.insert_many(history1)
    if history2:
        # We can reuse the insights cache or create a new one
        mongo.db.history2_cache.delete_many({})
        mongo.db.history2_cache.insert_many(history2)
        
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