import streamlit as st
from utils import get_quote

def main():
    st.title("Spruch-Frontend")
    if st.button("Rufe demotivierenden Spruch ab!"):
        st.balloons()
        quote_dict = get_quote()
        if not "quote" in quote_dict or not "category" in quote_dict:
            raise KeyError("Key 'quote' or 'category' not found in quote endpoint response!")
        st.markdown(f"# Spruch\n{quote_dict['quote']}\n\n# Category\n{quote_dict['category']}")


if __name__ == "__main__":
    main()
