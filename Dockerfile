# Start with Debian Python 3.11 base image
FROM python:3.11-bullseye
RUN pip install --upgrade pip

# Update environment
RUN apt update && apt upgrade -y

# Show stdout and stderr outputs instantly without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# get libreoffice
RUN apt-get install -y libreoffice --no-install-recommends
RUN apt-get install -y default-jre
RUN apt-get install -y unoconv

# get curl for healthchecks and vim for write config file
RUN apt-get install -y curl
RUN apt-get install -y vim

# Directory app
RUN mkdir -p /home/app/src
RUN mkdir -p /var/log/flask-app && \
    touch /var/log/flask-app/flask-app.err.log && \
    touch /var/log/flask-app/flask-app.out.lo
WORKDIR /home/app

# Copy from "host" to "container"
COPY . /home/app/src

# venv
ENV VIRTUAL_ENV=/home/app/venv

# python setup
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
RUN python3 -m pip --no-cache-dir install -r /home/app/src/requirements.txt

# Add all files from current directory on host to dockerised-example directory in container
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
COPY . .

# run command in cantainer
# CMD /home/app/venv/bin/gunicorn \
#    --workers 4 \
#    --log-config app/utilitys/gunicorn/gunicorn_logging.conf \
#    --bind 0.0.0.0:5000 \
#    run:app
    # = from run (file .py) import app (file .py)

ENTRYPOINT ["python3"]
CMD ["-m", "flask", "run"]
