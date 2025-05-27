from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_abcd = User.objects.create_user(username='abcd',password='somepassword')
        self.user_qwer = User.objects.create_user(username='qwer',password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_yammy = Tag.objects.create(name='맛도리', slug='맛도리')
        self.tag_animal = Tag.objects.create(name='동물', slug='동물')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            category=self.category_programming,
            author=self.user_abcd
        )
        self.post_001.tags.add(self.tag_yammy)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_qwer,
        )
        
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없을 수도 있죠',
            author=self.user_qwer,
        )
        self.post_003.tags.add(self.tag_yammy)
        self.post_003.tags.add(self.tag_animal)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='Categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})',categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})',categories_card.text)
        # self.assertIn(f'미분류 (1)', categories_card.text)
        

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code,200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_yammy.name, post_001_card.text)
        self.assertNotIn(self.tag_animal.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_yammy.name, post_002_card.text)
        self.assertNotIn(self.tag_animal.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.tag_yammy.name, post_003_card.text)
        self.assertIn(self.tag_animal.name, post_003_card.text)
        self.assertIn(self.user_abcd.username.upper(), main_area.text)
        self.assertIn(self.user_qwer.username.upper(), main_area.text)
        

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(),0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # # 1.1 포스트 목록 페이지를 가져온다
        # response = self.client.get('/blog/')
        # # 1.2 정상적으로 페이지가 로드된다
        # self.assertEqual(response.status_code, 200)
        # # 1.3 페이지 타이틀은 'Blog'
        # soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(soup.title.text, 'Blog')
        
        # self.navbar_test(soup)

        # # 2.1 메인 영역에 게시물이 하나도 없다면
        # self.assertEqual(Post.objects.count(), 0)
        # # 2.2 '아직 게시물이 없습니다' 라는 문구가 보인다
        # main_area = soup.find('div', id='main-area')
        # self.assertIn('아직 게시물이 없습니다', main_area.text)
        
        # # 3.1 게시물이 2개 있다면
        # post_001 = Post.objects.create(
        #     title='첫 번째 포스트입니다.',
        #     content='Hello World. We are the world.',
        #     author=self.user_abcd,
        # )
        # post_002 = Post.objects.create(
        #     title='두 번째 포스트입니다.',
        #     content='1등이 전부는 아니잖아요?',
        #     author=self.user_qwer,
            
        # )
        # self.assertEqual(Post.objects.count(), 2)
        
        # # 3.2 포스트 목록 페이지를 새로고침했을 때
        # response = self.client.get('/blog/')
        # soup = BeautifulSoup(response.content, 'html.parser')
        # self.assertEqual(response.status_code, 200)
        # # 3.3 메인 영역에 포스트 2개의 타이틀이 존재한다
        # main_area = soup.find('div', id='main-area')
        # self.assertIn(post_001.title, main_area.text)
        # self.assertIn(post_002.title, main_area.text)
        # # 3.4 '아직 게시물이 없습니다' 라는 문구는 더 이상 보이지 않는다
        # self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
        # self.assertIn(self.user_abcd.username.upper(), main_area.text)
        # self.assertIn(self.user_qwer.username.upper(), main_area.text)
        
        # # 4. footer test
        # footer = soup.find('footer')
        # self.assertIn('Jun\'s Website 2025', footer.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다.
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content='Hello World. We are the world.',
            author=self.user_abcd,
        )
        # 1.2 그 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')
        
        # 2. 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동한다(status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        self.navbar_test(soup)

        self.category_card_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 들어 있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        # 2.5 첫 번째 포스트의 작성자(author)가 포스트 영역에 있다
        # (아직 구현할 수 없음)
        # 2.6 첫 번째 포스트의 내용)content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_yammy.name, post_area.text)
        # self.assertIn(self.tag_animal.name, post_area.text)

        # 3. footer test
        footer = soup.find('footer')
        self.assertIn('2025', footer.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_yammy.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        # self.assertIn(self.tag_yammy.name, soup.h1.text)
        #
        # main_area = soup.find('div', id='main-area')
        # self.assertIn(self.tag_yammy.name, main_area.text)
        # self.assertIn(self.post_001.title, main_area.text)
        # # self.assertIn(self.post_002.title, main_area.text)
        # self.assertIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        response = self.client.get('/blog/create-post/')
        self.assertNotEqual(response.status_code, 200)

        self.client.login(username='qwer', password='somepassword')

        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'qwer')