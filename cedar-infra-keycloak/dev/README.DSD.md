# Theme development

This directory contains a docker-compose deployment to ease the development and update of themed UI-s for keycloak, eg. our customized login panel. The theme file are in [cedar-03](..%2Fconfig%2Fthemes%2Fcedar-03). Thse files are the actual files deployed in a cedar deployment and the [docker-compose.yml](docker-compose.yml) in this dev directory starts a keycloak to edit these very same files. When running [docker-compose.yml](docker-compose.yml) you can edit the files and see the changes by reloading the web page.

Reset:

    docker-compose down && docker volume rm dev_postgresql_data

Start:

    docker-compose up

Login:
    
    http://localhost:8024
    admin/admin

Open:

http://localhost:8024/realms/CEDAR/login-actions/authenticate?client_id=cedar-angular-app

Edit:

- [template.ftl](..%2Fconfig%2Fthemes%2Fcedar-03%2Flogin%2Ftemplate.ftl)
- [login.ftl](..%2Fconfig%2Fthemes%2Fcedar-03%2Flogin%2Flogin.ftl)
- [theme.properties](..%2Fconfig%2Fthemes%2Fcedar-03%2Flogin%2Ftheme.properties)
