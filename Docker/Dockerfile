FROM ubuntu

RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip install flask --break-system-packages

COPY app.py /app/

CMD ["python3","/app/app.py"]
