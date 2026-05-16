from flask import Flask, request
import logging

app = Flask(__name__)
logger = logging.getLogger('app')


@app.before_request
def log_request():
    logger.info(f'Request path: {request.path}')


@app.route('/health')
def health_check():
    return 'OK', 200