import os
import re
import shutil

import unittest

from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user
from flask_testing import TestCase

from app import app, db, models

from app.models import User, Petition

bcrypt = Bcrypt()

class FlaskTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    # https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUp
    def setUp(self):
        # Generate a copy of the file as placing the db in memory didn't work :(
        shutil.copyfile("app.db", "app_original.db")

        # Derived from: https://stackoverflow.com/questions/69853072/writing-unit-test-for-a-flask-application-using-unittest
        self.app = self.create_app().test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Create the test users & petitions
        self.create_test_user()
        self.create_test_petitions()

    # https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # Restore the original db file
        shutil.copyfile("app_original.db", "app.db")
        os.remove("app_original.db")

    def extract_token(self):
        response = self.client.get('/create')

        csrf_token = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', response.data.decode())

        return csrf_token.group(1)

    # Create a test user with the specified data
    def create_test_user(self):
        user = models.User(
            username='testuser',
            email='test@example.com',
        )
        user.set_password('secure_password123')
        db.session.add(user)
        db.session.commit()
        with self.client:
            login_user(user)

    # Create two test petitions with the specified data
    def create_test_petitions(self):
        # Fetch the user
        user = models.User.query.filter(User.email == "test@example.com").first()
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
            status_badges=['Victory']
        )
        db.session.add(petition1)
        db.session.add(petition2)
        db.session.commit()

    # Test the home page route
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag Line 1', response.data)

    # Test the browse page route
    def test_browse_page(self):
        response = self.client.get('/browse')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Petition 1', response.data)
        self.assertIn(b'Test Petition 2', response.data)

    # Test the petition details page route
    def test_petition_detail_page(self):
        petition = models.Petition.query.filter(Petition.title == "Test Petition 1").first()
        response = self.client.get(f'/petition/{petition.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Petition 1', response.data)

    # Test login route
    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    # Test signup route
    def test_signup_page(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    # Test search route
    def test_search_page(self):
        response = self.client.get('/search')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search Petitions', response.data)

    # Test the search route with a query
    def test_search_results(self):
        response = self.client.get('/search_results?query=Test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tag Line 1', response.data)
        self.assertIn(b'Tag Line 2', response.data)

    # Test the create petition route
    def test_create_petition(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='secure_password123'),
                             follow_redirects=True)

            # Extract csrf
            # Match all characters up until "
            csrf_token = self.extract_token()
            print(csrf_token)

            response = self.client.post('/create', data=dict(
                title='A Petition Title',
                description='A Petition Description',
                tag_line='A Tag Line',
                category='Academic',
                csrf_token=csrf_token
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'A Petition Title', response.data)

    # Test the create petition route when not logged in, expecting a redirect
    def test_create_petition_page_not_logged_in(self):
        with self.client:
            user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
            login_user(user)
            logout_user()
            response = self.client.get('/create', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data)

    # Create a petition with missing data for vulnerability testing
    # Missing fields shouldn't be possible locally unless a POST request is manually made
    def test_create_petition_missing_fields(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='secure_password123'),
                             follow_redirects=True)

            csrf_token = self.extract_token()

            response = self.client.post('/create', data=dict(
                title='Incomplete Petition',
                description='This petition is missing some fields.',
                csrf_token=csrf_token
            ))
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid', response.data)

    # Create a petition with invalid data for vulnerability testing
    def test_create_petition_invalid_data(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='secure_password123'),
                             follow_redirects=True)
            response = self.client.post('/create', data=dict(
                title='Invalid Petition',
                tag_line='This tag line is way too long' * 50,  # Invalid due to length
                description='Invalid petition description.',
                category='Invalid Category'
            ))
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid', response.data)

    def test_edit_petition(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='secure_password123'),
                             follow_redirects=True)

            petition = models.Petition.query.filter(Petition.title == 'Test Petition 1').first()

            csrf_token = self.extract_token()

            response = self.client.post(f'/petition/{petition.id}/edit', data=dict(
                title="New Petition Name",
                description="New Petition Description",
                tag_line="New Petition Tag Line",
                status="Victory",
                csrf_token=csrf_token
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'New Petition Name', response.data)

    # Test the tags and browse filtering
    def test_filter_petition(self):
        response = self.client.get('/browse?filter=victories')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Petition 2', response.data)

    # Test the sign petition route
    def test_sign_petition(self):
        with self.client:
            self.client.post('/login', data=dict(email='test@example.com', password='secure_password123'),
                             follow_redirects=True)
            petition = models.Petition.query.filter(Petition.title == "Test Petition 1").first()
            response = self.client.get(f'petition/{petition.id}')

            # Extract csrf
            # Match all characters up until "
            csrf_token = self.extract_token()

            response = self.client.post(f'/petition/{petition.id}/sign', data=dict(
                reason='just a test signature',
                is_anonymous=False,
                csrf_token=csrf_token
            ), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'just a test signature', response.data)

    # Login with invalid credentials
    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data=dict(email='invalid@example.com', password='WrongPassword'),
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid', response.data)

    # Attempt to create an account with an existing username
    def test_signup_existing_username(self):
        response = self.client.post('/signup', data=dict(
            username='testuser',  # Existing username
            email='newemail@example.com',
            password='NewPass_123',
            confirm_password='NewPass_123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    # Attempt to create an account with an existing email
    def test_signup_existing_email(self):
        response = self.client.post('/signup', data=dict(
            username='newuser',
            email='test@example.com',  # Existing email
            password='NewPass_123',
            confirm_password='NewPass_123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    # Try and access a restricted page expecting a redirect
    def test_logout_and_access_restricted_page(self):
        with self.client:
            user = db.session.execute(db.select(models.User).filter_by(email='test@example.com')).scalar()
            login_user(user)
            logout_user()
            response = self.client.get('/settings', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    unittest.main(testRunner=runner)
