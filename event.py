import datetime
import json


class Event:
    """
        Event class
        An event is represented by its date and a title.
        It has other attributes like:
        - description
        - imageLink
        - facebookLink
        - eventbriteLink
        - instagramLink
    """
    title = 'A title'
    description = 'Text'
    date = datetime.datetime(1943, 3, 13)  # year, month, day
    imageLink = str()  # optional
    facebookLink = str()  # optional
    eventbriteLink = str()  # optional
    instagramLink = str()  # optional

    def __init__(self, title, description, date, imageLink=None, facebookLink=None, eventbriteLink=None,
                 instagramLink=None):
        self.title = title
        self.description = description
        self.date = date
        self.imageLink = imageLink
        self.facebookLink = facebookLink
        self.eventbriteLink = eventbriteLink
        self.instagramLink = instagramLink


def load_events(langString):
    """
    Load from events.json the list of events with the same language
    of the one specified by the langString field
    """
    eventList = []
    # try catch
    try:
        with open("events.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for x in data:
                e = Event(
                    title=x["Title"],
                    date=datetime.datetime.strptime(x["Datetime"], "%Y %m %d"),
                    description=x["Description"],
                    imageLink=x["Image Link"],
                    eventbriteLink=x["Eventbrite Link"],
                    facebookLink=x["Facebook Link"],
                    instagramLink=x["Instagram Link"]
                )
                if x["Lang"] == langString:
                    eventList.append(e)
    except Exception as e:
        print("This error occurs: " + str(e))
        # If an error occurs I erase the eventList
        eventList = []
    return eventList
