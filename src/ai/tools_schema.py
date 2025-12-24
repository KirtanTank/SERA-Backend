TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current system time",
            "parameters": {
                "type": "object",
                "properties": {}
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_calendar_events",
            "description": "List upcoming Google Calendar events",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
  "type": "function",
  "function": {
    "name": "find_places",
    "description": "Find nearby places using Google Maps",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "latitude,longitude"
        },
        "type": {
          "type": "string",
          "description": "Place type (restaurant, cafe, gym)"
        }
      },
      "required": ["location"]
    }
  }
},
{
  "type": "function",
  "function": {
    "name": "send_email",
    "description": "Send an email to a recipient",
    "parameters": {
      "type": "object",
      "properties": {
        "to": { "type": "string" },
        "subject": { "type": "string" },
        "body": { "type": "string" }
      },
      "required": ["to", "subject", "body"]
    }
  }
}


]
