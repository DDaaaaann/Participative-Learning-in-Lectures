# Use the virtualenv

~~~
cd Django/
source bin/activate
~~~

After this, you can start the Django development server with:

~~~
python manage.py runserver
~~~

or with a specific port:

~~~
python manage.py runserver 0.0.0.0:8140
~~~

# Install or update virtualenv requirements

~~~
pip install -r requirements.txt
~~~

Note: make sure you are in Django/ dir and using the virtualenv.

# Generate virtualenv requirements list

~~~
pip freeze > requirements.txt
~~~

Note: make sure you are in Django/ dir and using the virtualenv.
