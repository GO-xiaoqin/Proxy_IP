#!/bin/sh

find /home/master/Proxy_IP/proxy_ip/logs/* -mtime +1 -name "*.log" -exec rm -rf {} \;
