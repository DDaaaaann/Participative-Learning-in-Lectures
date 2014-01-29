from django.test import TestCase
from courses.models import Course
# Create your tests here.
class CourseModelTest(TestCase):
	def test_creating_a_new_course_and_saving_it_to_the_database(self):
		course = Course()
		course.course_text = "This is an automatic test course"
		course.cat_number = "123TEST456"
		course.teacher = "test_teacher"

		course.save()

		# now check we can find it in the database again
		all_courses_in_database = Course.objects.all()
		self.assertEquals(len(all_courses_in_database), 1)
		only_course_in_database = all_courses_in_database[0]
		self.assertEquals(only_course_in_database, course)

		# and check that it's saved its three attributes: question, cat_number and teacher
		self.assertEquals(only_course_in_database.course_text, "This is an automatic test course")
		self.assertEquals(only_course_in_database.cat_number, course.cat_number)
		#self.assertEquals(only_course_in_database.teachers, course.teacher)