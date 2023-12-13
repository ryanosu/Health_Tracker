<h1>Welcome to the Health Tracker web app!</h1>

![login-page](https://github.com/ryanosu/Health_Tracker/assets/86269596/5126dc7b-22c4-46f8-90c9-c504493b5095)


Create an account with a username, password, and email. Then login.

![main-page](https://github.com/ryanosu/Health_Tracker/assets/86269596/fa3eda2e-40f1-4963-b2ec-ab8a6c333fc9)


Create, Edit, and Update foods or your calorie goal. <br><br> Note: currently, querying the USDA API currently takes 30-45 seconds for it to respond. To use it, you must sign up for an api key at https://fdc.nal.usda.gov/api-key-signup.html

<h2>About</h2>
This app allows the user to track their daily calories and macronutrients - protein, fat, and carbs. The app displays graphics about the foods inputted in the database that will be useful to their personal daily intake goals. <br> <br> If the user does not have all necessary information, there is also a function that allows the user to type in the name of the food and attempt to call the USDA API to get that information about the food. The user may add new food, edit existing food, delete a food, or delete the entire table. The user may also set the daily calorie goal. 

<h2>Technologies:</h2>
<li>Backend: Flask, MySQL</li>
<li>Frontend: JavaScript, HTML, CSS, Jinja2</li>

<h2>How to use:</h2>

1. Clone this repository

```sh
git clone https://github.com/ryanosu/Health_Tracker.git
```

2. View app.py and run the app

<h2>Or view mine live on AWS:</h2>

```sh
http://health-tracker.us-east-2.elasticbeanstalk.com
```
