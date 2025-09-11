from flask import Flask, render_template
from database.db import init_db
# from routes.health_routes import health_bp
# from routes.prediction_routes import prediction_bp
# from routes.alert_routes import alert_bp

def create_app():
    app = Flask(__name__)
    
    # Initialize DB
    init_db(app)
    
    # Register routes
    # app.register_blueprint(health_bp, url_prefix="/api/health")
    # app.register_blueprint(prediction_bp, url_prefix="/api/predict")
    # app.register_blueprint(alert_bp, url_prefix="/api/alerts")
    
    @app.route("/")
    def home():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
