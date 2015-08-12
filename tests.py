import unittest
import surveymongo

class TestSurveyMongo(unittest.TestCase):

  def test_upper(self):
    self.assertEqual('foo'.upper(), 'FOO')

  def test_get_question_details(self):
    session_id = '6256c72088fbf76de8c91be9be1dd6::410'
    question_id = '828670310'
    question_details = surveymongo.get_question_details(question_id)
    self.assertEqual(question_details['question_id'], question_id)

suite = unittest.TestLoader().loadTestsFromTestCase(TestSurveyMongo)
unittest.TextTestRunner(verbosity=2).run(suite)