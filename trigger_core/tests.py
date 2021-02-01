from django.test import TestCase
from trigger_core.services.trigger_actions import script as scripting

class ScriptActionTestCase(TestCase):

    def test_simple_script(self):
        script = """msg = "hello " + context["name"]\nprint(msg)\nreturn msg"""
        conf = {
            "slug": 'test_xyz_slug',
            "script": script
        }
        self.assertEqual(scripting(conf, {"name": 'jeff'}), 'hello jeff')
        self.assertEqual(scripting(conf, {"name": 'limit'}), 'hello limit')
    
    def test_script_change(self):
        script = """msg = "hello " + context["name"]\nprint(msg)\nreturn msg"""
        conf = {
            "slug": 'test_xyz_slug',
            "script": script
        }
        self.assertEqual(scripting(conf, {"name": 'jeff'}), 'hello jeff')
        script = """msg = "heyhey " + context["name"]\nprint(msg)\nreturn msg"""
        conf['script'] = script
        self.assertEqual(scripting(conf, {"name": 'limit'}), 'heyhey limit')
