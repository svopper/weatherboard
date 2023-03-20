FROM python:3.9-slim

# Copy and install requirements
RUN apt-get update && apt-get -y install \
    gcc \
    g++ \
    libfreetype6-dev \
    musl-dev \
    libjpeg-dev \
    zlib1g-dev \
    # libjpeg-dev \
    python3-dev \
    fontconfig \
    libcairo2-dev \
    locales

# Set the locale
RUN sed -i '/da_DK.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG da_DK.UTF-8  
ENV LANGUAGE da_DK:da  
ENV LC_ALL da_DK.UTF-8  

# Codebase setup
RUN mkdir /srv/weatherboard/
WORKDIR /srv/weatherboard/
RUN pip3 install requests pillow flask gunicorn pytz pycairo

# Add code
ENV PYTHONPATH /srv/weatherboard/server/
ADD . /srv/weatherboard/

# Add fonts
RUN mkdir -p /usr/share/fonts && cp /srv/weatherboard/fonts/Roboto* /usr/share/fonts && fc-cache

# Runtime
EXPOSE 80
ENV PORT 80
CMD ["/bin/sh", "-c", "exec gunicorn --bind :$PORT --workers 1 --threads 8 server:app"]
