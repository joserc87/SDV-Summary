from sdv import create_app
import unittest


class SDVTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')

        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()
