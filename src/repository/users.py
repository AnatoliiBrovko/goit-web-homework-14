from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session):
    """
    The get_user_by_email function takes in an email and a database session.
    It then queries the User table for a user with that email address.
    If it finds one, it returns the first result of that query.
    
    :param email: str: Pass the email address of the user to be retrieved from the database
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function takes a UserModel object and a database session as arguments.
    It then creates an avatar for the user using Gravatar, which is an online service that allows users to create avatars based on their email address.
    If there is no avatar available for the given email address, it will return None instead of raising an exception.
    The function then creates a new user with all of the information from body (the UserModel object) and adds it to our database session.
    
    :param body: UserModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A new user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session):
    """
    The update_token function updates the user's refresh token in the database.
    
    :param user: User: Get the user's id
    :param token: str | None: Set the refresh token for a user
    :param db: Session: Commit the changes to the database
    :return: The updated user
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes an email and a database session as arguments.
    It then queries the database for the user with that email address, sets their confirmed field to True,
    and commits those changes to the database.
    
    :param email: str: Get the email of the user that is being confirmed
    :param db: Session: Pass the database session to the function
    :return: Nothing
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function takes an email and a url as arguments.
    It then uses the get_user_by_email function to retrieve the user from the database.
    The avatar attribute of that user is set to be equal to the url argument, and then 
    the db session is committed so that it can be saved in our database.
    
    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed into the function
    :param db: Session: Pass the database session to the function
    :return: The updated user
    :doc-author: Trelent
    """    
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user