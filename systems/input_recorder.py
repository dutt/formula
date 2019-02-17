from components.events import KeyEvent, MouseEvent, InputType

events = []


def add_key_event(e):
    global events
    events.append(e)


def add_mouse_event(e):
    global events
    events.append(e)


def serialize_input(eventlist):
    retr = []
    for event in eventlist:
        retr.append(event.serialize())
    return retr


def deserialize_input(eventlist):
    retr = []
    for event in eventlist:
        if event["type"] == InputType.KEY.name:
            retr.append(KeyEvent.deserialize(event))
        elif event["type"] == InputType.MOUSE.name:
            retr.append(MouseEvent.deserialize(event))
    return retr
