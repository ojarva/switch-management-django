#!/bin/sh
#
# Add this file to crontab to start switches at boot:
# @reboot /home/switches/futurice_switchmanagement/bin/start.sh

PROJDIR=$HOME/futurice_switchmanagement
PIDFILE="$PROJDIR/switches.pid"
SOCKET="$PROJDIR/switches.sock"
OUTLOG="$PROJDIR/logs/access.log"
ERRLOG="$PROJDIR/logs/error.log"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

/usr/bin/env - \
  PYTHONPATH="../python:.." \
  ./manage.py runfcgi --settings=futurice_switchmanagement.settings socket=$SOCKET pidfile=$PIDFILE outlog=$OUTLOG errlog=$ERRLOG workdir=$PROJDIR

chmod a+w $SOCKET
