import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo


def main() -> None:
    """Main function for the Invit(ai)tions Streamlit app."""

    st.set_page_config(page_title="Invit(ai)tions", page_icon=":wave:")

    st.title("Welcome to Invit(ai)tions! :rocket:")

    add_logo("eleven_logo.jpeg", height=200)

    # Container to hold the content above the button
    content_container = st.container()

    with content_container:
        st.markdown(
            """
        Welcome to **Invit(ai)tions**, your premier destination for data-driven event management and client engagement strategies! Whether you're organizing exclusive gatherings, planning high-end events, or seeking insights to elevate your client interactions, our platform is here to empower you with actionable intelligence.

        ## What We Offer

        - **Data Analysis**: Dive deep into your event data with our intuitive analytics tools. Uncover key trends, identify influential factors, and gain valuable insights to enhance your event planning strategies.

        - **Client Recommendations**: Leverage the power of predictive analytics to identify potential attendees for your events. Our recommendation engine analyzes client data to suggest targeted invitations, maximizing attendance and engagement.

        ## How It Works

        1. **Upload Your Data**: Get started by uploading your event data and client information or continue with the pre-uploaded dataset

        2. **Explore Insights**: Dive into your data with our interactive analytics dashboard. Explore key metrics, visualize trends, and uncover actionable insights to inform your event planning strategies.

        3. **Receive Recommendations**: Receive personalized recommendations based on your historical data. Our recommendation engine utilizes machine learning algorithms to identify potential attendees and optimize your event guest list.

        4. **Plan Your Events**: Plan and manage your events with ease using our intuitive event management tools. From scheduling and logistics to guest list management and communication, we've got everything you need to ensure a successful event.
                    
        ##  Get Started Today!
        """
        )

    # Button to navigate to the inner page
    get_started_button = st.button("Get Started")

    if get_started_button:
        switch_page("data_analysis")


if __name__ == "__main__":
    main()
