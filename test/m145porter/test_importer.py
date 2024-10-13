from test.mocking_helper import mock_imports

mock_imports(["M145Porter"])

from unittest import TestCase
from m145porter._import import fzahl


class TestM145Porter(TestCase):
    def test_fzahl(self):
        ret = fzahl(text="1")
        self.assertEqual(ret, 1.0)
