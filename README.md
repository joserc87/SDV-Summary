# SDV-Summary
A Flask webapp using Python Image Library to reconstruct and display a summary of the player and farm from a Stardew Valley save file.

## Configuration
The `SDV_APP_SETTINGS` environment variable is used in order to specify
which python file to load for configuration. In that file the following settings
can used:

### Mandatory Settings
`UPLOAD_FOLDER`

`SECRET_KEY`

### Database

`USE_SQLITE`

#### SQLite
`DB_SQLITE`
#### PostgreSQL

`DB_NAME`

`DB_USER`

`DB_PASSWORD`

## Creating the database

Once the config file has been setup, run createdb.py and follow the prompts.
