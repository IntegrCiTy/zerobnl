FROM python:3

RUN pip install --upgrade pip

RUN git clone https://gitlab.com/ppuerto/zerobnl.git

RUN cd zerobnl && pip install --no-cache-dir -r requirements.txt
RUN cd zerobnl && python setup.py install

RUN mkdir /home/project
WORKDIR /home/project

ADD . $WORKDIR

ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python"]