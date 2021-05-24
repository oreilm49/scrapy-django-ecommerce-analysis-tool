# Scrapy Django Ecommerce Scraper
A scrapy webscraper that leverages Django's ORM for saving scraped data to the database and for managing web scraper functionality via the admin panel.

### Built With
- Python: Django & Scrapy
- Docker Compose
- Azure Container Instances
- PostgreSQL

## Get Started
This project uses docker as a development environment for ease of use.
1. As a first step, clone the repo
    ```
    $ git clone git@github.com:oreilm49/scrapy-django-ecommerce-analysis-tool.git
    ```
2. Assuming you have docker installed you can then build the project
    ```
    $ docker-compose build
    ```
3. Once the image is finished building, set up the database
    ```
    $ docker-compose run cms ./setupdatabase.sh
    ```
4. You can now run the development server
    ```
    docker-compose up -d
    ```
5. Open your favourite web browser at http://localhost:5000 to see the app running. A persistent volume is created for media and database data to preserve app data after you shut down the container :
    ```
    $ docker-compose down
    ```
6. To wipe the dev env and start from scratch, take down the container while passing `-v` to remove the volumes:
    ```
    $ docker-compose down -v
    ```

## Deploying to Azure Container Instances
As this was an expiremental project I deployed to ACI due to the cost savings vs AKS. If I was to deploy and run this as a commercial project I'd choose the latter.
### Prerequisites
- Azure account
- A remote container repository that azure can connect to - I used azure container registry.

### Deploying
If you're just deploying a new version of the app run `sh/deploy.sh`. This will run tests, build and push a new image and restart the container group on ACI.

If you're deploying for the first time, or you need to make changes to the ACI infrastructure like adding a new virtual machine, you need to run `sh/deploy_infrastructure.sh`. ACI can't modify the structure of an existing container group to add more resources, the whole thing needs to be deleted and a new one created. 

This also means that the public IP for the container groups changes. For this reason, if you want to point a domain to your container group, you're best off using the subdomain that ACI provides.