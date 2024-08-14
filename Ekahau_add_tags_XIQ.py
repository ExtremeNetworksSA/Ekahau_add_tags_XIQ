from zipfile import ZipFile
import os
import sys
import json
import math
import shutil
import pandas as pd
from colored import fg
from pprint import pprint as pp
from operator import itemgetter
import time
import inspect
#current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#parent_dir = os.path.dirname(current_dir)

PATH = os.path.dirname(os.path.abspath(__file__))

colorWhite = fg(255) ##DEFAULT Color: color pallete here: https://dslackw.gitlab.io/colored/tables/colors/
colorRed = fg(1) ##RED
colorGreen = fg(2) ##GREEN
colorPurple = fg(54) ##PURPLE
colorCyan = fg(6) ##CYAN
colorOrange = fg(94) ##ORANGE
colorGrey = fg(8)  ##GREY

# CSV columns to be used by script
csv_columns = ['AP Name', 'serial number', 'new AP Name']

def checkTags(tag_data):
    serial_tag_id = 0
    serial_tag_found = False
    for tag in tag_data['tagKeys']:
        if tag['key'] == 'serialNumber':
            serial_tag_found = True
            serial_tag_id = tag['id']
    if not serial_tag_found:
        tag_data['tagKeys'].append({
          "key": "serialNumber",
          "id": "3eff2bd4-f8b2-47fa-9bba-0ff590d1b725",
          "status": "CREATED"
        })
        serial_tag_id = "3eff2bd4-f8b2-47fa-9bba-0ff590d1b725"
    return serial_tag_id, tag_data

def importCSV(csv_file):
    csv_file = csv_file.replace("\\ ", " ")
    csv_file = csv_file.replace("'", "")
    try:
        csv_df = pd.read_csv(csv_file,dtype=str)
    except:
        log_msg = f"Unable to load csv file {csv_file}"
        print(f'{colorRed}{log_msg}')
        print("script is exiting....\n")
        raise SystemExit
    # Remove spaces from column names using strip() function
    csv_df.rename(columns=lambda x: x.strip(), inplace=True)

    return csv_df

def zip_folder(folder_path, output_filename):
    # Create a zip file
    with ZipFile(output_filename, 'w') as zipf:
        # Loop through the files in the folder
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                # Create complete filepath of file in directory
                file_path = os.path.join(foldername, filename)
                # Add file to zip
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

###################################################################################
#MAIN
###################################################################################

## CSV IMPORT
csv_file = str(input("Please enter the csv File: ")).strip()
csv_df = importCSV(csv_file)


## EKAHAU IMPORT
filename = str(input("Please enter the Ekahau File: ")).strip()
filename = filename.replace("\\ ", " ")
filename = filename.replace("'", "")

print("Gathering Ekahau Data.... ", end='')
sys.stdout.flush()
projectFolder = f"{PATH}/project"
if os.path.exists(projectFolder) and os.path.isdir(projectFolder):
    shutil.rmtree(projectFolder)
try:
    with ZipFile(filename, 'r') as zip:
        zip.extractall('project')
except FileNotFoundError:
    
    print(f"{colorRed}{filename} file does not exist\n")
    print("script is exiting....\n")
    raise SystemExit

#Check version
dir_list = os.listdir(projectFolder)
if 'project.xml' in dir_list:
    print(f"{colorRed}Older Ekahau file detected. Please update file using Ekahau 10.x and try again.\n")
    shutil.rmtree(projectFolder)
    print("script is exiting....\n")
    raise SystemExit
print(f"{colorGreen}Complete\n")

# Check / create serialNumber tag
tag_data = {}
existing_tags = False
if 'tagKeys.json' in dir_list:
    try:
        with open(f"{projectFolder}/tagKeys.json", 'r') as f:
            tag_data = json.load(f)
            serial_tag, tag_data = checkTags(tag_data)
    except json.JSONDecodeError:
        print(f"{colorRed}tagKeys.json file is corrupted, script cannot proceed\n")
        shutil.rmtree(projectFolder)
        print("script is exiting....\n")
        raise SystemExit
    except Exception as e:
        print(f"{colorRed}Error reading tagKeys.json with {str(e)}\n")
        shutil.rmtree(projectFolder)
        print("script is exiting....\n")
