# igenwo.py
from flask import Flask, g, render_template
from config import config
from app.models import db
from app.blueprint.auth import auth
from app.blueprint.views import flask_app
from app.blueprint.api import api_v1


def create_app():
    app = Flask(__name__, static_folder=config.static_folder)
    app.config.from_object(config)
    app.register_blueprint(auth)
    app.register_blueprint(flask_app)
    app.register_blueprint(api_v1)

    db.init_app(app)

    @app.teardown_appcontext
    def colse_db(error):
        if hasattr(g, 'cnn'):
            g.cnn.close()
        db.session.close()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=80)
