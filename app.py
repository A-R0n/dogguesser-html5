from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from guess_dog import guess_dog
from upload_file_to_s3 import upload_file_to_s3
import toml
import os


logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

p ='config.toml'
# p ="/home/ec2-user/app/config.toml"
with open(p, "r") as f:
    config = toml.load(f)

application.config.from_object(config)
application.config.secret_key = os.urandom(24)


@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config['app']['allowed_extensions']


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
        dog_guessed = guess_dog(file)
        upload_file_to_s3(file)
        return jsonify({"guess": dog_guessed, "visibility": "visible"})
    return jsonify({"guess": "None", "visibility": "visible"})


if __name__ == "__main__":
    # application.run(host=config['app']['host'], port=config['app']['port'])
    application.run(host=config['app']['host'], port=config['app']['port'], debug=True)
