FROM python:3

RUN git clone -b develop https://gitlab.com/ppuerto/zerobnl.git

RUN pip install --no-cache-dir -r requirements.txt
RUN cd zerobnl && python setup.py install

RUN mkdir /home/project
WORKDIR /home/project

ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python"]