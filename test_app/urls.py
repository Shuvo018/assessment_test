from django.urls import path
from . import views

urlpatterns = [
    # shared
    path("",                            views.dashboard_view,           name="dashboard"),

    # teacher — test CRUD
    path("tests/create/",                         views.test_create_view,         name="test_create"),
    path("tests/<uuid:pk>/edit/",                 views.test_update_view,         name="test_update"),
    path("tests/<uuid:pk>/delete/",               views.test_delete_view,         name="test_delete"),
    path("tests/<uuid:pk>/results/",              views.test_results_view,        name="test_results"),

    # teacher — questions
    path("tests/<uuid:pk>/questions/",            views.test_edit_questions_view, name="test_edit_questions"),
    path("tests/<uuid:test_pk>/questions/add/",   views.question_create_view,     name="question_create"),
    path("questions/<uuid:pk>/edit/",             views.question_update_view,     name="question_update"),
    path("questions/<uuid:pk>/delete/",           views.question_delete_view,     name="question_delete"),

    # student
    path("student/dashboard/",                    views.student_dashboard_view,   name="student_dashboard"),
    path("student/search/",                       views.test_search_view,         name="test_search"),
    path("tests/<uuid:pk>/start/",                views.test_start_view,          name="test_start"),
    path("attempts/<uuid:pk>/take/",              views.test_take_view,           name="test_take"),
    path("attempts/<uuid:pk>/score/",             views.test_score_view,          name="test_score"),
]