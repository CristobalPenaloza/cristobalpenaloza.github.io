import json
import os
import zipfile
import uuid

def detectSongs():
    if not os.path.exists('z64musicpacker.properties'):
      print('This is not an Z64 repository | Missing z64musicpacker.properties file')
      return False
    
    with open('z64musicpacker.properties') as propertiesFile:
        properties = json.load(propertiesFile)

        # Pack all the files in a single zip, to provide a faster download in the web tool
        with zipfile.ZipFile('binaries.zip', 'w', zipfile.ZIP_DEFLATED) as binariesZip:

            # Open the database, so we can modify it
            with open(properties['database'], 'r+') as databaseFile:
                database = json.load(databaseFile)
                songs = os.walk(properties['binaries'])
                
                # Check every single file inside the binaries folder
                for dirpath, dirnames, filenames in songs:
                    directory = dirpath.replace(properties['binaries'], '')

                    for filename in filenames:
                        try:
                            # Only check ootrs and mmrs files
                            if not filename.endswith('.ootrs') and not filename.endswith('.mmrs'): continue
                            
                            # Add this file to the main zip
                            osPath = os.path.join(dirpath, filename)
                            print('Repacking file: ' + osPath)
                            binariesZip.write(osPath)

                            # Check if the file is in the database
                            fullPath = os.path.join(directory, filename).replace("\\","/") 
                            detectedInDatabase = any(x["file"] == fullPath for x in database)
                            if detectedInDatabase: continue # <-- TODO: Re-add categories, usescustombank and usescustomsamples, for consistency

                            # Extract data from the file
                            isOOTRS = filename.endswith('.ootrs')
                            type, categories, usesCustomBank, usesCustomSamples = extractMetadataFromOOTRS(os.path.join(dirpath, filename))
                            
                            # If is not there, add it!
                            print('Adding missing file: ' + fullPath)
                            database.append({
                                'game': directory.replace("\\","/").split('/')[-1],
                                'song': filename.replace('.ootrs', ''),
                                'type': type,
                                'categories': categories,
                                'usesCustomBank': usesCustomBank,
                                'usesCustomSamples': usesCustomSamples,
                                'uuid': str(uuid.uuid4()),
                                'file': fullPath
                            })
                        except:
                            print("An error ocurred while processing the file " + filename)

                # Replace database with this one
                databaseFile.seek(0)
                json.dump(database, databaseFile, indent=2)
                databaseFile.truncate()

    return True


def extractMetadataFromOOTRS(path) -> tuple[str, str, bool, bool]:
    try:
        archive = zipfile.ZipFile(path, 'r')
        namelist = archive.namelist()

        for name in namelist:
            if name.endswith('.meta'):
                with archive.open(name) as meta_file:
                    lines = meta_file.readlines()
                    lines = [line.decode('utf8').rstrip() for line in lines]

                    # Extract the type and groups
                    seq_type = lines[2] if len(lines) >= 3 else 'bgm'
                    groups = [g.strip() for g in lines[3].split(',')] if len(lines) >= 4 else []

                    # Check if uses custom banks and samples
                    usesCustomBank = any(n.endswith('.zbank') for n in namelist)
                    usesCustomSamples = any(n.endswith('.zsound') for n in namelist)

                    return seq_type, groups, usesCustomBank, usesCustomSamples
    except:
        print("An error ocurred while processing the file " + path)


def main():
    result = detectSongs()

    if result: print("Process completed succesfully!")
    else: print("An error occured")


if __name__ == '__main__':
    main()
