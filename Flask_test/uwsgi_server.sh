export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

pidPath="./uwsgi.pid"

if [ $1 == "start" ];then
	workon proxy_ip
	uwsgi --ini uwsgi.ini
	echo "server started"
elif [ $1 == "stop" ];then
	if [ -e "$pidPath" ];then
		pid=$(cat uwsgi.pid)
		if [ "$pid" != "0" ];then
			workon proxy_ip
			uwsgi --stop uwsgi.pid
		else
			echo "pid not recorded."
		fi
	else
		echo "pid not exist."
	fi
else
echo "Please make sure the position variable is start or stop."
fi

