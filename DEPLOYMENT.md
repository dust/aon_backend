## env
#### supabase
* Transaction pooler OR Session pooler
* connection string

#### python 3.10+

## code
``` shell
git clone git@github.com:AONAgent/backend.git
```

## virtual env
``` shell
cd backend
python -m venv .
source bin/activate
pip install -r requirements.txt
```

## configration
* conf/config.yaml
```
SQLALCHEMY_DATABASE_URI=$connection_string_of_supabase
```

## run
``` shell
export SUPABASE_URL=$connection_string_of_supabase
python run.py
```

## nginx integration
* uwsgi
uwsgi.ini 中相关绝对路径

``` shell
uwsgi --ini ./uwsgi.ini
```
* nginx

` /etc/nginx/sites-available/aon.dexian.io `

```
server {
    listen 80;
    server_name aon.dexian.io;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name aon.dexian.io;

    ssl_certificate /etc/letsencrypt/live/aon.dexian.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aon.dexian.io/privkey.pem;

    location / {
        include uwsgi_params;
	add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' '*';
        #uwsgi_pass 127.0.0.1:8080;
	proxy_pass http://127.0.0.1:8080;
    }
}
```

nginx reload

```shell
ln -sf /etc/nginx/sites-available/aon.dexian.io /etc/nginx/sites-enabled/ 
nginx -t
nginx -s reload
```
