## Installation and configuration

### Step 1: Clone the repository
```bash
git clone https://github.com/Rubsun/flask-movie_actors
cd flask-movie_actors
```
### Step 2: Create a virtual environment and install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Create PostgreSQL container
```bash
docker run -d --name your_name -p your_port:5432 -e POSTGRES_PASSWORD=your_password -e POSTGRES_USER=your_user -e POSTGRES_DB=your_db postgres
```

### Step 4: Migrate
```bash
flask db migrate
```
### Step 5: Run
```bash
python3 app.py
```
