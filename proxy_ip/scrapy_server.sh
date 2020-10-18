export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

pidPath="./twistd.pid"

if [ $1 == "start" ];then
	workon proxy_ip
	nohup scrapyd >/dev/null 2>&1 &
	echo "server started"
elif [ $1 == "stop" ];then
	if [ -e "$pidPath" ];then
		pid=$(cat twistd.pid)
		if [ "$pid" != "0" ];then
			kill `cat twistd.pid`
		else
			echo "pid not recorded."
		fi
	else
		echo "pid not exist."
	fi
else
echo "Please make sure the position variable is start or stop."
fi

