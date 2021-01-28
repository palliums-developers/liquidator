
FROM python:3.8

RUN apt-get update
RUN apt-get upgrade -y

#Install git
RUN apt-get install git -y
RUN git clone -b v0.30 https://Xing-Huang:13583744689edc@github.com/palliums-developers/violas-client.git
RUN cp ./violas-client/violas_client /usr/local/lib/python3.8/ -rf
RUN pip3.8 install -r ./violas-client/requirements.txt


WORKDIR .
RUN mkdir app
COPY . /app/
RUN pip3.8 install -r /app/requirements.txt

CMD ["python3.8", "/app/app.py"]



