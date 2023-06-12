# Wildbook GUI

This app is a simple GUI for the Wildbook API. It allows the user to upload images to the Wildbook server and run the matching algorithm on them.

## Requirements
- The executable
- A running Wildbook server
- Docker

## Purpose
The GUI provides a very simple way to upload images to Wildbook and match the against the rest of  the Wildbook database. 

## Usage
1. Make sure Docker is running. The wildbook container does not need  to be running. 
2. Run the executable. After being prompted for the Wildbook port, Wildbook will be launched automatically. 
3. Make sure the Wildbook address is correct. If  you entered the correct port when prompted, this  should be correct.  
4. Click the "Upload images" button and select the images you want to upload. If you wish to upload multiple images at the same time, hold CTRL and click on the images you want to upload to select all of them, then click upload.
5. Wait for the images to upload and  be processed and matched. This may take a while depending on the number of images and the size of the images.  You can monitor the progress in the console which opens when you run the executable. 
6. Once the images have been processed, you will be shown the best match for each image and the corresponding score. If the match is correct, click "Confirm", otherwise click "Reject". 
7. The  score shown is the calculated likeness score of the two images. It is not on any specific scale, it is calculated by the underlying algorithm. It can  go as high as ~400 if matching two identical images, however this is not common. 
From testing, anything above 0.5 has a good chance of being a match, however you should not rely on the score alone adn you should confirm or reject the match by visually inspecting the pictures. 
8. You will be shown  a form to fill in the details of the seal. If you confirm a match, the form will be filled in with the name, age and gender of the matched image. You can edit these if they are incorrect. When you press submit, the details of the image you just uploaded will be sent to Wildbook and you will get a pop-up confirming this. 
9. You can now either repeat steps 4-7 to upload more images or close the app.
10. Closing the app will automatically shut down Wildbook. Due to this, closing the app might take several seconds. Do not force close the app, simply wait until it closes on its own. 

If for any reason you wish to change the details of an already uploaded picture, you can do so by simply uploading it again. Wildbook will recognize that the image is already in the database and won't make a duplicate. It will run the matching algorithm again and allow you to fill the details in again. 

## Using Wildbook
The Wildbook web UI can be accessed at http://localhost:8081. It can be used to view the database. However due to lack of granular control over the upload process, I have created an app which will let you upload new pictures and  match them against the existing Wildbook database.
The app can be found in the gui folder of this repository, where you will find the executable, source code and instructions.

## Contact
If you have any questions, anything is not working or you would like to report a bug, please create an issue in this GitHub repository and I will get back to you when possible.