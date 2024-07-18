# Pure Test
Author: Anthony Zakhaur

This project uses Django as the web framework, PostgreSQL as the database, and Celery for asynchronous task management. The development and execution environment is contained within Docker to simplify configuration and deployment. Commands are managed through a Makefile to streamline their usage.

## Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Make](https://www.gnu.org/software/make/)

## Steps to Run the Project

### 1. Configure Environment Variables

Copy the `.env.example` file and modify the variables as needed for your local environment:

```sh
cp .env.example .env
```

Edit the .env file with your local configurations.

### 2. Start the Development Environment

Run the following command to build and start the Docker containers:

```sh
make run
```

### 3. Create a superuser

To create a Django superuser, run the following command:

```sh
make create_superuser
```

Follow steps with the wishes credentials.

### 4. Access to App.

Once the containers are up and the superuser is created, you can access the app interface at the following URL:

```sh
http://localhost:8000/admin
```

Log in with credentials setted before.

## Load Generic Data

If you want to load generic data, you can run the following command, where 1000 is the number of chats to load:
```sh
make load_data n=1000
```

## Run Tests

To run the project's tests, use the following command:
```sh
make test
```

## Shut Down the Server
To stop all containers and shut down the development environment, run:
```sh
make shutdown
```

### Author
Author: Anthony Zakhaur
