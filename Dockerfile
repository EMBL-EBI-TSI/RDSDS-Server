# This file is a template, and might need editing before it works on your project.
FROM dockerhub.ebi.ac.uk/tsi/base-images/dsds_server_base:v1.0.0

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt 

#USER default

EXPOSE 5000

# For some other command
CMD ["python", "main.py"]
