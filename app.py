from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import logging
from guess_dog import guess_dog
from upload_file_to_s3 import upload_file_to_s3
from read_file_from_s3 import read_file_from_s3
import os
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if os.environ.get('FLASK_ENV') == 'production':
    print('were in prod')
    application.logger.warning('were in production')
    application.config.from_object('config.ProductionConfig')
else:
    print('were in dev')
    application.logger.warning('were in dev')
    application.config.from_object('config.DevelopmentConfig')


@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in application.config['ALLOWED_EXTENSIONS']


@application.route("/change_label", methods=["POST"])
def change_label():
    
    if 'user_file' not in request.files:
        application.logger.warning(f'uh oh')
        flash('No user_file key in request.files')
        return redirect(url_for('index'))
    
    file = request.files['user_file']

    if file.filename == '':
        application.logger.warning(f'oh no')
        flash('No selected file')
        return redirect(url_for('index'))


    if file and allowed_file(file.filename):
        new_file_name = upload_file_to_s3(file)
        img = read_file_from_s3(new_file_name)
        dog_guessed = guess_dog(img)
        return jsonify({"guess": dog_guessed, "visibility": "visible"})
    return jsonify({"guess": "None", "visibility": "visible"})


if __name__ == "__main__":
    application.run(
        host = application.config["HOST"],
        port = application.config["PORT"],
        debug = application.config["DEBUG"]
    )