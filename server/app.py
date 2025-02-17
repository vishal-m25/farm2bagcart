import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Tool
from vertexai.preview.generative_models import grounding
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
from pymongo import MongoClient

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Initialize Vertex AI Chatbot
def initialize_vertex_ai(project_id, datastore):
    vertexai.init(project=project_id, location="us-central1")
    tools = [
        Tool.from_retrieval(
            retrieval=grounding.Retrieval(
                source=grounding.VertexAISearch(datastore=datastore),
            )
        )
    ]
    model = GenerativeModel(
        "gemini-1.0-pro-002",
        tools=tools,
    )
    return model.start_chat()

# Configuration for generation and safety
generation_config = {
    "max_output_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
}

safety_settings = [
    SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
]

pre_prompt = """
You are Farm2Bag human assistant, and you ONLY answer using the provided data and information from www.farm2bag.com. Do not access or use any other external websites or data sources.

Your primary function is to answer user questions related to Farm2Bag's products, services, and operations, including adding items to a virtual cart. If a question or request cannot be answered using the provided information and www.farm2bag.com, respond with "Sorry, that's not available."

When answering questions:
Do not answer to any level of the valgur words in any of the language.
there is no item water in the given data so respond with "product not available"
* **Be Human-Like:** Use a conversational and friendly tone. Avoid overly technical jargon unless the user specifically requests it.
* **Tabular Format:** If a question lends itself to a tabular answer, present the information in a clear and visually appealing table. Consider using markdown for formatting tables.
* **Language Matching:** Respond in the same language the user is using.
* **Strict Grounding:** Absolutely no responses should be generated from information outside of what is explicitly provided or available on www.farm2bag.com. Do not speculate or make assumptions. If you are unsure, say "Sorry, that's not available."
* **Markdown format:** use markdown format in the response to improve attractiveness
* **product clarity:** *if the given item or product name is not present in the given document. respond with "product is not available"*. in case if the product or item is general name, list the related products.
**Adding to Cart:**

 only When you are requested to add an item to their cart, respond only with a JSON object containing the following, *extracted only* from the provided data:
```json
{
  "name": "Product Name",
  "price": Price(float),
  "measuring_base_value": "e.g., 1 kg, 500g, 1 dozen",
}
"""

# Initialize chat session
project_id = "hardy-mercury-449710-f9"
datastore = "projects/hardy-mercury-449710-f9/locations/global/collections/default_collection/dataStores/farm-store_1738555123738"
chat_session = initialize_vertex_ai(project_id, datastore)


client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if needed
db = client["farm2bag"]
cart_collection = db["cart"]

# Chat History & Cart Storage
chat_history = []
cart = []  
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    cart.append({
        "name": data.get("name"),
        "price": data.get("price"),
        "quantity": data.get("quantity"),
    })

    return jsonify({"response": "Item added to cart", "cart": cart})

@app.route("/view_cart", methods=["GET"])
def view_cart():
    return jsonify({"cart": cart})
# Sample product list

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").strip().lower()

    if not user_input:
        return jsonify({"response": "Please enter a valid message."})
    
    chat_history.append({"role": "user", "message": user_input})

    try:
        product = None
        full_chat_history = pre_prompt + "\n" + "\n".join(
            [f"{entry['role']}: {entry['message']}" for entry in chat_history]
        )

        response_text = chat_session.send_message(
            [full_chat_history],
            generation_config=generation_config,
            safety_settings=safety_settings,
        ).text
        match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
       # Extract JSON from the response.  Handle cases where it might not exist.
        if not match:
            match = re.search(r'\{.*?\}', response_text, re.DOTALL)

        if match:
            try:
                product_data = json.loads(match.group(1))
                product = {
                    "name": product_data.get("name"),
                    "price": product_data.get("price"),
                    "measuring_base_value": product_data.get("measuring_base_value"),
                }
                print(product)
                response_text=""
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Problematic JSON String: {match.group(1)}")  # Debugging
                # Handle the error gracefully, perhaps return a message to the user.
                response_text += "\nError: Could not retrieve product details."
                product = None # Set product to None since parsing failed
        elif "Sorry, that's not available" in response_text:
            product = None  # Explicitly set to None if not available
        else:
          # Handle the case where no JSON is found but the item may be available.
          # Perhaps extract the product details using a different method or return
          # a message asking the user to be more specific.
          print("Warning: No JSON found in response. Check the model prompt and data.")
          # Consider adding a message to the user:
          chat_history.append({"role": "assistant", "message": response_text})
          product = None

        return jsonify({"response": response_text, "product": product})

    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
