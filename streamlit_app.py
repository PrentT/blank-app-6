import streamlit as st
import requests
import json
import math

# Streamlit app configuration
st.set_page_config(page_title="Product Recommendations", layout="wide")

# App Title
st.title("Product Recommendations Viewer")

# User input for groupList
group_list = st.text_input("Enter a groupList (e.g., PB:cayman-wood-nightstand):", "PB:cayman-wood-nightstand")

# User input for OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

# API URL (replace with your actual API endpoint)
api_url = "https://www.uat3.potterybarn.com/svc/recommendation/v2/PB-USA/pages/"

# Make the API call if group_list is provided
if st.button("Get Recommendations"):
    try:
        # Making the API request
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        payload = {
            "groupList": [group_list],
            "rviCacheInvalid": False,
            "rviList": [],
            "cartList": [],
            "device": "desktop",
            "pageId": "COMPTEST",
            "purchasedList": [],
            "registryList": [],
            "searchList": [],
            "segment": "",
            "sflList": [],
            "suppressList": [],
            "variant": "Default",
            "zip": "55347"
        }

        # Expander to view the entire request for debugging purposes
        with st.expander("Show Request Details"):
            st.write("Request Headers:")
            st.json(headers)
            st.write("Request Payload:")
            st.json(payload)

        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Expander to view the entire response for debugging purposes
        with st.expander("Show API Response"):
            st.json(data)

        # Check if the response contains recommended products
        if "placements" in data and len(data["placements"]) > 0 and "products" in data["placements"][0]:
            products = data["placements"][0]["products"]

            # Store products for further enrichment
            enriched_products = products

            # Display products in groups of 6 (3 columns, 2 rows)
            num_products = len(enriched_products)
            num_groups = math.ceil(num_products / 6)

            for group_idx in range(num_groups):
                group_start = group_idx * 6
                group_end = min(group_start + 6, num_products)
                group_enriched_products = enriched_products[group_start:group_end]

                cols = st.columns(3)
                for idx, product in enumerate(group_enriched_products):
                    with cols[idx % 3]:
                        st.subheader(product["name"])
                        image_url = f"https://qark-images.pbimgs.com/pbimgs/qark/images/dp/wcm/{product['image']}"
                        st.image(image_url, width=300)

                        # Expander for additional product details
                        with st.expander("Show more details"):
                            price_set = product.get("priceSet", {})
                            low_price = price_set.get("lowSellingPrice", "N/A")
                            high_price = price_set.get("highSellingPrice", "N/A")
                            st.write("**Price Range**: ", f"${low_price} - ${high_price}")
                            st.write("**SKU**: ", product.get("id", "N/A"))
                            st.write("**URL**: ", f"https://www.potterybarn.com/{product.get('url', '')}")
                            st.write("**Available**: ", product.get("available", "N/A"))
                            st.write("**Rating**: ", product.get("rating", "N/A"))
                            st.write("**Other Data**: ", json.dumps(product, indent=2))
                # Draw a line between each group of 6 products
                st.markdown("---")
        else:
            st.warning("No products found in the response.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")

# Enrich the product data using ChatGPT if OpenAI API key is provided
if openai_api_key and 'products' in locals() and st.button("Enrich Product Data"):
    try:
        try:
            import openai
        except ModuleNotFoundError:
            st.error("OpenAI module not found. Please install it by running 'pip install openai'.")
            raise

        openai.api_key = openai_api_key
        enriched_products = []

        for product in products:
            product_data = {
                "name": product["name"],
                "description": product.get("description", ""),
                "category": product.get("superCategory", ""),
                "priceRange": f"${product.get('priceSet', {}).get('lowSellingPrice', 'N/A')} - ${product.get('priceSet', {}).get('highSellingPrice', 'N/A')}"
            }
            chatgpt_prompt = f"The following product is part of a home decor recommendation system for a bedroom. Analyze the product data and suggest the room type and additional styling categories or tags that would help group this product with others in a cohesive bedroom decor: {json.dumps(product_data)}"
            response = openai.Completion.create(
                engine="gpt-4",
                prompt=chatgpt_prompt,
                max_tokens=150
            )
            enriched_data = response.choices[0].text.strip()
            enriched_product = product.copy()
            enriched_product["enriched_data"] = enriched_data
            enriched_products.append(enriched_product)

        # Expander to view the entire enrichment request and response
        with st.expander("Show Enrichment Details"):
            st.write("Enrichment Prompt:")
            st.write(chatgpt_prompt)
            st.write("Enrichment Response:")
            st.json(enriched_data)

        # Update the enriched products list for display
        products = enriched_products

        # Display enriched products
        num_products = len(enriched_products)
        num_groups = math.ceil(num_products / 6)

        for group_idx in range(num_groups):
            group_start = group_idx * 6
            group_end = min(group_start + 6, num_products)
            group_products = enriched_products[group_start:group_end]

            cols = st.columns(3)
            for idx, product in enumerate(group_products):
                with cols[idx % 3]:
                    st.subheader(product["name"])
                    image_url = f"https://qark-images.pbimgs.com/pbimgs/qark/images/dp/wcm/{product['image']}"
                    st.image(image_url, width=300)

                    # Expander for additional product details
                    with st.expander("Show more details"):
                        price_set = product.get("priceSet", {})
                        low_price = price_set.get("lowSellingPrice", "N/A")
                        high_price = price_set.get("highSellingPrice", "N/A")
                        st.write("**Price Range**: ", f"${low_price} - ${high_price}")
                        st.write("**SKU**: ", product.get("id", "N/A"))
                        st.write("**URL**: ", f"https://www.potterybarn.com/{product.get('url', '')}")
                        st.write("**Available**: ", product.get("available", "N/A"))
                        st.write("**Rating**: ", product.get("rating", "N/A"))
                        st.write("**Enriched Data**: ", product.get("enriched_data", "N/A"))
                        st.write("**Other Data**: ", json.dumps(product, indent=2))
            # Draw a line between each group of 6 products
            st.markdown("---")
    except Exception as e:
        st.error(f"Error enriching data with ChatGPT: {e}")

# Styling (optional): Makes the app look cleaner
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Run the app with: streamlit run your_script_name.py
