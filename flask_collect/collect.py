# coding: utf-8

"""Define *Flask* extension."""

from flask._compat import string_types
from werkzeug.utils import import_string
from os import path as op


class Collect(object):

    """Extension object for integration to one or more Flask applications.

    :param app: Flask application

    .. code-block:: python

        app = Flask(__name__)
        collect = Collect(app)

    The second possibility is to create the object once and configure the
    application later to support it:

    .. code-block:: python

        collect = Collect()
        ...
        collect.init_app(app)

    """

    def __init__(self, app=None):
        """Initilize the extension object."""
        self.app = None
        self.static_root = None
        self.static_url = None
        self.storage = None
        self.filter = None
        self.blueprints = None
        self.add_hash = False
        self.hash_values = None
        self.hashed_files_index = None
        self.ignore = set()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize an application for the use with this collect setup.

        See :ref:`configuration`.

        :param app: Flask application
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['collect'] = self

        self.app = app
        self.static_root = app.config.get(
            'COLLECT_STATIC_ROOT',
            op.join(
                app.root_path,
                'static')).rstrip('/')
        self.static_url = app.static_url_path

        self.storage = app.config.get(
            'COLLECT_STORAGE', 'flask.ext.collect.storage.file')

        filter_ = app.config.get('COLLECT_FILTER')
        if filter_ is not None and isinstance(filter_, string_types):
            filter_ = import_string(filter_)
        self.filter = filter_ if filter_ is not None else list

        self.ignore = set(app.config.get('COLLECT_IGNORE', '').split(','))
        self.ignore.discard('')

        # Save link on blueprints
        self.blueprints = app.blueprints

        self.add_hash = not app.config.get('DEBUG', True)
        self.hashed_files_index = app.config.get('HASHED_FILE_INDEX', 'hashed_file_index.json')
        self.hash_values = {}

    def init_script(self, manager):
        """Initialize collect scripts with `Flask-Script`_ manager instance.

        :param manager: `Flask-Script`_ manager

        This added manager collect command:

        .. code-block:: console

            $ ./manage.py collect -h
            usage: ./manage.py collect [-h] [-v]

            Collect static from blueprints.

            optional arguments:
            -h, --help     show this help message and exit
            -v, --verbose

        .. _Flask-Script: http://packages.python.org/Flask-Script/
        """
        def collect(verbose=True):
            """Collect static from blueprints."""
            return self.collect(verbose=verbose)

        manager.command(collect)

    def collect(self, verbose=False):
        """Collect static files from blueprints.

        :param verbose: Show debug information.
        """
        mod = import_string(self.storage)
        cls = getattr(mod, 'Storage')
        storage = cls(self, verbose=verbose)
        return storage.run()
