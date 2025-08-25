# Postman v3 Cloudability API collection
A Customer Sevice repository to simplify inclusion of common API calls needed by Postman

![Postman](https://tenor.com/view/postman-letter-mail-courier-mailman-gif-12920117)


This repo provides the ability to:

- Program in Python, Node, Java, etc
- Add version control to scripts/tooling for the CS organization

# Developing

To get started with developing on this repo:

- Clone the repository 
 ```git clone git@github.com:cloudability/cs-hub.git```
- Create a new branch 
 ```git checkout -b updating_v3```
- Rename ```Cloudability.postman_collection.json.example``` to ```Cloudability.postman_collection.json``` and import into Postman as a collection
- Make your changes and export from Postman, then reimport - does data flow as expected?
- Enlist a helper to test your code - once you have a functional collection, have someone test your README.md and the tool itself by following your README.md
- The goal of this test is to evaluate both the code and the instructions.  Once the tool is merged with master, CS people should be empowered to run the tool without needing direct assistance

We want you to succeed and to succeed easily! Please reach out with any questions or comments

# Contributing

This repository requires 1 Code Review before new code can be added to Master. If you'd like to commit to this repo:

- Create a branch off master.
- Make your changes until your new report or feature works.
- Test (if possible) that all other pre-existing features work. If this seems hard or mysterious, let us know and we can do it.
- Check that your Python reasonably meets pep8 standards: $ pep8 #your_file#
- If your code editor has an Inspect Code feature, inspect it and make any reasonable changes.
- Combine the code with the current master branch. While on your branch, type in: $ git merge master
- Submit a Pull Request

For smaller pull requests, it will likely take a few days to thoroughly go over it and test it. For larger pull requests, it could take up to a week to fully review the code, test it, and make comments. 

When code is approved for merging, we'll plus one it, and it'll be up to you to merge the code and delete the branch
