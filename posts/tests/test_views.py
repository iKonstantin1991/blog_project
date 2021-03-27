import os
import shutil
import time

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User
from yatube.settings import BASE_DIR


@override_settings(MEDIA_ROOT=os.path.join(BASE_DIR, 'temp_folder'))
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создадим две записи, для одной из записей создадим группу
        еще одну группу создадим но оставим пустой для проверки"""
        super().setUpClass()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.empty_group = Group.objects.create(
            title='Группа без постов',
            slug='test_empty',
            description='Пустая тестовая группа',
        )
        cls.filled_group = Group.objects.create(
            title='Группа с постами',
            slug='test_filled',
            description='Тестовая группа c одним постом',
        )
        cls.test_post_with_gr = Post.objects.create(
            text='Текст первого поста который относится к группе с постами',
            author=User.objects.create(username='group_filled_username'),
            group=cls.filled_group,
            image=cls.uploaded,
        )
        time.sleep(0.1)
        cls.user_author = User.objects.create_user(
            username='group_empty_username'
        )
        cls.test_post_without_gr = Post.objects.create(
            text='Текст второго поста у которого нет группы',
            author=cls.user_author,
            image=cls.uploaded,
        )
        cls.edit_post_id = cls.test_post_without_gr.id

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user_author)

    def post_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('posts:index'),
            'new_post.html': reverse('posts:new_post'),
            'group.html': (
                reverse(
                    'posts:group_posts',
                    kwargs={'slug': f'{PostsPagesTests.empty_group.slug}'}
                )
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_list_is_2(self):
        """ Удостоверимся, что на главную страницу передаётся
        ожидаемое количество объектов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page']), 2)

    def test_group_filled_slug_page_list_is_1(self):
        """ Удостоверимся, что на страницу группы с одним постом передаётся
        ожидаемое количество объектов"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': f'{PostsPagesTests.filled_group.slug}'}
            )
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_group_filled_slug_page_list_is_0(self):
        """ Проверим, что пост не попал в группу,
            для которой не был предназначен"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': f'{PostsPagesTests.empty_group.slug}'}
            )
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(
            post_text_0,
            f'{PostsPagesTests.test_post_without_gr.text}'
        )
        self.assertTrue(post_image_0 is not None)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': f'{PostsPagesTests.filled_group.slug}'}
            )
        )
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(
            post_text_0,
            f'{PostsPagesTests.test_post_with_gr.text}'
        )
        self.assertEqual(
            response.context['group'].title,
            f'{PostsPagesTests.filled_group.title}'
        )
        self.assertEqual(
            response.context['group'].description,
            f'{PostsPagesTests.filled_group.description}'
        )
        self.assertEqual(
            response.context['group'].slug,
            f'{PostsPagesTests.filled_group.slug}'
        )
        self.assertTrue(post_image_0 is not None)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Страница профиля сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostsPagesTests.user_author.username}'}
            )
        )
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(
            post_text_0,
            f'{PostsPagesTests.test_post_without_gr.text}'
        )
        self.assertTrue(post_image_0 is not None)

    def test_post_show_correct_context(self):
        """Страница поста сформирована с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post',
                kwargs={
                    'username': f'{PostsPagesTests.user_author.username}',
                    'post_id': PostsPagesTests.edit_post_id,
                }
            )
        )
        first_object = response.context['post']
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(
            post_text,
            f'{PostsPagesTests.test_post_without_gr.text}'
        )
        self.assertTrue(post_image is not None)

    def test_post_edit_show_correct_context(self):
        """Страница редактирования поста сформирована
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': f'{PostsPagesTests.user_author.username}',
                    'post_id': PostsPagesTests.edit_post_id,
                }
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class IndexPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_user')
        for i in reversed(range(1, 14)):
            Post.objects.create(
                text=f'Тестовый текст {i}го поста',
                author=cls.author,
            )
            time.sleep(0.1)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """ На главной странице 10 постов """
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page']), 10)

    def test_second_page_contains_three_records(self):
        """ На второй странице должно быть три поста. """
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page')), 3)

    def test_index_page_show_correct_posts(self):
        """ Посты выводятся в правильном порядке"""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]
        post_text_0 = first_object.text
        self.assertEqual(
            post_text_0,
            'Тестовый текст 1го поста'
        )


class CacheIndexTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_cache_index_page(self):
        """Проверим что вывод главной страницы кэшируется корректно"""
        Post.objects.create(
            text='Тестовый текст первого поста',
            author=User.objects.create(
                username='test_username1'
            )
        )

        first_response = self.guest_client.get(reverse('posts:index'))

        Post.objects.create(
            text='Тестовый текст второго поста',
            author=User.objects.create(
                username='test_username2'
            )
        )

        second_response = self.guest_client.get(reverse('posts:index'))
        first_response_content = first_response.content
        second_response_content = second_response.content
        self.assertEqual(
            first_response_content,
            second_response_content
        )
        cache.clear()
        third_response = self.guest_client.get(reverse('posts:index'))
        third_response_content = third_response.content
        self.assertNotEqual(
            first_response_content,
            third_response_content
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.follower_user = User.objects.create_user(
            username='follower_user'
        )
        cls.followed_user = User.objects.create_user(
            username='followed_user'
        )

    def setUp(self):
        self.authorized_follower_client = Client()
        self.authorized_followed_client = Client()
        self.authorized_follower_client.force_login(
            FollowTests.follower_user
        )
        self.authorized_followed_client.force_login(
            FollowTests.followed_user
        )

    def test_follow_works_properly(self):
        """Проверим, что авторизованный пользователь может
        подписываться на других пользователей"""
        follower_number_initial = (FollowTests.followed_user.
                                   following.all().count())
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': f'{FollowTests.followed_user.username}',
                }
            )
        )
        follower_number_follow = (FollowTests.followed_user.
                                  following.all().count())
        self.assertNotEqual(
            follower_number_initial,
            follower_number_follow
        )

    def test_unfollow_works_properly(self):
        """Проверим, что авторизованный пользователь может
        удалять пользователей из подписок"""
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': f'{FollowTests.followed_user.username}',
                }
            )
        )
        follower_number_initial = (FollowTests.followed_user.
                                   following.all().count())
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': f'{FollowTests.followed_user.username}',
                }
            )
        )
        follower_number_unfollow = (FollowTests.followed_user.
                                    following.all().count())
        self.assertNotEqual(
            follower_number_initial,
            follower_number_unfollow
        )

    def test_new_posts_appear_in_follower_page(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан и не появляется в ленте тех, кто не подписан"""
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': f'{FollowTests.followed_user.username}',
                }
            )
        )
        follower_intial_response = self.authorized_follower_client.get(
            reverse('posts:follow_index')
        )
        followed_intial_response = self.authorized_followed_client.get(
            reverse('posts:follow_index')
        )
        follower_initial_post_quantity = len(follower_intial_response.
                                             context['page'])
        followed_initial_post_quantity = len(followed_intial_response.
                                             context['page'])

        Post.objects.create(
            text='Тестовый текст',
            author=FollowTests.followed_user
        )

        follower_second_response = self.authorized_follower_client.get(
            reverse('posts:follow_index')
        )
        followed_second_response = self.authorized_followed_client.get(
            reverse('posts:follow_index')
        )

        follower_second_post_quantity = len(follower_second_response.
                                            context['page'])
        followed_second_post_quantity = len(followed_second_response.
                                            context['page'])

        self.assertNotEqual(
            follower_initial_post_quantity,
            follower_second_post_quantity
        )
        self.assertEqual(
            followed_initial_post_quantity,
            followed_second_post_quantity
        )
