import os
import re
import sys
import time
import requests 
# For getting crewai supported sqlite3
import pysqlite3
sys.modules['sqlite3'] = pysqlite3
from crewai.tools import tool
from datetime import datetime, timedelta
 
from amadeus import Location, Client
from langchain_community.tools import DuckDuckGoSearchRun
 
# For flight search tool
amadeus = Client(
    client_id = os.environ.get("amadeus_client_id"),
    client_secret=os.environ.get("amadeus_client_secret")
)

# For hotel search tool
destinationSearchUrl = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
hotelSearchUrl = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
headers = {
"x-rapidapi-key": os.environ.get("rapidapi_key"),
"x-rapidapi-host": os.environ.get("rapidapi_host")
}

def convert_to_hours(duration: str) -> float:
    # Match ISO 8601 duration pattern (e.g. PT30H, PT7H40M, PT1H20M10S)
    match = re.match(r"^P?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", duration)
    
    if match:
        # Extract hours, minutes, and seconds, defaulting to 0 if not found
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        # Convert everything to hours
        total_hours = hours + (minutes / 60) + (seconds / 3600)
        return round(total_hours)
    else:
        raise ValueError("Invalid ISO 8601 duration format")
 
@tool("flight search")
def search_flights(source : str, destination: str, departureDate: str , numOfPerson: str):
  """
  Search flights between on source and destination using Amadeus API.

  parameters:
  - source (str): The city name, e.g., "Delhi", "New York".
  - destination (str): The city name, e.g., "London", "Bangkok".
  - departureDate (str): Date in format YYYY-MM-DD.
  - numOfPerson (str): Number of Adult passangers.

  Returns : list of dict containing flight_name, num_via_stops, price and other details.
  """
  start_time = time.time()
  print("entering")
  try:
    if len(source) < 3 or len(destination) < 3:
        return "Source and destination must be at least 3 characters."

    sourceResponse = amadeus.reference_data.locations.get(
        keyword=source,
        subType=Location.ANY
    )
    destinationResponse = amadeus.reference_data.locations.get(
        keyword=destination,
        subType=Location.ANY
    )
    if not sourceResponse.data or not destinationResponse.data:
      return "Invalid source or destination."
    
    source_iatacode, destination_iatacode = sourceResponse.data[0]['iataCode'], destinationResponse.data[0]['iataCode']

    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=source_iatacode,
        destinationLocationCode=destination_iatacode,
        departureDate=departureDate,
        adults=numOfPerson
    )
 
    print(f"length of getting flights are {len(response.data)}")

    num_of_flights = min(2, len(response.data))
    filtered_flights = response.data[:num_of_flights]
    cleaned = []
    
    for offer in filtered_flights:
        try:
            price_info = offer.get("price", {})
            airline_code = offer.get("validatingAirlineCodes", [None])[0]
            seats = offer.get("numberOfBookableSeats", 0)
            itinerary = offer.get("itineraries", [])[0]
            segments = itinerary.get("segments", [])
            
            segment_list = []
            total_stops = max(len(segments) - 1, 0)
            
            for seg in segments:
                # from_airport_code = amadeus.reference_data.locations.get(keyword=seg["departure"]["iataCode"], subType=Location.ANY).data
                # to_airport_code = amadeus.reference_data.locations.get(keyword=seg["arrival"]["iataCode"], subType=Location.ANY).data
                
                segment_list.append({
                    # "from_airport": from_airport_code[0].get('detailedName') if from_airport_code else seg["departure"]["iataCode"],
                    # "to_airport": to_airport_code[0].get('detailedName') if to_airport_code else seg["arrival"]["iataCode"],
                    "from_airport" : seg["departure"]["iataCode"],
                    "to_airport" : seg["arrival"]["iataCode"],
                    "departure_time": seg["departure"]["at"],
                    "arrival_time": seg["arrival"]["at"],
                    "flight_number": f'{seg["carrierCode"]}{seg["number"]}',
                    "carrier": seg["carrierCode"],
                    "duration_hour": convert_to_hours(seg["duration"]),
                    "stops": seg.get("numberOfStops", 0)
                })
            
            # baggage info (only first traveler & segment)
            fare_segments = offer.get("travelerPricings", [])[0].get("fareDetailsBySegment", [])
            cabin_class = fare_segments[0].get("cabin", "ECONOMY") if fare_segments else "ECONOMY"
            checked = fare_segments[0].get("includedCheckedBags", {}).get("weight", 0)
            cabin = fare_segments[0].get("includedCabinBags", {}).get("weight", 0)

            cleaned.append({
                "id": offer["id"],
                "flight_price": price_info.get("grandTotal"),
                "currency": price_info.get("currency"),
                "airline": amadeus.reference_data.airlines.get(airlineCodes=airline_code).data[0]["businessName"] ,
                "available_seats": seats,
                "total_duration_hour": convert_to_hours(itinerary.get("duration")),
                "stops": total_stops,
                "segments": segment_list,
                "cabin_class": cabin_class,
                "baggage": {
                    "cabin_bag": f"{cabin} KG" if cabin else "N/A",
                    "checked_bag": f"{checked} KG" if checked else "N/A"
                }
            })

        except Exception as e:
            print(f"Error parsing offer: {e}")

  except Exception as e:
    error_result = {
        "status": "error",
        "message": str(e)
    }
    print("getting exception", error_result)
    return str(error_result)

  print(f"Total time taken to search and proceed flight search is {time.time() - start_time} seconds")
  return cleaned
 
