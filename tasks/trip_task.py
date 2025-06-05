from crewai import Task
from textwrap import dedent 

class TripTasks:

    def flight_checking_task(self, agent, source, destination, departureDateFromSource, numOfPerson, budget, currency):
        return Task(
            description=(
                    f"""
                    Search for flights from {source} to {destination} on {departureDateFromSource} date 
                    for {numOfPerson} number of person under the budget of {budget} {currency}.
                    Find the best flight options considering price and timing.
                    Return the flight details.
                    """),
            expected_output=(
                "List of JSON formated flights details with flight name, arrival date and others details"
            ),
            agent=agent,
            output_file="flight_details.md" 
        ) 
    
    def hotel_checking_task(self, agent, destination, departureDateFromDest, numOfPerson, budget, currency, flight_task):
        return Task(
            description=(
                f"""
                    From the results of the previous flight search task, take each flight's arrival date at {destination}.
                    For each of these arrival dates, search for hotels in {destination} for {numOfPerson} adults.
                    The check-in date for the hotel search will be the flight's arrival date, and the check-out date will be {departureDateFromDest}.
                    Stay within a budget of {budget} {currency}.
                    Compile a list of suitable hotel options for each considered arrival date.
                """),
            expected_output=(
                "A JSON object. Each key in this object should be a specific arrival date (from a flight). "
                "The value for each key should be a list of dictionaries, where each dictionary contains hotel "
                "information (name, price, currency, etc.) for hotels available for that arrival date and the specified check-out date."
            ),
            agent=agent,
            output_file="hotel_details.md",
            context = [flight_task]
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
            output_file="activity_plan_details.md",
            context = [self.flight_checking_task]
        )
