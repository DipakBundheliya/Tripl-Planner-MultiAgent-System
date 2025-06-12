import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3
import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from langchain_groq import ChatGroq
from tools.trip_tools import search_activities, search_flights, search_hotels_dummy 

load_dotenv(override=True)
class TripAgents:

    def __init__(self): 
        self.llm = LLM(model='gemini/gemini-2.5-flash-preview-05-20', api_key=os.environ["GEMINI_API_KEY"]) 
        print("LLM initialized successfully:", self.llm)  

        try:
            test_response = self.llm.call("Hello, how are you?")
            print("LLM test success:", test_response)
        except Exception as e:
            print("LLM test fails:", str(e))
            
    def flight_search_agent(self): 
        return Agent(
                llm=self.llm,
                role = "Flight seach expert",
                goal = "Help users find flights between cities using city names, If any source city or destination city looks like not grametically correct, make it correct by yourself and after give it to flight search tool.",
                backstory ="""
                You are helpful assistant that uses the flight search tool.
                """,
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
                tools = [search_hotels_dummy],
                allow_delegation=False,
                verbose=True
            )

    def activity_plan_maker_agent(self): 
        return Agent(
                llm=self.llm,
                role = "Local activity expert",
                goal = "Use the search tool to find a {num_days}-day itinerary or list of local activities in {destination_city} "
                    "starting from {arrival_date} to {departure_date}. Include a list of activities each day with detailed descriptions. "
                    "Convert the raw search results into a structured {num_days}-day itinerary with specific activities and timing. "
                    "Parse web content and extract only relevant activity information.",
                backstory =(
                    "You are an expert travel planner who can read through travel websites and blogs "
                    "to extract the most relevant activities and experiences. You excel at parsing unstructured "
                    "web content and converting it into organized, actionable travel itineraries with diverse activity options."
                ),
                tools = [search_activities],
                allow_delegation=False,
                verbose=True
            )
    
    def trip_finaliser_agent(self): 
        return Agent(
                llm=self.llm,
                role = "Trip finaliser",
                goal =  "Extract arrival date from flight results, then create a structured daily itinerary with morning, afternoon, and evening activities. "
                "Use the search tool efficiently - call it only once to get comprehensive activity suggestions, then organize them into a day-by-day schedule. "
                "Always provide the final answer in the exact JSON format specified in the task.",  
                backstory = (
                    "You are an expert travel planner who efficiently organizes travel information. You understand how to extract key dates from flight data, "
                    "use search tools strategically without redundant calls, and structure itineraries in the precise format required. "
                    "You a      lways complete tasks with properly formatted JSON outputs."
                ),
                allow_delegation=False,
                verbose=True
            )