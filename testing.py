import unittest
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user
from flask_testing import TestCase
from app import app, db, models

bcrypt = Bcrypt()


class FlaskTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing return
        return app

    def setUp(self):
        self.app = self.create_app().test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.create_test_user()
        self.create_test_petitions()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
        if not user:
            user = models.User(
                username='testuser',
                email='test@example.com',
            )
            user.set_password('<PASSWORD>')
            db.session.add(user)
            db.session.commit()
        with self.client:
            login_user(user)

    def create_test_petitions(self):
        user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
        petition1 = models.Petition(
            title='Test Petition 1',
            tag_line='Tag Line 1',
            description='Description of test petition 1',
            author_id=user.id,
            status_badges=['Waiting']
        )
        petition2 = models.Petition(
            title='Test Petition 2',
            tag_line='Tag Line 2',
            description='Description of test petition 2',
            author_id=user.id,
            status_badges=['Waiting']
        )
        db.session.add(petition1)
        db.session.add(petition2)
        db.session.commit()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag Line 1', response.data)

    def test_browse_page(self):
        response = self.client.get('/browse')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Petition 1', response.data)
        self.assertIn(b'Test Petition 2', response.data)

    def test_petition_detail_page(self):
        petition = db.session.execute(db.select(models.Petition).filter_by(title='Test Petition 1')).scalar()
        response = self.client.get(f'/petition/{petition.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Petition 1', response.data)

    def test_create_petition_page_logged_in(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='Test_123'), follow_redirects=True)
            response = self.client.get('/create')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Select a Category', response.data)

    def test_create_petition_page_not_logged_in(self):
        with self.client:
            user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
            login_user(user)
            logout_user()
            response = self.client.get('/create', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data)

    def test_create_petition_missing_fields(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='Test_123'), follow_redirects=True)
            response = self.client.post('/create', data=dict(
                title='Incomplete Petition',
                description='This petition is missing some fields.'
            ))
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid', response.data)

    def test_create_petition_invalid_data(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='Test_123'), follow_redirects=True)
            response = self.client.post('/create', data=dict(
                title='Invalid Petition',
                tag_line='This tag line is way too long' * 50,  # Invalid due to length
                description='Invalid petition description.',
                category='Invalid Category'
            ))
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data=dict(email='invalid@example.com', password='WrongPassword'),
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid', response.data)

    def test_signup_existing_username(self):
        response = self.client.post('/signup', data=dict(
            username='testuser',  # Existing username
            email='newemail@example.com',
            password='NewPass_123',
            confirm_password='NewPass_123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_signup_existing_email(self):
        response = self.client.post('/signup', data=dict(
            username='newuser',
            email='test@example.com',  # Existing email
            password='NewPass_123',
            confirm_password='NewPass_123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_logout_and_access_restricted_page(self):
        with self.client:
            user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
            login_user(user)
            logout_user()
            response = self.client.get('/settings', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data)

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_signup_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_search_page(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Petitions', response.data)

    def test_search_results(self):
        response = self.client.get('/search_results?query=Test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag Line 1', response.data)
        self.assertIn(b'Tag Line 2', response.data)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
