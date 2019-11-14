FROM python:3.7

WORKDIR /files_store
COPY files_store /files_store
RUN pip install -r requirements.txt

COPY cmd.sh /
CMD ["/cmd.sh"]