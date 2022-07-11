build:
	(echo '#!/usr/bin/env python3' && (cd src && zip -r - * 2>/dev/null | cat)) > phd && chmod 755 phd
install: build
	sudo mv phd /usr/bin/; sudo chown root:root /usr/bin/phd; sudo chmod +rx /usr/bin/phd
