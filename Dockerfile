FROM python:3.6-jessie
MAINTAINER Andrew Dunai

RUN mkdir /home/telecast

COPY ./requirements /home/telecast/requirements

WORKDIR /home/telecast

# Install requirements
RUN \
    python3.6 -m pip install -r ./requirements/test.txt

COPY ./Makefile /home/telecast
COPY ./README.rst /home/telecast
#COPY ./pytest.ini /home/telecast
COPY ./setup.py /home/telecast
COPY ./tests /home/telecast/tests
COPY ./telecast /home/telecast/telecast
RUN python3.6 ./setup.py build && ln -s $PWD/build/lib/telecast tests/
