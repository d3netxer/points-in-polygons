FROM python:2.7

WORKDIR /opt/points-in-polygons

COPY requirements.txt /opt/points-in-polygons/requirements.txt
#COPY . /opt
RUN pip install -r requirements.txt && apt-get update && apt-get install -y \
    libspatialindex-dev

#RUN mkdir -p /opt/data

#CMD [ "python", "/opt/pointsinpolygons.py" ]

CMD [ "python", "/opt/points-in-polygons/time_pointsinpolygons.py" ]

