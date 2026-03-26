import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from app import mongo
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def main_dashboard():
    # Clear current draft on entering main dashboard to start fresh
    session.pop('campaign_draft', None)
    return redirect(url_for('dashboard.setup_step', step_id=1))

@dashboard_bp.route('/dashboard/step/<int:step_id>', methods=['GET', 'POST'])
@login_required
def setup_step(step_id):
    if step_id < 1 or step_id > 5:
        return redirect(url_for('dashboard.main_dashboard'))

    # Load draft from session or database
    draft = session.get('campaign_draft', {})

    if request.method == 'POST':
        # Update draft with incoming form data
        form_data = request.form.to_dict()
        draft.update(form_data)
        session['campaign_draft'] = draft

        if step_id < 5:
            return redirect(url_for('dashboard.setup_step', step_id=step_id + 1))
        else:
            # Final Step: Submit everything
            submission_data = draft
            submission_data['submitted_by'] = current_user.email
            submission_data['submitted_at'] = datetime.utcnow().isoformat()

            try:
                # Save to DB
                mongo.db.form_submissions.insert_one(submission_data)
                
                # Push to Webhook
                webhook_url = current_app.config.get('N8N_WEBHOOK_URL')
                submission_data.pop('_id', None) # Remove ObjectId
                if webhook_url:
                    try:
                        requests.post(webhook_url, json=submission_data, timeout=10)
                    except:
                        pass # Automation failure shouldn't stop flow
                
                session.pop('campaign_draft', None)
                flash('Strategic Recruitment Campaign Launched Successfully!', 'success')
                return redirect(url_for('candidates.candidate_insights'))
            except Exception as e:
                flash(f'Launch failed: {e}', 'danger')
                return redirect(url_for('dashboard.setup_step', step_id=5))

    return render_template('dashboard/dashboard.html', step_id=step_id, draft=draft)
