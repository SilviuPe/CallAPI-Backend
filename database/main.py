import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from database.models import User, ClientSession
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


    def get_all_users_data(self, id: int = 0) -> dict:
        """
        Method that gets all users data
        :return: dictionary with all users data or error information
        """
        try:

            if self.connection_response['status'] == 200:

                session: Session = self.connection_response["connection"]

                if id > 0:
                    user = session.query(User).filter(User.id == id).first()
                    print(user.email)
                    return {
                        'status': 200,
                        'data': {
                            'user': {
                                'name':user.username
                            }
                        }
                    }

                else:
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

    def create_session(self, user_id, session_hash, expires_at):


        try:

            if self.connection_response['status'] == 200:

                session: Session = self.connection_response["connection"]
                if not session.query(User).filter(User.id == user_id).first():
                    return {
                        'status': 400,
                        'data': {'message': f"User with ID \"{user_id}\" does not exist"}
                    }
                else:

                    new_session = ClientSession(
                        user_id=user_id,
                        session_hash=session_hash,
                        expires_at=expires_at
                    )

                    session.add(new_session)
                    session.commit()
                    session.refresh(new_session)

                    return {
                        'status': 201,
                        'data': {
                            'message': "Session token created successfully",
                            'session': new_session.to_dict()
                        }
                    }
        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error)}
            }

    def validate_session(self, session_hash: str) -> dict:
        """
        Method to validate the session
        :return: dictionary with validation data or error information
        """
        try:

            if self.connection_response['status'] == 200:

                session: Session = self.connection_response["connection"]

                client_session = session.query(ClientSession).filter(ClientSession.session_hash == session_hash).first()

                if client_session:
                    return {
                        'status': 302,
                        'data': {
                            'message': "Session token valid!",
                            'user_id' : client_session.user_id,
                        }
                    }
                else:
                    return {
                        'status': 401,
                        'data': {'message': "Session token expired!"}
                    }

            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error) }
            }

    def delete_session(self, session_hash: str):
        try:
            if self.connection_response['status'] == 200:
                session: Session = self.connection_response["connection"]

                client_session = (
                    session.query(ClientSession)
                    .filter(ClientSession.session_hash == session_hash)
                    .first()
                )

                if client_session:
                    session.delete(client_session)
                    session.commit()
                    return {
                        'status': 200,
                        'data': {'message': "Session deleted!"}
                    }
                else:
                    return {
                        'status': 404,
                        'data': {'message': "Session not found!"}
                    }

            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error)}
            }