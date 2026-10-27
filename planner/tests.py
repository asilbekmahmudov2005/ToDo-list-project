from datetime import date, time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from planner.models import Task


class PlannerComprehensiveTests(TestCase):
    def setUp(self):
        # Ikkita alohida foydalanuvchi yaratamiz
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123',
            first_name='Ali'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123',
            first_name='Vali'
        )
        self.client1 = Client()
        self.client1.login(username='user1', password='password123')

        self.client2 = Client()
        self.client2.login(username='user2', password='password123')

        self.today = date.today()

        # User1 uchun vazifalar
        self.task1 = Task.objects.create(
            user=self.user1,
            title='Dasturlash darsi',
            description='Django ORM o‘rganish',
            date=self.today,
            start_time=time(9, 0),
            end_time=time(10, 30),
            duration=90,
            priority=Task.Priority.HIGH,
            category=Task.Category.STUDY,
            is_completed=False
        )
        self.task2 = Task.objects.create(
            user=self.user1,
            title='Sport zalga borish',
            description='Kardio mashg‘ulot',
            date=self.today,
            priority=Task.Priority.MEDIUM,
            category=Task.Category.HEALTH,
            is_completed=True
        )

        # User2 uchun vazifa
        self.task_user2 = Task.objects.create(
            user=self.user2,
            title='Valining shaxsiy ishi',
            description='Sirli topshiriq',
            date=self.today,
            priority=Task.Priority.LOW,
            category=Task.Category.PERSONAL,
            is_completed=False
        )

    def test_user_data_isolation(self):
        """10-talab: Har bir foydalanuvchi faqat o'z vazifalarini ko'rishi kerak"""
        response = self.client1.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dasturlash darsi')
        self.assertContains(response, 'Sport zalga borish')
        self.assertNotContains(response, 'Valining shaxsiy ishi')

        # User1 boshqa foydalanuvchining vazifasini JSON orqali ololmasligi kerak (404 kutamiz)
        res_json = self.client1.get(reverse('task_detail_json', args=[self.task_user2.id]))
        self.assertEqual(res_json.status_code, 404)

        # User1 boshqa foydalanuvchining vazifasini o'chira olmasligi kerak
        res_del = self.client1.post(reverse('task_delete', args=[self.task_user2.id]))
        self.assertEqual(res_del.status_code, 404)
        self.assertTrue(Task.objects.filter(id=self.task_user2.id).exists())

    def test_task_create_crud(self):
        """4-talab: Vazifa yaratish"""
        response = self.client1.post(reverse('task_create'), {
            'title': 'Yangi vazifa 123',
            'description': 'Tavsif matni',
            'date': self.today.strftime('%Y-%m-%d'),
            'priority': 'medium',
            'category': 'work',
        })
        self.assertEqual(response.status_code, 302)
        new_task = Task.objects.filter(title='Yangi vazifa 123', user=self.user1).first()
        self.assertIsNotNone(new_task)
        self.assertEqual(new_task.user, self.user1)

    def test_task_update_crud(self):
        """4-talab: Vazifani tahrirlash"""
        response = self.client1.post(reverse('task_update', args=[self.task1.id]), {
            'title': 'Yangilangan vazifa nomi',
            'description': 'Yangi tavsif',
            'date': self.today.strftime('%Y-%m-%d'),
            'priority': 'low',
            'category': 'other',
        })
        self.assertEqual(response.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Yangilangan vazifa nomi')
        self.assertEqual(self.task1.priority, 'low')

    def test_task_delete_crud(self):
        """4-talab: Vazifani o'chirish"""
        task_id = self.task2.id
        response = self.client1.post(reverse('task_delete', args=[task_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task_id).exists())

    def test_task_toggle_status(self):
        """4-talab: Bajarilgan deb belgilash va qaytarish"""
        self.assertFalse(self.task1.is_completed)
        response = self.client1.post(
            reverse('task_toggle_status', args=[self.task1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.is_completed)

        # Qayta bosganda yana faol holatga qaytishi kerak
        response2 = self.client1.post(
            reverse('task_toggle_status', args=[self.task1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response2.status_code, 200)
        self.task1.refresh_from_db()
        self.assertFalse(self.task1.is_completed)

    def test_search_and_filters(self):
        """6-talab: Qidiruv va filterlash"""
        # Qidiruv
        res_search = self.client1.get(reverse('all_tasks') + '?q=Dasturlash')
        tasks_in_context = list(res_search.context['tasks'])
        self.assertIn(self.task1, tasks_in_context)
        self.assertNotIn(self.task2, tasks_in_context)

        # Kategoriya filteri
        res_cat = self.client1.get(reverse('all_tasks') + '?category=health')
        tasks_in_cat = list(res_cat.context['tasks'])
        self.assertIn(self.task2, tasks_in_cat)
        self.assertNotIn(self.task1, tasks_in_cat)

        # Holat filteri
        res_status = self.client1.get(reverse('all_tasks') + '?status=completed')
        tasks_in_status = list(res_status.context['tasks'])
        self.assertIn(self.task2, tasks_in_status)
        self.assertNotIn(self.task1, tasks_in_status)

    def test_statistics_and_calendar_views(self):
        """7 & 8-talablar: Taqvim va Statistika sahifalari muvaffaqiyatli yuklanishi"""
        res_cal = self.client1.get(reverse('calendar'))
        self.assertEqual(res_cal.status_code, 200)
        self.assertContains(res_cal, 'Taqvim')

        res_stat = self.client1.get(reverse('statistics'))
        self.assertEqual(res_stat.status_code, 200)
        self.assertContains(res_stat, 'Vazifalar statistikasi va tahlili')

    def test_registration_and_login(self):
        """10-talab: Ro'yxatdan o'tish va kirish"""
        guest_client = Client()
        reg_res = guest_client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'Jasur',
            'email': 'jasur@example.com',
            'password': 'strongpassword123',
            'confirm_password': 'strongpassword123',
        })
        self.assertEqual(reg_res.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
