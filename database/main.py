import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker  # <- aici
from dotenv import load_dotenv

from .models import User
from utils.hashpasswd import hash_password

load_dotenv('./.env')

DATABASE_HOST=os.getenv("DATABASE_HOST")
DATABASE_PORT=os.getenv("DATABASE_PORT")
DATABASE_USERNAME=os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
DATABASE_NAME=os.getenv("DATABASE_DBNAME")

DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database(object):

    def __init__(self) -> None:

        self.connection_response = self.get_connection()

    @staticmethod
    def get_connection() -> dict:
        """
        Method that connects to the database
        :return: dictionary with connection information or error information
        """
        try:
            db_session = SessionLocal()
            db_session.execute(text('SELECT 1'))  # simple query to test connection

            return {
                "status": 200,
                "connection": db_session
            }

        except Exception as error:

            return {
                'status': 400,
                'data': {
                    'message': str(error)
                }
            }

    def register_new_user(self, data : dict) -> dict:
        if self.connection_response['status'] == 200:

            session: Session = self.connection_response['connection']

            try:

                if session.query(User).filter(User.username == data['username']).first():

                    return {
                        'status': 409,
                        'data': {
                            'message': f"User \"{data['username']}\" already exists"
                        }
                    }
                elif session.query(User).filter(User.email == data['email']).first():
                    return {
                        'status': 409,
                        'data' : {
                            'message': f"Email \"{data['email']}\" already in use"
                        }
                    }
                else:

                    hashed_password = hash_password(data['password'])

                    new_user = User(
                        username=data['username'],
                        email=data['email'],
                        password=hashed_password
                    )

                    session.add(new_user)
                    session.commit()
                    session.refresh(new_user)

                    return {
                        'status': 201,
                        'data' : {
                            'message': "User registered successfully",
                            'user': new_user.to_dict()
                        }
                    }

            except Exception as error:

                return {
                    'status': 500,
                    'data' : {
                        'message': str(error)
                    }
                }

            finally:
                session.close()

        else:
            return self.connection_response


    def get_all_users_data(self) -> dict:
        """
        Method that gets all users data
        :return: dictionary with all users data or error information
        """
        try:

            if self.connection_response['status'] == 200:

                session: Session = self.connection_response["connection"]

                users = session.query(User).all()
                users = [user.to_dict() for user in users]

                return {
                    'status': 200,
                    'data': {
                        'users': users
                    }
                }

            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                    'data': {
                        'message': str(error)
                    }
            }