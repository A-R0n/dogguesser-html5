from flask import Flask,flash,render_template, request, redirect, url_for,make_response,jsonify
import boto3
from boto3.s3.transfer import TransferConfig
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import logging
from guess_dog import guess_dog
import time

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/app/static'

logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['SESSION_TYPE'] = 'filesystem'
application.secret_key="anystringhere"

def upload_file_to_s3(file, acl="public-read"):
    print(f'attempting to upload')
    # loop = asyncio.get_event_loop()
    # filename = secure_filename(file.filename)
    config = TransferConfig(multipart_threshold=1024*250, max_concurrency=10, multipart_chunksize=1024*250, use_threads=True)
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(
            file,
            'dogguesser',
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            },
            Config=config
        )
    except Exception as e:
        application.logger.warning(f'Something Happened: {e}')

    print(f'returning success')
    return "success"

@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def provide_dog_guess(guess: dict):
    return jsonify(guess)

@application.route("/change_label", methods=["POST"])
async def change_label():
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
        output = upload_file_to_s3(file)
        # output = True
        if output == 'success':
            return jsonify({"guess": dog_guessed, "visibility": "visible"})
        else:
            return jsonify({"guess": 'No output', "visibility": "visible"})
    #Return the text you want the label to be
    return jsonify({"guess": "None", "visibility": "visible"})
    # return message

if __name__ == "__main__":
      application.run(host='0.0.0.0', port='8080')
    #   application.run(host='0.0.0.0', port='8080', debug=True)