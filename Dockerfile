FROM python:3.11

EXPOSE 8008

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy files
COPY api.py /app/
CMD python3 api.py