else:
    print(f"{colorWhite}Creating tag data... ", end="")
    tag_data = {
      "tagKeys": [
        {
          "key": "serialNumber",
          "id": "3eff2bd4-f8b2-47fa-9bba-0ff590d1b725",
          "status": "CREATED"
        }
      ]
    }
    serial_tag = "3eff2bd4-f8b2-47fa-9bba-0ff590d1b725"

#  update tag file
try:
    with open(f"{projectFolder}/tagKeys.json", 'w') as f:
        json.dump(tag_data, f)
except Exception as e:
    print(f"{colorRed}Error updating tagKeys.json with {str(e)})\n")
    shutil.rmtree(projectFolder)
    print("script is exiting....\n")

print(f"{colorGreen}added tagKeys.json")

# update APs
print(f"{colorWhite}Reading AP data... ",end='')
if 'accessPoints.json' in dir_list:
    try:
        with open(f"{projectFolder}/accessPoints.json", 'r') as f:
            ap_data = json.load(f)
    except json.JSONDecodeError:
        print(f"{colorRed}accessPoints.json file is corrupted, script cannot proceed\n")
        shutil.rmtree(projectFolder)
        print("script is exiting....\n")
        raise SystemExit
    except Exception as e:
        print(f"{colorRed}Error reading accessPoints.json with {str(e)}\n")
        shutil.rmtree(projectFolder)
        print("script is exiting....\n")
print(f"{colorGreen}Completed")
print(f"{colorWhite}")
#pp(ap_data['accessPoints'])
updated_aps = []
for ap in ap_data['accessPoints']:
    if csv_df[csv_columns[0]].eq(ap['name']).any():
        filt = csv_df[csv_columns[0]] == ap['name']
        serial_number = csv_df.loc[filt,csv_columns[1]].values[0]
        new_name = csv_df.loc[filt,csv_columns[2]].values[0]
        ap_tags = [tag for tag in ap['tags'] if tag.get("tagKeyId") == serial_tag] # search tags for matching tagKeyId
        if ap_tags:
            print(f"{colorOrange} Serial number tag found for ap {ap['name']} - value is {ap_tags[0]['value']}") # print info, but make no changes to the AP.
            print("No changes will be made to this AP.")
        else:
            new_tag = {"tagKeyId" : f"{serial_tag}",
                    "value" : f"{serial_number.strip()}"}
            ap['tags'].append(new_tag)
        
        if isinstance(new_name, str) or not math.isnan(new_name):
            if new_name.strip() != "":
                ap['name'] = new_name.strip()
        updated_aps.append(ap)
        
    else:
        print(f"{colorOrange}AP {ap['name']} was not found in the csv")
        # add AP so it is not removed from Ekahau
        updated_aps.append(ap)

ap_data['accessPoints'] = updated_aps
print(f"{colorWhite}Updating AP data... ", end="")
try:
    with open(f"{projectFolder}/accessPoints.json", 'w') as f:
        json.dump(ap_data, f)
except Exception as e:
    print(f"{colorRed}Error updating accessPoints.json with {str(e)})\n")
    shutil.rmtree(projectFolder)
    print("script is exiting....\n")
print(f"{colorGreen}Updated accessPoints.json")


output_filename = filename.replace('.esx','_EXTREME.esx')
try:
    zip_folder(projectFolder,output_filename)
except:
    print(f"{colorRed}Error occurred updating Ekahau file...")
    shutil.rmtree(projectFolder)
    print("script is exiting....\n")
shutil.rmtree(projectFolder)
print(f"{colorGreen}Updated Ekahau file and saved as {output_filename}")