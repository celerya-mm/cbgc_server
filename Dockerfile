# Start with Debian Python 3.11 base image
FROM python:3.11-bullseye

MAINTAINER Marco Mazzini <mazzini@celerya.com>

RUN pip install --upgrade pip
RUN pip install pipenv

# Update environment
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get clean && apt-get update && apt-get upgrade -y && \
    apt-get install -y

# Show stdout and stderr outputs instantly without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# get libreoffice
RUN apt-get install -y apt-utils
RUN apt-get install -y dialog
RUN apt-get install -y wkhtmltopdf
#RUN apt-get install -y libreoffice
#RUN apt-get install python3-uno
#RUN apt-get install unoconv
#RUN apt-get install -y default-jre

# get curl for healthchecks and vim for write config file
RUN apt-get install -y curl
RUN apt-get install -y vim

# Directory app
RUN mkdir -p /home/app/src
RUN mkdir -p /var/log/app && \
    touch /var/log/app/flask-app.err.log && \
    touch /var/log/app/flask-app.out.log

# Copy from "host" to "container"
COPY . /home/app/src

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# add user
RUN useradd -ms /bin/bash celerya
WORKDIR /home/app

# Install dependencies
RUN $VIRTUAL_ENV/bin/python3.11 -m pip install -U --no-cache-dir pip setuptools wheel
RUN grep -v "pywin32" /home/app/src/requirements.txt | xargs $VIRTUAL_ENV/bin/python3.11 -m pip --no-cache-dir install --use-pep517

#RUN ln -s /usr/lib/python3/dist-packages/uno.py $VIRTUAL_ENV/lib/python3.11/site-packages/uno.py
#RUN ln -s /usr/lib/python3/dist-packages/unohelper.py $VIRTUAL_ENV/lib/python3.11/site-packages/unohelper.py

# clean package manager cache to reduce your custom image size...
RUN apt-get clean all \
    && rm -rvf /var/lib/apt/lists/*

# Add all files from current directory on host to dockerised-example directory in container
ENV FLASK_APP=wsgi.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
COPY . .

# run command in cantainer
#CMD $VIRTUAL_ENV/bin/gunicorn \
#    --workers 2 \
#    -t 60 \
#    --log-config app/utilitys/gunicorn/gunicorn_logging.conf \
#    --bind 0.0.0.0:5000 \
#    wsgi:app
##       = from run (file .py) import app (file .py)

ENTRYPOINT ["./gunicorn.sh"]

#ENTRYPOINT ["python3"]
#CMD ["-m", "flask", "run"]
