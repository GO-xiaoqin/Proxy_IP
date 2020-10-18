export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

pidPath="./pid"
pid="0"

if [ $1 == "start" ];then
	workon spiderkeeper
	nohup spiderkeeper --server=http://127.0.0.1:6800  >/dev/null 2>&1 &
	echo "$!" > pid
	echo "server started"
elif [ $1 == "stop" ];then
	if [ -e "$pidPath" ];then
		pid=$(cat pid)
		if [ "$pid" != "0" ];then
			kill `cat pid`
			echo "0" > pid
		else
			echo "pid not recorded."
		fi
	else
		echo "pid not exist."
	fi
else
echo "Please make sure the position variable is start or stop."
fi

