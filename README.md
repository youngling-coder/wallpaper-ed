<p align="center">
  <img width=192 src="https://github.com/youngling-coder/wallpaper-ed/assets/142408709/1fd235db-ad18-4ae5-bbd1-7747650b57a8" alt="Logo"/>
</p>

# 🖥️ WallpaperED

Tool that automatically sets a new wallpaper image from the Unsplash every new session. Powered by the Unsplash API.

### Disclaimer

This application is powered by the Unsplash API, which provides access to a library of photos. All the photos provided through this application belong to their respective owners and are distributed under the Unsplash License. For more information about the Unsplash License, please visit [Unsplash License](https://unsplash.com/license
). Additionally, users can find more information about the Unsplash API and its documentation at [Unsplash API Documentation](https://unsplash.com/documentation
).

## Installation

### Prerequisites
- python3
- python3-pip

### Installation steps

First things first download the source code

```sh
$ git clone https://github.com/youngling-coder/wallpaper-ed/
```

Or ZIP archive with source code using the GitHub official site.

Do not forget to extract the files from the archive!

As files are downloaded and extracted, all you need to do is to execute ```setup.sh``` script in source code folder. It will install all the required files and dependencies.

To launch the script execute following in terminal:

```sh
$ cd /path/to/source/wallpaper-ed
$ chmod +x setup.sh
$ ./setup.sh
```

**If no errors will occur, installation is done!**

### Unsplash API & Config setup
Now it's time to edit config file. It's responsible for storing relevant wallpaper queries that you would like to see on your desktop and all the data required for a proper API work. Open config file using any text editor or command

```sh
$ nano ~/.config/wallpaper-ed/config.json
```
To get things set up, the first thing you need to do is to paste your Unsplash API token in the config file.

```json
{
    "app": {
        "execute": [
            "gsettings set org.gnome.desktop.background picture-uri \"file://%PATH%\"",
            "gsettings set org.gnome.desktop.background picture-uri-dark \"file://%PATH%\""
        ],
        "wallpaper_filename": "unsplash_wallpaper.jpg",
        "download_directory": "~/.local/share/backgrounds/",
        "unsplash_access_token": "YOUR_TOKEN_HERE"
    },
    // ...
}
```

You may also like to set wallpaper that would match certain parameters. It may be specific topic, query, collection or even a username of an Unsplash user. For instance, if you want to see photos of apples created by someone with the username @itsmyname, you would modify the file as follows

```json
{
    // ...
    "image": {
        "query": "apples",
        "nickname": "itsmyname"
    }
}
```

Full list of available parameters you can see **[here](https://unsplash.com/documentation#get-a-random-photo)**.

### GUI Interface

This app is also has GUI powered by PyQt5. To launch GUI Instance of application run in your terminal

```sh
$ wallpaper-ed --gui
```

### Shortcuts

`Return` Generate new wallpaper

`Ctrl + Alt + Enter` Set current image as wallpaper

### Next steps

After all the installation and setup stuff is done we need to end current session and then log back in or launch GUI version of the application

#### Enjoy your new wallpapers!
