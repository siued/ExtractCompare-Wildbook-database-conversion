# Wildbook GUI

This app is a simple GUI for the Wildbook API. It allows the user to add seal sightings with or without images and match them against the existing Wildbook database. There is an option to view past sightings of a specific seal. There is also an option to change a seal's name or gender. 

## Requirements
- The executable
- A running Wildbook server
- Docker
- a sightings.json file in the same directory as the executable (if there isn't one, one will be created) 

## Purpose
The GUI provides a very simple way to upload images to Wildbook and match the against the rest of the Wildbook database as well as keep track of seal sightings just like ExtractCompare did. 

## First start
When you first launch the app, you don't need a running Wildbook container. If Docker is running when the app is launched, it will automatically download and run the Wildbook container (and ask you for teh directory where the database files should be stored). Keep in mind this will take some time (a 15GB download is required). 

## Usage
1. Make sure Docker is running. The wildbook container does not need to be running. 
2. Run the executable. After being prompted for the Wildbook port, Wildbook will be launched automatically. 
3. If you wish to add new sightings, click the "Add sightings" button. Here you can input sightings without images. If you wish to add sightings with images, follow steps 4-7. 
4. Click the "Upload images" button and select the images you want to upload. If you wish to upload multiple images at the same time, hold CTRL and click on the images you want to upload to select all of them, then click upload.
5. Wait for the images to upload and  be processed and matched. This may take a while depending on the number of images and the size of the images.  You can monitor the progress in the console which opens when you run the executable. 
6. Once the images have been processed, you will be shown the best match for each image and the corresponding score. If the match is correct, click "Confirm", otherwise click "Reject". 
7. The  score shown is the calculated likeness score of the two images. It is not on any specific scale, it is calculated by the underlying algorithm. It can  go as high as ~400 if matching two identical images, however this is not common. 
From testing, anything above 0.5 has a good chance of being a match, however you should not rely on the score alone and you should confirm or reject the match by visually inspecting the pictures. 
8. You will be shown  a form to fill in the details of the seal. If you confirm a match, the form will be filled in with the name, age and gender of the matched image. You can edit these if they are incorrect. When you press submit, the details will be added to the sightings table. 
9. You will be shown the sightings table again. You can keep adding sightings as you please. When you wish to save all the sightings, click "Save". This will save the sightings with images to wildbook and the ones without images to the ```sightings.json``` file.
10. Closing the app will automatically shut down Wildbook. Due to this, closing the app might take several seconds. Do not force close the app, simply wait until it closes on its own. 

If for any reason you wish to change the details of an already uploaded picture, you can do so by simply uploading it again. Wildbook will recognize that the image is already in the database and won't make a duplicate. It will run the matching algorithm again and allow you to fill the details in again. 

## Using Wildbook
The Wildbook web UI can be accessed at http://localhost:8081. It can be used to view the database. However, due to lack of granular control over the upload process, I have created an app which will let you upload new pictures and  match them against the existing Wildbook database.
The app can be found in the gui folder of this repository, where you will find the executable, source code and instructions.

## Saving the wildbook database
If you wish to make a copy of the wildbook database for any reason, you can do so by simply making a copy of the folder on your computer where the database is stored. If, for any reason, you created the Wildbook container without a mount (if you followed the instructions in db_conversion,  this is not the case) and you want to download the database, follow the instructions in ```database_save.md```

## Contact
If you have any questions, anything is not working, or you would like to report a bug, please create an issue in this GitHub repository and I will get back to you when possible.