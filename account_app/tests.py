from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from account_app.forms import ProfileForm, RegisterForm
from account_app.views import get_post_login_redirect

User = get_user_model()

DASHBOARD_URL_NAME = "dashboard"
STUDENT_DASHBOARD_URL_NAME = "student_dashboard"


def make_user(**overrides):
    defaults = {
        "email": "student@example.com",
        "username": "student1",
        "password": "supersecret123",
        "first_name": "Sam",
        "last_name": "Student",
        "role": User.Role.STUDENT,
    }
    defaults.update(overrides)
    return User.objects.create_user(**defaults)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------
class UserManagerTests(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", username="nobody", password="x")

    def test_create_user_requires_username(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="a@example.com", username="", password="x")

    def test_create_user_sets_hashed_password(self):
        user = make_user(password="mypassword123")
        self.assertNotEqual(user.password, "mypassword123")
        self.assertTrue(user.check_password("mypassword123"))

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(
            email="Test@EXAMPLE.com", username="tester", password="x12345678"
        )
        self.assertEqual(user.email, "Test@example.com")

    def test_create_superuser_defaults(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.Role.TEACHER)


class UserModelTests(TestCase):
    def test_full_name(self):
        user = make_user(first_name="Ada", last_name="Lovelace")
        self.assertEqual(user.full_name, "Ada Lovelace")

    def test_str_representation(self):
        user = make_user(first_name="Ada", last_name="Lovelace", email="ada@example.com")
        self.assertEqual(str(user), "Ada Lovelace (ada@example.com)")

    def test_is_teacher_and_is_student_flags(self):
        student = make_user(role=User.Role.STUDENT, email="s@example.com", username="s1")
        teacher = make_user(role=User.Role.TEACHER, email="t@example.com", username="t1")

        self.assertTrue(student.is_student)
        self.assertFalse(student.is_teacher)

        self.assertTrue(teacher.is_teacher)
        self.assertFalse(teacher.is_student)


class GetPostLoginRedirectTests(TestCase):
    """Direct unit tests for the helper, independent of URL configuration."""

    def test_teacher_redirects_to_dashboard(self):
        teacher = make_user(role=User.Role.TEACHER, email="t2@example.com", username="t2")
        self.assertEqual(get_post_login_redirect(teacher), "dashboard")

    def test_student_redirects_to_student_dashboard(self):
        student = make_user(role=User.Role.STUDENT, email="s2@example.com", username="s2")
        self.assertEqual(get_post_login_redirect(student), "student_dashboard")


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------
class RegisterFormTests(TestCase):
    def valid_data(self, **overrides):
        data = {
            "first_name": "New",
            "last_name": "User",
            "username": "newuser",
            "email": "newuser@example.com",
            "role": User.Role.STUDENT,
            "password": "supersecret123",
            "confirm_password": "supersecret123",
        }
        data.update(overrides)
        return data

    def test_valid_form_saves_user_with_hashed_password(self):
        form = RegisterForm(data=self.valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password("supersecret123"))

    def test_password_mismatch_adds_error_on_confirm_password(self):
        form = RegisterForm(data=self.valid_data(confirm_password="different123"))
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_password_too_short(self):
        form = RegisterForm(
            data=self.valid_data(password="short", confirm_password="short")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_duplicate_email_rejected(self):
        make_user(email="taken@example.com", username="existing")
        form = RegisterForm(data=self.valid_data(email="taken@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_duplicate_username_rejected(self):
        make_user(email="other@example.com", username="takenname")
        form = RegisterForm(data=self.valid_data(username="takenname"))
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_duplicate_email_and_password_mismatch_both_reported(self):
        make_user(email="taken2@example.com", username="existing2")
        form = RegisterForm(
            data=self.valid_data(email="taken2@example.com", confirm_password="nope")
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("confirm_password", form.errors)


class ProfileFormTests(TestCase):
    def test_only_first_and_last_name_are_editable(self):
        user = make_user()
        form = ProfileForm(
            data={"first_name": "Changed", "last_name": "Name"}, instance=user
        )
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.first_name, "Changed")
        self.assertEqual(updated.last_name, "Name")

    def test_blank_first_name_invalid(self):
        user = make_user()
        form = ProfileForm(data={"first_name": "", "last_name": "Name"}, instance=user)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------
class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_authenticated_user_is_redirected(self):
        user = make_user(role=User.Role.STUDENT)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(STUDENT_DASHBOARD_URL_NAME))

    def test_valid_post_creates_user_logs_in_and_redirects_to_dashboard(self):
        data = {
            "first_name": "New",
            "last_name": "User",
            "username": "brandnew",
            "email": "brandnew@example.com",
            "role": User.Role.TEACHER,
            "password": "supersecret123",
            "confirm_password": "supersecret123",
        }
        response = self.client.post(self.url, data=data)
        self.assertTrue(User.objects.filter(email="brandnew@example.com").exists())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(DASHBOARD_URL_NAME))

        # user should now be logged in (session persists across requests)
        profile_response = self.client.get(reverse("profile"))
        self.assertEqual(profile_response.status_code, 200)

    def test_invalid_post_shows_errors_and_sets_message(self):
        response = self.client.post(self.url, data={"email": "not-an-email"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("fix the errors" in str(m) for m in messages))


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse("login")
        self.user = make_user(email="login@example.com", username="loginuser", password="loginpass123")

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_authenticated_user_is_redirected(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(STUDENT_DASHBOARD_URL_NAME))

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            self.url, data={"username": "login@example.com", "password": "loginpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(STUDENT_DASHBOARD_URL_NAME))

    def test_valid_login_honors_next_param(self):
        next_url = reverse("profile")
        response = self.client.post(
            f"{self.url}?next={next_url}",
            data={"username": "login@example.com", "password": "loginpass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            self.url, data={"username": "login@example.com", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid email or password" in str(m) for m in messages))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.url = reverse("logout")
        self.user = make_user(email="logout@example.com", username="logoutuser")

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_post_logs_out_and_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

        # session should no longer be authenticated
        profile_response = self.client.get(reverse("profile"))
        self.assertEqual(profile_response.status_code, 302)

    def test_get_does_not_log_out_and_redirects_to_profile(self):
        """Current behavior: GET does NOT log the user out, it just redirects
        to profile. Documented here as-is -- you may want to change the view
        so a GET can't perform (or fake) a logout, or so GET actually logs
        the user out, depending on the intended UX."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("profile"))

        still_logged_in = self.client.get(reverse("profile"))
        self.assertEqual(still_logged_in.status_code, 200)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.url = reverse("profile")
        self.user = make_user(
            email="profile@example.com",
            username="profileuser",
            first_name="Old",
            last_name="Name",
        )

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_get_without_edit_param_shows_read_only_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["editing"])
        self.assertIsNone(response.context["form"])

    def test_get_with_edit_param_shows_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"edit": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["editing"])
        self.assertIsNotNone(response.context["form"])

    def test_valid_post_updates_profile_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, data={"first_name": "Updated", "last_name": "Name"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_invalid_post_rerenders_form_with_errors(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={"first_name": "", "last_name": "Name"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["editing"])
        self.assertFalse(response.context["form"].is_valid())

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Old")