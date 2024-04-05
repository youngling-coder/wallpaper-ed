# Set installation variables
APP_NAME=wallpaper-ed

BUILD_DIR=dist/
EXEC_DIR=/bin/
CONFIG_DIR=~/.config/$APP_NAME
ICON_DIR=/usr/share/icons/$APP_NAME
AUTOSTART_DIR=~/.config/autostart
APP_SHORTCUT_DIR=~/.local/share/applications/

# Installing python3 requirements
pip3 install -r requirements.txt

# Building application
pyinstaller --onefile --noconsole app/main.py --name $APP_NAME

# Make the application executable
chmod +x dist/$APP_NAME

# Create autostart directory if not exists
mkdir -p $AUTOSTART_DIR $CONFIG_DIR
sudo mkdir -p $ICON_DIR

# Install necessary files
sudo cp dist/$APP_NAME $EXEC_DIR
cp config.json $CONFIG_DIR
sudo cp app/icons/icon_128.png $ICON_DIR/icon.png
cp app/entries/$APP_NAME-autostart.desktop $AUTOSTART_DIR
cp app/entries/$APP_NAME-gui.desktop $APP_SHORTCUT_DIR

# Remove building files after install
rm -rf $BUILD_DIR
rm -rf build/
rm *.spec

# Setup API
printf "\nSpecify Unsplash API Access Token: "
read API_TOKEN

jq --arg token "$API_TOKEN" '.app.unsplash_access_token = $token' "$CONFIG_DIR/config.json" > "$CONFIG_DIR/tmp.json" && mv "$CONFIG_DIR/tmp.json" "$CONFIG_DIR/config.json"

printf "\nConfiguration file directory: %s " "$CONFIG_DIR"
printf "\nInstallation done!"
