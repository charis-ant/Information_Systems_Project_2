FROM ubuntu:16.04 
RUN apt-get update 
RUN apt-get install -y python3 python3-dev python3-pip
RUN pip3 install flask pymongo
RUN mkdir /app
COPY app2.py /app/app2.py
EXPOSE 5000
WORKDIR /app
ENTRYPOINT ["python3","-u","app2.py"] 