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
                "Convert from_airport and to_airport fields from IATA codes to full airport names."
            ),
            agent=agent,
            output_file="flight_details.json" 
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
            output_file="hotel_details.json",
            context = [flight_task]
        )

    def activity_planning_task(self, agent, destination, departureDateFromDest, numOfPerson, budget, currency, flight_task):
        return Task(
            description=( 
                 f"""
                Your goal is to create activity plan for travelers going to {destination}.

                STEP 1: First, examine the flight search results to extract the arrival_date. Calculate the number of days between arrival and {departureDateFromDest}.

                STEP 2: Use the `activity plan search` tool ONCE with the full trip duration to get comprehensive activity suggestions for {destination}.
                - Don't call the same tool multiple times with identical parameters
                - Focus on getting a broad range of activities that can be categorized into morning, afternoon, and evening options

                STEP 3: From the search results, create a structured day-by-day itinerary:
                - Start from the day after arrival date
                - For each day until {departureDateFromDest}, assign:
                  * One Morning activity (cultural sites, museums, markets)
                  * One Afternoon activity (landmarks, parks, tours) 
                  * One Evening activity (dining, entertainment, nightlife)
                - Use the activities found in your search, distributing them logically across days

                STEP 4: Your FINAL ANSWER must be in strict JSON format exactly as shown in expected_output.

                IMPORTANT: 
                - Call the search tool only ONCE with the full trip details
                - If search results are limited, create reasonable fallback activities based on common {destination} attractions
                - Always end with "Final Answer:" followed by the JSON structure
                """
            ),
            expected_output=(
                """
                Return a list of JSON objects. Each object corresponds to one flight option with this structure:

                [
                {
                    'arrival_date': 'YYYY-MM-DD',
                    'itinerary': [
                    {
                        'day': 'Day 1',
                        'date': 'YYYY-MM-DD',
                        'activities': {
                        'Morning': {'title': '...'},
                        'Afternoon': {'title': '...'},
                        'Evening': {'title': '...'}, 
                        }, 
                    },
                    ...
                    ], 
                },
                ...
                ]
                """
            ),
            agent=agent,
            output_file="activity_plan_details.json",
            context = [flight_task]
        )

    def trip_finaliser_task(self, agent, flight_task, hotel_task, activity_plan_task):
        return Task(
            description=(
                f"""
                From the results of the previous 
                - Flight search task
                - Hotel search task
                - Activity plan task

                Finalise one optimal end-to-end itinerary.

                Steps:
                1. Select the best flight based on earliest arrival time and most convenient schedule.
                2. Choose a hotel available on the same arrival date with the best rating and amenities.
                3. Use the matching activity plan that begins the day after arrival and ends one day before departure.
                4. Validate the final JSON structure is complete and properly formatted
                5. Ensure all brackets and braces are properly closed
                6. Use actual data, not placeholder values
                
                CRITICAL: The output must be valid, parseable JSON with all brackets properly closed. 
                IMPORTANT: Return ONLY the JSON structure with no markdown formatting, no code blocks, no additional text.
                """ 
            ),
            expected_output=(
                """
                Return ONLY a complete, valid JSON object with ALL brackets and braces properly closed.
                
                VALIDATION CHECKLIST:
                - All opening brackets { [ must have closing brackets } ]
                - flight_price must be a number (e.g., 222.08), not a string
                - hotel_price must be a number (e.g., 125.5)
                - Use real data, not placeholder URLs or "N/A" values
                - Ensure the JSON structure is complete and valid

                {
                    "flight_details": {
                        "id": "string",
                        "flight_price": number,
                        "currency": "string", 
                        "airline": "string",
                        "available_seats": number,
                        "total_duration_hour": number,
                        "stops": number,
                        "segments": [
                            {
                                "from_airport": "string",
                                "to_airport": "string", 
                                "departure_time": "YYYY-MM-DDTHH:MM:SS",
                                "arrival_time": "YYYY-MM-DDTHH:MM:SS",
                                "flight_number": "string",
                                "carrier": "string",
                                "duration_hour": number,
                                "stops": number
                            }
                        ],
                        "cabin_class": "string",
                        "baggage": {
                            "cabin_bag": "string",
                            "checked_bag": "string"
                        }
                    },
                    "hotel_details": {
                        "name": "string",
                        "hotel_price": number,
                        "currency": "string",
                        "rating": number,
                        "rating_text": "string", 
                        "review_count": number,
                        "stars": number,
                        "photo": "string",
                        "location": {
                            "latitude": number,
                            "longitude": number
                        },
                        "is_preferred": boolean
                    },
                    "activities": [
                        {
                            "day": "Day X",
                            "date": "YYYY-MM-DD",
                            "activities": {
                                "Morning": {"title": "string"},
                                "Afternoon": {"title": "string"},
                                "Evening": {"title": "string"}
                            }
                        }
                    ]
                }

                All fields must be filled using information from the three agents. Ensure dates are logically consistent. Return ONLY the JSON - no markdown, no explanations, no code blocks.
                """
                "FINAL CHECK: Ensure your JSON response ends with proper closing braces }} and is complete."
            ),
            agent=agent,
            output_file="final_trip_plan.json",
            context=[flight_task, hotel_task, activity_plan_task]
        )