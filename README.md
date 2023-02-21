### Databases setup
#### docker run --name postges_fastapi -e POSTGRES_PASSWORD=postgresd -p 5432:5432 -d postgres
#### docker run --name mongo_fastapi -d -p 27017:27017 mongo
##
### Project setup
#### In the root directory create a file called env_settings.py. Create class called Settings and inherit from Pydantic's BaseSettings. Create the following variables - google_oauth_client_id, google_oauth_client_secret, sib_api_key. Tge first two will be used for Google social authentication, the third is the SendInBlue key, that's for sending various emails around registration and account management.
#### Initialize alembic - alembic init alembic
#### In alembic.ini change with your db url - sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/fastapi
#### In env.py change - target_metadata = [Base.metadata]
#### To generate migration - alembic revision --autogenerate -m "First commit" --rev-id=<your_identifier>
#### To run migration - alembic upgrade head
#### To remove all migrations - alembic downgrade base
#### Run tests - pytest
#### Run app - uvicorn app.main:app --reload
#### Visit http://127.0.0.1:8000/docs
##
### Shell setup
#### from sqlalchemy import create_engine
#### engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/fastapi")
#### from sqlalchemy.orm import sessionmaker
#### Session = sessionmaker(bind=engine, future=True)
#### session = Session()
#### import sys
#### sys.path.append("path_to_project_root_directory")
#### from app.models.foo import *
#### from sqlalchemy import select
#### users = session.execute(select(User))
