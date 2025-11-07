"""
Vote-bar Streamlit application.

Main entry point for the experimental voting system using the "100% bar" concept.
"""

import streamlit as st
import plotly.express as px
from logic.vote_logic import VoteBar


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Vote Bar - Experimental Voting System",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Vote Bar - Experimental Voting System")
    st.markdown("""
    Welcome to Vote Bar! This is an experimental voting system where you distribute 
    your preferences across multiple options using a "100% bar" concept.
    
    **How it works:**
    - You have 100% to distribute across all available options
    - Allocate percentages based on your preferences
    - All allocations must sum to exactly 100%
    """)
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Initialize session state
    if 'vote_bar' not in st.session_state:
        default_options = ["Option A", "Option B", "Option C", "Option D"]
        st.session_state.vote_bar = VoteBar(default_options)
    
    # Options management
    st.sidebar.subheader("Voting Options")
    options_text = st.sidebar.text_area(
        "Enter options (one per line):",
        value="\n".join(st.session_state.vote_bar.options),
        height=150
    )
    
    if st.sidebar.button("Update Options"):
        new_options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
        if new_options:
            st.session_state.vote_bar = VoteBar(new_options)
            st.sidebar.success(f"Updated to {len(new_options)} options!")
        else:
            st.sidebar.error("Please provide at least one option!")
    
    # Main voting interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Cast Your Vote")
        
        if len(st.session_state.vote_bar.options) == 0:
            st.warning("Please add some voting options in the sidebar first!")
            return
        
        # Create sliders for each option
        vote = {}
        remaining = 100.0
        
        st.markdown("**Distribute 100% across the options:**")
        
        for i, option in enumerate(st.session_state.vote_bar.options):
            if i == len(st.session_state.vote_bar.options) - 1:
                # Last option gets remaining percentage
                vote[option] = max(0.0, remaining)
                st.slider(
                    f"{option}",
                    min_value=0.0,
                    max_value=100.0,
                    value=vote[option],
                    step=0.1,
                    disabled=True,
                    help="This option automatically gets the remaining percentage"
                )
            else:
                # Ensure max_value is always greater than min_value
                max_val = max(remaining, 0.1)
                vote[option] = st.slider(
                    f"{option}",
                    min_value=0.0,
                    max_value=max_val,
                    value=0.0,
                    step=0.1,
                    disabled=(remaining <= 0.0),
                    help="No remaining percentage available" if remaining <= 0.0 else None
                )
                if remaining > 0.0:
                    remaining -= vote[option]
                else:
                    vote[option] = 0.0
        
        # Show total
        total = sum(vote.values())
        if abs(total - 100.0) < 0.01:
            st.success(f"Total: {total:.1f}% ✓")
        else:
            st.error(f"Total: {total:.1f}% (must equal 100%)")
        
        # Submit vote button
        if st.button("Submit Vote", type="primary"):
            if st.session_state.vote_bar.add_vote(vote):
                st.success("Vote submitted successfully!")
                st.rerun()
            else:
                st.error("Invalid vote! Please check your allocations.")
    
    with col2:
        st.header("Current Results")
        
        if len(st.session_state.vote_bar.votes) == 0:
            st.info("No votes cast yet!")
        else:
            results = st.session_state.vote_bar.get_results()
            
            # Display results table
            st.subheader(f"Results ({len(st.session_state.vote_bar.votes)} votes)")
            st.dataframe(
                results,
                column_config={
                    "option": "Option",
                    "average_score": st.column_config.NumberColumn(
                        "Average Score (%)",
                        format="%.1f%%"
                    ),
                    "total_votes": "Times Voted For"
                },
                hide_index=True
            )
            
            # Visualization
            if len(results) > 0:
                fig = px.bar(
                    results,
                    x='option',
                    y='average_score',
                    title='Average Scores by Option',
                    labels={'average_score': 'Average Score (%)', 'option': 'Options'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Reset button
        if st.button("Reset All Votes", type="secondary"):
            st.session_state.vote_bar.votes = []
            st.success("All votes have been reset!")
            st.rerun()


if __name__ == "__main__":
    main()