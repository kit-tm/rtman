#!/bin/ash
touch /var/log/karaf_out
KARAF_REDIRECT="/var/log/karaf_out" bin/start
echo "Following /var/log/karaf_out..."
tail -f /var/log/karaf_out
