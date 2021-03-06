#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-02-22 14:00:05

import os
import time
import unittest

from processor import project_module
class TestProjectModule(unittest.TestCase):
    base_task = {
            'taskid': 'taskid',
            'project': 'test.project',
            'url': 'www.baidu.com/',
            'schedule': {
                'priority': 1,
                'retries': 3,
                'exetime': 0,
                'age': 3600,
                'itag': 'itag',
                'recrawl': 5,
                },
            'fetch': {
                'method': 'GET',
                'headers': {
                    'Cookie': 'a=b', 
                    },
                'data': 'a=b&c=d', 
                'timeout': 60,
                'save': [1, 2, 3],
                },
            'process': {
                'callback': 'callback',
                },
            }
    fetch_result = {
            'status_code': 200,
            'orig_url': 'www.baidu.com/',
            'url': 'http://www.baidu.com/',
            'headers': {
                'cookie': 'abc',
                },
            'content': 'test data',
            'cookies': {
                'a': 'b',
                },
            'save': [1, 2, 3],
            }

    def setUp(self):
        self.project = "test.project"
        self.script = open(os.path.join(os.path.dirname(__file__), 'data_handler.py')).read()
        self.env = {
                'test': True,
                }
        self.project_info = {
                'name': self.project,
                'status': 'DEBUG',
                }
        self.module = module = project_module.ProjectModule(self.project, self.script, self.env)
        module.rethrow()
        _class = module.get()
        self.instance = _class()._init(self.project_info)

    def test_2_hello(self):
        self.base_task['process']['callback'] = 'hello'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(ret.result, "hello world!")

    def test_3_echo(self):
        self.base_task['process']['callback'] = 'echo'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(ret.result, "test data")

    def test_4_saved(self):
        self.base_task['process']['callback'] = 'saved'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(ret.result, self.base_task['fetch']['save'])

    def test_5_echo_task(self):
        self.base_task['process']['callback'] = 'echo_task'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(ret.result, self.project)

    def test_6_catch_status_code(self):
        self.fetch_result['status_code'] = 403
        self.base_task['process']['callback'] = 'catch_status_code'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(ret.result, 403)
        self.fetch_result['status_code'] = 200

    def test_7_raise_exception(self):
        self.base_task['process']['callback'] = 'raise_exception'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNotNone(ret.exception)
        logstr = ret.logstr()
        self.assertIn('info', logstr)
        self.assertIn('warning', logstr)
        self.assertIn('error', logstr)

    def test_8_add_task(self):
        self.base_task['process']['callback'] = 'add_task'
        ret = self.instance.run(self.module, self.base_task, self.fetch_result)
        self.assertIsNone(ret.exception)
        self.assertEqual(len(ret.follows), 1)
        self.assertEqual(len(ret.messages), 1)
