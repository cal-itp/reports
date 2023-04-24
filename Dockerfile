FROM python:3.9

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

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Add reports user
RUN useradd -ms /bin/bash reports
USER reports

WORKDIR /home/reports
