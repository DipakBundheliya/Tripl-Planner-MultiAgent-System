import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3

from crewai import Crew
from agents.trip_agent import TripAgents
from tasks.trip_task import TripTasks
from datetime import datetime, timedelta  

class TripCrew:

    def __init__(self, source, destination, departureDateFromSource, departureDateFromDest, numOfPerson, budget, user_currency):
        self.source = source
        self.destination = destination
        self.departureDateFromSource = departureDateFromSource
        self.departureDateFromDest = departureDateFromDest
        self.numOfPerson = numOfPerson
        self.budget = budget
        self.currency = user_currency

    def run(self):
        """
        Runs 3 sequential crews to generate a final travel plan:
        - CREW 1: Flight search
        - CREW 2: Hotel + Activity planning
        - CREW 3: Final plan selection
        """
        agents = TripAgents()
        tasks = TripTasks() 

        flight_searcher_agent = agents.flight_search_agent()
        hotel_searcher_agent = agents.hotel_search_agent()
        activity_planner_agent = agents.activity_plan_maker_agent()
        final_plan_agent = agents.trip_finaliser_agent()

        flight_task = tasks.flight_checking_task(
            agent = flight_searcher_agent,
            source = self.source,
            destination= self.destination,
            departureDateFromSource= self.departureDateFromSource,
            numOfPerson= self.numOfPerson,
            budget= self.budget,
            currency = self.currency
        )

        hotel_task = tasks.hotel_checking_task(
            agent = hotel_searcher_agent,
            destination= self.destination,
            departureDateFromDest= self.departureDateFromDest,
            numOfPerson= self.numOfPerson,
            budget= self.budget,
            currency = self.currency,
            flight_task = flight_task
        )

        activity_plan_task = tasks.activity_planning_task(
            agent = activity_planner_agent, 
            destination= self.destination, 
            departureDateFromDest= self.departureDateFromDest, 
            numOfPerson= self.numOfPerson, 
            budget= self.budget, 
            currency= self.currency, 
            flight_task= flight_task
        )

        final_plan_task = tasks.trip_finaliser_task(
            agent = final_plan_agent,
            flight_task = flight_task,
            hotel_task = hotel_task,
            activity_plan_task = activity_plan_task 
        )

        crew_one = Crew(
            agents= [flight_searcher_agent, hotel_searcher_agent, activity_planner_agent, final_plan_agent],
            tasks= [flight_task, hotel_task, activity_plan_task, final_plan_task],
            verbose=True
        )

        result = crew_one.kickoff()

        return result


if __name__ == '__main__':
    # source, destination, departureDateFromSource, departureDateFromDest, numOfPerson, budget, user_currency
    trip_crew1 = TripCrew(
        source="Ahemadabad",
        destination="london",
        departureDateFromSource=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        departureDateFromDest=(datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        numOfPerson='1',
        budget='1000',
        user_currency='EUR'
    )

    response_one = trip_crew1.run() 
    print(response_one.raw)  # json dictionary 