@tool("hotel search")
def search_hotels(cityName: str, arrival_date: str, departure_date: str, adults: str):
    """
    Search for hotels in a specified city using the Rapid API.
    Parameters:
        cityName (str): The name of the city to search hotels in (e.g., "Delhi", "New York").
        arrival_date (str): The check-in date in 'YYYY-MM-DD' format.
        departure_date (str): The check-out date in 'YYYY-MM-DD' format.
        adults (str): The number of adults staying.
    Returns:
        list of dict: A list of dictionaries, each containing hotel information such as name, hotel price, and others
    Notes:
        Returns an empty list if no hotels are found for the specified city.
    """ 
    start_time = time.time()
    querystring = {"query":cityName}

    response = requests.get(destinationSearchUrl, headers=headers, params=querystring)
    response_json = response.json()

    print("destination id is", response_json)
    if "message" in response_json:
        return {"status": "error", "message": response_json["message"]}
    
    dest_id_list = [location['dest_id'] for location in response_json.get('data', []) if location.get("search_type") == 'city']

    if not dest_id_list:
        return []

    dest_id = dest_id_list[0]

    querystring = {"dest_id": dest_id, "search_type": "CITY", "arrival_date": arrival_date, "departure_date": departure_date, "adults": adults,
                   "children_age": "0,17", "room_qty": "1", "page_number": "1", "units": "metric", "temperature_unit": "c", "languagecode": "en-us", }
    response = requests.get(hotelSearchUrl, headers=headers, params=querystring)

    raw_response = response.json()

    if "message" in raw_response:
       return {"status": "error", "message": raw_response["message"]}
    print("hotel search response is", raw_response)

    hotels_data = raw_response.get('data', {}).get('hotels', [])
    if not hotels_data:
        return []
    
    # Clean the hotel data
    cleaned = []

    print(f"length of getting hotels are {len(hotels_data)}")
    min_num_hotels = min(len(hotels_data), 5)
    hotels_data = hotels_data[:min_num_hotels]

    for hotel in hotels_data:
        try:
            prop = hotel.get('property', {})
            price_info = prop.get('priceBreakdown', {}).get('grossPrice', {})

            cleaned.append({
                "name": prop.get("name"),
                "hotel_price": round(price_info.get("value", 0), 2),
                "currency": price_info.get("currency", "USD"),
                "rating": prop.get("reviewScore"),
                "rating_text": prop.get("reviewScoreWord"),
                "review_count": prop.get("reviewCount"),
                "stars": prop.get("propertyClass"),
                "photo": prop.get("photoUrls", [None])[0],
                "location": {
                    "latitude": prop.get("latitude"),
                    "longitude": prop.get("longitude")
                },
                "is_preferred": prop.get("isPreferred", False)
            })
        except Exception as e:
            print(f"Hotel parse error: {e}")

    print(f"Total time taken to search and proceed flight search is {time.time() - start_time} seconds")
    return cleaned

@tool("activity plan search")
def search_activities(num_days : int, destination: str, arrivalDate: str, departureDate: str):
    """
    Search for activities or travel itinerary in a destination city.

    parameters:
    - num_days: Number of days for which user wants to do activities
    - destination (str): The city name, e.g., "London", "Bangkok".
    - arrivalDate (str): The date when user will arrive at the destination
    - departureDate (str): The date when user will leave the destination

    Returns : list of dict containing activities details.
    """
    search_prompt = f"Best {num_days}-day travel itinerary or local tourist activities in {destination} between {arrivalDate} and {departureDate}"
    return DuckDuckGoSearchRun().run(search_prompt)

if __name__ == "__main__":
   
   # check flight search tool
#    response = search_flights("Goa", "London", (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "1" )
   
   #  check hotel details
   response = search_hotels("London", datetime.now().strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "1")
#    breakpoint()
   print(response)