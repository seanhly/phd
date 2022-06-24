if [ -e /usr/bin/apt-get ]; then
	deb_install() {
		apt-get -y install default-jre nginx redis
	}
	deb_install
	code=$?
	while [ "$code" != 0 ]; then
		sleep 1s
		deb_install
		code=$?
	fi
elif [ -e /usr/bin/pacman ]; then
	yes y | pacman -S jre11-openjdk-headless tmux nginx redis
fi	
pip3 install grobid-tei-xml dateparser
/usr/bin/git clone https://github.com/seanhly/phd
(cd phd && make install)
rm -r phd
ufw allow from ${SSH_CLIENT%% *}
curl https://raw.githubusercontent.com/seanhly/phd/master/grobid.nginx.conf > /etc/nginx/nginx.conf
systemctl enable nginx
systemctl enable redis
service nginx restart
service redis restart