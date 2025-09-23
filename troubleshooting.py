import streamlit as st

def troubleshooting_tab(assistant):
    st.header("Troubleshooting")
    st.write("Get solutions for common Git/GitHub errors")

    error_message = st.text_area("Paste your error message here")
    if st.button("Troubleshoot") and error_message:
        with st.spinner("Finding solution..."):
            solution = assistant.troubleshoot_error(error_message)
            st.markdown("### Solution")
            st.write(solution['explanation'])
            if solution['commands']:
                st.markdown("### Commands to Fix")
                for cmd in solution['commands']:
                    st.code(cmd, language='bash')
