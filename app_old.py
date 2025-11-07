"""
Enhanced Streamlit app for drag-and-drop style voting.

This version provides a more visual approach where users can place
option icons on a bar by specifying their positions.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from logic.vote_logic import VoteBar


def create_bar_visualization(option_positions, options, bar_width=800, bar_height=60):
    """
    Create a visual representation of the voting bar with positioned options.
    
    Args:
        option_positions: Dict mapping option names to (start, end) tuples
        options: List of all available options
        bar_width: Width of the bar in pixels
        bar_height: Height of the bar in pixels
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Define colors for options
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    option_colors = {option: colors[i % len(colors)] for i, option in enumerate(options)}
    
    # Add background bar
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=100, y1=1,
        fillcolor="lightgray",
        line=dict(color="darkgray", width=2)
    )
    
    # Add positioned options
    for option, (start, end) in option_positions.items():
        if start != end:  # Only show if option has some allocation
            fig.add_shape(
                type="rect",
                x0=start, y0=0, x1=end, y1=1,
                fillcolor=option_colors[option],
                line=dict(color="white", width=2)
            )
            
            # Add option label
            mid_point = (start + end) / 2
            fig.add_annotation(
                x=mid_point, y=0.5,
                text=f"{option}<br>{end-start:.1f}%",
                showarrow=False,
                font=dict(color="white", size=12, family="Arial Black"),
                bgcolor="rgba(0,0,0,0.3)",
                bordercolor="white",
                borderwidth=1
            )
    
    # Style the figure
    fig.update_layout(
        title="Voting Bar - Option Positions",
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            title="Percentage"
        ),
        yaxis=dict(
            range=[0, 1],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=""
        ),
        height=150,
        margin=dict(l=20, r=20, t=50, b=50),
        plot_bgcolor='white'
    )
    
    return fig


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Vote Bar - Drag & Drop Voting",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Vote Bar - Drag & Drop Voting System")
    st.markdown("""
    **New Visual Voting Experience!** 
    
    Position your preferred options on the 100% bar below. The space each option occupies 
    represents its percentage of your vote. Options not placed on the bar receive 0%.
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
            st.rerun()
        else:
            st.sidebar.error("Please provide at least one option!")
    
    # Main voting interface
    if len(st.session_state.vote_bar.options) == 0:
        st.warning("Please add some voting options in the sidebar first!")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🎯 Position Your Vote")
        
        st.markdown("**Drag the sliders to position options on the 100% bar:**")
        
        # Position controls for each option
        option_positions = {}
        
        for i, option in enumerate(st.session_state.vote_bar.options):
            st.markdown(f"**{option}**")
            
            col_start, col_size = st.columns([1, 1])
            
            with col_start:
                start_pos = st.slider(
                    f"Start position for {option}",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.1,
                    key=f"start_{i}",
                    label_visibility="collapsed"
                )
            
            with col_size:
                max_size = 100.0 - start_pos
                size = st.slider(
                    f"Size for {option}",
                    min_value=0.0,
                    max_value=max_size,
                    value=0.0,
                    step=0.1,
                    key=f"size_{i}",
                    label_visibility="collapsed"
                )
            
            end_pos = start_pos + size
            option_positions[option] = (start_pos, end_pos)
            
            # Show current allocation
            if size > 0:
                st.info(f"📍 {option}: {start_pos:.1f}% → {end_pos:.1f}% = **{size:.1f}%**")
            else:
                st.text(f"❌ {option}: Not on bar (0%)")
        
        # Validation and submission
        total_allocated = sum(end - start for start, end in option_positions.values())
        
        st.markdown("---")
        st.markdown(f"**Total Allocated: {total_allocated:.1f}%**")
        
        if total_allocated > 100.1:
            st.error("⚠️ Total allocation exceeds 100%! Please adjust positions.")
        elif total_allocated < 99.9 and total_allocated > 0:
            st.warning(f"ℹ️ You have {100-total_allocated:.1f}% unused space on the bar.")
        
        # Submit vote button
        if st.button("🗳️ Submit Position Vote", type="primary"):
            # Filter out options with 0 allocation
            filtered_positions = {
                option: pos for option, pos in option_positions.items() 
                if pos[1] - pos[0] > 0
            }
            
            if st.session_state.vote_bar.add_position_vote(filtered_positions):
                st.success("✅ Position vote submitted successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid vote! Please check for overlapping positions.")
    
    with col2:
        st.header("📊 Live Bar Preview")
        
        # Show current bar configuration
        bar_fig = create_bar_visualization(
            option_positions, 
            st.session_state.vote_bar.options
        )
        st.plotly_chart(bar_fig, use_container_width=True)
        
        # Results section
        st.header("📈 Current Results")
        
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
                    "total_votes": "Times Positioned"
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
                    labels={'average_score': 'Average Score (%)', 'option': 'Options'},
                    color='average_score',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Reset button
        if st.button("🔄 Reset All Votes", type="secondary"):
            st.session_state.vote_bar.votes = []
            st.success("All votes have been reset!")
            st.rerun()
    
    # Instructions
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        ### Drag & Drop Voting Instructions:
        
        1. **Position Options**: Use the sliders to place your preferred options on the 100% bar
        2. **Adjust Size**: The width of each option represents its percentage of your vote
        3. **Visual Feedback**: Watch the live preview to see your bar configuration
        4. **Submit Vote**: Click "Submit Position Vote" when satisfied with your allocation
        5. **View Results**: See aggregated results from all submitted votes
        
        ### Rules:
        - Options not placed on the bar receive 0%
        - Total allocation can be up to 100%
        - Options cannot overlap on the bar
        - You can leave unused space on the bar (partial allocation)
        """)


if __name__ == "__main__":
    main()