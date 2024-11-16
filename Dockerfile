ARG ALPINE_VERSION=3.20
ARG WORKDIR="/home/nobody/passdown/"
FROM alpine:${ALPINE_VERSION}
WORKDIR "/home/nobody/passdown/"

# Install packages
RUN apk add --no-cache \
    python3 \
    py3-pip

# Create a virtual env
RUN python -m venv /opt/venv

# Source virtual env
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN python3 -m pip install --no-cache-dir \
    "pelican[markdown]" \
    "python-telegram-bot" \
    "pyyaml" \
    "telegram"

# Create a directory for pelican
RUN mkdir -p pelican

# Copy all neccesary files
COPY "config.ini" /home/nobody/passdown
COPY "passdown.py" /home/nobody/passdown
COPY "errors.py" /home/nobody/passdown/
COPY "pelicanconf.py" /home/nobody/passdown/pelican
COPY "publishconf.py" /home/nobody/passdown/pelican/

# Change ownership of dirs to nobody
RUN chown -Rv nobody:nobody /home/nobody/passdown/ /home/nobody/passdown/pelican/

# Change to non-root user
USER nobody
# Run passdown bot
ENTRYPOINT [ "python3", "passdown.py" ]

