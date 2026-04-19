# README.md

## Deployment hints
logs are placed in ../logs  
deployment uses supervisord and gunicorn, remember to check if these are available in the virtual env after a system update  
site runs fine with sqlite but will need psycopg2 as python drivers for postgres if using this db  
