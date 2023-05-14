import json
import keyboards_

main = 'Instruction\n' + \
    '/cats to get picture or gif with cat\n' + \
    '/Write_location to ask weather in location which you want\n' + \
    f'Press button "{json.loads(keyboards_.button_location.as_json())["text"]}" to see weather ' +  \
    'in your own location(you also can drop custom location)\n' + \
    '/cancel to return in /start\n' + \
    '/stop to stop bot'

sorry_by_cats = "Sorry, i can't find a cats."

wrong_location = "Sorry, I couldn't find weather information for {location}.\n" + \
    "Please try again."
