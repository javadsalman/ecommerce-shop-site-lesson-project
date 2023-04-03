from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.

class LoginTest(TestCase):
    login_url = reverse('customer:login')
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('eli', 'eli@gmail.com', '1234')
        
    def test_get(self):
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_wrong_login(self):
        response = self.client.post(
            self.login_url,
            {'username': 'eli', 'password': '12asdfasd34'}
        )
        print(response.status_code)
        self.assertNotEqual(response.status_code, 302)
        if response.status_code != 302:
            self.assertIn('unsuccess', response.context)
            self.assertTrue(response.context['unsuccess'])
    
    def test_correct_not_next_login(self):
        response = self.client.post(
            self.login_url,
            {'username': 'eli', 'password': '1234'}
        )
        home_url = reverse('ecommerce:home')
        self.assertRedirects(response, home_url)


    def test_correct_next_login(self):
        response = self.client.post(
            self.login_url + '?next=' + reverse('customer:contact'),
            {'username': 'eli', 'password': '1234'}
        )
        nextUrl = response.wsgi_request.GET.get('next')
        self.assertRedirects(response, nextUrl, msg_prefix='Urldeki linke getmeli idi')
        
    
        