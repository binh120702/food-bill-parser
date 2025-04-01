import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

from ultils import extract_food_bills, get_client
from good_list import GoodsList
import pandas as pd
import time
from threading import Thread

import os
from dotenv import load_dotenv

# Streamlit page title
st.set_page_config(
    page_title="Food Bill Parser",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Pisan food bill parser. :3!"
    }
)

@st.cache_resource
def get_goods_list():
    return GoodsList()

class WorkerThread(Thread):
    def __init__(self, handle_task, bill_text, client, target):
        super().__init__()
        self.handle_task = handle_task
        self.bill_text = bill_text
        self.client = client
        self.return_value = None
        self.target = target
        
    def run(self):
        start_time = time.time()
        
        with self.target.status("Parsing bill..."):
            self.handle_task(self.bill_text, self.client)
            end_time = time.time()
            self.target.write(f"Task completed in {end_time - start_time:.2f} seconds!")

def parse_and_add_data(bill_text, client):
    parsed_goods_list = extract_food_bills(bill_text, client)
    
    goods_list = get_goods_list()
    goods_list.add_a_goods_list(parsed_goods_list)
    return True

def main():

    st.header("🍔 Pi Food Bill Parser")
    # Initialize session state for the bill queue
    if 'bill_queue' not in st.session_state:
        st.session_state.bill_queue = []
    if 'add_bill_to_queue' not in st.session_state:
        st.session_state.add_bill_to_queue = lambda bill_text: st.session_state.bill_queue.append(bill_text)
    
    # if key in dotenv, load it
    load_dotenv()
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        st.session_state["OPENAI_API_KEY"] = env_key
    
    with st.sidebar:
        key = st.text_input("OpenAI API Key", type="password")
        if key:
            st.session_state["OPENAI_API_KEY"] = key
    
    col1, col2 = st.columns(2)
    # Two parts: add bills to the queue and then a button to parse them
    # Text area for pasting the bill text
    
    # Button to parse the bill text
    with col2:
        if st.button("Parse Bill(s)"):
            if not "OPENAI_API_KEY" in st.session_state:
                st.error("Please enter your OpenAI API key.")
                return
            if len(st.session_state.bill_queue) > 0:
                try:
                    threads = []
                    for bill in st.session_state.bill_queue:
                        client = get_client(api_key=st.session_state["OPENAI_API_KEY"])
                        worker_thread = WorkerThread(parse_and_add_data, bill, client, st.container())
                        threads.append(worker_thread)
                        
                    for thread in threads:
                        add_script_run_ctx(thread, get_script_run_ctx())
                        thread.start()
                    for thread in threads:
                        thread.join()
                    
                    # Clear the queue after processing
                    st.session_state.bill_queue.clear()
                    st.write("All bills have been parsed and added to the list!")
                    
                except Exception as e:
                    st.error(f"An error occurred while parsing the bill: {e}")
            else:
                st.warning("Please paste the bill text before parsing.")
    
    with col1:
        bill_text = st.text_area("Paste your bill text here:", height=300)

        st.write("You can paste the bill text here. Make sure to format it correctly.")
    
        if st.button("Add Bill to Queue"):
            if bill_text:
                st.session_state.add_bill_to_queue(bill_text)
                st.toast("Bill added to queue!")
            else:
                st.warning("Please paste the bill text before adding to queue.")
        
        st.write(f"Current bills in queue: {len(st.session_state.bill_queue)}")
    
    
    
    
    st.subheader("Parsed Bill Data:")
    
    goods_list = get_goods_list()
    
    fields = ['datetime', 'quantity', 'price', 'name', 'person_in_charge']
    df = pd.DataFrame([{fn : getattr(good, fn) for fn in fields} for good in goods_list.goods])
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=False,
        num_rows="dynamic",
        column_config={
            "person_in_charge": st.column_config.SelectboxColumn(
                "Person in charge?",
                options=["shared", "me", 'steve'],
                help="Check if the goods are shared.",
            ),
        }
    )
     
    # calculate the total price of the goods for each participant: shared, me, steve
    if st.button("Calculate Total"):
        total_price = edited_df.groupby('person_in_charge')['price'].sum()
        st.write("Total price for each participant:")
        st.write(total_price)
    if st.button("List all goods by participant"):
        total_price = edited_df.groupby('person_in_charge')['name'].apply(lambda x: '___'.join(x)).reset_index()
        st.write("List of all goods by participant:")
        st.write(total_price)

if __name__ == "__main__":
    main()