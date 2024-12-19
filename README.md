# online Bookstore

An ecommerce platform for buying and selling books online. Built with Django, deployed using AWS EC2, Gunicorn, and Nginx.

## Features

- User Management: Registration, login, and profile management.

- Book Catalog: Browse books by category, author, or title.

- Search Functionality: Search books by keywords.

- Shopping Cart: Add, update, or remove books from the cart.

- Order Management: Place orders and view order history.

- Payment Gateway: Secure payment integration (Razorpay).

- Admin Panel: Manage books, orders, and users.

## Tech Stack

- Backend: Django

- Frontend: Django Templates, HTML, CSS, JavaScript

- Database: PostgreSQL

- Deployment: AWS EC2, Gunicorn, Nginx

## Prerequisites

- Python 3.8

- PostgreSQL

- AWS EC2 Instance

- Nginx

- Gunicorn

## Installation

### Clone the Repository

- git clone https://github.com/your-repo/estore.git

- cd estore

### Set Up a Virtual Environment

- python3 -m venv venv

- source venv/bin/activate

### Install Dependencies

- pip install -r requirements.txt

### Apply Migrations

- python manage.py makemigrations

- python manage.py migrate

### Create a Superuser

- python manage.py createsuperuser

### Collect Static Files

- python manage.py collectstatic

## Deployment

### Set Up AWS EC2 Instance

- Launch an EC2 instance (Ubuntu).

- Configure security groups to allow HTTP (port 80) and SSH (port 22).

### Install Required Software

- sudo apt update

- sudo apt install python3-pip python3-venv nginx

###  Transfer Project Files

- Git repository to transfer project files to the EC2 instance.

### Set Up Gunicorn

- pip install gunicorn

#### Install Gunicorn:

- pip install gunicorn

#### Run Gunicorn:

- gunicorn --bind 0.0.0.0:8000 projectname.wsgi:application

###  Configure Nginx

#### Create a new Nginx configuration file:

- sudo nano /etc/nginx/sites-available/online-bookstore

### Start Gunicorn as a Service

- sudo nano /etc/systemd/system/online-bookstore.service

### Usage

1. Access the website via the domain or public IP of your EC2 instance.

2. Admin panel: /admin

3. Start exploring the bookstore!







