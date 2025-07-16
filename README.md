# Data Catalog Backend
This project is a backend for the Data Catalog frontend, which is a component of the [Developer Portal](https://github.com/openearthplatforminitiative/developer-portal).


## Database
This backend relies on a postgis database. You can start one with docker compose:
```bash
docker compose up -d db
```

To run migrations, you can use:
```bash
poetry install
poetry shell # or any other way to activate the virtual environment
alembic upgrade head
```

## Environment Variables
The backend uses environment variables to configure the database connection and other settings. You can set these in a `.env` file in the root directory of the project. You can find an example in `.env.example`.

## Running the Backend
To run the backend, you can use the following command:
```bash
uvicorn data_catalog_backend.__main__:app --reload
```

