# The planning for a small GUI for the Seal-Pattern-Recognition project

## Usage
The app is primarily used to upload new pictures  to the wildbook database and run the  matching algorithm on them.



## Flow
- user opens the app
- they input the url to the wildbook server, there is a default one pre-set
- they upload one or more images
- the app uploads the images to the server using /api/upload/image
- the app runs the detection algorithm on the  new images using api/detect/cnn/yolo
- the app runs the matching algorithm on the new images using api/query/chip/dict/simple and gets the list of matches for each
- the app shows the user the best match for every new image and lets them choose whether it is amatch or not
- if no match, the user fills in a form with the seals' details, otherwise they get copied from the best match