import uuid
from django.db import models
from django.conf import settings


class Test(models.Model):
    class Status(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        PUBLISHED = "published", "Published"
        CLOSED    = "closed",    "Closed"

    teacher         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tests")
    title           = models.CharField(max_length=255)
    description     = models.TextField(blank=True)
    duration_minutes= models.PositiveIntegerField(default=30)
    status          = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    start_time      = models.DateTimeField(null=True, blank=True)
    end_time        = models.DateTimeField(null=True, blank=True)
    shared_code     = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tests"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def total_points(self):
        return self.questions.aggregate(
            total=models.Sum("points")
        )["total"] or 0

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    test          = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    order_index   = models.PositiveIntegerField(default=0)
    points        = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "questions"
        ordering = ["order_index"]

    def __str__(self):
        return f"Q{self.order_index + 1}: {self.question_text[:60]}"


class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="question_images/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "question_images"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Image for {self.question}"


class Option(models.Model):
    LABELS = [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]

    question     = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_label = models.CharField(max_length=1, choices=LABELS)
    option_text  = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to="option_images/", blank=True, null=True)
    is_correct   = models.BooleanField(default=False)

    class Meta:
        db_table = "options"
        ordering = ["option_label"]
        unique_together = [["question", "option_label"]]

    def __str__(self):
        return f"{self.option_label}. {self.option_text}"


class TestAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        SUBMITTED   = "submitted",   "Submitted"

    student            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    test               = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    status             = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)
    score              = models.PositiveIntegerField(default=0)
    total_points       = models.PositiveIntegerField(default=0)
    started_at         = models.DateTimeField(auto_now_add=True)
    submitted_at       = models.DateTimeField(null=True, blank=True)
    cheating_detected  = models.BooleanField(default=False)

    class Meta:
        db_table = "test_attempts"
        unique_together = [["student", "test"]]   # one attempt per student per test
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student} — {self.test} ({self.status})"

    @property
    def percentage(self):
        if self.total_points == 0:
            return 0
        return round((self.score / self.total_points) * 100)

    @property
    def grade(self):
        if self.cheating_detected:
            return "F"
        p = self.percentage
        if p >= 90: return "A"
        if p >= 80: return "B"
        if p >= 70: return "C"
        if p >= 60: return "D"
        return "F"


class Answer(models.Model):
    attempt          = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question         = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    selected_option  = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True, related_name="answers")
    is_correct       = models.BooleanField(default=False)

    class Meta:
        db_table = "answers"
        unique_together = [["attempt", "question"]]   # one answer per question per attempt

    def __str__(self):
        return f"{self.attempt.student} | {self.question} | correct={self.is_correct}"