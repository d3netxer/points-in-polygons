FROM python:2.7

WORKDIR /opt

#COPY requirements.txt /opt/requirements.txt
COPY . /opt
RUN pip install -r /opt/requirements.txt

#RUN mkdir -p /opt/data

CMD [ "python", "/opt/pointsinpolygons.py" ]

