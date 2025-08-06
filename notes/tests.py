from django.test import SimpleTestCase
class SmokeTest(SimpleTestCase):
    def test_homepage(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
