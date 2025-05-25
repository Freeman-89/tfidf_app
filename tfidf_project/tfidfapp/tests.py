from django.test import TestCase, Client
from django.contrib.auth.models import User

class UploadFileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/'

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_get_upload_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tfidfapp/base.html')

    def test_post_upload_viev(self):
        response = self.client.post(self.url, follow=True)  # следовать редиректу
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tfidfapp/base.html')
