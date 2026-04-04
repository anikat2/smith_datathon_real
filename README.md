# smith_datathon

## initial setup
install git 

open your terminal

enter `git clone https://github.com/anikat2/smith_datathon.git`

this will make a new repository with the source code from the main branch. any changes you make won't change what you see on github until you commit your changes.

now do `cd smith_datathon`

this will make your working directory the project you just cloned

now do `code .`

this will open the folder in vscode

## begin making your first feature

in the terminal again (ensure your working directory is smith_datathon), enter `git checkout -b FEATURE_NAME` 

replace FEATURE_NAME with the name of your feature.

then make your changes, and commit (next section)

## commit your changes

run `git add .` to add your changed files to the commit you're about to make

a commit means updating the repository for everyone, so if we pull (will explain) we will have your changes on our machine

do `git commit -m "COMMIT_MESSAGE"

replace COMMIT_MESSAGE with an informative but brief message about your changes

now do `git push` to update the website with your code

## pulling your code
typically you'll be pulling code from main. pulling lets you get the most updated version of the code from the website.

just run `git pull` in the smith_datathon directory to update from main

if you need to pull from a specific branch, run `git checkout -b BRANCH_NAME`

replace BRANCH_NAME with the name of the branch to pull from

then `git pull`


## making a pull request

to merge your branch with the main branch (put your code into the main branch), submit a pull request

you can do this on the website by navigating to the `Pull requests` tab on the Github website. if you don't see it, make sure you're in the repository.

then click the `New pull request` button

usually if you recently commited, there should be a yellow notification on the top of your screen making it easy to make a pull request

otherwise, on the 2 dropdowns, make `base: main` and `compare: BRANCH_NAME` and replace BRANCH_NAME with the name of your branch.

run `pip install -r requirements.txt`

then click `Create pull request`

if you see something called a merge conflict, you can use the merge conflict editor on the website, and pick either the code in main or the code in your branch.

if there's a merge conflict that means you and the main branch have conflicting code, so only one can exist at a time. usually you can just pick your code.
