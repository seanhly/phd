if [ -e /usr/bin/apt-get ]; then
	apt-get -y install default-jre
elif [ -e /usr/bin/pacman ]; then
	yes y | pacman -S jre-openjdk-headless tmux
fi	
pip3 install grobid-tei-xml dateparser
/usr/bin/git clone https://github.com/seanhly/phd
(cd phd && make install)
rm -r phd
