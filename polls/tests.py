import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question


def create_question(question_text, days):
    """
    Creates a question with the given 'question_text and published the given number of 'days' offset to now (negative for questions in the past)
    """
    time = timezone.now() + datetime.timedelta(days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        If past questions exist, it should be displayed on the index page
        """
        create_question('Past question.', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )


    def test_index_view_with_a_future_question(self):
        """
        If future questions exist, they shouldn't be displayed on the index page
        """
        create_question('Future question.', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(
            response, "No polls are available.", status_code=200
        )
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_and_a_future_question(self):
        """
        If a past and a future questions exist, only the past should be displayed on the index page
        """
        create_question('Past question.', -30)
        create_question('Future question.', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )


    def test_index_view_with_two_past_questions(self):
        """
        If twp past questions exist, they should be displayed on the index page
        """
        create_question('Past question 1.', -30)
        create_question('Past question 2.', -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>',
             '<Question: Past question 1.>',
             ]
        )


class QuestionIndexDetailTests(TestCase):
    """

    """


    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with the 'pub_date' in the future should return a 404 not found.
        """
        future_question = create_question('Future question.', 30)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)


    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with the 'pub_date' in the past should display the question's text.
        """
        past_question = create_question('Past question.', -30)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertContains(response, past_question.question_text, status_code=200)


class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return false for questions whose pub_date is in the future
        """
        future_question = create_question('future question?', 30)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return false for questions whose pub_date is more than 1 day old
        """
        past_question = create_question('past question?', -30)
        self.assertEqual(past_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return true for questions whose pub_date is in 1 day old
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), True)