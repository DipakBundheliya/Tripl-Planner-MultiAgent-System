import os
from langchain_groq import ChatGroq
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from tools.trip_tools import search_activities, search_flights, search_hotels

load_dotenv()

llm = ChatGroq(
    temperature = 0,
    model_name = 'groq/llama-3.3-70b-versatile'
)

class TripAgents:

    def flight_search_agent(self):
        return Agent(
                llm=llm,
                role = "Flight seach expert",
                goal = "Help users find flights between cities using only city names, If any source city or destination city looks like not grametically correct, make it correct by yourself and after give to it tools",
                backstory ="You are helpful assistant that uses the Flight_search tool. Always ensure you use short city names for both soure and destination",
                tools = [search_flights],
                allow_delagation=False,
                verbose=True
            )

    def hotel_search_agent(Self):
        return Agent(
                llm=llm,
                role = "Hotel search expert",
                goal = "Find suitable hotels for the user's trip in given city",
                backstory ="You are a travel assistant specialized in suggesting hotels that are affordable and comfortable,",
                tools = [search_hotels],
                allow_delagation=False,
                verbose=True
            )

    def activity_plan_maker_agent(self):
        return Agent(
            llm=llm,
            role = "Local activity expert",
            goal = "Use the search tool to find a {num_days}-day itinerary or list of local activities in {destination_city}"
                "Each day should include tourist-friendly things to do.",
            backstory =(
                "You are a travel assistant that helps travelers make the most of their trip by discovering top-rated, "
                "interesting, and enjoyable local activities. You use a search tool to gather up-to-date itinerary ideas."
            ),
            tools = [search_activities],
            allow_delagation=False,
            verbose=True
        )