import datetime
import hashlib
import io
import os
import random
import logging

from flask import g
from flask import json
from flask import redirect
from flask import render_template, jsonify
from flask import request
from flask import session
from flask import url_for
from flask_security import current_user

from sdv import imageDrone
from sdv.bigbase import dec2big
from sdv.farmInfo import getFarmInfo
from sdv.models import Save, db, Serial, Task
from sdv.playerInfo import playerInfo
from sdv.savefile import SaveFile
from sdv.zipuploads import zwrite
from . import frontend
from .forms import FarmUploadForm

from config import config

logger = logging.getLogger('frontend')


@frontend.errorhandler(404)
def error_404():
    """ Error handler for Page Not Found Errors. """
    pass


@frontend.errorhandler(500)
def error_500():
    """ Error handler for Internal Server Errors. """
    pass


@frontend.route('/')
def index():
    """ Homepage for Upload Farm. """
    pass


@frontend.route('/<url>/')
def display_farm(url):
    """ Display rendered farm. """
    pass


@frontend.route('/browse/')
def browse_farms():
    """ Browse all uploaded farms. """
    pass


@frontend.route('/blog/')
def blog():
    """ Browse blog posts. """
    pass


@frontend.route('/blog/<id>')
def blog_post(id):
    """ View specific blog post. """
    pass


@frontend.route('/faq/')
def faq():
    """ Frequently asked questions. """
    pass


@frontend.route('/plan/<url>/')
def display_plan(url):
    """ Render an plan uploaded from Stardew.Info """
    pass


@frontend.route('/imgur/')
def imgur():
    """ Upload render to Imgur. """
    pass


@frontend.route('/account/')
def account_page():
    """ Account information. """
    pass
