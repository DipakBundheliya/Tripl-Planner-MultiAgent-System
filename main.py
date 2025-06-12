from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import json
from datetime import datetime, timedelta
import uvicorn
from services.final_trip_plan_service import TripCrew

app = FastAPI(title="Travel Planning API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class TravelPlanRequest(BaseModel):
    source: str
    destination: str
    departure_date_from_source: str  # YYYY-MM-DD
    departure_date_from_dest: str    # YYYY-MM-DD
    num_of_person: str
    budget: str
    user_currency: str

# Response Model
class TravelPlanResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Travel Planning API", "status": "running"}

@app.post("/create-travel-plan", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelPlanRequest):
    try:
        # Here you would integrate with your TripCrew
        # For now, using the mock data structure you provided
         
        trip_crew = TripCrew(
            source=request.source,
            destination=request.destination,
            departureDateFromSource=request.departure_date_from_source,
            departureDateFromDest=request.departure_date_from_dest,
            numOfPerson=request.num_of_person,
            budget=request.budget,
            user_currency=request.user_currency
        )
        response_one = trip_crew.run()  
        try :
            trip_data = json.loads(response_one.raw)
        except json.JSONDecodeError as e:
            print("Agent response\n", response_one.raw)
            raise HTTPException(status_code=500, detail=f"Error decoding JSON response: {str(e)}")
        
        # Mock response (replace with actual TripCrew response)
        # trip_data = {
        #     'flight_details': {
        #         'id': '1', 
        #         'flight_price': '318.59', 
        #         'currency': request.user_currency, 
        #         'airline': 'EMIRATES', 
        #         'available_seats': 9, 
        #         'total_duration_hour': 12, 
        #         'stops': 1, 
        #         'segments': [
        #             {
        #                 'from_airport': 'AMD', 
        #                 'to_airport': 'DXB', 
        #                 'departure_time': f'{request.departure_date_from_source}T04:35:00', 
        #                 'arrival_time': f'{request.departure_date_from_source}T06:10:00', 
        #                 'flight_number': 'EK539', 
        #                 'carrier': 'EK', 
        #                 'duration_hour': 3, 
        #                 'stops': 0
        #             },
        #             {
        #                 'from_airport': 'DXB', 
        #                 'to_airport': 'LGW', 
        #                 'departure_time': f'{request.departure_date_from_source}T08:00:00', 
        #                 'arrival_time': f'{request.departure_date_from_source}T12:35:00', 
        #                 'flight_number': 'EK15', 
        #                 'carrier': 'EK', 
        #                 'duration_hour': 8, 
        #                 'stops': 0
        #             }
        #         ], 
        #         'cabin_class': 'ECONOMY', 
        #         'baggage': {'cabin_bag': 'N/A', 'checked_bag': '25 KG'}, 
        #         'arrival_date': request.departure_date_from_source
        #     }, 
        #     'hotel_details': {
        #         'name': 'Grand Palace Hotel', 
        #         'hotel_price': 125.5, 
        #         'currency': 'USD', 
        #         'rating': 8.6, 
        #         'rating_text': 'Excellent', 
        #         'review_count': 2345, 
        #         'stars': 5, 
        #         'photo': 'https://example.com/photo1.jpg', 
        #         'location': {'latitude': 28.6139, 'longitude': 77.209}, 
        #         'is_preferred': True, 
        #         'check_in_date': request.departure_date_from_source, 
        #         'check_out_date': request.departure_date_from_dest
        #     }, 
        #     'activities': [
        #         {
        #             'day': 'Day 1', 
        #             'date': request.departure_date_from_source, 
        #             'activities': {
        #                 'Morning': {'title': 'Visit the National Gallery'}, 
        #                 'Afternoon': {'title': 'Explore street markets'}, 
        #                 'Evening': {'title': 'Enjoy dinner at a traditional English pub'}
        #             }
        #         },
        #         {
        #             'day': 'Day 2', 
        #             'date': (datetime.strptime(request.departure_date_from_source, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'), 
        #             'activities': {
        #                 'Morning': {'title': 'Attend the champagne and polo event'}, 
        #                 'Afternoon': {'title': 'Discover new cultural institutions'}, 
        #                 'Evening': {'title': 'Enjoy a West End musical'}
        #             }
        #         },
        #         {
        #             'day': 'Day 3',
        #             'date': (datetime.strptime(request.departure_date_from_source, '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d'), 
        #             'activities': {
        #                 'Morning': {'title': 'Visit the British Museum'}, 
        #                 'Afternoon': {'title': 'Take a stroll in Hyde Park'}, 
        #                 'Evening': {'title': 'Enjoy a cruise on the Thames'}
        #             }
        #         }
        #     ]
        # }
        
        return TravelPlanResponse(
            status="success",
            message="Travel plan created successfully",
            data=trip_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rate limit exceeds while creating travel plan: {str(e)}")
    

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    # command to run : uvicorn main:app --host 0.0.0.0 --port 8000 --reload
