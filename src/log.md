**17.4**
- Successfully connected pyodbc to the seal database. 
- Obtained list of tables in the database.
- Most tables  are useless because they contain values related to the matching process. 
- Useful tables: 
  1. encounter - info about each encounter
  2. features - comment about encounter, has encounter_no
  3. IDs - name and photo ID
  4. image - encounter_no, image details
  5. location - loc details
  6. Paula_names - names and IDs
  7. save_encounter - more details per encounter
  8. sighting - time of sighting per sighting_no
- Opened DB in MS Access, found the self-reported table relationships
- It seems that save_encounters is unrelated to anything, no Ids match
- Newpic folder contains all the pictures

**18.4**
- Downloaded the ibeis source
- Found an online app called WildMe Seal Codex, which uses the IBEIS algorithm
- Sent a request for access to WildMe to explore whether it might be a better option
- tried to install ibeis using pip in Linux, errors out
- trying to run it from the source code on Windows, some packages arent able to install currently

**19.4**
- wrote starting form for the thesis
- got a negative reply from WildMe Codex, apparently they don't grant access to undergraduate students

**21.4**
- got IBEIS working on WSL
- exploring the app
- there is an option to start a web server, going to look into whether that is the correct way to interface with the API

**27.4**
- API works, can send requests to the server

**5.5**
- checked out WildID at the request of Beatriz
- WildID seems unfit for the task, mainly focuses on camera trap images
- started working on figuring out how IBEIS works

**9.5**
- able to  add images  to ibeis at /api/image/

**14.5**
- found wildbook
- downloaded wildbook docker image
- started working on getting it to run

**15.5**
- using wildbook instead of ibeis
- shares same API, but runs as a docker image and has a web UI
- exported database to excel for easier access
- figured out wildbook image workflow
- todo: seal species not supported, have to classify as zebra_grevys

**16.5**
- got underway, started uploading images to wildbook
- using the api, uploaded and autodetected images
- added all the data from the database to wildbook
- next: run the matching algorithm

**18.5**
- started working on the matching algorithm
- API has an endpoint for the matching algo, but it throws an exception (trying to access a NoneType object)
- trying to figure out how to run the matching algo
- option 1: import wildbook as a python module and run the matching algo from there (or create a query request that way)
- option 2: figure out the cfgdict parameter to avoid the error
- using the web  UI and the logs to try to find the proper way to run the matching algo
- can get the API to make a graph and get its UUID, but don't know how to use it or how to get the matching algo to run on the graph

**19.5**
- found why the matching endpoint wasn't working, a non-existing gid was being passed
- found how to match images using the API, had to trial/error three endpoints because two run into internal errors when returning the match list
- query/chip/dict/simple works, returns a list of match scores, can be used for adding single images
- or /query/graph/complete, matches all-to-all, returns a list of highest scores for each annotation, can be used to initialize

**20.5**
- found /api/review/query/chip/best/, which does the matching for one new annotation against all existing annotations
- probably the best option for adding new images
- figured out how to save the database created in a docker image, and how to start a new docker container using an existing database
- started uploading fielddb images to API, takes a long time

**22.5**
- finished uploading fielddb images to API, had to spend some time gathering their gid's because the original upload crashed a few times and they didn't get saved
- saved the database in db.json, so data isn't lost like gid pairings, aid to gid map etc
- then had to delete duplicates, since original db has multiple rows per 1 picture sometimes
- also added aid lists to each image in db.json
- looking into option of how to deploy the wildbook server, either locally (Docker or exe) or in the cloud (Oracle Cloud)
- locally: can use the docker python module
- started preparing to upload the second database
- started writing the README for the database conversion code  (main.py)
- database cleanup - same name can have unknown gender in one place and known in another
- finished uploading the entire field database and adding all necessary annotation data (2700 images, 2900 annotations, 1250 different seals)

**24.5**
- meeting with supervisor
- finished uploading the second database
- ~400 images are getting no detections, have to look into that
- realized that i could use the python module instead of a separate docker container, so i can make the entire app in python and just compile it  into an exe
- tried installing  the python module, getting an error because fcntl doesnt exist on windows
- won't work, fcntl doesn't exist and therefore wildbook is mac and linux only, back to docker we go

**25.5**
- found an overleaf template for the thesis
- started writing the thesis
- started working with the matching algorithm
- shared github with supervisor
- started making the GUI which will be used to upload images to the database
- GUI is partly generated with the help of chat gpt because it saves time