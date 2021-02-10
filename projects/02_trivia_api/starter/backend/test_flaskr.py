import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('demo1','pass1',
        'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """



    def test_add_question(self):
        res = self.client().post('/add', json={
        'question' :'Which football team is the most succesful?',
        'answer' :'Middlesbrough FC',
        'difficulty' : '2',
        'category' : '6'}
      )
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], 
            'Which football team is the most succesful?')
        self.assertEqual(data['answer'], 'Middlesbrough FC')
        self.assertEqual(data['difficulty'], '2')
        self.assertEqual(data['category'], '6')
        self.assertTrue(data['id'])
        self.assertEqual(res.status_code, 200)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()