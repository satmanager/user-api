# user-api

Basic user API based in Python 3.13

# Install the environment

pip install -r requirements.txt

# Run the app using 

uvicorn main:app --reload

# Please find the docs on the Browser Swagger (localhost:8000)

# Run the tests using

pytest test_main.py

# EVALUATION NOTE

# Only to test functionality, the create users endpoint (POST /api/v1/users) was left open.
# You can create an admin user to test all the other endpoints