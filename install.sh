apt-get -y install \
	python3 \
	python3-dateparser
pip3 install grobid-tei-xml
echo ok
/usr/bin/git clone https://github.com/seanhly/phd
(cd phd && make install)
rm -r phd