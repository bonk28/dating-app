import os
import os
from app import create_app, db, socketio
from app.admin.routes import init_admin
from app.achievements import create_default_achievements

app = create_app()
init_admin(app)

with app.app_context():
    db.create_all()
    create_default_achievements()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
