# -*- coding: utf-8 -*-
import os
import uuid
import tempfile

import pytest

import reporter


class TestFileBackend(object):
    def test_reporter_dir1(self):
        backend = reporter.FileBackend()
        assert backend._reporter_dir == '.'

    def test_reporter_dir2(self):
        with tempfile.TemporaryDirectory() as tempdir:
            os.environ['REPORTER_DIR'] = tempdir
            backend = reporter.FileBackend()
            assert backend._reporter_dir == tempdir

    def test_reporter_dir3(self):
        with tempfile.TemporaryDirectory() as tempdir:
            backend = reporter.FileBackend(tempdir)
            assert backend._reporter_dir == tempdir

    def test_reporter_dir4(self):
        with tempfile.TemporaryDirectory() as tempdir:
            reporter_dir = os.path.join(tempdir, 'reporter')
            assert not os.path.exists(reporter_dir)
            reporter.FileBackend(reporter_dir)
            assert os.path.exists(reporter_dir)

    def test_get_report_filename(self):
        report = reporter.FileBackend()
        assert report.get_report_filename('123') == 'reporter-report-123.json'

    def test_get_report_file(self):
        if 'REPORTER_DIR' in os.environ:
            del os.environ['REPORTER_DIR']
        report = reporter.FileBackend()
        assert report.get_report_file('123') == './reporter-report-123.json'

    def test_report_exists(self):
        with tempfile.TemporaryDirectory() as tempdir:
            backend = reporter.FileBackend(tempdir)
            assert not backend.report_exists('123')
            with open(os.path.join(tempdir, 'reporter-report-123.json'), 'w') as fp:
                pass
            assert backend.report_exists('123')

    def test_load1(self):
        with pytest.raises(reporter.ReporterError):
            with tempfile.TemporaryDirectory() as tempdir:
                backend = reporter.FileBackend(tempdir)
                backend.load('123')

    def test_load2(self):
        with tempfile.TemporaryDirectory() as tempdir:
            backend = reporter.FileBackend(tempdir)
            with open(os.path.join(tempdir, 'reporter-report-123.json'), 'w') as fp:
                fp.write('{"foo": "bar"}')
            data = backend.load('123')
            assert len(data) == 1
            assert data['foo'] == 'bar'

    def test_save(self):
        with tempfile.TemporaryDirectory() as tempdir:
            backend = reporter.FileBackend(tempdir)
            backend.save('123', {'foo': 'bar'})
            data = backend.load('123')
            assert len(data) == 1
            assert data['foo'] == 'bar'


class TestReport(object):
    def test_init_report_id1(self):
        with pytest.raises(reporter.ReporterError):
            reporter.Report('123')

    def test_init_report_id2(self):
        report = reporter.Report()
        try:
            uuid.UUID(report.report_id)
        except reporter.ReporterError as exc:
            pytest.fail('unexpected error %s' % exc)

    def test_init_report_backend1(self):
        if 'REPORTER_DIR' in os.environ:
            del os.environ['REPORTER_DIR']
        report = reporter.Report()
        assert isinstance(report.backend, reporter.FileBackend)
        assert report.backend._reporter_dir == '.'

    def test_repr(self):
        report_id = uuid.uuid4().hex
        string = '<Report: %s>' % report_id
        report = reporter.Report(report_id)
        assert str(report) == string

    def test_len(self):
        report = reporter.Report()
        assert len(report) == 0
        report << ('foo', 'bar')
        assert len(report) == 1

    def test_contains(self):
        report = reporter.Report()
        report << ('foo', 'bar')

        assert 'foo' in report
        assert 'bar' not in report

    def test_add1(self):
        report = reporter.Report()
        with pytest.raises(reporter.ReporterError):
            class A:
                pass
            report.add('foo', A())

    def test_add2(self):
        report = reporter.Report()
        report.add('foo', 'bar')
        assert report.get('foo') == 'bar'

    def test_check(self):
        report = reporter.Report()
        with pytest.raises(reporter.ReporterError):
            report._check('a')
        with pytest.raises(reporter.ReporterError):
            report._check([1, 2, 3])
        with pytest.raises(reporter.ReporterError):
            report._check([1, 2])

        try:
            report._check(['foo', 'bar'])
        except reporter.ReporterError as exc:
            pytest.fail('unexpected error %s' % exc)

    def test_lshift(self):
        report = reporter.Report()
        report << ('foo', 'bar')
        assert report.foo == 'bar'

    def test_add_and_getattr(self):
        report = reporter.Report()
        report + ('foo', 'bar')
        assert report.foo == 'bar'

    def test_iter(self):
        report = reporter.Report()
        report << ('foo', 'bar')

        assert list(iter(report)) == ['foo']

    def test_keys(self):
        report = reporter.Report()
        report << ('foo', 'bar')

        assert list(report.keys()) == ['foo']

    def test_values(self):
        report = reporter.Report()
        report << ('foo', 'bar')

        assert list(report.values()) == ['bar']

    def test_items(self):
        report = reporter.Report()
        report << ('foo', 'bar')

        assert list(report.items()) == [('foo', 'bar')]

    def test_get(self):
        report = reporter.Report()
        with pytest.raises(reporter.ReporterError):
            report.get('foo')
        report << ('foo', 'bar')
        assert report.get('foo') == 'bar'

    def test_pop(self):
        report = reporter.Report()
        with pytest.raises(reporter.ReporterError):
            report.pop('foo')
        report << ('foo', 'bar')
        assert report.pop('foo') == 'bar'

    def test_load(self):
        with tempfile.TemporaryDirectory() as tempdir:
            report_id = uuid.uuid4().hex
            report_file = os.path.join(tempdir, f'reporter-report-{report_id}.json')
            with open(report_file, 'w') as fp:
                fp.write('{"foo": "bar"}')
            backend = reporter.FileBackend(tempdir)
            report = reporter.Report(report_id, backend)
            assert len(report) == 0
            report.load()
            assert len(report) == 1
            assert 'foo' in report

    def test_save(self):
        with tempfile.TemporaryDirectory() as tempdir:
            report_id = uuid.uuid4().hex
            backend = reporter.FileBackend(tempdir)
            report = reporter.Report(report_id, backend)
            report << ('foo', 'bar')
            report.save()
            report_file = os.path.join(tempdir, f'reporter-report-{report_id}.json')
            with open(report_file) as fp:
                assert fp.read() == '{"foo": "bar"}'
