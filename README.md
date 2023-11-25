# E-Commerce Application

## Introduction
This e-commerce application is a Django-based web application designed to provide a seamless online shopping experience. It features product browsing, user authentication, order management, and more.

## Features
- User registration and authentication
- Product listing with detailed views
- Shopping cart and order placement functionality
- Merchant interfaces for managing products
- Automated email reminders for payment due dates
- Statistical analysis of product sales for merchants

## Technologies
- Django and Django REST Framework for the backend
- Celery for asynchronous task processing
- SQLite as the development database
- RabbitMQ as the message broker for Celery
- Other Django and Python libraries as required

## Installation
Follow these steps to set up the project:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/your-repository-name.git
   cd your-repository-name
    ```

2. **Set Up a Virtual Environment (Optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Run Migrations:**
    ```bash
    cd app/
    python manage.py migrate
    ```

5. **Create a Superuser (Optional):**
    ```bash
    python manage.py createsuperuser
    ```
6. **Run the Application:**
    ```bash
    python manage.py runserver
    ```

6. **Run Celery Worker (For tasks like email reminders):**
    -Ensure RabbitMQ is installed and running
    -In a new terminal, activate the virtual environment and run:
    ```bash
    celery -A app worker -l info
    ```

## Usage
After starting the server, the application will be accessible at http://localhost:8000. Use the Django admin panel for administrative tasks.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.
