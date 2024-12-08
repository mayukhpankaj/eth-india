from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from typing import Optional
import json
import os
from dotenv import load_dotenv
load_dotenv()


api_key = os.getenv('OPENAI_API_KEY')



# Define different possible schemas
intent_only_schema = [
    ResponseSchema(name="Intent", description="The intent of the query - either SEND or GET")
]

full_transaction_schema = [
    ResponseSchema(name="Intent", description="The intent of the query - either SEND or GET"),
    ResponseSchema(name="Value", description="The numerical value to be transferred"),
    ResponseSchema(name="currency", description="The cryptocurrency symbol (e.g., BTC, ETH)"),
    ResponseSchema(name="To", description="The receiver's domain name")
]

# Create separate parsers for each schema
intent_parser = StructuredOutputParser.from_response_schemas(intent_only_schema)
transaction_parser = StructuredOutputParser.from_response_schemas(full_transaction_schema)


# Define the response schemas
response_schemas = [
    ResponseSchema(name="Intent", description="The intent of the query - either SEND or GET"),
    ResponseSchema(name="Value", description="The numerical value to be transferred"),
    ResponseSchema(name="currency", description="The cryptocurrency symbol (e.g., BTC, ETH)"),
    ResponseSchema(name="To", description="The receiver's domain name")
]

# Create the parser
parser = StructuredOutputParser.from_response_schemas(response_schemas)


def parse_with_multiple_schemas(response_text: str) -> dict:
    """
    Attempts to parse the response text using multiple schemas in order of preference.
    
    Args:
        response_text (str): The raw response from the LLM
        
    Returns:
        dict: Parsed response using the appropriate schema
    """
    try:
        # First try parsing with intent-only schema
        parsed = intent_parser.parse(response_text)
        
        # If it's a GET request, we're done
        if parsed["Intent"] == "GET":
            return {"Intent": "GET"}
            
        # For SEND, we need to validate the full schema
        if parsed["Intent"] == "SEND":
            # Try parsing with full transaction schema
            full_parsed = transaction_parser.parse(response_text)
            return {
                "Intent": "SEND",
                "Value": float(full_parsed["Value"]),
                "currency": full_parsed["currency"],
                "To": full_parsed["To"]
            }
            
    except Exception as e:
        print(f"Parsing error: {e}")
        return {"error": "Failed to parse response"}



# Create the system message with examples
system_template = """You are a crypto transaction query parser. Analyze the user's query and extract relevant information.

Examples:
Query: "SEND 1 ETH TO john.base.eth"
Response: {{"Intent": "SEND", "Value": 1, "currency": "ETH", "To": "john.base.eth"}}

Query: "Transfer 2 BTC to mary.base.eth"
Response: {{"Intent": "SEND", "Value": 2, "currency": "BTC", "To": "mary.base.eth"}}

Query: "What's my wallet balance"
Response: {{"Intent": "GET"}}

Query: "How much fund I have"
Response: {{"Intent": "GET"}}

Rules:
1. For SEND intents (including transfer, payment, dispense), extract Value, currency, and receiver domain
2. For GET intents (balance queries), only return the intent
3. Value must be a number
4. Currency must be a crypto symbol
5. Receiver must be a domain name

{format_instructions}
"""

# Create the prompt template
prompt = PromptTemplate(
    template=system_template + "\nQuery: {query}\nResponse: ",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

def process_crypto_query(query: str) -> dict:
    """
    Process a crypto-related query and extract relevant information.
    
    Args:
        query (str): The user's query string
        
    Returns:
        dict: Structured response containing Intent and optionally Value, currency, and To fields
    """
    # Generate the formatted prompt
    formatted_prompt = prompt.format(query=query)
    
    # Get response from LLM
    response = llm.predict(formatted_prompt)
    
    return parse_with_multiple_schemas(response)


# Example usage
# test_queries = [
#     "SEND 1 ETH TO john.base.eth",
#     "Transfer 2 BTC to mary.base.eth",
#     "What's my wallet balance",
#     "How much fund I have",
#     "Send 0.5 BTC to alice.crypto.eth"
# ]

# if __name__ == "__main__":
#     for query in test_queries:
#         result = process_crypto_query(query)
#         print(f"\nQuery: {query}")
#         print(f"Result: {json.dumps(result, indent=2)}")