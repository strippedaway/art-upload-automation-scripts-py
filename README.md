# Form Upload Automator in Python

This is a collection of scripts to use selenium in python to automate form filling with data upload.

This uses vanilla firefox/geckodriver as the main agent of browsing using a default firefox profile to browse and ideally avoid being bot-detected.

## To Do List:

- Debug Current functionality
- write scripts for catalog generation
- Add more fieldtypes
- Create form-scanner to arrange grab selectors for various input field options based on url. 
- Possible AI-agent addition implementation to be able to automate any sort of framework of data. 
- Rewrite profile to work with cookie and session exraction. 

## Usage:

In order to use the scripts, you will need to create `secrets.json` and `ff-profile.json` files inside `/data/` folder. 

`secrets.json` is populated as such:

```json
[

    {
        "platform": "platform-name",
        "address": "https://www.plat-form.com/en/login",
        "email": {
            "value": "email",
            "field": "email-input-selector-value"
        },
        "password": {
            "value": "password",
            "field": "password-input-selector-value"
        },
        "button": "log-in-button-selector"
    },

},

{
        "next": "entry", 
        ...
}
]
```

For now you have to grab those elements manually. However, in the future the plan is to restructure and automate field selector extraction. You generally find the selectors like you would if you were to write a function in selenium. But here all you need to do for now is do the extraction on your own. 



`ff-profile.json` is filled out by adding a firefox profile directory to it. This imports your sessions and so on. This should be revised. but as this function runs locally for now it is fine. In the future 

```json
{

"ffprofile": "/home/user/.mozilla/firefox/<profile-folder-directory>"

}
```

In addition to that. you need to create appropriate appropriate catalogs and fieldset files and place them in the folders `/data/catalogs` and `/data/fieldsets`

it is important that `platform-name` is consistent across the names of `*.json` files. So that you it is referencable by the prompt in the script. 

These two files are planned to become generatable in the future. For the original purposes I have manually gathered these catalogs and fieldsets myself. On the other hand, I do intended to work on a field-gathering and a catalog generating script, so that you could feed the script some pages. Prepare some data and have one script prepare the catalogs and another script to prepare the fieldsets. 




