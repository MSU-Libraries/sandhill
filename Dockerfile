FROM python:3.12-trixie

# Set the working directory
WORKDIR /sandhill

# Copy the current directory contents into the container
COPY . /sandhill

# Install the dependencies
RUN pip install -r requirements.txt && \
    # Install requirements for A11y testing
    cd /tmp && \
    wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz && \
    tar -xf geckodriver-v0.35.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    apt update && \
    apt install firefox-esr xvfb -y

# Expose the port
EXPOSE 8080

# Run the command to start uWSGI
CMD ["uwsgi", "uwsgi.ini"] 
