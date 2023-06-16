# ExtractCompare database conversion

This app takes one or more databases created with the ExtractCompare (EC) tool and uploads them to a wildbook-ia server, which has much better features and UI. 

## Requirements
1. An ExtractCompare database
2. A wildbook-ia server (instructions on how to set up later)
3. Docker (instructions later)

## The database
The EC database is a Microsoft Access database. If you are using ExtractCompare, you should know where it is. Alternatively, you can open it with MS Access and find the path to it in the lower left corner as 'path to local files'. 
To use this software, you will need to export it to an Excel file. In the MS Access interface, click on 'Export  to Excel', then a window should open asking where to save it. The app can be buggy sometimes, so if nothing happens, 
try clicking on it again. If that doesn't get it to export, close MS Access and then reopen the database. Remember the Excel file location, as you will need it later. Also remember the location of the original database file, because you will need to enter the location of the 'newpic' folder where all the photos are stored. 

## Setting up Docker and Wildbook
1. Download Docker Desktop (https://www.docker.com/products/docker-desktop/). If the link doesn't lead anywhere, search for Docker  and download from there
2. Open the docker desktop installer you downloaded and follow the instructions. If your computer supports hyper-v, you can use Docker with it. If not, you will have to install WSL2. 
The Docker installer should instruct you further. TODO check this. 
3. If you are running Docker with the hyper-v backend, go to the Docker settings, Resources, Advanced, and set the allowed memory to at least 4GB. Wildbook may run slow or crash if it doesn't have enough RAM. Note that Docker will always use all the RAM you allow it while running. Also note that hyper-v Docker RAM usage will not be shown in Task Manager, so it may look like your computer's RAM is being used up by nothing. You can also give it more CPU cores if you don't mind the computer being slow while Wildbook ir running detection/matching. 
4. If you plan to use the GUI app (in the src/gui folder in this repository), you can simply run the GUI app at this point. On launch, it will check whether a Wildbook container already exists and create one otherwise. If you wish to do this manually, follow the following instructions. 
5. Open the Docker Desktop app, go to images in the menu on the left, and search for 'wildme/wbia'. Pull the image (15GB download, may take a long time). 
6. Open Powershell (press the Windows key, type in 'powershell', and press Enter). If you are on a different operating system, any terminal utility will do
7. Find the path to the directory where you would like your database to be stored (go to the folder in Windows explorer, right click on it, properties, and copy the location from there)
8. Paste the following command into Powershell, replacing the part in caps with the path from step 6. 
```docker container run -d -p 8081:5000 -m 4g --name wildbook-ia -v PATH/TO/YOUR/DATABASE/:/data/db/ wildme/wbia:latest```
If an error is printed saying the docker daemon isn't running, make sure that Docker is running and try again. 
9. Press Enter. The docker container should start, and a container id like ```e17e67870d8fe3a391e1ab76b0558d0626ce655ec3bd25b3184e57c011cce654``` should be printed in Powershell. You should also be able to see the running container in Docker if you open the container section in the menu on the left. 
10. After waiting for a minute for wildbook to initialize, open a web browser and go to http://localhost:8081. You should see the Wildbook UI. If you don't, try restarting the container in Docker.
11. If you were trying to load an already existing Wildbook database, go to View and confirm that the number of images, annotations and names are not 0. The database will not be loaded if you input the incorrect directory. If this happens, delete the Docker container and try again. 

## Converting your existing ExtractCompare database to Wildbook
Once you have your database exported to Excel and your Wildbook server running, you can start the conversion process.
1. Download the executable or the source code from this repository. If you downloaded the source code, you will need to install the dependencies listed in requirements.txt. For a guide on how to do this, search the internet on how to run a python project.
    - If you are using the source code, you can edit the code to change the behavior, if needed. If you don't need to change anything, use the executable. 
    - If you are using the source code, refer to the Wildbook terminology section in this document to understand the code better. 
    - To run the source code you will need a Python interpreter. 
2. Run the executable. In the popups, select all the required paths. 
3. The executable will create a json file with the seal information. Do not remove this file during the conversion as you might lose progress if you do so. 
4. Now simply wait for the conversion to finish. It may take several hours to even days, depending on the size of your database (around 2500 images took 8+ hours on a powerful 2020 desktop computer). If you think nothing is happening, you can check the wildbook container's logs. Go to  Docker, containers and click on the wildbook container. You will see a live feed of logs form wildbook, indicating what is happening. 
5. If you are matching the newly converted database against an existing one in Wildbook, expect this to take a long time as well. Each picture has to be preprocessed to be ready to be matched and this takes a long time. Once the preprocessing is done, it is saved and will not need to be redone. So the first matching process on a new set of images will always take much longer than any subsequent matching processes. 
6. Once the conversion is finished, you can go to the Wildbook UI and check that the database was uploaded correctly and view the pictures. You can also safely remove the .json file. If you wish to keep the .json file, you can use it with Python or other programing languages to analyze your database. 
7. If you wish to convert another database, you can simply run the executable again and give it the other database's Excel file and a different name  for the .json file.

## Matching
There  is an option to photo-match the entire freshly uploaded database against the pre-existing Wildbook database. This is disabled by default, because there are various ways to treat the results. If you wish to do this, you will have to download the source code and enable the matching function manually. 
The received matches will be stored in matching_results.json in the same folder as the executable. To further process these matches, you will have to write your own code which reads them in and analyzes them because the  desired actions differ on a case-by-case basis. 

## Known issues
Note that sometimes Wildbook crashes during intense workloads. If you are converting a large database and experience a crash during the process, you may have to restart wildbook and start the conversion process again. The progress is saved in the .json file so the conversion will pick up where it left off. 

## Using Wildbook
The Wildbook web UI can be accessed at http://localhost:8081. It can be used to view the database. However due to lack of granular control over the upload process, I have created an app which will let you upload new pictures and  match them against the existing Wildbook database.
The app can be found in the gui folder of this repository, where you will find the executable, source code and instructions.

## Contact
If you have any questions, anything is not working or you would like to report a bug, please create an issue in this GitHub repository and I will get back to you when possible. 

### Wildbook terminology
- gid - id of an uploaded picture
- annotation - a section of an image with an object of interest in it (seal in this case)
- aid - id of an annotation in a picture  (many-to-one relationship with gid)
- uuid - unique id of any object in the database (ex. annotation, picture, graph, job, etc.)
- detect: request for animal detection in an image (find annotation in image)
- query: request for the matching engine (identify matching annotations)