## Fire Tracker

### About

Fire Tracker, KPCC's tool for following & researching California wildfires, contains fire information displayed by the California Department of Forestry and Fire Protection -- also known as CalFire -- which protects more than 31 million acres of California's privately-owned wildlands and provides emergency services in 36 of the State's 58 counties.

### About the Data

* Data and information contained in Fire Tracker is updated twice a day and is based on the [latest updates](http://cdfdata.fire.ca.gov/incidents/incidents_current) from [CalFire](http://www.calfire.ca.gov/)
. As such, Fire Tracker is a news tool and does not contain the latest information from emergency management officials, nor should it be used to make decisions that affect you and your family.
* Data for fires under the jurisdiction of the [U.S. Forest Service](http://www.fs.fed.us/) -- displayed on the department's [InciWeb Incident Information System](http://www.inciweb.org/incident/3307/) -- currently is not represented.
* Mapped locations are based on the approximate location of the fire as released by CalFire and should not be used to make decisions that affect you and your family.
* Data for fires that have reached 100 percent containment may contain inaccuracies.
* In cases where data for a particular item is not available or not clear, we display it as "n/a", or not available.
* To determine the number of fires and acreage affected by wildfires in Southern California we have added the number of fires that CalFire has tracked in Los Angeles, Orange, Riverside, San Bernardino and Ventura counties. This figure does not necessarily take into consideration wildfires for which another organization has jurisdiction.
* The 2012 aggregate data is based on data from the [CalFire archives](http://cdfdata.fire.ca.gov/incidents/incidents_archived).
* The 2013 aggregate data is based on 2013 fires contained in the database, and as such does not necessarily take into consideration wildfires for which another organization has jurisdiction.
* Air quality data is periodically updated based on [AirNow](http://airnow.gov/) ratings and based on an approximate zipcode.

### Initial Setup

* Create a new virtualenv firetracker

        mkvirtualenv firetracker

* Install dependencies from requirements.txt. You'll have to first remove titlecase==0.5.1 as a dependency has to be installed first and I haven't found a way around this.

        pip install -r requirements.txt

* Re-run to install titlecase==0.5.1

        pip install -r requirements.txt

### Docker Setup

These instructions assume you've created a Docker Network that includes a MySQL|MariaDB instance.

* Get a Deploybot token and assign it to an environment variable.  Skip this if you set up your own database.

        export DEPLOYBOT_TOKEN=xxxxxxxxxx

* Compose the Docker containers.

        docker-compose up -d

### Running the Scraper

`python manage.py scraper_wildfires`

### License

**GNU General Public License V2**
