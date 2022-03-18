FROM python:3.8-slim-buster

WORKDIR /

COPY /requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_trf
RUN python -m spacy download de_dep_news_trf

COPY . .

WORKDIR /WordGrabbing/

CMD [ "python", "-u", "/WikidataChemicalGrabbing.py" ]
