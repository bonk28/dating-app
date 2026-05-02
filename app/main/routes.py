from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user, logout_user
from app import db
from app.main import bp
from app.models import User, Like, Match, Message, UserPhoto, Report, Story, UserAchievement, Defi, DefiParticipant, DefiVote
from werkzeug.utils import secure_filename
import os, random
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    liked_ids = [like.liked_id for like in current_user.likes_sent.all()]
    liked_ids.append(current_user.id)
    potential = User.query.filter(~User.id.in_(liked_ids), User.is_active == True)
    if current_user.looking_for:
        potential = potential.filter(User.gender == current_user.looking_for)
    matches = potential.all()
    for match in matches:
        if current_user.latitude and current_user.longitude and match.latitude and match.longitude:
            lat1, lon1 = radians(current_user.latitude), radians(current_user.longitude)
            lat2, lon2 = radians(match.latitude), radians(match.longitude)
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            match.distance = int(6371 * c)
        match.compatibility = current_user.get_compatibility(match)
    matches.sort(key=lambda x: x.compatibility, reverse=True)
    return render_template('dashboard.html', matches=matches[:30], current_user=current_user)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio')
        current_user.interests = request.form.get('interests')
        current_user.location = request.form.get('location')
        current_user.looking_for = request.form.get('looking_for')
        current_user.signe = request.form.get('signe')
        current_user.animal = request.form.get('animal')
        current_user.voyage = request.form.get('voyage')
        current_user.pays = request.form.get('pays')
        current_user.serie = request.form.get('serie')
        current_user.musique = request.form.get('musique')
        current_user.plat = request.form.get('plat')
        current_user.loisir = request.form.get('loisir')
        current_user.profession = request.form.get('profession')
        current_user.citation = request.form.get('citation')
        current_user.max_distance = request.form.get('max_distance', 50, type=int)
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = secure_filename(f"{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                photo = UserPhoto(filename=filename, user_id=current_user.id, is_primary=not current_user.photos.first())
                db.session.add(photo)
                current_user.photo = filename
        db.session.commit()
        flash('Profil mis à jour !', 'success')
        return redirect(url_for('main.profile'))
    from app.models import Match; match_count = Match.query.filter((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)).count(); return render_template('profile.html', user=current_user, match_count=match_count)

@bp.route('/matches')
@login_required
def matches():
    user_matches = Match.query.filter(((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)), Match.is_active == True).order_by(Match.created_at.desc()).all()
    matched_users = []
    for match in user_matches:
        other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
        other_user = User.query.get(other_id)
        if other_user:
            last_msg = Message.query.filter_by(match_id=match.id).order_by(Message.created_at.desc()).first()
            unread = Message.query.filter_by(match_id=match.id, sender_id=other_id, is_read=False).count()
            matched_users.append({'user': other_user, 'match': match, 'last_message': last_msg, 'unread': unread})
    return render_template('matches.html', matched_users=matched_users)

@bp.route('/chat/<int:match_id>')
@login_required
def chat(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('main.matches'))
    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = User.query.get(other_id)
    messages_list = Message.query.filter_by(match_id=match.id).order_by(Message.created_at).all()
    from datetime import date
    today_date = date.today().strftime('%d/%m/%Y')
    return render_template('chat.html', match=match, other_user=other_user, messages=messages_list, today_date=today_date)



@bp.route('/profile/<int:user_id>')
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return redirect(url_for('main.profile'))
    compatibility = current_user.get_compatibility(user)
    distance = None
    if current_user.latitude and current_user.longitude and user.latitude and user.longitude:
        lat1, lon1 = radians(current_user.latitude), radians(current_user.longitude)
        lat2, lon2 = radians(user.latitude), radians(user.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = int(6371 * c)
    photos = UserPhoto.query.filter_by(user_id=user.id).all()
    existing_like = Like.query.filter_by(liker_id=current_user.id, liked_id=user.id).first()
    return render_template('view_profile.html', user=user, compatibility=compatibility, distance=distance, photos=photos, existing_like=existing_like)

@bp.route('/features')
@login_required
def features():
    return render_template('features.html')

@bp.route('/stories')
@login_required
def stories_page():
    return render_template('stories.html')

@bp.route('/blind-date')
@login_required
def blind_date():
    potential = User.query.filter(User.id != current_user.id, User.is_active == True).all()
    if potential:
        partner = random.choice(potential)
        match = Match(user1_id=min(current_user.id, partner.id), user2_id=max(current_user.id, partner.id), compatibility=random.randint(50, 100))
        db.session.add(match)
        db.session.commit()
        return redirect(url_for('main.blind_chat', match_id=match.id))
    flash('Personne disponible.', 'info')
    return redirect(url_for('main.dashboard'))

@bp.route('/blind-chat/<int:match_id>')
@login_required
def blind_chat(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return redirect(url_for('main.dashboard'))
    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = User.query.get(other_id)
    moods = ['🎭','🤔','😊','🎨','📚','🎵','✈️','🍕','🏃','💡']
    return render_template('blind_chat.html', match=match, other_user=other_user, moods=moods)

@bp.route('/quiz-page')
@login_required
def quiz_page():
    return render_template('quiz_page.html')

@bp.route('/icebreakers-page')
@login_required
def icebreakers_page():
    return render_template('icebreakers_page.html')

@bp.route('/achievements-page')
@login_required
def achievements_page():
    return render_template('achievements_page.html')

@bp.route('/events')
@login_required
def events_page():
    return render_template('events.html')

@bp.route('/daily-question-page')
@login_required
def daily_question_page():
    return render_template('daily_question.html')

@bp.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')

@bp.route('/top-profiles')
@login_required
def top_profiles():
    top = User.query.filter(User.id != current_user.id, User.is_active == True).order_by(User.last_seen.desc()).limit(10).all()
    return render_template('top_profiles.html', users=top)

@bp.route('/compliments')
@login_required
def compliments():
    comps = ["Ton sourire illumine ma journée ☀️","Tu as un humour incroyable 😄","J'adore ta façon de voir les choses 💭","Tes yeux sont magnifiques ✨","Tu es une personne intéressante 🌟"]
    return render_template('compliments.html', compliments=comps)

@bp.route('/my-stats')
@login_required
def my_stats():
    stats = {
        'total_likes_sent': Like.query.filter_by(liker_id=current_user.id).count(),
        'total_likes_received': Like.query.filter_by(liked_id=current_user.id).count(),
        'total_matches': Match.query.filter((Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)).count(),
        'total_messages': Message.query.filter_by(sender_id=current_user.id).count(),
        'swipes_today': Like.query.filter_by(liker_id=current_user.id).filter(Like.created_at >= datetime.now().date()).count(),
    }
    return render_template('my_stats.html', stats=stats)

@bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        password = request.form.get('password')
        if current_user.check_password(password):
            uid = current_user.id
            Like.query.filter((Like.liker_id == uid) | (Like.liked_id == uid)).delete()
            Match.query.filter((Match.user1_id == uid) | (Match.user2_id == uid)).delete()
            Message.query.filter_by(sender_id=uid).delete()
            UserPhoto.query.filter_by(user_id=uid).delete()
            Report.query.filter((Report.reporter_id == uid) | (Report.reported_id == uid)).delete()
            Story.query.filter_by(user_id=uid).delete()
            UserAchievement.query.filter_by(user_id=uid).delete()
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Compte supprimé.', 'info')
            return redirect(url_for('main.index'))
        flash('Mot de passe incorrect.', 'error')
    return render_template('delete_account.html')



@bp.route('/love-letter')
@login_required
def love_letter():
    return render_template('love_letter.html')



@bp.route('/night-mode')
@login_required
def night_mode():
    return render_template('night_mode.html')

@bp.route('/confessions')
@login_required
def confessions():
    return render_template('confessions.html')

@bp.route('/color-match')
@login_required
def color_match():
    return render_template('color_match.html')

@bp.route('/pet-match')
@login_required
def pet_match():
    return render_template('pet_match.html')

@bp.route('/hot-or-not')
@login_required
def hot_or_not():
    return render_template('hot_or_not.html')

@bp.route('/dj-match')
@login_required
def dj_match():
    return render_template('dj_match.html')

@bp.route('/love-weather')
@login_required
def love_weather():
    return render_template('love_weather.html')

@bp.route('/map')
@login_required
def map_view():
    return render_template('map.html')


@bp.route('/defis')
@login_required
def defis_page():
    defis = Defi.query.filter(Defi.is_active==True, Defi.expires_at > datetime.utcnow()).order_by(Defi.created_at.desc()).all()
    return render_template('defis.html', defis=defis)

@bp.route('/wall')
@login_required
def wall():
    return render_template('wall.html')

@bp.route('/about')
@login_required
def about():
    return render_template('about.html')

@bp.route('/call/video/<int:match_id>')
@login_required
def video_call(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return redirect(url_for('main.matches'))
    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = User.query.get(other_id)
    return render_template('video_call.html', match=match, other_user=other_user)

@bp.route('/call/voice/<int:match_id>')
@login_required
def voice_call(match_id):
    match = Match.query.get_or_404(match_id)
    if current_user.id not in [match.user1_id, match.user2_id]:
        return redirect(url_for('main.matches'))
    other_id = match.user2_id if match.user1_id == current_user.id else match.user1_id
    other_user = User.query.get(other_id)
    return render_template('voice_call.html', match=match, other_user=other_user)
