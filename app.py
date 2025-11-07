"""
Vote-bar Streamlit application - Simple Voronoi voting system.

Users select options and assign positions on a 0-100 bar.
Each option's share is determined by 1D Voronoi diagram logic
(territory based on midpoints between adjacent positions).
"""

import streamlit as st
import plotly.graph_objects as go
from logic.vote_logic import VoteResult


def create_results_bar_chart(vote_result: VoteResult) -> go.Figure:
    """Create a horizontal stacked bar chart showing vote shares with position markers."""
    if not vote_result.shares:
        return go.Figure()
    
    # Get sorted results for consistent display
    sorted_results = vote_result.get_sorted_results()
    
    fig = go.Figure()
    
    # Colors for the options
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    cumulative_width = 0
    for i, (option, position, share) in enumerate(sorted_results):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Bar(
            y=['Vote Distribution'],
            x=[share],
            name=f"{option} ({share:.1f}%)",
            orientation='h',
            marker_color=color,
            text=f"{option}<br>{share:.1f}%",
            textposition='inside',
            showlegend=True
        ))
        
        cumulative_width += share
    
    # Add position markers as scatter points
    for i, (option, position, share) in enumerate(sorted_results):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=[position],
            y=['Vote Distribution'],
            mode='markers',
            marker=dict(
                size=12,
                color='white',
                line=dict(color=color, width=3),
                symbol='circle'
            ),
            text=f"{option}: {position:.1f}",
            textposition="top center",
            showlegend=False,
            hovertemplate=f"<b>{option}</b><br>Position: {position:.1f}<br>Share: {share:.1f}%<extra></extra>"
        ))
    
    fig.update_layout(
        barmode='stack',
        xaxis_title="Position (0-100)",
        yaxis=dict(visible=False),
        height=120,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=5, r=20),
        xaxis=dict(range=[0, 100])
    )
    
    return fig


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Vote Bar - Voronoi Voting",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Vote Bar - Voronoi Voting System")
    st.markdown("""
    Select options and assign positions (0-100). Each option controls territory 
    based on **midpoints** between adjacent positions (1D Voronoi diagram).
    """)
    
    # Initialize session state
    if 'available_options' not in st.session_state:
        st.session_state.available_options = ['Option A', 'Option B', 'Option C', 'Option D']
    
    # Sidebar for option management
    st.sidebar.header("📝 Manage Options")
    
    # Add new option with form (allows Enter key to submit)
    with st.sidebar.form("add_option_form", clear_on_submit=True):
        new_option = st.text_input("Add new option:")
        submitted = st.form_submit_button("➕ Add Option")
        
        if submitted and new_option.strip():
            if new_option.strip() not in st.session_state.available_options:
                st.session_state.available_options.append(new_option.strip())
                st.rerun()
            else:
                st.warning("Option already exists!")
    
    # Display current options
    st.sidebar.subheader("Current Options:")
    for i, option in enumerate(st.session_state.available_options):
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(f"{i+1}. {option}")
        if col2.button("🗑️", key=f"delete_{i}", help=f"Delete {option}"):
            st.session_state.available_options.remove(option)
            st.rerun()
    
    # Main voting interface
    st.header("🗳️ Cast Your Vote")
    
    if not st.session_state.available_options:
        st.warning("Please add some options in the sidebar first!")
        return
    
    # SECTION 1: Option Selection (Checkboxes)
    st.subheader("1. Select Options")
    
    # Display checkboxes in columns
    checkbox_cols = st.columns(4)
    for i, option in enumerate(st.session_state.available_options):
        col = checkbox_cols[i % 4]
        with col:
            st.checkbox(f"**{option}**", key=f"select_{option}")
    
    # Collect selected options and their positions
    selected_positions = {}
    for option in st.session_state.available_options:
        if st.session_state.get(f"select_{option}", False):
            position = st.session_state.get(f"pos_{option}", 50.0)
            selected_positions[option] = position
    
    if not selected_positions:
        st.info("👆 Select at least one option above to continue")
        return
    
    st.divider()
    
    # SECTION 2: Live Distribution Visualization
    st.subheader("2. Distribution Preview")
    
    # Compute vote shares in real-time
    vote_result = VoteResult(selected_positions)
    chart = create_results_bar_chart(vote_result)
    st.plotly_chart(chart, use_container_width=True)
    
    st.divider()
    
    # SECTION 3: Position Adjustment (Compact sliders in single column)
    st.subheader("3. Adjust Positions")
    
    for option in st.session_state.available_options:
        if st.session_state.get(f"select_{option}", False):
            position = st.slider(
                f"{option}:",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=0.1,
                key=f"pos_{option}",
                help=f"Set position for {option} on the 0-100 bar"
            )
    
    # FAQ Section at the bottom
    st.divider()
    st.header("❓ FAQ")
    
    with st.expander("🧠 How the calculation works"):
        if selected_positions:
            vote_result = VoteResult(selected_positions)
            sorted_results = vote_result.get_sorted_results()
            st.write("**Current positions and territories:**")
            
            for i, (option, position, share) in enumerate(sorted_results):
                left_boundary = 0.0
                right_boundary = 100.0
                
                if i > 0:
                    prev_pos = sorted_results[i-1][1]
                    left_boundary = (prev_pos + position) / 2.0
                
                if i < len(sorted_results) - 1:
                    next_pos = sorted_results[i+1][1]
                    right_boundary = (position + next_pos) / 2.0
                
                st.write(f"- **{option}** at position {position:.1f} → "
                       f"territory {left_boundary:.1f}–{right_boundary:.1f} = **{share:.1f}%**")
        else:
            st.write("Select options above to see territory calculations.")
    
    with st.expander("ℹ️ How to use this voting system"):
        st.markdown("""
        ### Voting Process:
        1. **Select options** using checkboxes
        2. **Set positions** using sliders (0-100 scale)
        3. **Watch** the distribution update automatically above
        
        ### How shares are calculated:
        - Each option controls territory based on **midpoints** between adjacent positions
        - This creates a **1D Voronoi diagram** on the 0-100 bar
        - Single option → gets 100%
        - Multiple options → territory boundaries at midpoints
        
        ### Examples:
        - Two options at 30 and 70 → midpoint at 50 → 50% each
        - Three options at 20, 50, 80 → boundaries at 35 and 65 → 35%, 30%, 35%
        """)


if __name__ == "__main__":
    main()