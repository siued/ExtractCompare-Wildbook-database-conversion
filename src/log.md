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

**21.4**
- got IBEIS working on WSL
- exploring the app
- there is an option to start a web server, going to look into whether that is the correct way to interface with the API