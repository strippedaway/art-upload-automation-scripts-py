
# Form Upload Automator in Python

This is a collection of scripts to use selenium in python to automate form filling with data upload. 

This uses vanilla firefox/geckodriver as the main agent of browsing using a default ff profile to browse. 


In order to use the scripts, you will need to create a 

`secrets.json` and `ff-profile.json` files.

`secrets.json` is populated as such:

```json
[
    {
        "platform": "Platform1",
        "email": "email-address",
        "password": "password"
    },
    {
        "platform": "Platform2",
        "email": "email-address",
        "password": "password2"
    }
]
```
```json

`ff-profile.json` is filled out by adding a ff profile 
```{
    "ffprofile": "/home/user/.firefox/<profile-folder-directory>"
}
```

It requires the creation of an artwork-image folder and placing each set of artwork photos in a directory, you then have to reference such directory in the catalog files with specific references to each image within it. Blank-catalog files are given in the repo, they are based on the upload process so that you can fill in the fields accordingly. You must create an array out of the one copy for each site, the general structure of the json array is as:

```json
[
    {
        //entry1,
    },
    {
        //entry2
    }
]
```

and within each set of `{}` you have a blank version of all the fields for the platform. the blank single filled json files will be provided. you just have to create a version without the `-blank-` in its name in the root folder of the repo. 

