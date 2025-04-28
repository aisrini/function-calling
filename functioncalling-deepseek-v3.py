import requests
import json

# Step 1: Define the function that the model can call
def get_weather(location: str) -> str:
    """
    Dummy function to get weather for a given location.
    In a real scenario, this might call an external weather API.
    """
    print(f"[Function] Fetching weather for {location}...")  # debug log
    # Simulate a result (in real life, you'd use `requests` to an API here)
    # Note: the return value must be a JSON string
    return json.dumps({
        "temperature": "25",
        "condition": "Sunny"
    }) # pretend this came from a weather API



# Step 2: Define the function schema to pass to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetch the current weather for a specified city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city for which to get the current weather"
                    }
                },
                "required": ["location"]
            }
        }
    }
]


# API endpoint and headers (using Fireworks AI's inference endpoint)
api_url = "https://api.fireworks.ai/inference/v1/chat/completions"
headers = {
    "Authorization": "<API_KEY>",
    "Content-Type": "application/json"
}

# The chat messages for the model
messages = [
    {"role": "user", "content": "What's the weather in London today?"}
]

# Construct the payload with model, messages, and function definitions
payload = {
    "model": "accounts/fireworks/models/deepseek-v3",  # DeepSeek v3 model ID on Fireworks
    "messages": messages,
    "tools": tools  
}

print("[Request] Sending prompt to DeepSeek v3...")
response = requests.post(api_url, headers=headers, json=payload)
result = response.json()
print("result: ", result)


# Step 3: Handle the model's tool call response
if result["choices"][0]["message"].get("tool_calls"):
    func_call = result["choices"][0]["message"]["tool_calls"]
    function_name = func_call[0]["function"]["name"]

    arguments = json.loads(func_call[0]["function"].get("arguments", "{}"))
    print(f"[Model] Tool call requested: {function_name} with arguments {arguments}")
    
    messages.append(result["choices"][0]["message"])

    # Execute the requested function if it matches one we have
    if function_name == "get_weather":
        func_result = get_weather(arguments.get("location", ""))

        # Append the function result to the message history for the model
        messages.append({
            "role": "tool",  # 'tool' role indicates a function result
            "tool_call_id": func_call[0]["id"],
            "content": func_result
        })
        print("messages after tool call: ", messages)

# Now send the updated conversation (with the function result) back to the model
followup_payload = {
    "model": "accounts/fireworks/models/deepseek-v3",
    "messages": messages,
    "tools": tools
}
print("followup_payload: ", followup_payload)
print("[Request] Sending tool result back to model...")
final_resp = requests.post(api_url, headers=headers, json=followup_payload)
final_result = final_resp.json()
print("final_result: ", final_result)
answer = final_result["choices"][0]["message"]["content"]
print("[Model] Final answer:", answer)
