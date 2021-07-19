from django.test import Client, TestCase


class SiteTestCase(TestCase):

    def setUp(self):
        pass

    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
