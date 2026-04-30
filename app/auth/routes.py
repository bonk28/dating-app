from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.models import User

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        
        print(f"📝 Tentative d'inscription : {username}, {email}")
        
        # Validation simple
        if not username or not email or not password:
            print("❌ Champs vides")
            flash('Tous les champs sont obligatoires.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            print("❌ Username déjà pris")
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            print("❌ Email déjà utilisé")
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            user = User(username=username, email=email, age=age or 18, gender=gender or 'autre')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"✅ Utilisateur créé : {username}")
            login_user(user)
            flash('Bienvenue ' + username + ' !', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            print(f"❌ Erreur DB : {e}")
            flash('Erreur lors de la création du compte.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            print(f"✅ Connexion : {username}")
            return redirect(url_for('main.dashboard'))
        
        flash('Identifiants incorrects.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
