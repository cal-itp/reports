FROM python:3.8

# Install npm/node for creating reports website
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
  && apt-get install -y nodejs

# Install gcloud-cli for downloading/uploading files
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] \
  http://packages.cloud.google.com/apt cloud-sdk main" \
  | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
  | tee /usr/share/keyrings/cloud.google.gpg && apt-get update -y \
  && apt-get install google-cloud-cli -y

# Add reports user
RUN useradd -ms /bin/bash reports
USER reports

WORKDIR /home/reports

# Create python virtual environment, install python packages
COPY requirements.txt requirements.txt

ARG VIRTUAL_ENV=/home/reports/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python packages
RUN mkdir -p ~/.config/matplotlib
RUN python -m pip install -r requirements.txt \
  && ipython kernel install --user --name venv-notebooks \
  && ipython kernel install --user --name venv-calitp-py \
  && python -c "import matplotlib"

WORKDIR /home/reports/app