from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.utils.gsheets import fetch_google_sheet_data
from app import mongo

candidates_bp = Blueprint('candidates', __name__)

# --- Google Sheet URLs ---
# It's better to store these in config, but for simplicity, we'll define them here.
SHEET_URL_INSIGHTS = "https://docs.google.com/spreadsheets/d/12xDq4BvuXsoRTUHcuuD_y9xHDNEaylS43bzehemy_wA/edit?gid=1456820656"
SHEET_URL_HISTORY_1 = "https://docs.google.com/spreadsheets/d/12xDq4BvuXsoRTUHcuuD_y9xHDNEaylS43bzehemy_wA/edit?gid=0"
SHEET_URL_RESPONSE = "https://docs.google.com/spreadsheets/d/1UIfB60ao9-vIJEaqIUHQW6wlEMEXBYlkE8NLOQvnNUg/edit?gid=1586095684"

@candidates_bp.route('/candidate-insights')
@login_required
def candidate_insights():
    df = fetch_google_sheet_data(SHEET_URL_INSIGHTS)
    if df.empty:
        flash('Could not fetch candidate insights data from the new sheet.', 'danger')
        candidates = []
    else:
        # Pre-process the records to parse scores
        records = df.to_dict('records')
        candidates = []
        for c in records:
            # Parse 'Score' like "5 / 30" -> percentage
            score_str = str(c.get('Score', '0'))
            pct = 0
            if '/' in score_str:
                try:
                    parts = score_str.split('/')
                    pct = int((float(parts[0].strip()) / float(parts[1].strip())) * 100)
                except (ValueError, ZeroDivisionError):
                    pct = 0
            c['score_pct'] = pct
            candidates.append(c)

        if candidates:
            mongo.db.candidate_insights_cache.delete_many({})
            mongo.db.candidate_insights_cache.insert_many(candidates)
            
    return render_template('candidates/insights.html', candidates=candidates)

@candidates_bp.route('/history')
@login_required
def history():
    df1 = fetch_google_sheet_data(SHEET_URL_HISTORY_1)
    df2 = fetch_google_sheet_data(SHEET_URL_INSIGHTS)

    history1 = df1.to_dict('records') if not df1.empty else []
    history2 = df2.to_dict('records') if not df2.empty else []
        
    return render_template('candidates/history.html', history1=history1, history2=history2)

@candidates_bp.route('/response-score/<email>')
@login_required
def response_score(email):
    # Fetch from the actual quiz response sheet we are now using
    df = fetch_google_sheet_data(SHEET_URL_INSIGHTS)
    candidate_data = None
    columns = []

    if df.empty:
        flash(f'Could not fetch response score data for {email}.', 'danger')
    else:
        # The key in the sheet is 'Email Address'
        # Safely pad/clean the email string because trailing spaces like %20 break matches
        clean_target_email = email.strip().lower()
        
        # Apply lower() and strip() safely to the entire Series before matching
        if 'Email Address' in df.columns:
            matches = df[df['Email Address'].astype(str).str.strip().str.lower() == clean_target_email]
            if not matches.empty:
                candidate_data = matches.to_dict('records')[0]
                columns = df.columns.tolist()
                
                # Optionally parse score again here just in case template needs it
                score_str = str(candidate_data.get('Score', '0'))
                pct = 0
                if '/' in score_str:
                    try:
                        pct = int((float(score_str.split('/')[0].strip()) / float(score_str.split('/')[1].strip())) * 100)
                    except:
                        pass
                candidate_data['score_pct'] = pct
                
                # Save to MongoDB
                mongo.db.response_scores_cache.update_one(
                    {'email': clean_target_email},
                    {'$set': candidate_data},
                    upsert=True
                )
            else:
                flash(f'No response score data found for candidate with email: {clean_target_email}', 'warning')
        else:
            flash("The dataset does not contain an 'Email Address' column.", 'danger')
            
    return render_template('candidates/response_score.html', candidate=candidate_data, email=email, columns=columns)