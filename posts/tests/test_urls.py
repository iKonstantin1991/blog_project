from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тест',
            slug='test',
            description='Тестовая группа'
        )
        cls.test_user_owner = User.objects.create(username='test_user_owner')
        cls.test_post = Post.objects.create(
            text='Тест текст',
            author=cls.test_user_owner,
            group=cls.test_group,
        )
        cls.test_post_id = cls.test_post.id
        cls.url_list_guest_client = (
            '/',
            f'/group/{cls.test_group.slug}/',
            f'/{cls.test_user_owner.username}/',
            f'/{cls.test_user_owner.username}/{cls.test_post_id}/',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_rejected = User.objects.create_user(username='test_name')
        self.authorized_client_owner = Client()
        self.authorized_client_rejected = Client()
        self.authorized_client_owner.force_login(PostsURLTests.test_user_owner)
        self.authorized_client_rejected.force_login(self.user_rejected)

    def test_urls_exist_at_desired_location(self):
        """Страницы index, одтдельной группы, пользователя и
           отдельного поста доступны любому пользователю"""
        for url in PostsURLTests.url_list_guest_client:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_exists_at_desired_location(self):
        """ Страница /new/ доступна авторизированному пользователю """
        response = self.authorized_client_rejected.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_redirects_anonymous(self):
        """ Страница /new/ перенаправляет анонимного пользователя """
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)

    def test_new_redirects_anonymous_on_admin_login(self):
        """Страница по адресу /new/ перенаправит анонимного
        пользователя на страницу логина. """
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_edit_page_available_for_owner(self):
        """Страница редактирования поста доступна автору"""
        response = self.authorized_client_owner.get(
            f'/{PostsURLTests.test_user_owner.username}'
            f'/{PostsURLTests.test_post_id}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_page_redirect_users(self):
        """Страница редактирования поста перенаправляет пользователей"""
        self.users_list = [self.authorized_client_rejected, self.guest_client]
        for user in self.users_list:
            with self.subTest():
                response = user.get(
                    f'/{PostsURLTests.test_user_owner.username}'
                    f'/{PostsURLTests.test_post_id}/edit'
                )
                self.assertEqual(response.status_code, 301)

    def test_new_redirects_other_users_on_admin_login(self):
        """Страница редактирования поста перенаправит
           пользователей на страницу поста. """
        self.users_list = [self.authorized_client_rejected, self.guest_client]
        for user in self.users_list:
            with self.subTest():
                response = user.get(
                    f'/{PostsURLTests.test_user_owner.username}'
                    f'/{PostsURLTests.test_post_id}/edit',
                    follow=True
                )
                self.assertRedirects(
                    response, f'/{PostsURLTests.test_user_owner.username}'
                              f'/{PostsURLTests.test_post_id}/',
                    status_code=301
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            f'/group/{PostsURLTests.test_group.slug}/': 'group.html',
            '/new/': 'new_post.html',
            f'/{PostsURLTests.test_user_owner.username}'
            f'/{PostsURLTests.test_post_id}'
            '/edit/': 'new_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_owner.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_exists_at_desired_location(self):
        """ Ошибка 404 если страница не найдена """
        response = self.authorized_client_rejected.get('/doesnt_exist/')
        self.assertEqual(response.status_code, 404)

    def test_only_authorized_can_comment(self):
        """ Только авторизированный пользователь может комментировать посты"""
        response = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={
                    'username': f'{PostsURLTests.test_user_owner.username}',
                    'post_id': f'{PostsURLTests.test_post.id}',
                }
            )
        )
        self.assertEqual(response.status_code, 302)


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        """Страницы about и tech доступны любому пользователю"""
        url_list_guest_client = ['/about/author/', '/about/tech/']
        for url in url_list_guest_client:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
