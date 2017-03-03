**Item Catalog**

- The project involves building an application that provides a list of items within a variety of categories. It also includes user registration and authentication. Registered users will have the ability to post, edit and delete their own items.
- This web application is built using the Python framework Flask along with Google OAuth authentication
- The project implements JSON endpoints that serve the same information as displayed in the HTML endpoints for the catalog, a category and an arbitrary item in the catalog.

**Quick Start**

- Install Vagrant and VirtualBox
- Start Vagrant: Open cmd/Git bash and go to the Vagrant folder. Use the command 'vagrant up' to launch your vitual machine. Type the command 'vagrant ssh' to log into it
- Database: Go to /vagrant/catalog folder
    - Create the database: python database_setup.py
    - Populate the categories: python database_init.py
- Run application: Run the application (python application.py). The item catalog can be accessed at localhost:8000/
- JSON end points:
    - Catalog: /catalog/json/
    - Category: /category/<category id>/json
    - Item: /item/<item id>/json