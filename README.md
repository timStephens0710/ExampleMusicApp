# Installation guide
#### Mac

1. **Install Homebrew** (if not already installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Install Git**:
    - link: https://git-scm.com/downloads/mac

3. **Install Miniconda**:
    ```bash
    brew install --cask miniconda
    ```


### Docker

1. **Download Docker Desktop for mac:**:
    - link: https://www.docker.com/

2. **Test installation**:
    ```bash
    docker --version
    docker-compose --version
    ```


### Create conda env
1. Create the virutal env via the environment.yml file
    ```bash
    conda env create environment.yml -n music_app
    ```
    ```bash
    conda init
    ```

2. Close the terminal and open a new, then run the following command:
    ```bash
    source ~/.bash_profile
    ```

3. Run conda acivate conda_env_name


### Installing psycopg2
1. Run the following command:
    ```bash
    brew install postgresql
    ```

2. Export the path
    ```bash
    brew install postgresql
    ```

3. Run pip install:
    ```bash
    pip install psycopg2==2.9.10
    ```
    

### Running the Application for Debug

1. **Create Database Migrations**:
    ```bash
    python manage.py makemigrations
    ```

2. **Run Database Migrations**:
    ```bash
    python manage.py migrate
    ```

3. **Create Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

4. **Run the Server**:
    ```bash
    python manage.py runserver
    ```

### API References

- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **Main Website**: [http://localhost:8000/](http://localhost:8000/)

### Docker

1. **Install Docker Compose**:
    ```bash
    sudo apt-get install -y docker-compose
    ```

2. **Run Docker Compose**:
    ```bash
    docker-compose up
    ```
