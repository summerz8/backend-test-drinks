## Run instructions
To run this, open a terminal and make sure you are in the same folder as drinks.py.
And run with below command:

`export FLASK_APP=drinks`

`python3 -m flask run`

If your machine does not have Flask installed. Please install Flask with:

`pip install Flask`

If `pip` is not installed, please follow instructions to install `pip` here: https://pip.pypa.io/en/stable/installation/ 

## Some assumptions on top of the task requirements
- Assuming empty object from the public API is either empty dictionary {} or with insufficient keys in the dictionary. 
- From existing data retrieve from the two public APIs, I’m unable to identify the non-drink objects in neither the results from API a nor b. Please not the non-drink object is not handled at the moment.
- Price of the drink needs to be in format “$X.99”. However the source of API b, the “price” given is not in this format, e.g. {'price': '$11.49', ... ‘id': 142}. Assuming the source "price" of API b takes priority.




