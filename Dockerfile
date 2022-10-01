FROM python:3.10-buster
RUN /usr/local/bin/python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
COPY . /code/