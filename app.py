from keras.models import load_model 
import streamlit as st
from PIL import Image
import numpy as np
import requests
import time
from streamlit_lottie import st_lottie
import re

def identify_vegetable(image_array):
    model = load_model("keras_Model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()

    img = Image.fromarray(image_array)
    img = img.convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.uint8)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    prediction = model.predict(img_array)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    return class_name[2:].lower()

def get_recipe_recommendations(vegetable, max_recipes=10):
    api_key = ""  
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": vegetable,
        "apiKey": api_key,
        "number": max_recipes
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipes = response.json()
        detailed_recipes = []
        for recipe in recipes:
            recipe_id = recipe["id"]
            recipe_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
            recipe_params = {
                "apiKey": api_key
            }
            recipe_response = requests.get(recipe_url, params=recipe_params)
            if recipe_response.status_code == 200:
                recipe_info = recipe_response.json()
                detailed_recipes.append(recipe_info)
                time.sleep(3)
            else:
                print("Failed to retrieve recipe information for ID:", recipe_id)
        return detailed_recipes
    else:
        print("Error occurred while retrieving recipe recommendations:", response.status_code)
        return None

def main():
    st.set_page_config(
        page_title="What the Veggie",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    st.markdown(
        """
        <style>
        body {
            background-color: white;
        }
        .title-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 32px;
            font-weight: bold;
            margin-right: 10px;
        }
        .animation-container {
            display: flex;
            align-items: center;
        }
        .search-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    main_animation_url = "https://assets6.lottiefiles.com/packages/lf20_EY6Lg2udYI.json"
    main_lottie = st_lottie(main_animation_url, height=300)

    st.markdown(
        "<div class='title-container'>"
        "<h1 class='title'>What the Veggie</h1>"
        "</div>"
        "<div class='description'>"
        "Introducing What The Veggie, the app that'll make your veggies spill the beans! Upload an image of those mysterious greens, and watch as our sneaky AI uncovers their true identities. From hiding in your salads to masquerading as side dishes, no veggie can escape our veggie-spying powers. Get ready for a hilarious veggie revelation like never before! So come on, don't be shy and let us see those beautiful veggies you've got!"
        "</div>"
        "<div class='animation-container'>"
        "<div id='animation-main'></div>"
        "</div>",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        
        img_array = np.array(img)
        vegetable = identify_vegetable(img_array)

        if vegetable:
            
            with st.spinner("Fetching recipe recommendations..."):
               
                loading_animation_url = "https://assets9.lottiefiles.com/packages/lf20_jbt4j3ea.json"
                loading_lottie = st_lottie(loading_animation_url, height=400)

                
                recipes = get_recipe_recommendations(vegetable, max_recipes=10)

            
            loading_lottie = None

            if recipes:
                
                for i, recipe in enumerate(recipes):
                    recipe_name = recipe["title"]
                    cleaned_name = re.sub(r'\W+', ' ', recipe_name)
                    recipes[i]["title"] = cleaned_name

                    with st.expander(cleaned_name):
                        st.subheader(recipe_name)
                        st.image(recipe["image"], use_column_width=True)
                        st.markdown("Instructions:")
                        st.write(recipe["instructions"])
                        st.markdown("---")
            else:
                st.warning("Failed to retrieve recipe recommendations.")
        else:
            st.error("Failed to identify the vegetable.")

if __name__ == "__main__":
    main()