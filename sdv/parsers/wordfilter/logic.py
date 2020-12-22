try:
    import os
    import random
    import re
    from flask import request
    from jinja2 import Markup
except ImportError:
    print("Missing dependencies")

WORDLIST = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "data", "wordlist.txt"
)
CENSORCHARS = "!$%^&*#"


class Censor:
    def __init__(self, app=None, wordlist=WORDLIST, censorchars=CENSORCHARS):
        if app != None:
            self.init_app(app=app)
        else:
            self.import_wordlist(wordlist)
            self.set_censorchars(censorchars)
            self._refresh_pool()

    def init_app(self, app=None):
        self.__init__(
            wordlist=app.config.get("CENSOR_WORDLIST", WORDLIST),
            censorchars=app.config.get("CENSORCHARS", CENSORCHARS),
        )

        @app.template_filter("censor")
        def censor_filter(text):
            return self.censor(text)

    def import_wordlist(self, wordlist):
        with open(wordlist, "r") as f:
            self.words = set([word.strip() for word in f.readlines()])

    def censor(self, input_string):
        self._temp_string = input_string
        for word in self.words:
            regex = re.compile(re.escape(word), re.IGNORECASE)
            try:
                self._temp_string = regex.sub(
                    self._get_redacted_string(word), self._temp_string
                )
            except TypeError:
                pass
        return self._temp_string

    def set_censorchars(self, censorchars):
        self.censorchars = list(censorchars)

    def _refresh_pool(self):
        self._pool = list(self.censorchars)

    def _get_from_pool(self):
        if not len(self._pool):
            self._refresh_pool()
        return self._pool.pop(random.randrange(len(self._pool)))

    def _get_redacted_string(self, word):
        random.seed(word)
        self._refresh_pool()
        return "".join([self._get_from_pool() for i in word])
