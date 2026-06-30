#!/data/data/com.termux/files/usr/bin/sh
# Skrypt do zarz?dzania blogiem SEO
# U?ycie: ./blog-manager.sh start|stop|restart|status

PIDFILE="$HOME/blog-seo/server.pid"

case "$1" in
  start)
    cd ~/blog-seo
    nohup python3 -m http.server 8080 --bind 0.0.0.0 > /dev/null 2>&1 &
    echo $! > "$PIDFILE"
    echo "Blog uruchomiony na http://localhost:8080"
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      kill $(cat "$PIDFILE") 2>/dev/null
      rm "$PIDFILE"
      echo "Blog zatrzymany"
    else
      echo "Blog nie jest uruchomiony"
    fi
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
      echo "Blog DZIA?A na http://localhost:8080"
    else
      echo "Blog NIE DZIA?A"
    fi
    ;;
  generate)
    python3 ~/generator-seo.py single
    ;;
  *)
    echo "U?ycie: $0 start|stop|restart|status|generate"
    ;;
esac
