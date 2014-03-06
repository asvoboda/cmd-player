import json


env_file = "env.json"


def save(file, environment):
    f = open(file, 'w')
    f.write(json.dumps(environment))
    f.close()


def load_json(file):
    with open(file) as json_file:
        try:
            json_data = json.load(json_file)
        except ValueError:
            print("Error parsing environment file!")
            return {}
        return json_data


def load_definition():
    file = "info.json"
    return load_json(file)


def load_environment():
    file = env_file
    try:
        env = load_json(file)
    except IOError:
        f = open(file, 'w')
        f.close()
        env = {}
    return env


def wizard(environment):
    new_definition = environment
    for key, value in environment.items():
        if not value:
            # Fix Python 2.x. raw_input -> input breaking change
            try: input = raw_input
            except NameError: pass
            new_value = input("Enter value for %s: " % key)
            new_definition[key] = new_value
    return new_definition


def get_environment():
    definition = load_definition()
    environment = load_environment()
    definition.update(environment)

    updated_environment = wizard(definition)
    save(env_file, updated_environment)

    return updated_environment

print(get_environment())
