FROM ubuntu:18.04
# Tested on x86_64/amd64 system only.
RUN dpkg --add-architecture i386
ENV PATH /usr/local/bin:$PATH
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
# Install required packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y tshark
RUN apt-get update && apt-get install -y \
    python-dev \
    python3.7-dev \
    python3-pip \
    apt-utils \
    git-core \
    iputils-ping \
    traceroute \
    telnet \
    wget \
    curl \
    vim \
    bsdmainutils \
    zip \
    expect \
    sshpass

# -- Install java
RUN apt-get update && apt-get install -y openjdk-8-jdk ant
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# -- Install firefox
RUN apt-get update && apt-get install -y firefox libcanberra-gtk-module libcanberra-gtk3-module xserver-xorg dbus-x11

# -- Make python3.7 a default python interpreter
RUN cp /usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so
RUN rm /usr/bin/python3 && ln /usr/bin/python3.7 /usr/bin/python3 && \
    rm /usr/bin/python && ln /usr/bin/python3.7 /usr/bin/python

# -- Install allure
RUN wget http://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.10.0/allure-commandline-2.10.0.zip
RUN unzip allure-*.zip && rm allure-*.zip && mv allure-* allure && mv allure /opt/
ENV ALLURE_GEN_FILE=/opt/allure/bin/allure-gen
COPY allure-gen ${ALLURE_GEN_FILE}
RUN chmod a+x ${ALLURE_GEN_FILE}
ENV PATH="/opt/allure/bin:${PATH}"

# -- Install pycharm
RUN wget https://download.jetbrains.com/python/pycharm-community-2018.3.5.tar.gz
RUN tar xf pycharm-community*.tar.gz -C /opt && rm pycharm-community*.tar.gz && \
    mv /opt/pycharm-community* /opt/pycharm && ln -s /opt/pycharm/bin/pycharm.sh /opt/pycharm/bin/pycharm
RUN apt-get update && apt-get install -y libxslt-dev libswt-gtk-3-java
ENV PATH="/opt/pycharm/bin/:${PATH}"

# -- Install GeckoDriver
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz

RUN pip3 install pipenv
RUN mkdir -p /plume

# -- Adding Pipfiles
COPY Pipfile Pipfile.lock ./

# -- Install dependencies:
RUN set -x && pipenv install --deploy --system --ignore-pipfile

CMD ["bash"]
