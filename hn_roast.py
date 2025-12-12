import requests
import streamlit as st
from openai import OpenAI

# Configuration
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "tngtech/deepseek-r1t2-chimera:free"

def get_top_stories(limit=10):
    try:
        response = requests.get(HN_TOP_STORIES_URL)
        response.raise_for_status()
        story_ids = response.json()[:limit]
        
        stories = []
        for sid in story_ids:
            item_resp = requests.get(HN_ITEM_URL.format(sid))
            item_resp.raise_for_status()
            item = item_resp.json()
            
            title = item.get('title', 'No Title')
            url = item.get('url', 'No URL')
            
            stories.append({'title': title, 'url': url})
            
        return stories
    except Exception as e:
        st.error(f"Error fetching stories: {e}")
        return []

def get_roast(stories):
    if not stories:
        return "No stories using to roast."

    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )

    headlines_text = "\n".join([f"{i+1}. {s['title']} ({s['url']})" for i, s in enumerate(stories)])

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a sarcastic tech investor. Look at these headlines and tell me which ONE is overhyped and why."
                },
                {
                    "role": "user",
                    "content": headlines_text
                }
            ],
            timeout=60
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI: {e}"

# Streamlit UI
st.title("Harsha's AI Tech Oracle")

if st.button("Analyze the News"):
    with st.spinner('Fetching top 10 stories from Hacker News...'):
        top_stories = get_top_stories(10)
    
    if top_stories:
        st.subheader("Top Headlines")
        for i, story in enumerate(top_stories, 1):
            st.write(f"**{i}.** [{story['title']}]({story['url']})")
        
        with st.spinner('Consulting the Oracle...'):
            roast = get_roast(top_stories)
            
        st.subheader("The Oracle Speaks")
        st.success(roast)
