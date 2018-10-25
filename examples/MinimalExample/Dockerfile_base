FROM python:3

RUN pip install --upgrade pip

ARG BRANCH=simple_feature
RUN git clone --single-branch -b $BRANCH https://github.com/IntegrCiTy/zerobnl.git

RUN cd zerobnl && pip install --no-cache-dir -r requirements.txt
RUN cd zerobnl && python setup.py install

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python"]