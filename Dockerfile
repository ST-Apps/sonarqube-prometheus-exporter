# set base image (host OS)
FROM python:3.8-alpine

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

# Define the required variables for our exporter
ARG SONAR_SERVER
ENV SONAR_SERVER=$SONAR_SERVER

ARG SONAR_USERNAME
ENV SONAR_USERNAME=$SONAR_USERNAME

ARG SONAR_PASSWORD
ENV SONAR_PASSWORD=$SONAR_PASSWORD

ARG POLLING_INTERVAL
ENV POLLING_INTERVAL=$POLLING_INTERVAL

EXPOSE 8181

# command to run on container start
CMD ["sh", "-c", "python3 ./exporter.py 8181 $SONAR_SERVER $SONAR_USERNAME $SONAR_PASSWORD $POLLING_INTERVAL"]
