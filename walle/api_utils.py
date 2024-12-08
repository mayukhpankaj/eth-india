import streamlit as st
from llm import process_crypto_query

def get_api_response(question, session_id, model):

    response = process_crypto_query(question)
    return {"answer":response}


