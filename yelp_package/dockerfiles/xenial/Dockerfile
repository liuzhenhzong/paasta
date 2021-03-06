# Copyright 2015-2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM ubuntu:xenial

RUN echo "deb http://repos.mesosphere.com/ubuntu xenial main" > /etc/apt/sources.list.d/mesosphere.list && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv 81026D0004C44CF7EF55ADF8DF7D54CBE56151BF

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        debhelper \
        dpkg-dev \
        gcc \
        gdebi-core \
        git \
        help2man \
        libffi-dev \
        libssl-dev \
        libyaml-dev \
        pyflakes \
        python-dev \
        python-pytest \
        python-setuptools \
        python-tox \
        python-yaml \
        wget \
        zip \
        zsh \
    && apt-get clean

RUN cd /tmp && \
    wget http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb && \
    gdebi -n dh-virtualenv*.deb && \
    rm dh-virtualenv_*.deb

# mesos.native is not available on pypi, so we can either build mesos from
# source or do this, and building from source takes a long time.
# Conveniently, the .so's included in this wheel seem to be self-contained and don't link against the system libmesos.
# So that we know if this changes, we remove the mesos system package after creating the .whl, so itests run without
# a system mesos package.
RUN apt-get install -yq mesos=1.0.1-2.0.93.ubuntu1604 && \
    cd /usr/lib/python2.7/site-packages && \
	zip -r /root/mesos.native-1.0.1-py27-none-any.whl mesos/native mesos.native-1.0.1.dist-info && \
	zip -r /root/mesos.executor-1.0.1-py27-none-any.whl mesos/executor mesos.executor-1.0.1.dist-info && \
	zip -r /root/mesos.scheduler-1.0.1-py27-none-any.whl mesos/scheduler mesos.scheduler-1.0.1.dist-info && \
	apt-get remove -yq mesos

ADD mesos-slave-secret /etc/mesos-slave-secret

WORKDIR /work
