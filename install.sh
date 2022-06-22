if [ -e /usr/bin/phd ]; then
	/usr/bin/phd run-grobid
else
	/usr/bin/git clone {GIT_SOURCE} {POOL_LABEL}
	(cd {POOL_LABEL} && make install)
	rm -r {POOL_LABEL}
fi