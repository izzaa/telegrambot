import aiml
import requests

GEO_CODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
PLACE_SEARCH_BY_TEXT = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_SEARCH_NEARBY = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
API_KEY = "AIzaSyDmjPhTY_4Qf-DhstKVatrnYb2v1PBOzgA"
UNKNOWN_RESPONSE = "UNKNOWN"
MAX_RESULT = 10

ASK_FOR_RADIUS = "ASK FOR RADIUS"
latitude_KEY = "latitude"
LONGITUDE_KEY = "LONGITUDE"
LOCATION_KEY = "LOCATION"
RADIUS_KEY = "RADIUS"
ACTION_KEY = "ACTION"
NAME_KEY = "NAME"

action_place_type_map = {'makan': 'restaurant', 'liburan': 'zoo'}

# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml b")


def extract_latitude_longitude(json_result):
    location_geo = json_result.get('results')[0].get('geometry').get('location')
    return location_geo.get('lat'), location_geo.get('lng')


def generate_geocode_url(location):
    complete_url = GEO_CODE_URL + "?address=" + location
    complete_url += "&key=" + API_KEY
    return complete_url


def generate_place_search_by_text_url(action, query, lat, lng, radius):
    complete_url = PLACE_SEARCH_BY_TEXT + "?query=" + query
    complete_url += "&location=" + str(lat) + "," + str(lng)
    complete_url += "&radius=" + str(radius)
    complete_url += "&type=" + action_place_type_map[action]
    complete_url += "&key=" + API_KEY
    return complete_url


def generate_place_search_nearby_url(action, name, lat, lng, radius):
    complete_url = PLACE_SEARCH_NEARBY + "?location=" + str(lat) + "," + str(lng)
    complete_url += "&radius=" + str(radius)
    complete_url += "&keyword=" + name
    complete_url += "&type=" + action_place_type_map[action]
    complete_url += "&key=" + API_KEY
    return complete_url


def extract_place_name(json_result):
    ctr = 0
    places = ''
    results = json_result.get('results')

    if len(results) == 0:
        return "Maaf kami tidak dapat menemukan tempat yang anda inginkan"

    # print("result size : " + str(len(results)))
    for r in results:
        if ctr > MAX_RESULT:
            break

        if places:
            places = places + ", "

        ctr += 1
        places = places + r.get("name")

    print(places)
    return places


def log(action, name, location, radius, lat, lng):
    if action:
        print("action : " + action)
    if name:
        print("name : " + name)
    if location:
        print("location : " + location)
    if radius:
        print("radius : " + radius)
    if lat:
        print("latitude : " + str(lat))
    if lng:
        print("longitude : " + str(lng))


def query_place_by_nearby(action, name, lat, lng, radius):
    print("spec is completed, will search " + action_place_type_map[action] + " nearby " + str(lat) + ", lng : " + str(lng))
    placesearch_url = generate_place_search_nearby_url(action, name, lat, lng, radius)
    print(placesearch_url)

    place_json = requests.post(placesearch_url).json()
    places = extract_place_name(place_json)
    return places


def query_place_by_text_search(action, name, location, radius):
    print("spec is completed, will search by text " + name + " in " + location)

    geocode_url = generate_geocode_url(location)
    print(geocode_url)

    json = requests.post(geocode_url).json()
    lat, lng = extract_latitude_longitude(json)

    placesearch_url = generate_place_search_by_text_url(action, name, lat, lng, radius)
    print(placesearch_url)

    place_json = requests.post(placesearch_url).json()
    places = extract_place_name(place_json)
    return places


def set_location(chat_id, location):
    lat = location["latitude"]
    lng = location["longitude"]
    print("got location, latitude : " + str(lat) + ", longitude : " + str(lng))
    kernel.setPredicate(latitude_KEY, lat, chat_id)
    kernel.setPredicate(LONGITUDE_KEY, lng, chat_id)


def clear_session(chat_id):
    kernel.setPredicate(ACTION_KEY, "", chat_id)
    kernel.setPredicate(NAME_KEY, "", chat_id)
    kernel.setPredicate(LOCATION_KEY, "", chat_id)
    kernel.setPredicate(RADIUS_KEY, "", chat_id)
    kernel.setPredicate(latitude_KEY, "", chat_id)
    kernel.setPredicate(LONGITUDE_KEY, "", chat_id)


def answer(chat_id, content_type, message):
    response = ""
    if content_type == "text":
        response = kernel.respond(message, chat_id)
    elif content_type == "location":
        set_location(chat_id, message)
        return kernel.respond(ASK_FOR_RADIUS, chat_id)

    action = kernel.getPredicate(ACTION_KEY, chat_id)
    name = kernel.getPredicate(NAME_KEY, chat_id)
    location = kernel.getPredicate(LOCATION_KEY, chat_id)
    radius = kernel.getPredicate(RADIUS_KEY, chat_id)
    lat = kernel.getPredicate(latitude_KEY, chat_id)
    lng = kernel.getPredicate(LONGITUDE_KEY, chat_id)
    log(action, name, location, radius, lat, lng)

    if action and name and location and radius:
        clear_session(chat_id)
        return query_place_by_text_search(action, name, location, radius)
    elif action and lat and lng and radius:
        clear_session(chat_id)
        return query_place_by_nearby(action, name, lat, lng, radius)
    elif response == message:
        print("unknown response for " + message)
        return UNKNOWN_RESPONSE
    else:
        return response


def debug():
    # Press CTRL-C to break this loop
    while True:
        action = kernel.getPredicate('ACTION', 123)
        name = kernel.getPredicate('NAME', 123)
        location = kernel.getPredicate('LOCATION', 123)
        radius = kernel.getPredicate('RADIUS', 123)
        log(action, name, location, radius)

        if action and name and location and radius:
            break
        else:
            print(kernel.respond(raw_input("Enter your message >> "), 123))

    print("spec is completed, will search " + name + " in " + location)

    geocode_url = generate_geocode_url(location)
    print(geocode_url)

    json = requests.post(geocode_url).json()
    lat, lng = extract_latitude_longitude(json)

    placesearch_url = generate_place_search_by_text_url(action, name, lat, lng, radius)
    print(placesearch_url)

    place_json = requests.post(placesearch_url).json()
    places = extract_place_name(place_json)
    print(places)

# debug()
