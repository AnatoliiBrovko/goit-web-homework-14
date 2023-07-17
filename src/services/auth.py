from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.config.config import settings


class Auth:

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the CryptContext instance to verify that
        the plain-text password matches the hashed version. If it does, it returns True;
        otherwise, False.
        
        :param self: Make the method a bound method, which means that the first parameter passed to it will be an instance of its class
        :param plain_password: Check if the password entered by the user matches with the hashed_password
        :param hashed_password: Store the hashed password
        :return: True if the password is correct and false otherwise
        :doc-author: Trelent
        """

        return self.pwd_context.verify(plain_password, hashed_password)


    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password and returns the hashed version of it.
        The hashing algorithm is defined in the settings file, which is imported at the top of this file.
        
        :param self: Represent the instance of the class
        :param password: str: Pass the password to be hashed into the function
        :return: A hash of the password
        :doc-author: Trelent
        """

        return self.pwd_context.hash(password)


    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.
            The function takes in two parameters: data and expires_delta.
            Data is a dictionary that contains information about the user, such as their username and email address.
            Expires_delta is an optional parameter that specifies how long the access token will be valid for.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A jwt access token
        :doc-author: Trelent
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token


    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            The function takes in two arguments: data and expires_delta.
            Data is a dictionary containing the user's id, username, email address, and password hash.
            Expires_delta is an optional argument that sets how long before the refresh token expires.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's id, username and email
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A refresh token that is encoded with the data, current time, and expiration date
        :doc-author: Trelent
        """

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token


    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
            The function will check if the scope of the payload is 'refresh_token'. If it's not, an HTTPException will be raised.
            If it's valid, then we return email from payload['sub'].
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user who sent the refresh token
        :doc-author: Trelent
        """

        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            if it's valid, or raises an exception otherwise.
        
        :param self: Access the class attributes
        :param token: str: Get the token from the request header
        :param db: Session: Get a database session from the dependency
        :return: The user object of the current logged in user
        :doc-author: Trelent
        """

        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user


    def create_email_token(self, data: dict):
        """
        The create_email_token function is used to create a token that will be sent in an email.
        The token contains the user's id and email address, as well as the time it was created (iat)
        and when it expires (exp). The function takes a dictionary of data containing these values, 
        then creates a copy of this dictionary called to_encode. It then adds iat and exp values to 
        to_encode using datetime objects from Python's datetime module. Finally, it uses PyJWT's jwt 
        module to encode the data into JSON Web Token format with our SECRET_KEY and AL
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the data to be encoded
        :return: A token that can be used to verify a user's email
        :doc-author: Trelent
        """

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    
    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        If the token is invalid, it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Decode the token
        :return: The email address from the token
        :doc-author: Trelent
        """

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload['sub']
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid token for email verification')


auth_service = Auth()