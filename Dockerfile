# dockerfile:1
FROM ubuntu as Base

LABEL authors="zoey"
LABEL version="1.0"
LABEL decsription="E-business Django Application"

#Install system dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

#Create applicaion user
RUN groupadd -r appuser && useradd -r -g appuser appuser

#Set working directory
WORKDIR /app

#Copy pyproject.toml for dependency installation
COPY pyproject.toml .

#Install Python dependencies from pyproject.toml
RUN pip3 install .

#Copy app
COPY . .

#Change file ownership to appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]