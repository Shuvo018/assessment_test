from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import Test, Question, Option, TestAttempt, Answer
from .forms import TestForm, QuestionForm, OptionFormSet
from .decorators import teacher_required, student_required


# ─────────────────────────────────────────────
# SHARED
# ─────────────────────────────────────────────

@login_required
def dashboard_view(request):
    user = request.user
    if user.is_teacher:
        tests = Test.objects.filter(teacher=user)
        return render(request, "tests/teacher_dashboard.html", {"tests": tests})
    else:
        return redirect("student_dashboard")


# ─────────────────────────────────────────────
# TEACHER — TEST CRUD
# ─────────────────────────────────────────────

@teacher_required
def test_create_view(request):
    form = TestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        test = form.save(commit=False)
        test.teacher = request.user
        test.save()
        messages.success(request, "Test created. Now add your questions.")
        return redirect("test_edit_questions", pk=test.pk)
    return render(request, "tests/test_form.html", {"form": form, "action": "Create"})


@teacher_required
def test_update_view(request, pk):
    test = get_object_or_404(Test, pk=pk, teacher=request.user)
    form = TestForm(request.POST or None, instance=test)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Test updated.")
        return redirect("dashboard")
    return render(request, "tests/test_form.html", {"form": form, "action": "Update", "test": test})


@teacher_required
def test_delete_view(request, pk):
    test = get_object_or_404(Test, pk=pk, teacher=request.user)
    if request.method == "POST":
        test.delete()
        messages.success(request, f'"{test.title}" has been deleted.')
        return redirect("dashboard")
    return render(request, "tests/test_confirm_delete.html", {"test": test})


# ─────────────────────────────────────────────
# TEACHER — QUESTION & OPTION MANAGEMENT
# ─────────────────────────────────────────────

@teacher_required
def test_edit_questions_view(request, pk):
    test      = get_object_or_404(Test, pk=pk, teacher=request.user)
    questions = test.questions.prefetch_related("options").all()
    return render(request, "tests/test_edit_questions.html", {
        "test":      test,
        "questions": questions,
    })


@teacher_required
def question_create_view(request, test_pk):
    test = get_object_or_404(Test, pk=test_pk, teacher=request.user)
    q_form  = QuestionForm(request.POST or None)
    formset = OptionFormSet(request.POST or None)
    if request.method == "POST" and q_form.is_valid() and formset.is_valid():
        with transaction.atomic():
            question             = q_form.save(commit=False)
            question.test        = test
            question.order_index = test.questions.count()
            question.save()
            formset.instance = question
            formset.save()
        messages.success(request, "Question added.")
        return redirect("test_edit_questions", pk=test.pk)
    return render(request, "tests/question_form.html", {
        "test": test, "q_form": q_form, "formset": formset, "action": "Add",
    })


@teacher_required
def question_update_view(request, pk):
    question = get_object_or_404(Question, pk=pk, test__teacher=request.user)
    test     = question.test
    q_form  = QuestionForm(request.POST or None, instance=question)
    formset = OptionFormSet(request.POST or None, instance=question)
    if request.method == "POST" and q_form.is_valid() and formset.is_valid():
        with transaction.atomic():
            q_form.save()
            formset.save()
        messages.success(request, "Question updated.")
        return redirect("test_edit_questions", pk=test.pk)
    return render(request, "tests/question_form.html", {
        "test": test, "q_form": q_form, "formset": formset, "action": "Edit",
    })


@teacher_required
def question_delete_view(request, pk):
    question = get_object_or_404(Question, pk=pk, test__teacher=request.user)
    test     = question.test
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted.")
    return redirect("test_edit_questions", pk=test.pk)


# ─────────────────────────────────────────────
# TEACHER — RESULTS
# ─────────────────────────────────────────────

