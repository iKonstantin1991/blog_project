import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user_author = User.objects.create_user(
            username='test_user'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
        )
        cls.group = Group.objects.create(
            title='Тестовая',
            slug='test',
            description='Тестовая группа',
        )
        cls.edit_post_id = cls.test_post.id

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user_author)

    def test_create_post(self):
        """Валидная ли форма создает запись в new"""
        posts_count = Post.objects.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Тестовый текст',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                text='Тестовый текст',
                image='posts/small.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Изменяется ли запись после редактирования"""
        posts_count = Post.objects.count()
        another_small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='another_small.gif',
            content=another_small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Измененый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': PostFormTests.user_author.username,
                    'post_id': PostFormTests.edit_post_id,
                }),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post',
                kwargs={
                    'username': PostFormTests.user_author.username,
                    'post_id': PostFormTests.edit_post_id,
                }),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                text='Измененый текст',
                image='posts/another_small.gif',
            ).exists()
        )
