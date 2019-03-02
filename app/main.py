import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.
    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#B1FFCB"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)

    x = data["you"]["body"][0]["x"]
    y = data["you"]["body"][0]["y"]
    tempDirectionX = "right"
    revDirectionX = "left"
    tempDirectionY = "down"
    revDirectionY = "up"

    nearby = findNearby(data, x, y)

    foodList = data["board"]["food"]
    if len(foodList) == 0: #if no food
        tail = data["you"]["body"][len(data["you"]["body"]) - 1]

        if x > tail["x"]:
            tempDirectionX = "left"
            revDirectionX = "right"
        if y > tail["y"]:
            tempDirectionY = "up"
            revDirectionY = "down"

        if abs(x - tail["x"]) > abs(y - tail["y"]):
            if nearby[tempDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                direction = tempDirectionX
            else:
                if nearby[tempDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                    direction = tempDirectionY
                elif nearby[revDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                    direction = revDirectionY
                else:
                    direction = revDirectionX
        else:
            if nearby[tempDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                direction = tempDirectionY
            else:
                if nearby[tempDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                    direction = tempDirectionX
                elif nearby[revDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                    direction = revDirectionX
                else:
                    direction = revDirectionY

    #elif: #if health = x
    #elif: #if other snake can be trapped
    else: #if food
        nearestFood = foodList[0]
        for i in range(1,len(foodList)):
            if (abs(x - foodList[i]["x"]) + abs(y - foodList[i]["y"]) < abs(x - nearestFood["x"]) + abs(y - nearestFood["y"])):
                nearestFood = foodList[i]

        if x > nearestFood["x"]:
            tempDirectionX = "left"
            revDirectionX = "right"
        if y > nearestFood["y"]:
            tempDirectionY = "up"
            revDirectionY = "down"

        if abs(x - nearestFood["x"]) > abs(y - nearestFood["y"]):
            if nearby[tempDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                direction = tempDirectionX
            else:
                if nearby[tempDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                    direction = tempDirectionY
                elif nearby[revDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                    direction = revDirectionY
                else:
                    direction = revDirectionX
        else:
            if nearby[tempDirectionY] == "open" or nearby[tempDirectionY] == "your-snake-tail":
                direction = tempDirectionY
            else:
                if nearby[tempDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                    direction = tempDirectionX
                elif nearby[revDirectionX] == "open" or nearby[tempDirectionX] == "your-snake-tail":
                    direction = revDirectionX
                else:
                    direction = revDirectionY

    return move_response(direction)

def findNearby(data, x, y):
    nearby = {"up": "open", "down": "open", "left": "open", "right": "open"}
    #wall, snake-head, snake-tail, snake, your-snake, your-snake-tail
    if y == 0:
        nearby["up"] = "wall"
    elif y == data["board"]["width"] - 1:
        nearby["down"] = "wall"
    if x == 0:
        nearby["left"] = "wall"
    elif x == data["board"]["height"] - 1:
        nearby["right"] = "wall"

    yourBody = data["you"]["body"]
    for i in range(0 , len(yourBody) - 1):
        bodyX = yourBody[i]["x"]
        bodyY = yourBody[i]["y"]
        if bodyX - 1 == x:
            if i == len(yourBody) - 1:
                nearby["right"] = "your-snake-tail"
            else:
                nearby["right"] = "your-snake"
        elif bodyX + 1 == x:
            if i == len(yourBody) - 1:
                nearby["left"] = "your-snake-tail"
            else:
                nearby["left"] = "your-snake"
        if bodyY - 1 == y:
            if i == len(yourBody) - 1:
                nearby["down"] = "your-snake-tail"
            else:
                nearby["down"] = "your-snake"
        elif bodyY + 1 == y:
            if i == len(yourBody) - 1:
                nearby["up"] = "your-snake-tail"
            else:
                nearby["up"] = "your-snake"

    snakes = data["board"]["snakes"]
    for i in range(0, len(snakes) - 1):
        body = snakes[i]["body"]
        for i in range(0 , len(body) - 1):
            bodyX = body[i]["x"]
            bodyY = body[i]["y"]
            if bodyX - 1 == x:
                direction = "right"
                if i == 0:
                    nearby[direction] = "snake-head"
                elif i == len(yourBody) - 1:
                    nearby[direction] = "snake-tail"
                else:
                    nearby[direction] = "snake"
            elif bodyX + 1 == x:
                direction = "left"
                if i == 0:
                    nearby[direction] = "snake-head"
                elif i == len(yourBody) - 1:
                    nearby[direction] = "snake-tail"
                else:
                    nearby[direction] = "snake"
            if bodyY - 1 == y:
                direction = "down"
                if i == 0:
                    nearby[direction] = "snake-head"
                elif i == len(yourBody) - 1:
                    nearby[direction] = "snake-tail"
                else:
                    nearby[direction] = "snake"
            elif bodyY + 1 == y:
                direction = "up"
                if i == 0:
                    nearby[direction] = "snake-head"
                elif i == len(yourBody) - 1:
                    nearby[direction] = "snake-tail"
                else:
                    nearby[direction] = "snake"
    return nearby




@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
