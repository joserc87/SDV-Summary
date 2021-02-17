import os
import tempfile

import pytest

from sdv import app
from sdv.createdb import init_db

@pytest.fixture
def working_sqlite():
    assert app.config.get('USE_SQLITE'), \
        'For safety, we only run tests on sqlite. Check config.py USE_SQLITE in TestConfig'
    init_db(no_prompt=True)


@pytest.fixture
def client(working_sqlite):
    assert app.config.get('USE_SQLITE'), \
        'For safety, we only run tests on sqlite. Check config.py USE_SQLITE in TestConfig'

    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            # flaskr.init_db()
            pass
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_root_loaded(client):
    rv = client.get('/')
    text = rv.data.decode()
    title = '<title>upload.farm Stardew Valley Summary Generator</title>'
    assert title in text
