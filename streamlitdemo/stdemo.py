import streamlit as st

# Page config
st.set_page_config(page_title="Colorful Calculator", page_icon="🧮", layout="centered")

# Custom CSS
st.markdown("""
<style>

body {
background: linear-gradient(135deg,#667eea,#764ba2);
}

.main {
background: linear-gradient(135deg,#667eea,#764ba2);
}

.title {
text-align:center;
font-size:45px;
font-weight:800;
color:white;
margin-bottom:30px;
}

.card {
background: rgba(255,255,255,0.15);
backdrop-filter: blur(10px);
padding:30px;
border-radius:15px;
box-shadow:0px 10px 25px rgba(0,0,0,0.3);
}

.result {
background: linear-gradient(90deg,#ff7eb3,#ff758c,#ff7eb3);
padding:25px;
border-radius:12px;
text-align:center;
font-size:30px;
font-weight:bold;
color:white;
margin-top:20px;
}

button[kind="primary"] {
background: linear-gradient(90deg,#36d1dc,#5b86e5);
border:none;
border-radius:8px;
font-size:18px;
font-weight:600;
padding:10px;
}

</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="title">🧮 Colorful Calculator</div>', unsafe_allow_html=True)

# Card container
st.markdown('<div class="card">', unsafe_allow_html=True)

# Inputs
col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("Enter First Number")

with col2:
    num2 = st.number_input("Enter Second Number")

operation = st.selectbox(
    "Choose Operation",
    ["Addition", "Subtraction", "Multiplication", "Division"]
)

# Button
if st.button("Calculate", use_container_width=True):

    if operation == "Addition":
        result = num1 + num2

    elif operation == "Subtraction":
        result = num1 - num2

    elif operation == "Multiplication":
        result = num1 * num2

    elif operation == "Division":
        if num2 != 0:
            result = num1 / num2
        else:
            result = "Cannot divide by zero"

    st.markdown(f'<div class="result">Result: {result}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)