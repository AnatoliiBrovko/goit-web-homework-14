from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse
from src.services.auth import auth_service
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=list[ContactResponse], description='Over 10 requests/min', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact_by_params(skip: int = 0, limit: int = Query(default=10),
                                first_name: Optional[str] = Query(default=None),
                                last_name: Optional[str] = Query(default=None),
                                email: Optional[str] = Query(default=None),
                                db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_params function returns a list of contacts that match the parameters passed in.
        If no contact is found, it will return an HTTP 404 error.
    
    
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param first_name: Optional[str]: Filter contacts by first name
    :param last_name: Optional[str]: Filter the contacts by last name
    :param email: Optional[str]: Filter the contacts by email
    :param db: Session: Get the database session
    :param current_user: User: Get the user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """

    contact = await repository_contacts.get_contacts(skip, limit, first_name, last_name, email, current_user, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contact


@router.get("/birthdays", response_model=list[ContactResponse], description='Over 10 requests/min', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_birthdays(skip: int = 0, limit: int = Query(default=10), 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_birthdays function returns a list of contacts with birthdays in the next 30 days.
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts that have birthdays in the next 7 days
    :doc-author: Trelent
    """

    contacts = await repository_contacts.get_contacts_birthdays(skip, limit, current_user, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='Over 10 requests/min', dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns a contact by its id.
        If the contact does not exist, it raises an HTTP 404 error.
    
    
    :param contact_id: int: Get the contact_id from the url
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """

    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")
    return contact


@router.post("/", response_model=ContactResponse, description='Over 3 requests/ 5 min', dependencies=[Depends(RateLimiter(times=3, minutes=5))], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        It takes a ContactModel object as input, and returns the newly created contact.
    
    :param body: ContactModel: Pass the data to create a new contact
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user's id from the token
    :return: A dict with the new contact's data
    :doc-author: Trelent
    """

    new_contact = await repository_contacts.create_contact(body, current_user, db)
    return new_contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        It takes an id, and a body containing the updated information for that contact.
        The function returns the updated contact.
    
    :param body: ContactModel: Specify the data that is required to update a contact
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contactmodel object
    :doc-author: Trelent
    """
    
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(contact_id: int, 
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_tag function takes a contact_id and removes the tag from the database.
        It returns an HTTP status code of 404 if no contact is found with that id.
    
    :param contact_id: int: Specify the contact to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact
    :doc-author: Trelent
    """

    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact