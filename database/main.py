import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from database.models import User, ClientSession, Collection, Endpoint
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
        # The connection with the database it's initialized the moment when the
        # Database() object is created.
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
        """
        Method that registers a new user
        :param data: Dictionary with user information
        :return: Dictionary with new user information or error information
        """
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


    def get_all_users_data(self, user_id: int = 0) -> dict:
        """
        Method that gets all users data
        :param user_id ID of the user to look for. If it's 0 all users are returned
        :return: dictionary with all users data or error information
        """
        try:

            if self.connection_response['status'] == 200:

                session: Session = self.connection_response["connection"]

                if user_id > 0:
                    user = session.query(User).filter(User.id == user_id).first()
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

    def create_session(self, user_id, session_hash, expires_at) -> dict:
        """
        Method that creates a new session
        :param user_id: ID of the user
        :param session_hash: hash of the session to be saved in the DB
        :param expires_at: Date/Time when the session expires
        :return: Dictionary with new session information or error information
        """
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
            else:
                return self.connection_response
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

    def delete_session(self, session_hash: str) -> dict:
        """
        Method to delete the session
        :param session_hash:  hash of the user session
        :return: dictionary with deleted data or error information (It doesn't matter too much since the scope of this is
                    to delete the session. If the session doesn't exist, it will be deleted. If the session is still
                    active in the database this might be a problem.)
        """
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

    def get_collections_from_user(self, user_id: int) -> dict:
        """
        Method to get all collections (this includes as well the endpoints) from a user.
        :usage: On the DASHBOARD of the frontend
        :param user_id: ID of the user
        :return: dictionary with all collections or error information
        """
        try:

            if self.connection_response['status'] == 200:
                session: Session = self.connection_response["connection"]
                collections = session.query(Collection).filter(Collection.user_id == user_id).all()

                if collections:
                    collections = [collection.to_dict() for collection in collections]
                    for collection in collections:
                        collection_id = collection['id']
                        endpoints = self.get_endpoints_from_collection(collection_id)

                        if endpoints['status'] == 200:
                            collections[collections.index(collection)].update(endpoints['data'])

                        del collections[collections.index(collection)]['id']
                        del collections[collections.index(collection)]['user_id']
                    return {
                        'status': 200,
                        'data': {'collections': collections}
                    }
                else:
                    return {
                        'status': 404,
                        'data': {'message': "Collection not found!"}
                    }
            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error)}
            }

    def get_endpoints_from_collection(self, collection_id: int) -> dict:
        """
        Method to get all endpoints from a collection.
        :usage: On the DASHBOARD of the frontend
        :param collection_id: ID of the collection
        :return: dictionary with all endpoints or error information
        """
        try:

            if self.connection_response['status'] == 200:
                session: Session = self.connection_response["connection"]
                endpoints = session.query(Endpoint).filter(Endpoint.collection_id == collection_id).all()

                endpoints = [endpoint.to_dict() for endpoint in endpoints]

                for endpoint in endpoints:
                    del endpoints[endpoints.index(endpoint)]['id']
                    del endpoints[endpoints.index(endpoint)]['collection_id']

                return {
                    'status': 200,
                    'data': {'endpoints': endpoints}
                }
            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error)}
            }

    def remove_collections_from_user(self, user_id: int, collection_title: str) -> dict:

        try:
            if self.connection_response['status'] == 200:
                session: Session = self.connection_response["connection"]
                collection = session.query(Collection).filter(Collection.user_id == user_id, Collection.title == collection_title).first()

                if collection:
                    session.delete(collection)
                    session.commit()
                    return {
                        'status': 200,
                        'data': {'message': "Collection removed!"}
                    }
                else:
                    return {
                        'status': 404,
                        'data': {'message': "Collection not found!"}
                    }
            else:
                return self.connection_response

        except Exception as error:
            print(error)
            return {
                'status': 400,
                'data': {'message': str(error)}
            }