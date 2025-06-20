"""
Main Streamlit application for the NGEN Consultor
"""
import streamlit as st
import asyncio
from pathlib import Path

from agents.description_agent import DescriptionAgent
def main():
    st.set_page_config(
        page_title="NGEN Project Report Generator",
        page_icon="��",
        layout="wide"
    )
    
    st.title("🤖 NGEN Consultor")
    st.markdown("Generate technical and financial reports using multiple AI models")
    
    # Initialize session state
    if "agent" not in st.session_state:
        st.session_state.agent = DescriptionAgent()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Project Information")
        st.markdown("This tool will help you generate comprehensive project reports using multiple AI models.")
        
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.header("💬 Project Consultation")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Tell me about your project..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(st.session_state.agent.start_conversation(prompt))
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Report generation section
    st.header("📊 Generate Reports")
    
    if st.button("🚀 Generate Reports with All Models"):
        with st.spinner("Generating reports..."):
            results = asyncio.run(st.session_state.agent.generate_reports(st.session_state.messages))
            
            # Display results
            for model_name, result in results.items():
                st.subheader(f"📄 {model_name.upper()} Reports")
                
                if "error" in result:
                    st.error(f"Error generating {model_name} reports: {result['error']}")
                else:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(result['analysis'].get("technical",""))
                    
                    with col2:
                        st.markdown(result['analysis'].get("financial",""))

if __name__ == "__main__":
    main()