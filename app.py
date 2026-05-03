import logging
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.before_request
def log_request():
    logger.info(request.path)


@app.route('/')
def index():
    return 'Hello'


if __name__ == '__main__':
    app.run()
