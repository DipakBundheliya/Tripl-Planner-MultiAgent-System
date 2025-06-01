from agents.trip_agent import TripAgents
from tasks.trip_task import TripTasks
from datetime import datetime, timedelta

class TripCrew:

    def __init__(self, source, destination, departureDate, departureDateFromDest, numOfPerson, budget):
        self.source = source
        self.destination = destination
        self.departureDate = departureDate
        self.departureDateFromDest = departureDateFromDest
        self.numOfPerson = numOfPerson
        self.budget = budget

    def run(self):
        agents = TripAgents() 
    
trip_crew1 = TripCrew("Ahemadabad", 
         "london", 
         datetime.now().strftime("%Y-%m-%d"), 
         (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
         '1',
         '1000')
trip_crew1.run()