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
- won't work, fcntl library doesn't exist on windows and therefore wildbook is mac and linux only, back to docker we go

**25.5**
- found an overleaf template for the thesis
- started writing the thesis
- started working with the matching algorithm
- shared github with supervisor
- started making the GUI which will be used to upload images to the database
- GUI is partly generated with the help of chat gpt because it saves time

**26.5**
- working on GUI
- after initial preprocessing of the data on the first few matching API calls  which only happens once and gets cached, matching is quite fast (5s for 2 vs 2000 images)

**28.5**
- working on GUI
- reading HotSpotter algorithm research paper
- reading wildbook source code to find algorithm configuration flags because they aren't listed anywhere
- made a list of the config flags found, though they were found mostly in tests or directly inside the codebase
- started testing config flags to see if they even work: vsone throws errors, vsmany is the standard algorithm, smk is a different algorith i think
- other flags like fg_on and sv_on do give different results, so they will need to be tested

**29.5**
- it's my birthday :)
- started working on testing the algorithm configuration flags
- 600 pics from field db aren't getting any detections, have to look into that
- testing the algorithm will take a very long time, will have to look into reducing the number of images being tested in order to get any results in time

**2.6**
- working on gui, debugging and testing

**3.6**
- working on docker integration to abstract it away from the user
- created a docker_util file with all the docker functions
- added docker util into the gui code, now the gui starts and stops the backend on its own

**4.6**
- running more algorithm tests
- looking into using pyinstaller to compile the python code into an executable
- working on making requirements.txt for the project
- dealt with some Docker issues
- started writing thesis

**5.6**
- had to reupload the database because the docker container was being weird
- wrote a bit of thesis
- made a requirements.txt file
- looking into how to set an entire image as an annotation manually for the ones where seals dont get detected
- figured ^ out, added it to the database import code

**6.6**
- made the gui add an annotation over the whole image if no detections are found
- finished reuploading database
- writing thesis - EC, wildbook sections

**7.6**
- writing thesis - EC, conversion, wildbook sections
- debugging gui
- added a button to the gui to open the wildbook web UI
- will have to look into how to export the docker container's data

**8.6**
- testing on my laptop to ensure the database works on other devices without issues

**9.6**
- thesis - introduction
- compiled to exe using pyinstaller
- debugging/testing gui
- created directories and made everything in the repo more organized