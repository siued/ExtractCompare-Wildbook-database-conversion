To save the database which was created in a Docker container, download the database files:
1. open the Docker Desktop app
2. go to the container
3. open the files tab
4. locate the database folder in data/db/_ibsdb
5. download the images and uploads folders, and the four .sqlite files(staging, staging_backup, database, database_backup)
6. To download a file or folder, right click on it and select save, then pick where it should be saved on your computer
7. store them in a folder structure like the original one: db/_ibsdb/ibeis_staging.sqlite etc
8. store in a safe place :)

To create a new Docker container using  the saved database, run the following command:
```docker container run -d -p <external_port>:5000 --name wildbook-ia -v full/path/to/database/db/:/data/db/ wildme/wbia:latest```
where <external_port> is the port on the host machine which will be used to access the web UI and API, and full/path/to/database/db/ is the full path to the database folder on the host machine.
