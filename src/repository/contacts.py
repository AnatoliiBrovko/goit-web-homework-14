from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(skip: int, limit: int, first_name: str, last_name: str, email: str, user: User, db: Session):
    """
    The get_contacts function is used to retrieve contacts from the database.
    It takes in a skip, limit, first_name, last_name and email as parameters.
    The skip parameter is used to determine how many records should be skipped before returning results.
    The limit parameter determines how many records should be returned after skipping the specified number of records (skip). 
    If no value for either of these parameters are provided then all contacts will be returned by default. 
    The first_name and last_name parameters are optional string values that can be passed in order to filter out any contact whose name does not match the specified value(s).
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the amount of contacts returned
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: str: Filter contacts by email
    :param user: User: Get the user_id from the logged in user
    :param db: Session: Access the database
    :return: A list of contacts that match the search criteria
    :doc-author: Trelent
    """
    first_name_query = db.query(Contact).filter(and_(Contact.first_name == first_name, Contact.user_id == user.id))
    last_name_query = db.query(Contact).filter(and_(Contact.last_name == last_name, Contact.user_id == user.id))
    email_query = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id))
    if first_name and last_name and email:
        return first_name_query.union(last_name_query).union(email_query).all()
    if first_name and last_name:
        return first_name_query.union(last_name_query).all()
    if first_name and email:
        return first_name_query.union(email_query).all()
    if last_name and email:
        return last_name_query.union(email_query).all()
    if first_name:
        return first_name_query.all()
    if last_name:
        return last_name_query.all()
    if email:
        return email_query.all()
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_birthdays(skip: int, limit: int, user: User, db: Session):
    """
    The get_birthdays function takes in a skip, limit, user and db as parameters.
    It then creates an empty list called contacts_with_birthdays. It also gets the current date and year from the datetime module.
    Then it queries all of the contacts that belong to a specific user with an offset and limit (for pagination). 
    For each contact in those queried contacts, it checks if their birthday is within 7 days of today's date by subtracting today's date from their birthday for this year (current_year) using timedelta(). If so, they are added to the list created earlier called contacts_with_
    
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user id from the database
    :param db: Session: Access the database
    :return: A list of contacts with birthdays in the next 7 days
    :doc-author: Trelent
    """
    contacts_with_birthdays = []
    today = date.today()
    current_year = today.year
    contacts = db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    for contact in contacts:
        td = contact.date_of_birth.replace(year=current_year) - today
        if 0 <= td.days <= 7:
            contacts_with_birthdays.append(contact)
        else:
            continue
    return contacts_with_birthdays


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    The get_contact_by_id function takes in a contact_id and user, and returns the first contact that matches
    the given id. If no such contact exists, it returns None.
    
    :param contact_id: int: Find the contact in the database
    :param user: User: Check if the user is authorized to access the contact
    :param db: Session: Pass the database session to the function
    :return: A contact if it exists, otherwise none
    :doc-author: Trelent
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Pass the contact information to the function
    :param user: User: Get the user id from the token
    :param db: Session: Access the database
    :return: The contact object that is created
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactModel): The updated information for the Contact object.  This is a Pydantic model, so it will be validated before being passed into this function.  See models/contact_model for more details on what fields are required and how they are validated by Pydantic's validation engine.
    
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactModel: Pass the contact model to the function
    :param user: User: Ensure that the user is logged in and has access to the contact
    :param db: Session: Access the database
    :return: The contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.date_of_birth = body.date_of_birth
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact.
    
    :param contact_id: int: Specify the contact to be deleted
    :param user: User: Get the user id of the current user
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """    
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact