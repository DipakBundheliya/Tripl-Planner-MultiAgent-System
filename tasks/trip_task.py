from crewai import Task
from textwrap import dedent 

class TripTasks:

    def flight_checking_task(self, agent, source, destination, departureDateFromSource, numOfPerson, budget):
        return Task(
            description=(f"Search for flights between {source} and {destination} only on {departureDateFromSource} for {numOfPerson} passangers under the budget of {budget} USD in minimum duration"),
            expected_output=(
                "List of flights deatils in json format with flight name, number of via stops, price and others"
            ),
            agent=agent,
            timeout = 30
        ) 
    
    def hotel_checking_task(self, agent, source, destination, departureDate, departureDateFromDest, numOfPerson, budget):
        return Task(
            description=("Search hotels on given {destination} city, for {departureDate} departure date, for {numOfPerson} adults for trip plan,    Only return options that, when added with the flight cost, stay within {budget} USD."
                        "based on flight arrival date at destination."),
            expected_output=(
                "Return list of dict containing hotels information like name, price, cuurency and others. "
            ),
            agent=agent,
            timeout = 30
        )

    def activity_planning_task(self, agent, source, destination, departureDate, departureDateFromDest, numOfPerson, budget):
        return Task(
            description=(
                "Use the search tool to find a 2-day itinerary or list of local activities in {destination}. "
                "These should be popular, tourist-friendly places or experiences."
            ),
            expected_output=(
                "Return a JSON list where each item represents a day with a list of 2–4 activities in that city. "
                "Each day must include 'Morning', 'Afternoon', and optionally 'Evening' activities."
            ),
            agent=agent,
            timeout=60
        )
