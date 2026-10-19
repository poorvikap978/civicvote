from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from datetime import date
import hashlib
import time

app = Flask(__name__)
app.secret_key = 'civicvote_secure_key_2026'

DB_CONFIG = {
    'dbname': 'civicvote',
    'user': 'poorvikap',  # Change to your PostgreSQL username
    'password': '',
    'host': 'localhost',
    'port': '5432'
}

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = None
    if fetchone:
        result = cur.fetchone()
    elif fetchall:
        result = cur.fetchall()
    if commit:
        conn.commit()
    cur.close()
    conn.close()
    return result

# ── Home ─────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Admin Auth ───────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# ── Admin Dashboard ──────────────────────────────────────
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    elections = query('SELECT * FROM elections ORDER BY created_at DESC', fetchall=True)
    total_voters = query('SELECT COUNT(*) as c FROM voters', fetchone=True)['c']
    total_votes = query('SELECT COUNT(*) as c FROM votes', fetchone=True)['c']
    total_candidates = query('SELECT COUNT(*) as c FROM candidates', fetchone=True)['c']
    recent_logs = query('SELECT al.*, v.full_name FROM audit_log al LEFT JOIN voters v ON al.voter_id = v.voter_id ORDER BY logged_at DESC LIMIT 10', fetchall=True)
    turnout = query('SELECT * FROM voter_turnout', fetchall=True)

    return render_template('admin_dashboard.html',
        elections=elections,
        total_voters=total_voters,
        total_votes=total_votes,
        total_candidates=total_candidates,
        recent_logs=recent_logs,
        turnout=turnout
    )

# ── Manage Voters ────────────────────────────────────────
@app.route('/admin/voters', methods=['GET', 'POST'])
def manage_voters():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['full_name']
        voter_card = request.form['voter_card_no']
        aadhaar = request.form['aadhaar_no']
        dob = request.form['date_of_birth']
        constituency_id = request.form['constituency_id']
        try:
            query('''INSERT INTO voters (full_name, voter_card_no, aadhaar_no, date_of_birth, constituency_id, is_verified)
                     VALUES (%s, %s, %s, %s, %s, TRUE)''',
                  (name, voter_card, aadhaar, dob, constituency_id), commit=True)
            flash('Voter registered successfully!', 'success')
        except Exception as e:
            flash(str(e), 'error')
        return redirect(url_for('manage_voters'))

    voters = query('''SELECT v.*, c.name as constituency_name FROM voters v
                      LEFT JOIN constituencies c ON v.constituency_id = c.constituency_id
                      ORDER BY v.registered_at DESC''', fetchall=True)
    constituencies = query('SELECT * FROM constituencies', fetchall=True)
    return render_template('manage_voters.html', voters=voters, constituencies=constituencies)

# ── Manage Elections ─────────────────────────────────────
@app.route('/admin/elections', methods=['GET', 'POST'])
def manage_elections():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        constituency_id = request.form['constituency_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']
        try:
            query('''INSERT INTO elections (title, description, constituency_id, start_date, end_date, status)
                     VALUES (%s, %s, %s, %s, %s, %s)''',
                  (title, description, constituency_id, start_date, end_date, status), commit=True)
            flash('Election created!', 'success')
        except Exception as e:
            flash(str(e), 'error')
        return redirect(url_for('manage_elections'))

    elections = query('''SELECT e.*, c.name as constituency_name FROM elections e
                         LEFT JOIN constituencies c ON e.constituency_id = c.constituency_id
                         ORDER BY e.created_at DESC''', fetchall=True)
    constituencies = query('SELECT * FROM constituencies', fetchall=True)
    return render_template('manage_elections.html', elections=elections, constituencies=constituencies)

# ── Manage Candidates ────────────────────────────────────
@app.route('/admin/candidates', methods=['GET', 'POST'])
def manage_candidates():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['full_name']
        party = request.form['party']
        symbol = request.form['party_symbol']
        election_id = request.form['election_id']
        constituency_id = request.form['constituency_id']
        manifesto = request.form.get('manifesto', '')
        try:
            query('''INSERT INTO candidates (full_name, party, party_symbol, election_id, constituency_id, manifesto)
                     VALUES (%s, %s, %s, %s, %s, %s)''',
                  (name, party, symbol, election_id, constituency_id, manifesto), commit=True)
            flash('Candidate added!', 'success')
        except Exception as e:
            flash(str(e), 'error')
        return redirect(url_for('manage_candidates'))

    candidates = query('''SELECT c.*, e.title as election_title FROM candidates c
                          JOIN elections e ON c.election_id = e.election_id
                          ORDER BY c.candidate_id DESC''', fetchall=True)
    elections = query('SELECT * FROM elections', fetchall=True)
    constituencies = query('SELECT * FROM constituencies', fetchall=True)
    return render_template('manage_candidates.html', candidates=candidates,
                           elections=elections, constituencies=constituencies)

