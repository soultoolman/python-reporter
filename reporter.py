# -*- coding: utf-8 -*-
"""
python-reporter:
"""
import os
import sys
import json
import codecs
import logging
from uuid import UUID, uuid4
from collections import OrderedDict


logger = logging.getLogger('reporter')


def get_enc():
    return sys.getfilesystemencoding() or sys.getdefaultencoding()


class ReporterError(Exception):
    """all reporter exceptions"""


class Backend(object):
    def load(self, report_id):
        raise NotImplemented(f'load method of {self.__class__.__name__} not implement.')

    def save(self, report_id, data):
        raise NotImplemented(f'save method of {self.__class__.__name__} not implement.')


class FileBackend(Backend):
    def __init__(self, reporter_dir=None):
        if reporter_dir is None:
            reporter_dir = os.environ.get('REPORTER_DIR', '.')
        if not os.path.exists(reporter_dir):
            os.makedirs(reporter_dir)
        self._reporter_dir = reporter_dir

    @staticmethod
    def get_report_filename(report_id):
        return f'reporter-report-{report_id}.json'

    def get_report_file(self, report_id):
        return os.path.join(self._reporter_dir, self.get_report_filename(report_id))

    def report_exists(self, report_id):
        report_file = self.get_report_file(report_id)
        return os.path.exists(report_file)

    def load(self, report_id):
        if not self.report_exists(report_id):
            raise ReporterError(f"Report {self.get_report_file(report_id)} doesn't exist.")
        try:
            with codecs.open(self.get_report_file(report_id), encoding=get_enc()) as fp:
                return json.load(fp)
        except Exception as exc:
            logger.exception(exc)
            raise ReporterError(f"Can't read file {self.get_report_file(report_id)}")

    def save(self, report_id, data):
        with codecs.open(self.get_report_file(report_id), 'w', encoding=get_enc()) as fp:
            json.dump(data, fp)


class Report(object):
    def __init__(self, report_id=None, backend=None):
        if report_id is None:
            report_id = uuid4().hex
        try:
            UUID(report_id)
        except ValueError as exc:
            raise ReporterError(exc)
        self.report_id = report_id

        # backend
        if not backend:
            backend = FileBackend()
        self.backend = backend

        # initialize empty data dict
        self._data = OrderedDict()

    def __repr__(self):
        return f'<Report: {self.report_id}>'

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        return item in self._data

    def add(self, name, value):
        # must be serializable
        try:
            json.dumps(value)
        except TypeError as exc:
            raise ReporterError(exc)

        # print warning message if already in report
        if name in self._data:
            logger.warning(f'Overwrite existed variable {name}.')

        self._data[name] = value
        return self

    @staticmethod
    def _check(other):
        if not (isinstance(other, tuple) or isinstance(other, list)):
            raise ReporterError(f'Invalid type {other.__class__.__name__}, must be list or tuple.')
        if len(other) != 2:
            raise ReporterError('Invalid list or tuple, length must be 2.')
        if not isinstance(other[0], str):
            raise ReporterError(f'First element of list or tuple must be str, not {other[0].__class__.__name__}')

    def __lshift__(self, other):
        self._check(other)
        return self.add(*other)

    def __add__(self, other):
        self._check(other)
        return self.add(*other)

    def __getattr__(self, item):
        return self.get(item)

    def __iter__(self):
        return iter(self._data.keys())

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def get(self, name):
        if name not in self._data:
            raise ReporterError(f'{name} not in report.')
        return self._data[name]

    def pop(self, name):
        if name not in self._data:
            raise ReporterError(f'{name} not in report.')
        return self._data.pop(name)

    def load(self):
        self._data = self.backend.load(self.report_id)

    def save(self):
        self.backend.save(self.report_id, self._data)
        return self.report_id
