# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test import TestCase

# from account_app.models import User
# from .models import Option, OptionImage, Question, Test


# class OptionImageModelTests(TestCase):
#     def setUp(self):
#         self.teacher = User.objects.create_user(
#             email="teacher@example.com",
#             username="teacher",
#             password="secret123",
#             first_name="Ada",
#             last_name="Lovelace",
#             role=User.Role.TEACHER,
#         )
#         self.test = Test.objects.create(
#             teacher=self.teacher,
#             title="Sample Test",
#             description="Test description",
#         )
#         self.question = Question.objects.create(
#             test=self.test,
#             question_text="What is 2 + 2?",
#             order_index=0,
#             points=1,
#         )
#         self.option = Option.objects.create(
#             question=self.question,
#             option_label="A",
#             option_text="4",
#         )

#     def test_option_can_have_multiple_images(self):
#         first_image = SimpleUploadedFile("first.png", b"first-image-bytes", content_type="image/png")
#         second_image = SimpleUploadedFile("second.png", b"second-image-bytes", content_type="image/png")

#         OptionImage.objects.create(option=self.option, image=first_image)
#         OptionImage.objects.create(option=self.option, image=second_image)

#         self.assertEqual(self.option.images.count(), 2)
