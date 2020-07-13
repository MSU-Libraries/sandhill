FROM python:3.8.2

# Set the working directory
WORKDIR /sandhill

# Copy the current directory contents into the container
COPY . /sandhill

# Install the dependencies
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "uwsgi.ini"] 


