from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models.models import Subject, User, Admin

class SubjectViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin_user = User.objects.create_user(
            username='@admin',
            first_name='Name',
            last_name='Surname',
            email='admin@example.com',
            password='admin123'
        )
        self.admin_user.save()
        self.admin = Admin.objects.create(user=self.admin_user)

        self.subject1 = Subject.objects.create(name="Python")
        self.subject2 = Subject.objects.create(name="C++")

        self.url = reverse('subjects_list')

    def test_create_subject_url(self):
        self.assertEqual(self.url, '/dashboard/subjects/')


    def test_subjects_list_view(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('subjects_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subjects_list.html')
        self.assertIn(self.subject1, response.context['page_obj'])
        self.assertIn(self.subject2, response.context['page_obj'])

    def test_subject_edit_view_get(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('subject_edit', args=[self.subject1.subject_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subject_edit.html')
        self.assertEqual(response.context['subject.py'], self.subject1)

    def test_subject_edit_view_post(self):
        self.client.login(username="@admin", password="admin123")

        response = self.client.post(
            reverse('subject_edit', args=[self.subject1.subject_id]),
            {'name': self.subject1.name, 'description': 'Updated Python'},
            follow=False
        )

        self.assertEqual(response.status_code, 302)
        redirect_url = response['Location']
        self.assertEqual(redirect_url, reverse('subjects_list'))

        response = self.client.get(redirect_url)

        self.assertEqual(response.status_code, 200)
        self.subject1.refresh_from_db()
        self.assertEqual(self.subject1.name, 'Python')
        self.assertEqual(self.subject1.description, 'Updated Python')

    def test_subject_delete_view(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(reverse('subject_delete', args=[self.subject2.subject_id]), follow=False)
        self.assertRedirects(response, reverse('subjects_list'))
        self.assertFalse(Subject.objects.filter(subject_id=self.subject2.subject_id).exists())

    def test_subject_create_view_get(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('new_subject'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subjects_list.html')

    def test_subject_create_view_post(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(
            reverse('new_subject'),
            {'name': 'Updated Python', 'description': 'Updated Python description'},
            follow=False
        )

        self.assertEqual(response.status_code, 302)

        redirect_url = response['Location']
        self.assertEqual(redirect_url, reverse('subjects_list'))

        response = self.client.get(redirect_url)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(Subject.objects.filter(name='Updated Python').exists())

    def test_subject_view_permissions(self):
        response = self.client.get(reverse('subjects_list'))
        self.assertNotEqual(response.status_code, 200)

        normal_user = User.objects.create_user(username="@user", password="user123")
        self.client.login(username="@user", password="user123")
        response = self.client.get(reverse('subjects_list'))
        self.assertNotEqual(response.status_code, 200)

    def test_get_with_subject_id(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('subject_edit', args=[self.subject1.subject_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subject_edit.html')
        self.assertEqual(response.context['subject.py'], self.subject1)

    def test_get_subjects_list_with_admin(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('subjects_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subjects_list.html')
        self.assertIn(self.subject1, response.context['page_obj'])
        self.assertIn(self.subject2, response.context['page_obj'])

    def test_get_subjects_list_without_admin_profile(self):
        normal_user = User.objects.create_user(username="@user", password="user123")
        self.client.login(username="@user", password="user123")
        response = self.client.get(reverse('subjects_list'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect or deny access


    def test_post_to_delete_subject(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(reverse('subject_delete', args=[self.subject2.subject_id]))
        self.assertRedirects(response, reverse('subjects_list'))
        self.assertFalse(Subject.objects.filter(subject_id=self.subject2.subject_id).exists())

    def test_handle_subject_form_valid(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(reverse('new_subject'), {'name': 'JavaScript', 'description': 'A subject.py about historical events.'}, follow=False)
        self.assertEqual(response.status_code, 302)  # Expecting redirect
        self.assertRedirects(response, reverse('subjects_list'))
        self.assertTrue(Subject.objects.filter(name='JavaScript').exists())

    def test_handle_subject_form_invalid(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(reverse('new_subject'), {'name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_subjects/subject_create.html')
        self.assertFalse(Subject.objects.filter(name='').exists())
        self.assertContains(response, "This field is required")

    def test_edit_subject_invalid_id(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.get(reverse('subject_edit', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_subject_invalid_id(self):
        self.client.login(username="@admin", password="admin123")
        response = self.client.post(reverse('subject_delete', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        # Non-logged-in user
        response = self.client.get(reverse('subjects_list'))
        self.assertNotEqual(response.status_code, 200)

        # Non-admin user
        normal_user = User.objects.create_user(username="@user", password="user123")
        self.client.login(username="@user", password="user123")
        response = self.client.get(reverse('subjects_list'))
        self.assertNotEqual(response.status_code, 200)

