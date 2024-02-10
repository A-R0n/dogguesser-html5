from flask import Flask,flash,render_template, request, redirect, url_for,make_response,jsonify
import boto3
from boto3.s3.transfer import TransferConfig
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import logging
from guess_dog import guess_dog

class LabelClass:
    def __init__(self):
        self.label = None

lc = LabelClass()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/app/static'

data = {
    "guess": "N/A",
    "visibility": "hidden"
}

logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['SESSION_TYPE'] = 'filesystem'
application.secret_key="anystringhere"

# @app.route("/")
# def index():
#     return "<h1 style='color:blue'> A very simple Flask server!</h1>"

def upload_file_to_s3(file, acl="public-read"):
    print(f'attempting to upload')
    filename = secure_filename(file.filename)
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
        ## if we do this below, then that means even the root user cant look at the image
    # try:
    #     s3.upload_fileobj(
    #         file,
    #         'dogguesser',
    #         file.filename
    #     )
    except Exception as e:
        application.logger.warning(f'Something Happened: {e}')
    # return file.filename


@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route("/change_label", methods=["POST", "GET"])
def change_label():
    global lc
    guess = str(lc.label)
    file = request.files['user_file']
    if file and allowed_file(file.filename):
        print(f'fileeeee {file}')
        dog_guessed = guess_dog(file)
        upload_file_to_s3(file)

        return jsonify({"guess": dog_guessed, "visibility": "visible"})
    #Return the text you want the label to be
    return jsonify({"guess": guess, "visibility": "visible"})
    # return message


@application.route("/upload", methods=["POST"])
def create():
    global lc
    print(f'inside create')
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
        ## this is a `<FilStorage: 'daniel_dog.JPG ('image/jpeg')` object
        ## https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html
        print(file)
        # output = upload_file_to_s3(file)
        output = None
        dog_guessed = guess_dog(file)
        data = {"guess": dog_guessed, "visibility": "visible"}
        lc.label = dog_guessed

        if output:
            flash("Success upload")
            ## we need to send our dog_guessed variable to a p tag in our html
            return 'nice'
        else:
            flash("Unable to upload, try again")
            return redirect(url_for('change_label'))
        
    else:
        flash("File type not accepted,please try again.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    # application.run(host='0.0.0.0', port='8080')
      application.run(host='0.0.0.0', port='8080')