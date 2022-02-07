# syntax=docker/dockerfile:1
FROM python:3.8
WORKDIR /imdbot
COPY ../ ./
RUN ls -lah
RUN pip install -r requirments.txt
RUN python ./automation/manage.py migrate
EXPOSE 8000
CMD python ./automation/manage.py runserver 0.0.0.0:8000


# dependencies: python3.8 (docker image), django 3.2, selenium, ~/Downloads/chromedriver_v96_0 (exec permissions), djangorestframework_simplejwt


# pip install djangorestframework_simplejwt
# python -m pip install -U Selenium
# pip install Django
# wget https://chromedriver.storage.googleapis.com/98.0.4758.80/chromedriver_mac64.zip (unarchive->save in /local/bin/)