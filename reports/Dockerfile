FROM python:3.8

RUN useradd -ms /bin/bash reports
USER reports

WORKDIR /home/reports

ADD requirements.txt requirements.txt

RUN python3 -m venv venv

RUN . venv/bin/activate \
  && python -m pip install -r requirements.txt \
  && ipython kernel install --user --name venv-notebooks
