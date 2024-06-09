Z64 REPO KIT
This is a collection of files, to be used to convert any normal repository into a Z64 repository!


PROVIDE THE FILES
First you need to put the following files in the ROOT of your repository:

z64_missing_song_detector.py
z64games.json
z64musicpacker.properties
z64songs.json

It's VERY important that no file name is changed; the files have to have those specific names!


CONFIGURE THE PROPERTIES
Open the z64musicpacker.properties and modify it's contents so that they match your repository.

name: the name of your repository.
description: a short description of your repository.
binaries: a local path to the folder your music is contained (e.g. data/Music/)
avatarUrl: a web image path to an icon that represents your repository


SETUP THE MISSING SONG DETECTOR
The missing song detector is an automated process that triggers every commit, and helps in finding
any missing song, and updating their metadata. Is ideal for manual submissions and to provide an
extra step of consistency in the data.

First, in your repo, go to "Settings > Actions > General".
Under "Actions permissions" select "Allow all actions and reusable workflows" and Save.
Under "Workflow permissions" select "Read and write permissions" and Save.

Now, select the "Actions" options on the top navbar (the one that's between to Pull-request and Projects)
and press the "New workflow" button.
Under "Choose a workflow" select "setup a workflow yourself".

In the workflow creation page, set the name of the workflow to "z64_workflow.yml".
Now copy and paste the contents of the provided z64_workflow.yml file to the creation page.
Make sure to edit the "branches" and "if: github.repository ==" sections to the information of your own
repository (they are labed with an IMPORTANT comment).
Press the "Commit changes", and you are done!


TEST THE REPO
// TODO: there is currently no way to add a repo without modifing the code of the song packer and submission form.
// TODO: make this a posibility for new users in the future.
