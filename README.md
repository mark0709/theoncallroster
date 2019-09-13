# theoncallroster
Django On Call Roster / TOIL tracker 
Group of containers to run the oncall roster. 
 
nginx: display static content (reverse proxy for django) 
django: the oncall roster 
redis: used as a broker for celery 
celery-worker: celery worker 
celery-beat: celery 

## Django requirements

python>=3.7  
Django>=2.2  
mysqlclient>=1.3.13 (requires mysql/mariadb development packages installed)    
pytz>=2018.7   
django-auth-ldap>=1.7.0  
holidays>=0.9.10 (used to determine public holidays)  
gunicorn>=19.9.0 (used to display dynamic content)  
redis>=3.3.8
django-redis>=4.10.0
celery>=4.3
django-celery-results>=1.1.2


## Environment Files
Create a .env file in the root of the project: 

DJANGO_SECRET_KEY='"axr)ya3dob@*jzr9(eurplq%@b71$0%4wst6_+t&oqxgbe4xve"'  
DB_DATABASE=DB NAME  
DB_USERNAME=DB user 
DB_PASSWORD=password of DB user 
DB_HOSTNAME=IPADDR or HOSTNAME of MySQL DB 
DB_PORT=3306 
DEBUG=False 
LDAPURI="" 

## Restore The Database
DB Schema not provided here  

## Start the environment with docker-compose
docker-compose build  
docker-compose up -d  
