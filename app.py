import streamlit as st
import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import plotly.express as px
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Aerosus Data Analyzer",
    page_icon="🛠️",
    layout="wide"
)

# --- NLTK Resource Check ---
@st.cache_resource
def ensure_nltk_resources():
    for resource in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource)

ensure_nltk_resources()

# --- Caching Data Loading and All Processing ---
@st.cache_data
def load_and_process_data():
    # (Data generation code is the same, collapsed for brevity)
    products_data = {
        'sku': ['AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004'],
        'product_name': ['Front Air Spring | Audi A8 D4', 'Rear Air Spring | Audi A8 D4', 'Front Shock Absorber | Audi Q7', 'Rear Shock Absorber | Audi Q7', 'Air Suspension Compressor | Audi', 'Air Suspension Compressor | BMW', 'Valve Block | Audi Q7', 'Front Air Strut | Mercedes S-Class W221', 'Rear Air Strut | Mercedes S-Class W221', 'Front Air Spring | BMW X5 E70', 'Air Suspension Compressor | Mercedes', 'Valve Block | Mercedes S-Class', 'Rear Air Strut | BMW 5 Series F07', 'Front Air Spring | Land Rover Range Rover L322', 'Air Suspension Compressor | Land Rover', 'Valve Block | BMW X5', 'Front Air Strut | Porsche Panamera', 'Rear Air Spring | Bentley Continental GT', 'Air Suspension Compressor | Porsche', 'Valve Block | Land Rover'],
        'category': ['Air Spring', 'Air Spring', 'Shock Absorber', 'Shock Absorber', 'Compressor', 'Compressor', 'Valve Block', 'Shock Absorber', 'Shock Absorber', 'Air Spring', 'Compressor', 'Valve Block', 'Shock Absorber', 'Air Spring', 'Compressor', 'Valve Block', 'Shock Absorber', 'Air Spring', 'Compressor', 'Valve Block'],
        'brand': ['Audi', 'Audi', 'Audi', 'Audi', 'Audi', 'BMW', 'Audi', 'Mercedes', 'Mercedes', 'BMW', 'Mercedes', 'Mercedes', 'BMW', 'Land Rover', 'Land Rover', 'BMW', 'Porsche', 'Bentley', 'Porsche', 'Land Rover']
    }
    products_df = pd.DataFrame(products_data)
    tickets_data = {
        'ticket_id': range(1001, 1121),
        'sku': ['AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004', 'AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004', 'AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004', 'AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004', 'AS-2801', 'AS-2802', 'AS-3011', 'AS-3012', 'AC-8100', 'AC-8200', 'VB-5001', 'SA-7850', 'SA-7851', 'AS-2803', 'AC-8300', 'VB-5002', 'SA-7900', 'AS-2804', 'AC-8400', 'VB-5003', 'SA-7950', 'AS-2805', 'AC-8500', 'VB-5004', 'SA-7850', 'AC-8200', 'AS-2803', 'AS-2801', 'SA-7950', 'AC-8400', 'VB-5001', 'SA-7900', 'AS-2804', 'VB-5004', 'SA-7850', 'AC-8200', 'AS-2803', 'AS-2801', 'SA-7950', 'AC-8400', 'VB-5001', 'SA-7900', 'AS-2804', 'VB-5004'],
        'description': ["The AS-2801 air spring for my Audi A8 is leaking air. Poor quality.", "Rear air spring AS-2802 makes a hissing sound.", "How do I install the AS-3011 shock absorber?", "The SA-3012 for my Q7 is fantastic! Great ride quality.", "My AC-8100 compressor is very noisy.", "The AC-8200 BMW compressor arrived with a cracked housing.", "The VB-5001 valve block is stuck open.", "My SA-7850 Mercedes strut is leaking oil.", "SA-7851 rear strut failed after just one week.", "The AS-2803 air spring for my X5 was dead on arrival.", "AC-8300 compressor is getting extremely hot.", "The VB-5002 valve block doesn't fit my S-Class. I need to return it.", "SA-7900 strut for my BMW 5 series is a perfect fit. 5 stars.", "The AS-2804 Range Rover spring is sagging.", "My AC-8400 Land Rover compressor is weak.", "The VB-5003 for my X5 has a wiring issue.", "SA-7950 Panamera strut has a horrible clunking noise.", "The AS-2805 Bentley spring is not holding pressure.", "The AC-8500 Porsche compressor is leaking.", "VB-5004 valve block fixed my suspension problem. Thanks!", "Great value for the AS-2801 air spring.", "The AS-2802 was easy to install on my Audi.", "The AS-3011 shock absorber is a quality part.", "My mechanic loves the AS-3012 for the Q7.", "Shipping for the AC-8100 was very slow.", "The AC-8200 compressor is powerful and quiet.", "The VB-5001 valve block was a perfect OEM replacement.", "My Mercedes S-Class rides like new with the SA-7850.", "The SA-7851 strut was a great price.", "My BMW X5 is level again thanks to the AS-2803.", "The AC-8300 is a fantastic compressor.", "The VB-5002 was easy to wire up.", "The SA-7900 provides a comfortable ride.", "My ENG-014 kit came with everything needed.", "The FLT-015 cabin filter is great.", "The EXH-016 muffler has a nice deep tone.", "LGT-017 tail lights were plug-and-play.", "My fuel economy improved with the ELEC-018 MAF.", "FUEL-019 injectors gave a noticeable power boost.", "All gaskets in the ENG-020 set were a perfect fit.", "The AS-2801 didn't last long. I want to return it.", "AS-2802 air spring has a slow leak.", "The AS-3011 ride is too harsh.", "AS-3012 is a cheap knockoff. I'm returning it.", "The AC-8100 compressor is burning out.", "AC-8200 is making a grinding noise.", "The VB-5001 is leaking from the fittings.", "My SA-7850 strut is defective.", "The SA-7851 failed and left me stranded.", "AS-2803 doesn't hold air overnight. Needs to be returned.", "The AC-8300 compressor failed after a month. Defective product.", "The threads on the VB-5002 are wrong. I need to return this.", "The SA-7900 is not as good as the original.", "The AS-2804 is a poor quality spring.", "AC-8400 compressor is not building enough pressure.", "The VB-5003 is faulty.", "My SA-7950 strut is noisy over bumps.", "The AS-2805 bag is torn. Clearly a defect.", "AC-8500 compressor doesn't work. Return needed.", "The VB-5004 is a cheap plastic part. I will be returning it.", "What is the warranty on the AS-2801?", "Do I need new bolts for the AS-2802?", "Is there a video for the AS-3011 install?", "What are the torque specs for the AS-3012?", "Is AC-8100 a direct replacement for my Audi?", "Do I need to program the car after installing the AC-8200?", "Is the VB-5001 easy to replace?", "Does the SA-7850 come with a new seal?", "What is the warranty on the SA-7851?", "Compatibility check for AS-2803 on a 2012 X5.", "Do you have a guide for the AC-8300 install?", "Are the VB-5002 fittings included?", "How much stiffer is the SA-7900 than stock?", "What is the service interval for the AS-2804?", "How often should I replace the AC-8400 relay?", "What's the diameter of the VB-5003 air lines?", "Is the SA-7950 for the left or right side?", "Question about AS-2805 pressure.", "Is the AC-8500 a twin-piston compressor?", "Does the VB-5004 include o-rings?", "AS-2801 arrived with a cracked top mount.", "The box for AS-2802 was damaged.", "My AS-3011 shock was missing from the order.", "AS-3012 arrived with scratches.", "The AC-8100 compressor was lost in shipping.", "The AC-8200 I received looks used. I am returning this.", "The VB-5001 airline fitting was bent.", "SA-7850 has a dent on the body.", "You sent the wrong SA-7851 strut. I need to return it.", "The AS-2803 air spring box was open.", "The AC-8300 compressor housing is cracked.", "VB-5002 was left in the rain by the courier.", "The SA-7900 has the wrong wiring connector.", "The AS-2804 kit is missing the o-ring.", "The AC-8400 is the wrong model for my Rover. Return.", "The VB-5003 was supposed to be new, but it's refurbished.", "SA-7950 is for the wrong model year Panamera. Returning it.", "You sent the wrong AS-2805. Please process a return.", "The AC-8500 is not the one I ordered. Initiating a return.", "The VB-5004 is for a different car. I have to return it.", "I love the AS-3012 kit! My Audi feels brand new.", "The AS-2802 air spring is a nightmare, so much noise.", "The AC-8100 is a piece of junk. Failed in a week.", "AC-8200 is the best money I've ever spent.", "The AS-2801 is decent for the price.", "The ride from the SA-7850 is perfect!", "SA-7851 is a perfect fit, very high quality.", "AS-2803 is a safety hazard, it collapsed while driving.", "AC-8300 pump left me stranded.", "The AS-2804 failed and cost me thousands in repairs.", "I'm very disappointed with the SA-7900 ride quality.", "Your customer service was amazing sorting out my AS-2802 issue.", "AC-8100 compressor is working great so far.", "The AC-8200 is giving me constant error codes.", "The AS-2801 was a small but noticeable improvement.", "The noise from the SA-7850 is giving me a headache.", "The SA-7851 was a pain to install.", "AS-2803 install was super easy.", "The AC-8300 works as advertised.", "I'm worried about the reliability of the AS-2804 kit."],
    }
    tickets_df = pd.DataFrame(tickets_data)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=730)
    date_range_for_sampling = pd.date_range(start=start_date, end=end_date)
    random_dates = date_range_for_sampling.to_series().sample(n=len(tickets_df), replace=True).sort_values()
    tickets_df['created_date'] = random_dates.values
    df = pd.merge(tickets_df, products_df, on='sku', how='left')
    def clean_text(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        return [word for word in tokens if word not in stop_words]
    df['cleaned_description'] = df['description'].apply(clean_text)
    def classify_ticket_topic(description):
        description = description.lower()
        if any(word in description for word in ['return', 'wrong', 'sent', 'returning', 'refund']): return 'Return'
        elif any(word in description for word in ['fail', 'broken', 'defective', 'leak', 'noise', 'cracked', 'sagging', 'weak', 'faulty', 'torn', 'dead on arrival']): return 'Defect'
        else: return 'Question'
    df['topic'] = df['description'].apply(classify_ticket_topic)
    return df

# --- Load the Data ---
df = load_and_process_data()

# --- Reusable Function for Topic Analysis Pages ---
def create_analysis_page(page_topic, dataframe):
    st.title(f"🔎 {page_topic} Analysis")
    topic_df = dataframe[dataframe['topic'] == page_topic]
    st.header(f"Filtered Results: {len(topic_df)} {page_topic} Tickets")
    total_topic_tickets = len(topic_df)
    total_tickets = len(dataframe)
    topic_percentage = total_topic_tickets / total_tickets * 100 if total_tickets > 0 else 0
    col1, col2 = st.columns(2)
    col1.metric(f"Total {page_topic} Tickets", f"{total_topic_tickets}")
    col2.metric(f"% of All Tickets in Filter", f"{topic_percentage:.1f}%")
    st.subheader(f"Top 5 Products with Most '{page_topic}' Tickets")
    if not topic_df.empty:
        top_products = topic_df['product_name'].value_counts().reset_index()
        top_products.columns = ['Product Name', f'Number of {page_topic}s']
        st.dataframe(top_products.head(5), use_container_width=True, hide_index=True)
    else:
        st.info(f"No '{page_topic}' tickets found for the selected filters.")
    st.subheader(f"Common Words in '{page_topic}' Tickets")
    if not topic_df.empty:
        topic_words = [word for tokens in topic_df['cleaned_description'] for word in tokens]
        word_counts = Counter(topic_words)
        pain_points_df = pd.DataFrame(word_counts.most_common(10), columns=['Word', 'Frequency'])
        st.dataframe(pain_points_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"No text to analyze for '{page_topic}' tickets.")
    with st.expander("View Raw Data for this Topic"):
        st.dataframe(topic_df)

# --- SIDEBAR ---
st.sidebar.title("Navigation")
page_options = ["Overall Dashboard", "Product Deep Dive", "Return Analysis", "Defect Analysis", "Question Analysis"]
page = st.sidebar.radio("Go to", page_options)

st.sidebar.header("Global Filter Options")
today = datetime.today().date()
min_data_date = df['created_date'].min().date()
start_date = st.sidebar.date_input("Start Date", value=min_data_date, min_value=min_data_date, max_value=today)
end_date = st.sidebar.date_input("End Date", value=today, min_value=min_data_date, max_value=today)
if start_date > end_date:
    st.sidebar.error("Error: End date must be after start date.")
    st.stop()

# ADDED BRAND FILTER BACK
brand_list = ['All Brands'] + sorted([str(b) for b in df['brand'].dropna().unique()])
selected_brand = st.sidebar.selectbox("Filter by Brand", brand_list)

# Apply global filters
df_selection = df[(df['created_date'].dt.date >= start_date) & (df['created_date'].dt.date <= end_date)]
if selected_brand != 'All Brands':
    df_selection = df_selection[df_selection['brand'] == selected_brand]

# --- PAGE ROUTING ---
if page == "Overall Dashboard":
    st.title("🛠️ Aerosus Data Analyzer")
    st.header(f"Filtered Results: {len(df_selection)} of {len(df)} Total Tickets")
    total_tickets = len(df_selection)
    if total_tickets > 0:
        defect_rate = len(df_selection[df_selection['topic'] == 'Defect']) / total_tickets * 100
        return_rate = len(df_selection[df_selection['topic'] == 'Return']) / total_tickets * 100
        question_rate = len(df_selection[df_selection['topic'] == 'Question']) / total_tickets * 100
    else:
        defect_rate, return_rate, question_rate = 0, 0, 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tickets", f"{total_tickets}")
    col2.metric("Defect Rate", f"{defect_rate:.1f}%")
    col3.metric("Return Rate", f"{return_rate:.1f}%")
    col4.metric("Question Rate", f"{question_rate:.1f}%")
    st.header("Problem Trends Over Time")
    if not df_selection.empty:
        df_selection.loc[:, 'month'] = df_selection['created_date'].dt.to_period('M').astype(str)
        monthly_analysis = df_selection.groupby('month').agg(
            Defect_Tickets=('topic', lambda x: (x == 'Defect').sum()),
            Return_Tickets=('topic', lambda x: (x == 'Return').sum())
        ).reset_index()
        fig_trends = px.line(
            monthly_analysis, x='month', y=['Defect_Tickets', 'Return_Tickets'],
            title="Defect & Return Tickets Per Month", labels={'value': 'Number of Tickets', 'month': 'Month'}
        )
        st.plotly_chart(fig_trends, use_container_width=True)

# NEW PRODUCT DEEP DIVE PAGE
elif page == "Product Deep Dive":
    st.title("🔎 Product Deep Dive Report")
    st.info("Use the **global brand filter** in the sidebar to narrow down the product list below.")
    
    products_in_selection = sorted(df_selection['product_name'].unique())
    if not products_in_selection:
        st.warning("No products available for the selected Brand and Date range.")
    else:

        product_to_analyze = st.selectbox("Select a Product to Analyze", options=products_in_selection)
        if product_to_analyze:
            product_df = df_selection[df_selection['product_name'] == product_to_analyze]
            st.subheader(f"Metrics for: {product_to_analyze}")
            
            total_prod_tickets = len(product_df)
            if total_prod_tickets > 0:
                defect_rate_prod = len(product_df[product_df['topic'] == 'Defect']) / total_prod_tickets * 100
                return_rate_prod = len(product_df[product_df['topic'] == 'Return']) / total_prod_tickets * 100
            else:
                defect_rate_prod, return_rate_prod = 0, 0

            col1p, col2p, col3p = st.columns(3)
            col1p.metric("Total Tickets for this Product", f"{total_prod_tickets}")
            col2p.metric("Defect Rate", f"{defect_rate_prod:.1f}%")
            col3p.metric("Return Rate", f"{return_rate_prod:.1f}%")

            st.subheader("Common Complaint Words (from Defect & Return tickets)")
            problem_df = product_df[product_df['topic'].isin(['Defect', 'Return'])]
            if not problem_df.empty:
                problem_words = [word for tokens in problem_df['cleaned_description'] for word in tokens]
                pain_point_counts = Counter(problem_words)
                pain_points_df = pd.DataFrame(pain_point_counts.most_common(5), columns=['Complaint Word', 'Frequency'])
                st.dataframe(pain_points_df, use_container_width=True, hide_index=True)
            else:
                st.info("No defect or return tickets found for this product.")
            
            with st.expander("View Recent Tickets for this Product"):
                st.dataframe(product_df[['created_date', 'description', 'topic']])

# Rest of the page routing
elif page == "Return Analysis":
    create_analysis_page("Return", df_selection)
elif page == "Defect Analysis":
    create_analysis_page("Defect", df_selection)
elif page == "Question Analysis":
    create_analysis_page("Question", df_selection)


#