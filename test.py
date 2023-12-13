import requests

def personalise_linkedin_connection_request(first_name, linkedin_url, product_context, my_company, relevance_api_key):
    """
    Personalize LinkedIn Connection Request based on user posts.

    Parameters:
    first_name (str): The first name of your prospect.
    linkedin_url (str): LinkedIn URL of your prospect.
    product_context (str): More context equals better tailored connection requests.
    my_company (str): The name of your company, whose products and services you're looking to sell.
    relevance_api_key (str): API key for authentication.

    Returns:
    dict: The response data from the server.
    """
    # API endpoint URL
    api_url = "https://api-d7b62b.stack.tryrelevance.com/latest/studios/26787101-7a5a-4fcf-becf-656217ee0471/trigger_llm_friendly"

    # Headers for authentication
    headers = {
        "Authorization": relevance_api_key
    }

    # Request body
    body = {
        "first_name": first_name,
        "linkedin_url": linkedin_url,
        "product_context": product_context,
        "my_company": my_company
    }

    # Make the POST request with headers and JSON body
    response = requests.post(api_url, json=body, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        response = response.json()
        output = response['output']['personalised_opening_line']
        return f"Personalised Message: {output}"
    else:
        return {"error": "Request failed", "status_code": response.status_code}
    

print(personalise_linkedin_connection_request(first_name="Sulieman", 
                                        linkedin_url="https://www.linkedin.com/in/sulalramahi/", 
                                        product_context= "AI SalesMate, an innovative outbound sales copilot designed to enhance customer engagement and streamline sales processes.",
                                        my_company = "NovaTech Solutions",
                                        relevance_api_key= "c716cd9c875d-4599-82d1-cf9e8f9fa22c:sk-MDMyYWU1OGMtZGQ1NC00OWY2LTlmYjMtNDI2YTAzZTU3Y2Ni"
                                        ))