@teacher_required
def test_results_view(request, pk):
    test     = get_object_or_404(Test, pk=pk, teacher=request.user)
    attempts = test.attempts.filter(
        status=TestAttempt.Status.SUBMITTED
    ).select_related("student").order_by("-score")
    return render(request, "tests/test_results.html", {
        "test": test, "attempts": attempts,
    })


# ─────────────────────────────────────────────
# STUDENT — DASHBOARD & TEST SEARCH
# ─────────────────────────────────────────────

@student_required
def student_dashboard_view(request):
    user = request.user

    # All attempts (submitted + in-progress)
    attempts    = TestAttempt.objects.filter(student=user).select_related("test")
    attempt_map = {str(a.test_id): a for a in attempts}

    # Tests the student has joined
    joined_ids = [a.test_id for a in attempts]
    my_tests   = Test.objects.filter(id__in=joined_ids).select_related("teacher").order_by("-created_at")

    return render(request, "tests/student_dashboard.html", {
        "my_tests":    my_tests,
        "attempt_map": attempt_map,
    })


@student_required
def test_search_view(request):
    """Student enters a test UUID to find and join a test."""
    query      = request.GET.get("code", "").strip()
    found_test = None
    error      = None

    if query:
        try:
            found_test = Test.objects.select_related("teacher").get(pk=query)
            if found_test.status == Test.Status.DRAFT:
                error      = "This test is not yet published by the teacher."
                found_test = None
            elif found_test.status == Test.Status.CLOSED:
                error      = "This test is closed and no longer accepting submissions."
                found_test = None
        except (Test.DoesNotExist, ValueError):
            error = "No test found with that code. Please check and try again."

    return render(request, "tests/test_search.html", {
        "query":      query,
        "found_test": found_test,
        "error":      error,
    })


# ─────────────────────────────────────────────
# STUDENT — TAKE TEST
# ─────────────────────────────────────────────

@student_required
def test_start_view(request, pk):
    test = get_object_or_404(Test, pk=pk, status=Test.Status.PUBLISHED)

    if TestAttempt.objects.filter(student=request.user, test=test).exists():
        messages.warning(request, "You have already attempted this test.")
        return redirect("student_dashboard")

    if request.method == "POST":
        attempt = TestAttempt.objects.create(
            student      = request.user,
            test         = test,
            total_points = test.total_points,
        )
        return redirect("test_take", pk=attempt.pk)

    return render(request, "tests/test_start.html", {"test": test})


@student_required
def test_take_view(request, pk):
    attempt   = get_object_or_404(
        TestAttempt, pk=pk, student=request.user, status=TestAttempt.Status.IN_PROGRESS
    )
    test      = attempt.test
    questions = test.questions.prefetch_related("options").all()

    if request.method == "POST":
        with transaction.atomic():
            score = 0
            for question in questions:
                selected_id = request.POST.get(f"question_{question.pk}")
                selected    = None
                is_correct  = False
                if selected_id:
                    try:
                        selected   = question.options.get(pk=selected_id)
                        is_correct = selected.is_correct
                        if is_correct:
                            score += question.points
                    except Option.DoesNotExist:
                        pass
                Answer.objects.update_or_create(
                    attempt=attempt, question=question,
                    defaults={"selected_option": selected, "is_correct": is_correct},
                )
            attempt.score        = score
            attempt.status       = TestAttempt.Status.SUBMITTED
            attempt.submitted_at = timezone.now()
            attempt.save()
        messages.success(request, "Test submitted successfully!")
        return redirect("test_score", pk=attempt.pk)

    return render(request, "tests/test_take.html", {
        "attempt": attempt, "test": test, "questions": questions,
    })


@student_required
def test_score_view(request, pk):
    attempt = get_object_or_404(
        TestAttempt, pk=pk, student=request.user, status=TestAttempt.Status.SUBMITTED
    )
    answers = attempt.answers.select_related(
        "question", "selected_option"
    ).prefetch_related("question__options").order_by("question__order_index")
    return render(request, "tests/test_score.html", {
        "attempt": attempt, "answers": answers,
    })