# ── Voter Verification (Simulated Biometric) ─────────────
@app.route('/verify', methods=['GET', 'POST'])
def verify_voter():
    if request.method == 'POST':
        voter_card = request.form['voter_card_no']
        aadhaar = request.form['aadhaar_no']

        voter = query('''SELECT v.*, c.name as constituency_name
                         FROM voters v
                         LEFT JOIN constituencies c ON v.constituency_id = c.constituency_id
                         WHERE v.voter_card_no = %s AND v.aadhaar_no = %s''',
                      (voter_card, aadhaar), fetchone=True)

        if not voter:
            query('''INSERT INTO audit_log (action, status, details)
                     VALUES (%s, %s, %s)''',
                  ('VERIFY_ATTEMPT', 'failed', f'Invalid credentials: {voter_card}'), commit=True)
            flash('❌ Verification failed. Invalid Voter ID or Aadhaar number.', 'error')
            return redirect(url_for('verify_voter'))

        if voter['has_voted']:
            query('''INSERT INTO audit_log (voter_id, action, status, details)
                     VALUES (%s, %s, %s, %s)''',
                  (voter['voter_id'], 'VERIFY_ATTEMPT', 'blocked', 'Voter already voted'), commit=True)
            flash('⚠️ You have already cast your vote. Duplicate voting is not allowed.', 'error')
            return redirect(url_for('verify_voter'))

        session['verified_voter_id'] = voter['voter_id']
        session['verified_voter_name'] = voter['full_name']
        session['voter_constituency_id'] = voter['constituency_id']
        return redirect(url_for('select_election'))

    return render_template('verify.html')

# ── Select Election ──────────────────────────────────────
@app.route('/elections')
def select_election():
    if not session.get('verified_voter_id'):
        return redirect(url_for('verify_voter'))

    constituency_id = session.get('voter_constituency_id')
    elections = query('''SELECT * FROM elections
                         WHERE status = %s AND constituency_id = %s''',
                      ('active', constituency_id), fetchall=True)

    if not elections:
        elections = query("SELECT * FROM elections WHERE status = 'active'", fetchall=True)

    return render_template('select_election.html',
                           elections=elections,
                           voter_name=session['verified_voter_name'])

# ── Cast Vote ────────────────────────────────────────────
@app.route('/vote/<int:election_id>', methods=['GET', 'POST'])
def cast_vote(election_id):
    if not session.get('verified_voter_id'):
        return redirect(url_for('verify_voter'))

    if request.method == 'POST':
        candidate_id = request.form.get('candidate_id')
        voter_id = session['verified_voter_id']

        if not candidate_id:
            flash('Please select a candidate.', 'error')
            return redirect(url_for('cast_vote', election_id=election_id))

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT voter_card_no, aadhaar_no FROM voters WHERE voter_id = %s', (voter_id,))
            voter = cur.fetchone()
            cur.execute('CALL cast_vote(%s, %s, %s, %s)',
                        (voter[0], voter[1], int(candidate_id), election_id))
            conn.commit()
            cur.close()
            conn.close()
            session.pop('verified_voter_id', None)
            session.pop('verified_voter_name', None)
            session['vote_success'] = True
            return redirect(url_for('vote_success'))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('cast_vote', election_id=election_id))

    election = query('SELECT * FROM elections WHERE election_id = %s', (election_id,), fetchone=True)
    candidates = query('SELECT * FROM candidates WHERE election_id = %s ORDER BY candidate_id',
                       (election_id,), fetchall=True)

    return render_template('vote.html', election=election, candidates=candidates,
                           voter_name=session.get('verified_voter_name'))

# ── Vote Success ─────────────────────────────────────────
@app.route('/success')
def vote_success():
    if not session.pop('vote_success', False):
        return redirect(url_for('index'))
    return render_template('success.html')

# ── Live Results ─────────────────────────────────────────
@app.route('/results')
def results():
    elections = query('SELECT DISTINCT election_id, election_title FROM live_results', fetchall=True)
    results_data = query('SELECT * FROM live_results', fetchall=True)
    turnout = query('SELECT * FROM voter_turnout', fetchall=True)
    return render_template('results.html', elections=elections,
                           results=results_data, turnout=turnout)

# ── PWA ──────────────────────────────────────────────────
@app.route('/manifest.json')
def manifest():
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    from flask import send_from_directory
    return send_from_directory('static', 'service-worker.js',
                               mimetype='application/javascript')

if __name__ == '__main__':
    app.run(debug=True, port=5009)