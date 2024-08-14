# EKahau Add Serial Number Tag
### Ekahau_add_tags_XIQ.py
## Purpose
The script will prompt the user for a CSV file and an Ekahau file. This script will read a CSV file that includes the names of the APs in an Ekahau file, the serial numbers of those APs, and an optional name to update the APs. The script will then open up the Ekahau file, find the APs based on the name added in the CSV. The script will then add a serialNumber tag to the AP and add the serial number value from the CSV. If the CSV has a name to update the AP to the script will change the AP name. Once the script has completed all APs, the script will save a new Ekahau file using the same name and appending _EXTREME to it. 
With this updated file you can easily import the Ekahau file in XIQ's real time maps and have the APs onoboarded or moved to the new floorplan.

## Information
##### CSV file
The script will prompt for a csv file. The script will look for 3 columns in the CSV, any other columns will be ignored. 
The first column it looks for is 'AP Name'. This column should include the name of the AP as it appears in the Ekahau file.
The second column it looks for is 'serial number'. This column should include the XIQ serial numbers for the APs.
the third column it looks for is 'New AP Name'. This column needs to be in the CSV but does not need to be filled out if the AP names are not changing. If you do need to update the names, names in this column will be added to the Ekahau file in replacement to the 'AP Name' on the same row of the CSV.
###### <span style="color:purple"> Ekahau_tag.csv is included as an example.</span>
##### Ekahau file
The script will prompt for the Ekahau file. Once the script finishes running the updated Ekahau file will be saved with the same name with _EXTREME appended to it. The original file will not be modified.

original_file: "Extreme Networks Import.esx"
output_file: "Extreme Networks Import_EXTREME.esx"

## Running the script
open the terminal to the location of the script and run this command.
```
python Ekahau_add_tags_XIQ.py
```
## requirements
There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.