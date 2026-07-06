# ASSESSMENT Platform
A MCQ assessment taking platform.
- Teacher can create MCQ Test
- MCQ question types text and image
- Teacher can see all students submitted test results
- Student can participate the test using shared code
- After complete the test student can see there results

Detect cheating:
- if students create new tab
- if students go to another tab

Tools: Django, CICD, Docker

live: https://assessmenttest-production.up.railway.app/

## ER diagram

![ER diagram](./github_images/ER_image.png)

# web images
## Teachers views
### create account
![create account](./github_images/create_account.png)

### create test
![create test](./github_images/create_test.png)

### add question
![add question](./github_images/add_question.png)

### question list
![question list](./github_images/question_list.png)

### submission list
![submission list](./github_images/student_submission_list.png)

## Student views
### student dashboard
![student dashboard](./github_images/student_dashboard.png)

### student find test
![find test](./github_images/find_test.png)

### test start
![test start](./github_images/test_start.png)

### see result
![see result](./github_images/see_result.png)



## Setup & Run

### Prerequisites

- Python 3.11+

---

### 1. Clone the Repository

```bash
git clone https://github.com/Shuvo018/assessment_test.git
cd assessment_test
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```


### 6. Run the Development Server

```bash
python manage.py runserver
```

App: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---