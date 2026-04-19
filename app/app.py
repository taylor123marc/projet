from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hopital-yaounde-secret-2024')

# Configuration MySQL
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'hopital_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'HopitalYaounde2024!')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'hopital_yaounde')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ──────────────────────────────────────────────
# PAGE D'ACCUEIL
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ──────────────────────────────────────────────
# PRENDRE UN RENDEZ-VOUS
# ──────────────────────────────────────────────
@app.route('/rendez-vous', methods=['GET', 'POST'])
def prendre_rdv():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services ORDER BY nom")
    services = cur.fetchall()
    cur.execute("SELECT * FROM medecins ORDER BY nom")
    medecins = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        nom          = request.form['nom'].strip()
        prenom       = request.form['prenom'].strip()
        telephone    = request.form['telephone'].strip()
        email        = request.form.get('email', '').strip()
        service_id   = request.form['service_id']
        medecin_id   = request.form['medecin_id']
        date_rdv     = request.form['date_rdv']
        heure_rdv    = request.form['heure_rdv']
        motif        = request.form.get('motif', '').strip()

        # Validations simples
        if not all([nom, prenom, telephone, service_id, medecin_id, date_rdv, heure_rdv]):
            flash('Veuillez remplir tous les champs obligatoires.', 'danger')
            return render_template('rendez_vous.html', services=services, medecins=medecins)

        # Vérifier si le créneau est disponible
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id FROM rendez_vous
            WHERE medecin_id = %s AND date_rdv = %s AND heure_rdv = %s
            AND statut != 'annule'
        """, (medecin_id, date_rdv, heure_rdv))
        existant = cur.fetchone()

        if existant:
            flash('Ce créneau est déjà réservé. Veuillez choisir un autre horaire.', 'warning')
            cur.close()
            return render_template('rendez_vous.html', services=services, medecins=medecins)

        # Enregistrer le rendez-vous
        cur.execute("""
            INSERT INTO rendez_vous
            (nom, prenom, telephone, email, service_id, medecin_id, date_rdv, heure_rdv, motif)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nom, prenom, telephone, email, service_id, medecin_id, date_rdv, heure_rdv, motif))
        mysql.connection.commit()
        rdv_id = cur.lastrowid
        cur.close()

        flash(f'Votre rendez-vous a été enregistré avec succès ! Référence : RDV-{rdv_id:05d}', 'success')
        return redirect(url_for('confirmation', rdv_id=rdv_id))

    return render_template('rendez_vous.html', services=services, medecins=medecins)

# ──────────────────────────────────────────────
# CONFIRMATION
# ──────────────────────────────────────────────
@app.route('/confirmation/<int:rdv_id>')
def confirmation(rdv_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.*, s.nom AS service_nom, m.nom AS medecin_nom, m.prenom AS medecin_prenom
        FROM rendez_vous r
        JOIN services s ON r.service_id = s.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.id = %s
    """, (rdv_id,))
    rdv = cur.fetchone()
    cur.close()
    if not rdv:
        flash('Rendez-vous introuvable.', 'danger')
        return redirect(url_for('index'))
    return render_template('confirmation.html', rdv=rdv)

# ──────────────────────────────────────────────
# CONSULTER / ANNULER UN RENDEZ-VOUS
# ──────────────────────────────────────────────
@app.route('/mes-rendez-vous', methods=['GET', 'POST'])
def mes_rdv():
    rdvs = []
    telephone_recherche = ''
    if request.method == 'POST':
        telephone_recherche = request.form['telephone'].strip()
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT r.*, s.nom AS service_nom, m.nom AS medecin_nom, m.prenom AS medecin_prenom
            FROM rendez_vous r
            JOIN services s ON r.service_id = s.id
            JOIN medecins m ON r.medecin_id = m.id
            WHERE r.telephone = %s
            ORDER BY r.date_rdv DESC, r.heure_rdv DESC
        """, (telephone_recherche,))
        rdvs = cur.fetchall()
        cur.close()
        if not rdvs:
            flash('Aucun rendez-vous trouvé pour ce numéro.', 'info')
    return render_template('mes_rdv.html', rdvs=rdvs, telephone=telephone_recherche)

@app.route('/annuler/<int:rdv_id>', methods=['POST'])
def annuler_rdv(rdv_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE rendez_vous SET statut = 'annule' WHERE id = %s", (rdv_id,))
    mysql.connection.commit()
    cur.close()
    flash('Votre rendez-vous a été annulé.', 'success')
    return redirect(url_for('mes_rdv'))

# ──────────────────────────────────────────────
# ADMIN – LISTE DES RENDEZ-VOUS DU JOUR
# ──────────────────────────────────────────────
@app.route('/admin')
def admin():
    # Authentification simple par session (admin/admin123)
    if not session.get('admin'):
        return redirect(url_for('login'))

    filtre_date = request.args.get('date', date.today().isoformat())
    filtre_service = request.args.get('service', '')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services ORDER BY nom")
    services = cur.fetchall()

    query = """
        SELECT r.*, s.nom AS service_nom, m.nom AS medecin_nom, m.prenom AS medecin_prenom
        FROM rendez_vous r
        JOIN services s ON r.service_id = s.id
        JOIN medecins m ON r.medecin_id = m.id
        WHERE r.date_rdv = %s
    """
    params = [filtre_date]
    if filtre_service:
        query += " AND r.service_id = %s"
        params.append(filtre_service)
    query += " ORDER BY r.heure_rdv"

    cur.execute(query, params)
    rdvs = cur.fetchall()
    cur.close()

    return render_template('admin.html', rdvs=rdvs, services=services,
                           filtre_date=filtre_date, filtre_service=filtre_service)

@app.route('/admin/statut/<int:rdv_id>/<statut>', methods=['POST'])
def changer_statut(rdv_id, statut):
    if not session.get('admin'):
        return redirect(url_for('login'))
    if statut in ['confirme', 'annule', 'en_attente']:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE rendez_vous SET statut = %s WHERE id = %s", (statut, rdv_id))
        mysql.connection.commit()
        cur.close()
    return redirect(request.referrer or url_for('admin'))

# ──────────────────────────────────────────────
# LOGIN ADMIN
# ──────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'Admin2024!':
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Identifiants incorrects.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

# ──────────────────────────────────────────────
# API – médecins par service (AJAX)
# ──────────────────────────────────────────────
@app.route('/api/medecins/<int:service_id>')
def api_medecins(service_id):
    from flask import jsonify
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nom, prenom, specialite FROM medecins WHERE service_id = %s AND actif = 1", (service_id,))
    medecins = cur.fetchall()
    cur.close()
    return jsonify(medecins)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
