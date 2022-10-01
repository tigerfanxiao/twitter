FROM python:3.10-buster
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/