from fastapi import APIRouter, Depends, Body, HTTPException, status, Header
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from .. import schemas, oauth2
from .. import database
from ..models import *
from ..services import auth_service



router = APIRouter(tags=['Authentication'])

@router.post('/api/auth/register', response_model=schemas.UserResponse,
             summary="Register a New User")

async def register(user_credentials: schemas.UserCreate = Body(..., description="User credentials including username, email, and password.")
                   , db: Session = Depends(database.get_db)):
    """
    Register a new user by providing the required credentials.

    **Description:**
    - This endpoint creates a new user account.
    - It requires a `UserCreate` schema that includes the username, email, and password.

    **Parameters:**
    - `user_credentials` (UserCreate): A schema containing user details required for registration.
    - `db` (Session, optional): The database session dependency.

    **Returns:**
    - `UserResponse`: A model containing:
        - `id` (str): The unique identifier of the newly created user.
        - `username` (str): The username of the newly created user.
        - `email` (str): The email of the newly created user.

    **Responses:**
    - **201 Created**: Returns the details of the newly created user.
    - **400 Bad Request**: Returned if the provided credentials are invalid or if there is an issue creating the user.

    **Example Request:**

    ```json
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password": "securepassword"
    }
    ```

    **Example Response:**

    ```json
    {
      "id": "12345",
      "username": "john_doe",
      "email": "john@example.com"
    }
    ```
    - `id`: The unique identifier of the newly created user.
    - `username`: The username of the newly created user.
    - `email`: The email of the newly created user.
    """
    return auth_service.create_user(user_credentials, db)

@router.post("/api/auth/login", response_model=schemas.Token,
             summary="User Login")
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(database.get_db)):
    """
    Authenticate a user and return an access token.

    **Description:**
    - This endpoint authenticates a user by verifying their username and password.
    - On successful authentication, it returns an access token.

    **Parameters:**
    - `user_credentials` (OAuth2PasswordRequestForm): A form containing the username and password for authentication.
    - `db` (Session, optional): The database session dependency.

    **Returns:**
    - `Token`: A model containing:
        - `access_token` (str): The JWT access token.
        - `token_type` (str): The type of the token, which is typically "bearer".

    **Responses:**
    - **200 OK**: Returns an access token upon successful authentication.
    - **401 Unauthorized**: Returned if the username or password is incorrect.

    **Example Request:**

    ```json
    {
      "username": "john_doe",
      "password": "securepassword"
    }
    ```

    **Example Response:**

    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
      "token_type": "bearer"
    }
    ```
    - `access_token`: The JWT access token issued upon successful login.
    - `token_type`: The type of the token, typically "bearer".
    """
    return auth_service.login_user(user_credentials, db)



@router.post("/api/auth/verify")
async def verify_token(token_info: schemas.TokenData,
                       db: Session = Depends(database.get_db)):
    """
    Verify the authenticity and validity of a JWT access token.

    **Description:**
    - This endpoint takes a JWT access token and validates it.
    - It ensures the token is not expired, malformed, or revoked.
    - It checks if the associated user still exists in the database.

    **Parameters:**
    - `token_info` (TokenData): The token data containing the JWT to be verified.
    - `db` (Session, optional): The database session dependency.

    **Returns:**
    - `Dict[str, str]`: A dictionary containing the user's ID and username if the token is valid.
        - `user_id` (str): The ID of the authenticated user.
        - `username` (str): The username of the authenticated user.

    **Responses:**
    - **200 OK**: Returns the user's ID and username if the token is valid.
    - **401 Unauthorized**: Returned if the token is invalid, expired, or the user is not found.

    **Example Response:**

    ```json
    {
      "user_id": "12345",
      "username": "john_doe"
    }
    ```
    - `user_id`: The ID of the authenticated user.
    - `username`: The username of the authenticated user.
    """
    return auth_service.verify_user_token(token_info.token, db)




@router.post("/api/auth/logout")
async def logout(authorization:str = Header(...),
                 db: Session = Depends(database.get_db)):
    """
    Logout the user by invalidating their JWT token.

    **Description:**
    - This endpoint logs out a user by deleting their JWT token from the database.
    - It checks if the token provided in the Authorization header is valid and revokes it.
    - The token is removed from the database to prevent further use.

    **Parameters:**
    - `authorization` (str): The Authorization header containing the JWT token in the format "Bearer <token>".
    - `db` (Session, optional): The database session dependency.

    **Returns:**
    - `Dict[str, str]`: A dictionary with a success message upon successful logout.
        - `detail` (str): A success message indicating the user has been logged out.

    **Responses:**
    - **200 OK**: Returned when the user is successfully logged out and their token is invalidated.
    - **401 Unauthorized**: Returned if the token is missing, malformed, or invalid.

    **Example Response:**

    ```json
    {
      "detail": "Successfully logged out"
    }
    ```
    - `detail`: The success message confirming the user has been logged out.
    """
    
    return auth_service.perform_logout(authorization, db)


