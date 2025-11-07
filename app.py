"""
Vote-bar Streamlit application - Simple Voronoi voting system.

Users select options and assign positions on a 0-100 bar.
Each option's share is determined by 1D Voronoi diagram logic
(territory based on midpoints between adjacent positions).
"""

import uuid
import streamlit as st
import plotly.graph_objects as go
from logic.vote_logic import VoteResult
from logic.room_manager import get_room_manager


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
    
    # Get room manager
    room_manager = get_room_manager()
    
    # Initialize persistent participant ID
    # Try to get from query params first (persists across refreshes)
    query_params = st.query_params
    if 'participant_id' in query_params:
        participant_id = query_params['participant_id']
    else:
        # Generate new UUID and store in query params
        participant_id = str(uuid.uuid4())
        st.query_params['participant_id'] = participant_id
    
    # Store in session state for easy access
    st.session_state.participant_id = participant_id
    
    # Initialize session state
    if 'room_code' not in st.session_state:
        st.session_state.room_code = None
    if 'available_options' not in st.session_state:
        st.session_state.available_options = ['Option A', 'Option B', 'Option C', 'Option D']
    
    # Sidebar - Room Management
    st.sidebar.header("🏠 Room Management")
    
    if st.session_state.room_code is None:
        # Not in a room - show create/join options
        st.sidebar.info("👤 Solo Mode - Create or join a room to collaborate!")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🆕 Create Room", use_container_width=True):
                room_code = room_manager.create_room(st.session_state.available_options)
                st.session_state.room_code = room_code
                
                # Clear all checkboxes and positions for new room
                for option in st.session_state.available_options:
                    if f"select_{option}" in st.session_state:
                        del st.session_state[f"select_{option}"]
                    if f"pos_{option}" in st.session_state:
                        del st.session_state[f"pos_{option}"]
                st.session_state.vote_submitted = False
                
                st.rerun()
        
        with col2:
            if st.button("🚪 Join Room", use_container_width=True):
                st.session_state.show_join_form = True
                st.rerun()
        
        # Show join form if requested
        if st.session_state.get('show_join_form', False):
            with st.sidebar.form("join_room_form"):
                join_code = st.text_input("Enter Room Code:", max_chars=8).upper()
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Join", use_container_width=True):
                        room = room_manager.join_room(join_code)
                        if room:
                            st.session_state.room_code = join_code
                            st.session_state.available_options = room.available_options.copy()
                            st.session_state.show_join_form = False
                            
                            # Check if this participant has already voted in this room
                            if st.session_state.participant_id in room.participant_votes:
                                # Restore their previous vote
                                previous_vote = room.participant_votes[st.session_state.participant_id]
                                for option, position in previous_vote.items():
                                    st.session_state[f"select_{option}"] = True
                                    st.session_state[f"pos_{option}"] = position
                                st.session_state.vote_submitted = True
                            else:
                                # Clear all checkboxes and positions for new voter
                                for option in room.available_options:
                                    if f"select_{option}" in st.session_state:
                                        del st.session_state[f"select_{option}"]
                                    if f"pos_{option}" in st.session_state:
                                        del st.session_state[f"pos_{option}"]
                                st.session_state.vote_submitted = False
                            
                            st.rerun()
                        else:
                            st.error("Room not found!")
                
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_join_form = False
                        st.rerun()
    
    else:
        # In a room - show room info and leave option
        room = room_manager.get_room(st.session_state.room_code)
        
        if room:
            st.sidebar.success(f"🏠 **Room Code:**")
            
            # Display room code in a text input for easy copying
            st.sidebar.code(st.session_state.room_code, language=None)
            
            st.sidebar.caption(f"👥 {room.participant_count} participant(s)")
            st.sidebar.caption(f"🕐 Updated: {room.last_updated.strftime('%H:%M:%S')}")
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("🔄 Update", use_container_width=True, help="Refresh room state"):
                    room = room_manager.get_room(st.session_state.room_code)
                    if room:
                        st.session_state.available_options = room.available_options.copy()
                        
                        # Check if this participant has already voted in this room
                        if st.session_state.participant_id in room.participant_votes:
                            # Restore their previous vote
                            previous_vote = room.participant_votes[st.session_state.participant_id]
                            for option, position in previous_vote.items():
                                st.session_state[f"select_{option}"] = True
                                st.session_state[f"pos_{option}"] = position
                            st.session_state.vote_submitted = True
                        else:
                            # Clear all checkboxes and positions for new voter
                            for option in room.available_options:
                                if f"select_{option}" in st.session_state:
                                    del st.session_state[f"select_{option}"]
                                if f"pos_{option}" in st.session_state:
                                    del st.session_state[f"pos_{option}"]
                            st.session_state.vote_submitted = False
                        
                        st.rerun()
            
            with col2:
                if st.button("🚪 Leave", use_container_width=True, help="Leave room"):
                    st.session_state.room_code = None
                    st.rerun()
        else:
            st.sidebar.error("Room no longer exists!")
            st.session_state.room_code = None
            st.rerun()
    
    st.sidebar.divider()
    
    # Sidebar for option management
    st.sidebar.header("📝 Manage Options")
    
    # Add new option with form (allows Enter key to submit)
    with st.sidebar.form("add_option_form", clear_on_submit=True):
        new_option = st.text_input("Add new option:")
        submitted = st.form_submit_button("➕ Add Option")
        
        if submitted and new_option.strip():
            if new_option.strip() not in st.session_state.available_options:
                st.session_state.available_options.append(new_option.strip())
                # Sync with room if in one
                if st.session_state.room_code:
                    room_manager.update_room_options(
                        st.session_state.room_code,
                        st.session_state.available_options
                    )
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
            # Sync with room if in one
            if st.session_state.room_code:
                room_manager.update_room_options(
                    st.session_state.room_code,
                    st.session_state.available_options
                )
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
    
    # Collect selected options
    selected_options = []
    for option in st.session_state.available_options:
        if st.session_state.get(f"select_{option}", False):
            selected_options.append(option)
    
    if not selected_options:
        st.info("👆 Select at least one option above to continue")
        return
    
    st.divider()
    
    # SECTION 2: Adjust Positions with Live Preview
    st.subheader("2. Adjust Positions")
    
    # Collect current positions from sliders for preview
    current_positions = {}
    for option in selected_options:
        current_positions[option] = st.session_state.get(f"pos_{option}", 50.0)
    
    # Live preview chart
    vote_result = VoteResult(current_positions)
    chart = create_results_bar_chart(vote_result)
    st.plotly_chart(chart, use_container_width=True, key="preview_chart")
    
    # Position sliders (no divider for tight spacing)
    for option in selected_options:
        position = st.slider(
            f"{option}:",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.get(f"pos_{option}", 50.0),
            step=0.1,
            key=f"pos_{option}",
            help=f"Set position for {option} on the 0-100 bar"
        )
    
    st.divider()
    
    # SECTION 3: Submit Vote
    st.subheader("3. Submit Your Vote")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Submit Vote", type="primary", use_container_width=True):
            # Recalculate current positions at submit time
            submit_positions = {}
            for option in selected_options:
                submit_positions[option] = st.session_state.get(f"pos_{option}", 50.0)
            
            # Generate participant ID if not exists
            
            # Save to room if in one
            if st.session_state.room_code:
                success = room_manager.update_room_positions(
                    st.session_state.room_code,
                    st.session_state.participant_id,
                    submit_positions
                )
                if success:
                    st.success("✅ Vote submitted successfully!")
                    st.session_state.last_vote = submit_positions.copy()
                    st.session_state.vote_submitted = True
                else:
                    st.error("❌ Failed to submit vote. Room may no longer exist.")
            else:
                st.success("✅ Vote recorded! (Solo mode - create/join room to share)")
                st.session_state.last_vote = submit_positions.copy()
                st.session_state.vote_submitted = True
    
    # Show submitted vote distribution
    if st.session_state.get('vote_submitted', False) and st.session_state.room_code:
        st.divider()
        st.subheader("📊 Room Results")
        
        room = room_manager.get_room(st.session_state.room_code)
        if room and room.participant_votes:
            # Get aggregated results
            aggregated_points = room.get_aggregated_results()
            
            # Sort by points (highest to lowest), filter out zero points
            sorted_results = sorted(
                [(option, points) for option, points in aggregated_points.items() if points > 0],
                key=lambda x: x[1],
                reverse=True
            )
            
            st.markdown(f"**👥 {room.participant_count} participant(s) voted**")
            st.markdown(f"**🕐 Last updated:** {room.last_updated.strftime('%H:%M:%S')}")
            
            # Display as ordered list
            st.markdown("### Ranking:")
            for rank, (option, points) in enumerate(sorted_results, 1):
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
                st.markdown(f"{medal} **{option}** — {points:.1f} points")
            
            # Show detailed breakdown
            with st.expander("📈 Detailed Breakdown"):
                st.write(f"**Total votes:** {room.participant_count}")
                for rank, (option, points) in enumerate(sorted_results, 1):
                    avg_share = points / room.participant_count if room.participant_count > 0 else 0
                    st.write(f"**{rank}. {option}:** {points:.1f} total points (avg {avg_share:.1f}% per voter)")
        else:
            st.info("No votes submitted yet in this room.")
    elif st.session_state.get('vote_submitted', False):
        st.divider()
        st.subheader("📊 Your Vote")
        st.info("💡 Create or join a room to see aggregated results with other participants!")
    
    # FAQ Section at the bottom
    st.divider()
    st.header("❓ FAQ")
    
    with st.expander("🧠 How the calculation works"):
        if current_positions:
            vote_result = VoteResult(current_positions)
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