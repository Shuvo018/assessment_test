# base image
FROM python:3.11-slim

# 2. Set environment variables to optimize Python inside Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# copy the requirements file to the container
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy the application code to the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# CMD to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]