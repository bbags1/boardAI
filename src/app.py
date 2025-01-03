import streamlit as st
from main import AdvisoryBoard

def initialize_board():
    if 'board' not in st.session_state:
        st.session_state.board = AdvisoryBoard()
        # Initialize with our core advisors
        st.session_state.board.add_advisor("legal")
        st.session_state.board.add_advisor("financial")
        st.session_state.board.add_advisor("technology")

def main():
    st.title("AI Advisory Board")
    initialize_board()

    # Sidebar for selecting advisors
    st.sidebar.header("Select Advisors for Discussion")
    advisor_options = {
        "Legal Advisor": "legal",
        "Financial Advisor": "financial",
        "Technology Advisor": "technology"
    }
    
    selected_advisors = []
    for advisor_name, advisor_role in advisor_options.items():
        if st.sidebar.checkbox(advisor_name, True):
            selected_advisors.append(advisor_role)

    # Main chat interface
    st.write("### Board Discussion")
    
    # Chat input
    user_input = st.text_area("Enter your topic or question for the board:", height=100)
    
    if st.button("Get Board Advice"):
        if not user_input:
            st.warning("Please enter a topic for discussion.")
            return
        
        if not selected_advisors:
            st.warning("Please select at least one advisor.")
            return

        # Create placeholders for each advisor
        advisor_placeholders = {role: st.empty() for role in selected_advisors}
        synthesis_placeholder = st.empty()
        
        # Get individual analyses first
        for role in selected_advisors:
            full_response = ""
            message_placeholder = advisor_placeholders[role].container()
            message_placeholder.markdown(f"### {role.upper()} ADVISOR:")
            
            response_placeholder = message_placeholder.empty()
            for chunk in st.session_state.board.get_individual_analysis(user_input, role):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.write("---")
        
        # Get group discussion if multiple advisors selected
        if len(selected_advisors) > 1:
            synthesis_container = synthesis_placeholder.container()
            synthesis_container.markdown("### Board Discussion and Synthesis")
            synthesis_text = ""
            response_placeholder = synthesis_container.empty()
            
            for chunk in st.session_state.board.facilitate_discussion(user_input, selected_advisors):
                synthesis_text += chunk
                response_placeholder.markdown(synthesis_text + "▌")
            response_placeholder.markdown(synthesis_text)

if __name__ == "__main__":
    main()