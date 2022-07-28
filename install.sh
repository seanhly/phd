echo "Clone repository..."
/usr/bin/git clone https://github.com/seanhly/phd /phd
echo "Make..."
(cd phd && make install)
echo "Install and start..."
phd install