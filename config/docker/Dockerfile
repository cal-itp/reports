FROM python:3.8

RUN useradd -ms /bin/bash reports
USER reports

WORKDIR /home/reports

ADD requirements.txt requirements.txt

ARG VIRTUAL_ENV=/home/reports/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN mkdir -p ~/.config/matplotlib

RUN python -m pip install -r requirements.txt \
  && ipython kernel install --user --name venv-notebooks \
  && ipython kernel install --user --name venv-calitp-py \
  && python -c "import matplotlib"

WORKDIR /home/reports/app