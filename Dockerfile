# This file is a template, and might need editing before it works on your project.
FROM centos/python-38-centos7

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt 

#USER default

EXPOSE 5000

# For some other command
CMD ["python", "main.py"]
