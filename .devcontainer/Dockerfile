FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye
ARG vscode
#RUN if [[ -z "$devcontainercli" ]] ; then printf "\nERROR: This Dockerfile needs to be built with VS Code !"RUN exit 1; else printf "VS Code is detected: $devcontainercli"; fi

ARG firefox_ver=130.0
ARG geckodriver_ver=0.35.0

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends --no-install-suggests \
            ca-certificates
RUN update-ca-certificates
RUN apt-get install -y --no-install-recommends --no-install-suggests \
            curl bzip2
 # Install dependencies for Firefox
RUN apt-get install -y --no-install-recommends --no-install-suggests \
            `apt-cache depends firefox-esr | awk '/Depends:/{print$2}'` \
            # additional 'firefox-esl' dependencies which is not in 'depends' list
            libxt6
 # Download and install Firefox
RUN curl -fL -o /tmp/firefox.tar.bz2 \
         https://ftp.mozilla.org/pub/firefox/releases/${firefox_ver}/linux-x86_64/en-GB/firefox-${firefox_ver}.tar.bz2
RUN tar -xjf /tmp/firefox.tar.bz2 -C /tmp/
RUN mv /tmp/firefox /opt/firefox
 # Download and install geckodriver
RUN curl -fL -o /tmp/geckodriver.tar.gz \
         https://github.com/mozilla/geckodriver/releases/download/v${geckodriver_ver}/geckodriver-v${geckodriver_ver}-linux64.tar.gz
RUN tar -xzf /tmp/geckodriver.tar.gz -C /tmp/
RUN chmod +x /tmp/geckodriver
RUN mv /tmp/geckodriver /usr/local/bin/
 # Cleanup unnecessary stuff
#RUN apt-get purge -y --auto-remove \
#                  -o APT::AutoRemove::RecommendsImportant=false \
#            curl bzip2
RUN rm -rf /var/lib/apt/lists/* \
           /tmp/*

# As this image cannot run in non-headless mode anyway, it's better to forcibly
# enable it, regardless whether WebDriver client requests it in capabilities or
# not.
ENV MOZ_HEADLESS=1
ENV PATH=$PATH:/opt/firefox