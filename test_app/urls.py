from django.urls import path
from . import views

urlpatterns = [
    # shared
    path("",                            views.dashboard_view,           name="dashboard"),

    # teacher — test CRUD
    path("tests/create/",                         views.test_create_view,         name="test_create"),
    path("tests/<int:pk>/edit/",                  views.test_update_view,         name="test_update"),
    path("tests/<int:pk>/delete/",                views.test_delete_view,         name="test_delete"),
    path("tests/<int:pk>/results/",               views.test_results_view,        name="test_results"),

    # teacher — questions
    path("tests/<int:pk>/questions/",             views.test_edit_questions_view, name="test_edit_questions"),
    path("tests/<int:test_pk>/questions/add/",    views.question_create_view,     name="question_create"),
    path("questions/<int:pk>/edit/",              views.question_update_view,     name="question_update"),
    path("questions/<int:pk>/delete/",            views.question_delete_view,     name="question_delete"),

    # student
    path("student/dashboard/",                    views.student_dashboard_view,   name="student_dashboard"),
    path("student/search/",                       views.test_search_view,         name="test_search"),
    path("tests/<int:pk>/start/",                 views.test_start_view,          name="test_start"),
    path("attempts/<int:pk>/take/",               views.test_take_view,           name="test_take"),
    path("attempts/<int:pk>/score/",              views.test_score_view,          name="test_score"),
]