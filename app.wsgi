import sys
import logging
 
sys.path.insert(0, '/var/www/dogguesser-html5')
sys.path.insert(0, '/var/www/dogguesser-html5/env/lib/python3.9/site-packages/')
 
# Set up logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

activate_this = '/var/www/dogguesser-html5/env/bin/activate_this.py'

with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

# Import and run the Flask app
from app import main
application = main()