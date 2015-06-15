# -*- coding: utf-8 -*-
#
# This file is part of Flask-Collect.
# Copyright (C) 2012, 2014 Kirill Klenov.
# Copyright (C) 2014 CERN.
#
# Flask-Collect is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Copy files from all static folders to root folder."""

from os import path as op, makedirs, remove
from shutil import copy
import hashlib
import string
from .base import BaseStorage


class Storage(BaseStorage):

    """Storage that copies static files."""

    def run(self):
        """Collect static files from blueprints."""
        self.log("Collect static from blueprints.")

        for bp, f, o in self:
            destination = op.join(self.collect.static_root, o)

            destination_dir = op.dirname(destination)
            if not op.exists(destination_dir):
                makedirs(destination_dir)

            if op.exists(destination):

                if op.getmtime(destination) >= op.getmtime(f):
                    continue

                remove(destination)

            copy(f, destination)

            if self.collect.add_hash:
                # We'll also add a new file with a hashed component
                with open(destination) as f:
                    m = hashlib.sha224()
                    m.update(f.read())
                    hex_val = m.hexdigest()

                    pos = string.rfind(destination, '.')
                    if pos == -1:
                        hashed_destination = destination + hex_val
                    else:
                        hashed_destination = '%s.%s%s' % (destination[:pos], hex_val[:12], destination[pos:])

                    if not op.exists(hashed_destination):
                        copy(destination, hashed_destination)

                    self.log(
                        "Copied: [%s] '%s'" % (bp.name, op.join(self.collect.static_url, hashed_destination)))

            self.log(
                "Copied: [%s] '%s'" % (bp.name, op.join(self.collect.static_url, destination)))
