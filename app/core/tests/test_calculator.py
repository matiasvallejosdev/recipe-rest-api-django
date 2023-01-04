from django.test import SimpleTestCase


class TestCalculator(SimpleTestCase):

    def test_add_x_y(self):
        x = 4
        y = 4
        result = 8
        self.assertEqual(x + y, result)
