import os
import requests 
from crewai.tools import tool
from dotenv import load_dotenv
from amadeus import Location, Client
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

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
 
@tool("flight search")
def search_flights(source : str, destination: str, departureDate: str , numOfPerson: str):
  """
  Search flights between on source and destination using Amadeus API.

  parameters:
  - source (str): The city name, e.g., "Delhi", "New York".
  - destination (str): The city name, e.g., "London", "Bangkok".
  - departureDate (str): Date in format YYYY-MM-DD.
  - numOfPerson (str): Number of Adult passangers.

  Returns : list of dict containing flight_name, num_via_stops, price.
  """
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
 
    print(f"length of flights are {len(response.data)}")

    num_of_flights = min(10, len(response.data))
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
                segment_list.append({
                    "from": seg["departure"]["iataCode"],
                    "to": seg["arrival"]["iataCode"],
                    "departure": seg["departure"]["at"],
                    "arrival": seg["arrival"]["at"],
                    "flight_number": f'{seg["carrierCode"]}{seg["number"]}',
                    "carrier": seg["carrierCode"],
                    "duration": seg["duration"],
                    "stops": seg.get("numberOfStops", 0)
                })

            # baggage info (only first traveler & segment)
            fare_segments = offer.get("travelerPricings", [])[0].get("fareDetailsBySegment", [])
            cabin_class = fare_segments[0].get("cabin", "ECONOMY") if fare_segments else "ECONOMY"
            checked = fare_segments[0].get("includedCheckedBags", {}).get("weight", 0)
            cabin = fare_segments[0].get("includedCabinBags", {}).get("weight", 0)

            cleaned.append({
                "id": offer["id"],
                "price": price_info.get("grandTotal"),
                "currency": price_info.get("currency"),
                "airline": airline_code,
                "available_seats": seats,
                "duration": itinerary.get("duration"),
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
    
  return cleaned
 
@tool("hotel search")
def search_hotels(cityName: str, arrival_date: str, departure_date: str, adults: str):
  """
  Search Hotels in cityName using Rapid API.

  parameters:
  - cityName (str): The city name, e.g., "Delhi", "New York"

  Returns : list of dict containing hotels information like name, price, cuurency and others. 
  """

  querystring = {"query":cityName}

  response = requests.get(destinationSearchUrl, headers=headers, params=querystring)
  print(response.json())
  dest_id_list = [location['dest_id'] for location in response.json()['data'] if location["search_type"] == 'city']
  
  if not dest_id_list:
      return []

  dest_id = dest_id_list[0] 

  querystring = {"dest_id":dest_id,"search_type":"CITY","arrival_date":arrival_date,"departure_date":departure_date,"adults":adults,
                "children_age":"0,17","room_qty":"1","page_number":"1","units":"metric","temperature_unit":"c","languagecode":"en-us",}
  response = requests.get(hotelSearchUrl, headers=headers, params=querystring)

  raw_response = response.json()
  
  hotels_data = raw_response.get('data', {}).get('hotels', [])
  cleaned = []

  for hotel in hotels_data:
      try:
          prop = hotel.get('property', {})
          price_info = prop.get('priceBreakdown', {}).get('grossPrice', {})

          cleaned.append({
              "name": prop.get("name"),
              "price": round(price_info.get("value", 0), 2),
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

  return cleaned

@tool("activity plan search")
def search_activities(num_days : int, destination: str, arrivalDate: str, departureDate: str):
  """
  Search flights between on source and destination using Amadeus API.

  parameters:
  - num_days: Number of days for which user wants to do activities
  - destination (str): The city name, e.g., "London", "Bangkok".
  - arrivalDate (str): The date of day after that day when user will arrive at his destination
  - departureDate (str): The date of day before that date when user will leave his destination

  Returns : list of dict containing activities details.
  """
  search_prompt = f"Best {num_days}-day travel itinery or local tourist activities in {destination}"
  return DuckDuckGoSearchRun().run(search_prompt)


if __name__ == "__main__":
   # check flight search tool
   response = search_flights("Goa", "London", "2025-06-10", "1" )
   print(response)