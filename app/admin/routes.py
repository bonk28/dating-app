from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.models import User, Match, Message, Report
from app import db
from datetime import datetime

def init_admin(app):
    
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return "Accès refusé", 403
        
        stats = {
            'total_users': User.query.count(),
            'total_matches': Match.query.count(),
            'total_messages': Message.query.count(),
            'reports': Report.query.filter_by(is_resolved=False).count(),
            'new_today': User.query.filter(
                User.created_at >= datetime.now().date()
            ).count(),
            'active_today': User.query.filter(
                User.last_seen >= datetime.now().date()
            ).count()
        }
        
        users = User.query.order_by(User.created_at.desc()).limit(20).all()
        recent_matches = Match.query.order_by(Match.created_at.desc()).limit(10).all()
        pending_reports = Report.query.filter_by(is_resolved=False).all()
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             users=users,
                             recent_matches=recent_matches,
                             pending_reports=pending_reports)
    
    @app.route('/admin/user/<int:user_id>/toggle')
    @login_required
    def toggle_user(user_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Non autorisé'}), 403
        
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({'success': True, 'is_active': user.is_active})
    
    @app.route('/admin/report/<int:report_id>/resolve')
    @login_required
    def resolve_report(report_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Non autorisé'}), 403
        
        report = Report.query.get_or_404(report_id)
        report.is_resolved = True
        db.session.commit()
        
        return jsonify({'success': True})
