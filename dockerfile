FROM python:3

WORKDIR /!!!Your/Workdir/Name!!!
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["python" "src/main.py"]
