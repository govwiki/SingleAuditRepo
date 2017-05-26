########################################################
# Dockerfile for the Federal Audit Clearinghouse (FAC)
# Audit Fetcher
#
# Patrick K. Bohan <votiputox@gmail.com>
# May 22, 2017
#
# A rw volume should be mounted at runtime to /fac
# Volume should have the structure:
#   [vol]/in
#   [vol]/downloads
#   [vol]/pdfs
#
# Dependency Versions:
# - Ubuntu 16.04 LTS
# - Selenium 3.4.2
# - geckodriver 0.16.1
########################################################

FROM ubuntu:16.04

MAINTAINER Patrick K. Bohan

##################################
# Install Sun's version of Java 8
##################################

RUN apt-get update && apt-get -y install software-properties-common
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update && echo "yes" | apt-get -y install oracle-java8-installer

##############################
# Install miscellaneous stuff
##############################

RUN apt-get -y install curl git xvfb

#################################################
# Install Firefox (it has a lot of dependencies)
#################################################

RUN apt-get -y install firefox

#########################
# Install Python modules
#########################

RUN apt-get -y install python3-pip
RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install PyVirtualDisplay
RUN python3 -m pip install selenium==3.4.2
RUN python3 -m pip install openpyxl
RUN python3 -m pip install bs4

###########################################
# Fetch geckodriver and put it in the path
###########################################

WORKDIR /usr/local/bin
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.16.1/geckodriver-v0.16.1-linux64.tar.gz | tar xz

##############################
# Set up a user and work path
##############################

RUN groupadd fac
RUN useradd -ms /bin/sh -g fac fac

########################
# Make some directories
########################

RUN mkdir -p -m 0700 /fac
RUN chown -R fac:fac /fac

#####################
# Clone the FAC repo
#####################

USER fac
WORKDIR /home/fac
RUN git clone https://github.com/govwiki/SingleAuditRepo.git
WORKDIR /home/fac/SingleAuditRepo

########################################
# Munge the parameters file
#
# - set headless mode to ON
# - point directories to mounted volume
# - unset the password
########################################

RUN sed -i -e 's/\(^\s*"headlessMode\"\s*\:\s*\).*/\11\,/'                       \
           -e 's/\(^\s*"dir_in\"\s*\:\s*\"\).*/\1\/fac\/in\/\"\,/'               \
           -e 's/\(^\s*"dir_downloads\"\s*\:\s*\"\).*/\1\/fac\/downloads\/\"\,/' \
           -e 's/\(^\s*"dir_pdfs\"\s*\:\s*\"\).*/\1\/fac\/pdfs\/\"\,/'           \
           -e 's/\(^\s*"password\"\s*\:\s*\).*/\1\"\"/'                          \
           FAC_parms.txt

##########################
# Drop a bootstrap script
##########################

RUN echo "#!/bin/sh\ncp SingleAuditees.xlsx /fac/in\npython3 get_FAC.py" > bootstrap
RUN chmod 755 bootstrap

ENTRYPOINT /home/fac/SingleAuditRepo/bootstrap


