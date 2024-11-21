import streamlit as st
import requests
import json

# Streamlit app configuration
st.set_page_config(page_title="Product Recommendations", layout="wide")

# App Title
st.title("Product Recommendations Viewer")

# User input for groupList
group_list = st.text_input("Enter a groupList (e.g., PB:cayman-wood-nightstand):", "PB:cayman-wood-nightstand")

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
            "pageId": "PIP",
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

            # Display each product
            for product in products:
                # Product name and image
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
        else:
            st.warning("No products found in the response.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")

# Styling (optional): Makes the app look cleaner
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Run the app with: streamlit run your_script_name.py
