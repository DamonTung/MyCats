from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_sqlalchemy import SQLAlchemy

# import camera driver
os.environ['CAMERA'] = "opencv"
basedir = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera
print("CAMERA is -> " + os.environ['CAMERA'])
# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super_secret_salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'tmp/test.db')
# Create database connection object
db = SQLAlchemy(app)
# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='MYSELF_MAIL_ADDRESS', password='P@ssw0rd*#321')
    db.session.commit()

@app.route('/')
@login_required
def index():
    """Video streaming home page."""
    return render_template('index.html')
    


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/shutdown')
def shutdown_os():
    os.system('shutdown -s')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
