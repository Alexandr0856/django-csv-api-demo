# django-csv-api-demo
A demonstration project showcasing a Django-based API for uploading and querying CSV files. 

## Requirements

Before running the project, make sure you have the following components installed:

- Python 3.12 or later
- PostgreSQL 14 or later

## Setting up the PostgreSQL Database

Ensure that your PostgreSQL database is running and configured. Create a database and user for the project.


## Setting Environment Variables

The project uses environment variables for configuration. Create a `.env` file in the root directory of the project and add the following variables:

```env
SECRET_KEY=your_secret_key
POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Installing Dependencies

Ensure you have created and activated a Python virtual environment. Then, install the required dependencies:

```sh
pip install -r requirements.txt
```

## Applying Migrations

Run the database migrations to create the necessary tables:

```sh
python manage.py makemigrations
python manage.py migrate
```

## Running the Project

Start the project with the following command:

```sh
python manage.py runserver
```

Your project should now be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Using the API

### Uploading a CSV File

Make a POST request to `http://127.0.0.1:8000/api/upload-csv/` with a JSON body containing the URL to the CSV file and the table name. Optionally, you can specify the `overwrite` parameter.

```json
{
    "url": "URL_TO_CSV_FILE",
    "table_name": "desired_table_name",
    "overwrite": true
}
```

### Retrieving Data with Filtering

Make a GET request to `http://127.0.0.1:8000/api/data/?table=desired_table_name&column1=value1` to retrieve data from the table filtered by `column1`.

### Examples

Examples of how to use the API endpoints can be found in the demo.http file.
