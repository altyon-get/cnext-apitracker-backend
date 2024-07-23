#mkdir -p /var/log/python
#mkdir -p /home/ubuntu/main/cnext-apitracker-backend/sitemap
#touch /var/log/python/debug.log
nohup python3 manage.py runserver 
#nohup celery -A cnext_apitracker_backend worker --loglevel=info &
#nohup celery -A cnext_apitracker_backend beat --loglevel=info &
tail -f /var/log/python*

