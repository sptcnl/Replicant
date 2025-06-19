FROM python:3.12.9

WORKDIR /app


COPY backend/ .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]