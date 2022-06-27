if [ -e /usr/bin/apt-get ]; then
	deb_install() {
		apt-get -y install default-jre nginx redis
	}
	deb_install
	code=$?
	while [ "$code" != 0 ]; do
		sleep 1s
		deb_install
		code=$?
	done
elif [ -e /usr/bin/pacman ]; then
	yes y | pacman -S jre11-openjdk-headless tmux nginx redis
fi	
pip3 install grobid-tei-xml dateparser
/usr/bin/git clone https://github.com/seanhly/phd
(cd phd && make install)
rm -r phd
ufw allow from ${SSH_CLIENT%% *}
curl https://raw.githubusercontent.com/seanhly/phd/master/grobid.nginx.conf > /etc/nginx/nginx.conf
curl https://raw.githubusercontent.com/seanhly/phd/master/transmission.json > /etc/transmission-daemon/settings.json
for s in nginx redis-server transmission-daemon; do
	systemctl enable $s
	service $s restart
done