import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3
import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from langchain_groq import ChatGroq
from tools.trip_tools import search_activities, search_flights, search_hotels
 
load_dotenv(override=True)
class TripAgents:

    def __init__(self): 
        self.llm = LLM(model='groq/llama-3.3-70b-versatile')
        print("LLM initialized successfully:", self.llm)
        print("api key:", os.environ.get("GROQ_API_KEY"))

        try:
            test_response = self.llm.call("Hello, how are you?")
            print("LLM test success:", test_response)
        except Exception as e:
            print("LLM test fails:", str(e))
            
    def flight_search_agent(self):
        return Agent(
                llm=self.llm,
                role = "Flight seach expert",
                goal = "Help users find flights between cities using city names, If any source city or destination city looks like not grametically correct, make it correct by yourself and after give it to flight search tool",
                backstory ="You are helpful assistant that uses the flight search tool.",
                tools = [search_flights],
                allow_delegation=False,
                verbose=True
            )

    def hotel_search_agent(self):
        return Agent(
                llm=self.llm,
                role = "Hotel search expert",
                goal = "Find suitable hotels for the user's trip in given city based on given arrival dates and departure date for each flight",
                backstory ="You are a hotel booking expert who knows how to find the best accomodations that match traveler's needs, budget, and location preferences using hotel search tool. You work well with arrival dates and departure dates provided by the flight search expert",
                tools = [search_hotels],
                allow_delegation=False,
                verbose=True
            )

    def activity_plan_maker_agent(self):
        return Agent(
                llm=self.llm,
                role = "Local activity expert",
                goal = "Use the search tool to find a {num_days}-day itinerary or list of local activities in {destination_city}"
                    "Each day should include tourist-friendly things to do.",
                backstory =(
                    "You are a travel assistant that helps travelers make the most of their trip by discovering top-rated, "
                    "interesting, and enjoyable local activities. You use a search tool to gather up-to-date itinerary ideas."
                ),
                tools = [search_activities],
                allow_delegation=False,
                verbose=True
            )