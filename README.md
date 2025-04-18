# numbersms_updated

## Running the Project with Docker

To run this project using Docker, follow these steps:

### Prerequisites

- Ensure Docker and Docker Compose are installed on your system.
- Verify that the required Python version is 3.9 as specified in the Dockerfile.

### Environment Variables

- Create a `.env` file in the project root directory if not already present.
- Define the necessary environment variables as per the `docker-compose.yml` file:
  ```env
  MYSQL_ROOT_PASSWORD=example
  MYSQL_DATABASE=app_db
  ```

### Build and Run Instructions

1. Build the Docker images and start the services:
   ```bash
   docker-compose up --build
   ```
2. Access the application at `http://localhost:5000`.

### Exposed Ports

- Application: `5000` (mapped to `5000` on the host)
- Database: Not exposed externally

### Notes

- The application uses a MySQL database. Ensure the `db_data` volume is properly configured for persistent storage.
- Modify the `docker-compose.yml` file if additional customization is required.

For further details, refer to the project documentation or contact the development team.