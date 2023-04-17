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