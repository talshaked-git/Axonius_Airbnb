Axonius home assignment:
This project automates testing of Airbnb flow using Playwright (Python) and uses Page Object Model.

The first test searches with given terms, validates search terms and gets all results and filters them by rating and price,
then logs max rating results info (rating, price, url) and cheapest results info (rating, price, url).

The second scenario also searches with given terms, validates search terms and gets all results and filters by highest rating
and amongst the highest rating - most reviewed rating and starts the reservation process for it. 

This project is fully logged with clear logs and assertions for every step.


Before cloning and running this, please make sure you have Python 3.8+ and then do the following:

~~~
git clone https://github.com/talshaked-git/Axonius_Airbnb
cd Axonius_Airbnb
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
playwright install

and then run the tests by running:
pytest
