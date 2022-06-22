apt-get -y install \
	python3 \
	python3-dateparser
/usr/bin/git clone https://github.com/seanhly/phd
(cd phd && make install)
rm -r phd