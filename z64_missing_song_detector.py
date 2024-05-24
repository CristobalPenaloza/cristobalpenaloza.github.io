import json
import os
import zipfile
import uuid
import traceback

def detectSongs():
    if not os.path.exists('z64musicpacker.properties'):
      print('This is not an Z64 repository | Missing z64musicpacker.properties file')
      return False
    
    with open('z64musicpacker.properties') as propertiesFile:
        properties = json.load(propertiesFile)
        binaries = properties['binaries']

        # Pack all the files in a single zip, to provide a faster download in the web tool
        with zipfile.ZipFile('binaries.zip', 'w', zipfile.ZIP_DEFLATED) as binariesZip:

            # Open the database, so we can modify it
            with open(properties['database'], 'r+') as databaseFile:
                database = json.load(databaseFile)
                
                # First, check if the names and files are correct
                # The database name has priority in this
                for i, entry in enumerate(database):

                    # Check if the file is there...
                    actualPath = entry['file']
                    if os.path.isfile(os.path.join(binaries, actualPath)):
                        
                        # If the file exists, check if the path is the intended one
                        intendedPath = entry['game'] + '/' + entry['song'] + os.path.splitext(actualPath)[1]
                        if intendedPath != actualPath:
                            print('DIFFERENT PATH DETECTED')
                            print('Intended path: ' + intendedPath)
                            print('Actual path:   ' + entry['file'])
                            print('Fixing... ')

                            # Only rename it if we find it... It may have changed already!
                            database[i]['file'] = intendedPath
                            os.rename(os.path.join(binaries, actualPath), os.path.join(binaries, intendedPath))
                    
                    # If we don't find it, then remove it from the database
                    # Still, evaluate if this is ok to do...
                    else:
                        print('MISSING ENTRY DETECTED')
                        print('Path: ' + actualPath)
                        print('Removing...')
                        database.pop(i)



                # Check every single file inside the binaries folder
                songs = os.walk(binaries)
                for dirpath, dirnames, filenames in songs:
                    directory = dirpath.replace(binaries, '')

                    # Remove empty folders
                    if len(os.listdir(dirpath)) == 0:
                        print("EMPTY FOLDER DETECTED")
                        print("Folder: " + dirpath)
                        print("Clean up... Clean up...")
                        os.rmdir(dirpath)
                        continue

                    # Check every single file inside this  folder
                    for filename in filenames:
                        try:
                            # Only check ootrs and mmrs files
                            if not filename.endswith('.ootrs') and not filename.endswith('.mmrs'): continue

                            # Extract data from the file
                            type, categories, usesCustomBank, usesCustomSamples = extractMetadata(os.path.join(dirpath, filename))

                            # Check if the file is in the database
                            fullPath = os.path.join(directory, filename).replace("\\","/")
                            detectedInDatabase = any(x["file"] == fullPath for x in database)

                            # If the file is in the DB, instead check it's integrity
                            if detectedInDatabase:
                                print('Updating file on DB: ' + fullPath)
                                i = [x["file"] for x in database].index(fullPath)
                                database[i]["type"] = type
                                database[i]["categories"] = categories
                                database[i]["usesCustomBank"] = usesCustomBank
                                database[i]["usesCustomSamples"] = usesCustomSamples

                            # If is not there, add it!
                            else:
                                print('Adding missing file to DB: ' + fullPath)
                                database.append({
                                    'game': directory.replace("\\","/").split('/')[-1],
                                    'song': filename.replace('.ootrs', '').replace('.mmrs', ''),
                                    'type': type,
                                    'categories': categories,
                                    'usesCustomBank': usesCustomBank,
                                    'usesCustomSamples': usesCustomSamples,
                                    'uuid': str(uuid.uuid4()),
                                    'file': fullPath
                                })

                            # Add this file to the main zip
                            osPath = os.path.join(dirpath, filename)
                            binariesZip.write(osPath)

                        except Exception:
                            print("An error ocurred while processing the file " + filename + ": " + traceback.format_exc())

                # Replace database with this one
                databaseFile.seek(0)
                json.dump(database, databaseFile, indent=2)
                databaseFile.truncate()

    return True


def extractMetadata(path) -> tuple[str, list, bool, bool]:
    isOOTRS = path.endswith('.ootrs')
    if isOOTRS: return extractMetadataFromOOTRS(path)
    else: return extractMetadataFromMMRS(path)


def extractMetadataFromOOTRS(path) -> tuple[str, list, bool, bool]:
    archive = zipfile.ZipFile(path, 'r')
    namelist = archive.namelist()

    for name in namelist:
        if name.endswith('.meta'):
            with archive.open(name) as meta_file:
                lines = meta_file.readlines()
                lines = [line.decode('utf8').rstrip() for line in lines]

                # Extract the type and groups
                seq_type = (lines[2] if len(lines) >= 3 else 'bgm').lower()
                groups = [g.strip() for g in lines[3].split(',')] if len(lines) >= 4 else []

                # Check if uses custom banks and samples
                usesCustomBank = any(n.endswith('.zbank') for n in namelist)
                usesCustomSamples = any(n.endswith('.zsound') for n in namelist)

                return seq_type, groups, usesCustomBank, usesCustomSamples


def extractMetadataFromMMRS(path) -> tuple[str, list, bool, bool]:
    archive = zipfile.ZipFile(path, 'r')
    namelist = archive.namelist()

    for name in namelist:
        if name == 'categories.txt':
            with archive.open(name) as categories_file:
                lines = categories_file.readlines()
                lines = [line.decode('utf8').rstrip() for line in lines]

                # Extract the categories
                categories = [g.strip() for g in lines[0].replace('-', ',').split(',')] if len(lines) >= 1 else []

                # Define the type by checking the categories
                isFanfare = all(cat in ['8', '9', '10'] for cat in categories) and len(categories) > 0
                seq_type = 'fanfare' if isFanfare else 'bgm'

                # Check if uses custom banks and samples
                usesCustomBank = any(n.endswith('.zbank') for n in namelist)
                usesCustomSamples = any(n.endswith('.zsound') for n in namelist)

                return seq_type, categories, usesCustomBank, usesCustomSamples


def main():
    result = detectSongs()

    if result: print("Process completed succesfully!")
    else: print("An error occured")


if __name__ == '__main__':
    main()
