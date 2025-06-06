import os
import json
import pandas as pd

from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

#setup api
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY") # lay gemini api key
genai.configure(api_key=google_api_key)

#load config ban đầu

# Add encoding='utf-8' when opening the config.json file
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    functions = config.get('function', 'giới thiệu nhà hàng ')
    initial_bot_message = config.get('initital_bot_mesage', 'Xin chào bạn cần hỗ trợ gì')


#load nội dung menu
menu_df = pd.read_csv("menu.csv", index_col=[0])

#Tạo LLM
model = genai.GenerativeModel("gemini-1.5-flash",
                              system_instruction=f"""
                              Bạn là trợ lý AI tên CloudBot của một nhà hàng Michellin ẩm thực Việt Nam tại Mỹ. Có rất nhiều khách muốn hỏi thêm thông tin về các món trong menu để đặt bàn. Để có thể giải đáp cho khách hàng 24/7 và tiết kiệm chi phí thuê nhân sự, bạn muốn lập trình một ứng dụng trả lời các câu hỏi thường gặp từ khách hàng.
                              1. Giới thiệu nhà hàng : Nhà hàng có tên là Ngọc Cuisine lập bởi người Việt, ở địa chỉ 329 Scottmouth, Georgia, USA
                              2. Giới thiệu menu của nhà hàng, gồm các món: {', '.join(menu_df['name'].to_list())}.
                              Ngoài hai chức năng trên, bạn không hỗ trợ chức năng nào khác. Đối với các câu hỏi ngoài chức năng mà bạn hỗ trợ, trả lời bằng 'Tôi đang không hỗ trợ chức năng này. Xin liên hệ nhân viên nhà hàng qua hotline 318-237-3870 để được trợ giúp.'
                              Hãy có thái độ thân thiện và lịch sự khi nói chuyện với khác hàng, vì khách hàng là thượng đế.
                              """)

#Hàm trò chuyện củ chatbot
def restaurant_chatbot():
    st.title("Restaurant Assistant Cloudbot")
    st.write("Xin chào tôi là trợ lý của nhà hàng Ngọc cuisine. Bạn cần trợ giúp gì ")
    st.write("Bạn có thể hỏi tôi về menu món ăn, giờ mở cửa,...")

    #Chưa lịch sửa trò chuyện
    if 'history_log' not in st.session_state:
        st.session_state.history_log = [
            {"role": "assistant", "content" : initial_bot_message}
        ]
    #Nếu đã có lịch sửa trò chuyện
    for message in st.session_state.history_log:
        if message["role"] != "system" :
            with st.chat_message(message["role"]):
                st.write(message["content"])
    #khi người dùng nhập promt

    if prompt := st.chat_input("Nhập yêu cầu của bạn tại đây...."):
        with st.chat_message("user"):
            st.write(prompt)
        #thêm vào log
        st.session_state.history_log.append({"role":"user","content":prompt})

        #LLM tạo câu trả lời
        response = model.generate_content(prompt)
        bot_reply = response.text

        with st.chat_message("assistant"):
            st.write(bot_reply)
            st.write(st.session_state.history_log)
        #thêm vào log
        st.session_state.history_log.append({"role":"assistant","content": bot_reply})

if __name__ == "__main__" :
    restaurant_chatbot()