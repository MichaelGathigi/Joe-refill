from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import ContactMessage, Order


class PublicPagesTests(TestCase):
    def test_public_pages_render(self):
        for name in ['home', 'product', 'contact', 'login', 'register']:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_contact_form_saves_message(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Jane', 'email': 'jane@example.com', 'phone': '0712 345 678', 'message': 'Do you deliver to Mwatate?',
        })
        self.assertRedirects(response, reverse('contact'))
        msg = ContactMessage.objects.get()
        self.assertEqual(msg.phone, '0712345678')


class AuthTests(TestCase):
    def test_register_logs_user_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser', 'email': 'new@example.com',
            'password1': 'Refill!2024pass', 'password2': 'Refill!2024pass',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user('a', 'dup@example.com', 'x')
        response = self.client.post(reverse('register'), {
            'username': 'b', 'email': 'DUP@example.com',
            'password1': 'Refill!2024pass', 'password2': 'Refill!2024pass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='b').exists())

    def test_login_with_username_or_email(self):
        User.objects.create_user('joe', 'joe@example.com', 'Refill!2024pass')
        for identifier in ['joe', 'joe@example.com']:
            with self.subTest(identifier=identifier):
                response = self.client.post(reverse('login'), {'username': identifier, 'password': 'Refill!2024pass'})
                self.assertRedirects(response, reverse('home'))
                self.client.post(reverse('logout'))

    def test_login_redirects_to_next(self):
        User.objects.create_user('joe', 'joe@example.com', 'Refill!2024pass')
        response = self.client.post(reverse('login'), {
            'username': 'joe', 'password': 'Refill!2024pass', 'next': reverse('order_now'),
        })
        self.assertRedirects(response, reverse('order_now'))

    def test_login_ignores_external_next(self):
        User.objects.create_user('joe', 'joe@example.com', 'Refill!2024pass')
        response = self.client.post(reverse('login'), {
            'username': 'joe', 'password': 'Refill!2024pass', 'next': 'https://evil.example.com/',
        })
        self.assertRedirects(response, reverse('home'))

    def test_bad_login_shows_error(self):
        response = self.client.post(reverse('login'), {'username': 'nobody', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('joe', 'joe@example.com', 'Refill!2024pass')
        self.order_data = {
            'product': 'water', 'quantity': 20, 'location': 'Voi Town',
            'delivery_address': 'Block B, House 4', 'phone': '+254712345678',
            'delivery_date': (timezone.localdate() + timedelta(days=1)).isoformat(), 'notes': '',
        }

    def test_order_requires_login(self):
        response = self.client.get(reverse('order_now'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('order_now')}")

    def test_place_order(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('order_now'), self.order_data)
        order = Order.objects.get()
        self.assertRedirects(response, reverse('order_success', args=[order.pk]))
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')

    def test_order_rejects_past_date_and_zero_quantity(self):
        self.client.force_login(self.user)
        data = dict(self.order_data, quantity=0, delivery_date=(timezone.localdate() - timedelta(days=1)).isoformat())
        response = self.client.post(reverse('order_now'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_my_orders_only_shows_own_orders(self):
        other = User.objects.create_user('other', 'o@example.com', 'x')
        Order.objects.create(user=other, product='oil', quantity=5, location='Mwatate', delivery_address='X',
                             phone='0700000000', delivery_date=timezone.localdate())
        self.client.force_login(self.user)
        response = self.client.get(reverse('my_orders'))
        self.assertContains(response, "You haven't placed any orders yet")

    def test_cannot_view_someone_elses_order(self):
        other = User.objects.create_user('other', 'o@example.com', 'x')
        order = Order.objects.create(user=other, product='oil', quantity=5, location='Mwatate', delivery_address='X',
                                     phone='0700000000', delivery_date=timezone.localdate())
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('order_success', args=[order.pk])).status_code, 404)

    def test_cancel_pending_order_only(self):
        self.client.force_login(self.user)
        order = Order.objects.create(user=self.user, product='water', quantity=10, location='Voi',
                                     delivery_address='X', phone='0700000000', delivery_date=timezone.localdate())
        self.client.post(reverse('cancel_order', args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

        order.status = 'delivered'
        order.save()
        self.client.post(reverse('cancel_order', args=[order.pk]))
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')
