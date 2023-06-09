# ExtractCompare database conversion

This app takes one or more databases created with the ExtractCompare (EC) tool and uploads them to a wildbook-ia server, which has much better features and UI. 

## Requirements
1. An ExtractCompare database
2. A wildbook-ia server (instructions on how to set up later)
3. Python 3.9

## The database
The EC database is a Microsoft Access database. If you are using ExtractCompare, you should know where it is. Alternatively, you can open it with MS Access and find the path to it in the lower left corner as 'path to local files'. 
To use this software, you will need to export it to an Excel file. In the MS Access interface, click on 'Export  to Excel', then a window should open asking where to save it. The app can be buggy sometimes, so if nothing happens, 
try clicking on it again. If that doesn't get it to export, close MS Access and then reopen the database. Remember the file location, as you will need it later.


## Usage
Note that sometimes wildbook crashes during intense workloads. If you are uploading a large database and experience a crash, you may have to restart wildbook and start the upload again. The photos which have already been uploaded will be skipped. 


### Wildbook terminology
- gid - id of an uploaded picture
- annotation - a section of an image with an object of interest in it (seal in this case)
- aid - id of an annotation in a picture  (many-to-one relationship with gid)
- uuid - unique id of any object in the database (ex. annotation, picture, graph, job, etc.)
- detect: request for animal detection in an image (find annotation in image)
- query: request for the matching engine (identify matching annotations)