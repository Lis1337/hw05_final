import time, random
from django.test import TestCase, Client
from .models import Post, User, Group, Follow, Comment
from .forms import PostForm
from django.contrib.auth.decorators import login_required

# Create your tests here.

class hw_04(TestCase):
    def setUp(self):
        self.client = Client()
        self.random_user = User.objects.create_user(username="vasya_pupkin", email="vasya_pupkin@mail.ru", password="12345678")
        self.client.login(username="vasya_pupkin", password="12345678")
        self.group_create = Group.objects.create(title="random1", slug="random1", description="random_random")
        self.post_create =  Post.objects.create(
            text='test_test',
            author=self.random_user,
            group=self.group_create,
            image='posts/pogba.jpg'              #вставить свой адрес картинки
        )
        print("setUp")


    def test_profile(self):           
        print("тест профайла")
        response = self.client.get(f"/{self.random_user}/")
        self.assertEqual(response.status_code, 200)


    def test_newpost_login(self):     
        print("тест авторизации")
        response = self.client.get("/new/", follow=True)
        self.assertEqual(response.status_code, 200)
                

    def test_newpost_logout(self):    
        print("тест редиректа")
        self.client.logout()
        response = self.client.get("/new/")
        self.assertRedirects(response, expected_url="/auth/login/?next=/new/", status_code=302, target_status_code=200)


    def test_index(self):                                                     
        print("тест новой записи")
        time.sleep(20)
        response = self.client.get("/")
        self.assertContains(response, 'test_test', status_code=200)

        response_1 = self.client.get(f'/{self.random_user}/')
        self.assertContains(response_1, 'test_test', status_code=200)

        response_2 = self.client.get(f'/{self.random_user}/{self.post_create.id}/')
        self.assertContains(response_2, 'test_test', status_code=200)

    
    def test_post_edit(self):             
        print("тест изменения поста")

        response = self.client.post(f'/{self.random_user}/{self.post_create.id}/edit/', {"text": "asdfg"})
        self.assertEqual(response.status_code, 302)
        time.sleep(20)
        
        response_1 = self.client.get("/")
        self.assertContains(response_1, text="asdfg", status_code=200)

        response_2 = self.client.get(f'/{self.random_user}/')
        self.assertContains(response_2, text="asdfg", status_code=200)

        response_3 = self.client.get(f'/{self.random_user}/{self.post_create.id}/')
        self.assertContains(response_3, text="asdfg", status_code=200)

    
    def test_404(self):
        print("тест 404")
        response = self.client.get('/asdfghjkkl/')
        self.assertEqual(response.status_code, 404)


    def test_pictures(self):
        print("тест на наличие картинок на главной\профайле\группе")
        
        response = self.client.get(f'/{self.random_user}/{self.post_create.id}/')
        self.assertContains(response, text='<img')

        response_2 = self.client.get('')
        self.assertContains(response_2, text='<img')
        
        response_3 = self.client.get(f'/group/{self.group_create.slug}')
        self.assertContains(response_3, text='<img')


    def test_wrong_format(self):
        print("тест на недопустимые форматы картинки")
        with open ('requirements.txt') as fp:
            response = self.client.post('/new/', {'text': 'txt_load', 'image': fp})
            self.assertFormError(response, 'form', 'image', "Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.")

    
    def test_cache(self):
        print("тест кэша")
        response = self.client.get('')
        random_text = random.getrandbits(30)
        self.client.post(f'/{self.random_user}/{self.post_create.id}/edit/', {"text": random_text})
        time.sleep(5)
        self.assertContains(response, 'test_test', status_code=200)
        
        time.sleep(15)
        response_2 = self.client.get("/")
        self.assertContains(response_2, text=random_text, status_code=200)


    def test_only_authorised_follow(self):
        print("юзер может фоловить\анфоловить")
        User.objects.create(username='random_2', password='qwerty12345')
        random_2 = User.objects.get(username='random_2')
        
        self.client.get('/random_2/follow')
        self.assertTrue(Follow.objects.filter(user=self.random_user, author=random_2).exists())
        self.client.get('/random_2/unfollow')
        self.assertFalse(Follow.objects.filter(user=self.random_user, author=random_2).exists())
        

    def test_follow_index(self):
        print("новая запись появляется только в ленте подписчиков")
        User.objects.create(username='random_2', password='qwerty12345')
        random_2 = User.objects.get(username='random_2')
        random_2_post = Post.objects.create(author=random_2, text="qazwsxedcrfv")
        Follow.objects.create(user=self.random_user, author=random_2)

        response = self.client.get('/follow/')
        self.assertContains(response, text=random_2_post.text, status_code=200)

        self.client.login(username='random_2', password='qwerty12345')
        self.assertNotContains(response, text=self.post_create.text, status_code=200)


    def test_comments(self):
        print("только залогиненный пользователь может писать коменты")
        new_comment = random.getrandbits(30)
        self.client.post(f'/{self.random_user}/{self.post_create.id}/comment/', {'text': new_comment})
        self.assertTrue(Comment.objects.filter(post=self.post_create, author=self.random_user, text=new_comment).exists())
        
        self.client.logout()
        response = self.client.get(f'/{self.random_user}/{self.post_create.id}/comment/')
        expected_url = f'/auth/login/?next=/{self.random_user}/{self.post_create.id}/comment/'
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)


    def tearDown(self):
        print("tearDown")
