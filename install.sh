apt install python3
if [ -e /usr/bin/phd ]; then
	#/usr/bin/phd run-grobid
	echo ok
else
	/usr/bin/git clone https://github.com/seanhly/phd
	(cd phd && make install)
	rm -r phd
fi