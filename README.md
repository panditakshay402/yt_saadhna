#YT SAADHNA

# Requirement:

pip install django djangorestframework google-cloud-speech google-api-python-client requests sumy yt-dlp




# create a virtual environment
```bash
virtualenv -p python3 venv

```

# activate the virtual environment
```bash
source venv/bin/activate
.\venv\Scripts\activate

```

# install dependencies
```bash
pip install -r requirements.txt
```

# create .env
copy .env.example to create .env

# set pre-commit hook
```bash
pre-commit install
```

# run db migrations
```bash
python manage.py migrate
```
# run the app
```bash
python manage.py runserver
```

# create migrations
```bash
python manage.py makemigrations
```

# update requirements when installing new libraries
```bash
pip freeze > requirements.txt
```

