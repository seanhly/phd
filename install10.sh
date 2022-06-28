if [ -e /usr/bin/apt-get ]; then
	deb_install() {
		echo "Installing DEB dependencies..."
		apt-get -y install default-jre nginx redis transmission-daemon python3-redis python3-dateparser 2>&1 \
		| while read line; do
			printf "\r                                                                    "
			printf "\r%s" "$line"
		done
		echo 
	}
	deb_install
	code=$?
	while [ "$code" != 0 ]; do
		sleep 1s
		deb_install
		code=$?
	done
	echo "Installing PIP dependencies..."
	pip3 install grobid-tei-xml >/dev/null 2>/dev/null
elif [ -e /usr/bin/pacman ]; then
	yes y | pacman -S jre11-openjdk-headless tmux nginx redis transmission-daemon \
	| while read line; do
		printf "\r                                                                    "
		printf "\r%s" "$line"
	done
	echo
	echo "Installing PIP dependencies..."
	pip3 install grobid-tei-xml dateparser redis >/dev/null 2>/dev/null
fi	
echo "Cloning repository..."
/usr/bin/git clone https://github.com/seanhly/phd >/dev/null 2>/dev/null
echo "Making..."
(cd phd && make install) >/dev/null 2>/dev/null
echo "Clean up..."
rm -r phd
echo "Allowing SSH..."
ufw allow from ${SSH_CLIENT%% *} >/dev/null 2>/dev/null
echo "Transferring configs..."
curl -s https://raw.githubusercontent.com/seanhly/phd/master/grobid.nginx.conf > /etc/nginx/nginx.conf 2>/dev/null
curl -s https://raw.githubusercontent.com/seanhly/phd/master/transmission.json > /etc/transmission-daemon/settings.json 2>/dev/null
curl -s https://raw.githubusercontent.com/seanhly/phd/master/redis.conf > /etc/redis/redis.conf 2>/dev/null
for s in nginx redis-server transmission-daemon; do
	echo "Enabling $s..."
	systemctl enable $s
	service $s restart
done
echo "Done."
