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

    def activity_planning_task(self, agent, destination, departureDateFromDest, numOfPerson, budget, currency, flight_task):
        return Task(
            description=( 
                f"""
                    From the results of the previous flight search task, take each flight's arrival date at {destination}.
                    For each of these arrival dates, use activity plan search tool to plan a itinerary at {destination} for {numOfPerson} person.
                    consider days from one day after arrival date to {departureDateFromDest} date. 
                    Stay within a budget of {budget} {currency}.
                    Each day must include 'Morning', 'Afternoon', and optionally 'Evening' activities.
                    Consider num_days as the number of days from the arrival date to the departure date.
                """),
            expected_output=(
                    "Return a list of JSON objects. Each object corresponds to one flight option and must have the following structure:\n"
                    "[\n"
                    "  {\n"
                    "    'arrival_date': 'YYYY-MM-DD',\n"
                    "    'itinerary': [\n"
                    "      {\n"
                    "        'day': 'Day 1',\n"
                    "        'date': 'YYYY-MM-DD',\n"
                    "        'activities': {\n"
                    "          'Morning': '...activity...',\n"
                    "          'Afternoon': '...activity...',\n"
                    "          'Evening': '...activity (optional)...'\n"
                    "        }\n"
                    "      },\n"
                    "      ... (repeat for each day)\n"
                    "    ]\n"
                    "  },\n"
                    "  ... (repeat for other flight options)\n"
                    "]\n\n"
                    "Make sure each 'itinerary' list starts from one day after the arrival date and ends one day before the user's departure date.\n"
                    "If multiple flights have the same arrival_date, generate the itinerary only once for that date and do not repeat it in the output."
                ),
            agent=agent,
            output_file="activity_plan_details.md",
            context = [flight_task]
        )
