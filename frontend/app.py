import streamlit as st
import requests
import json

st.set_page_config(layout="wide")

st.title("AI Docker Compose & Dockerfile Generator")

repo_url = st.text_input("Enter GitHub Repo URL", placeholder="https://github.com/username/repo")

col_analyze, col_dockerfile = st.columns(2)
with col_analyze:
    analyze_button = st.button("🔍 Analyze Repository", use_container_width=True)
with col_dockerfile:
    generate_both = st.checkbox("Generate both Dockerfile & docker-compose", value=True)

if analyze_button and repo_url:
    with st.spinner("Analyzing repository..."):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/analyze",
                params={
                    "repo_url": repo_url,
                    "include_dockerfile": generate_both
                },
                timeout=60
            )

            data = response.json()

            if "error" in data:
                st.error(f"❌ Error: {data['error']}")

            else:
                # Main layout with multiple columns
                st.success("✅ Analysis Complete!")
                
                # Tech Stack Detection Summary
                st.divider()
                st.subheader("🔎 Tech Stack Detection")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Primary Stack Detected",
                        data.get("primary_stack", "unknown").upper(),
                        delta=None
                    )
                
                with col2:
                    detected_stacks = data.get("detected_stacks", {})
                    if detected_stacks:
                        st.metric(
                            "Total Stacks Found",
                            len(detected_stacks),
                            delta=f"{len(detected_stacks)} tech(s)"
                        )
                
                # Detailed stack detection
                if detected_stacks:
                    st.write("**Detected Technology Stack Signals:**")
                    for stack, confidence in sorted(detected_stacks.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"  • **{stack.capitalize()}**: {confidence} file indicator(s)")
                
                st.divider()
                
                # Repository Structure
                st.subheader("📁 Repository Structure")
                with st.expander("View file tree", expanded=False):
                    st.code(data["tree"], language="text")
                
                # Docker Configuration Outputs
                st.subheader("🐳 Docker Configurations")
                
                tab1, tab2 = st.tabs(["docker-compose.yml", "Dockerfile"])
                
                with tab1:
                    st.write("**Generated docker-compose.yml:**")
                    st.code(data["docker_compose"], language="yaml")
                    st.download_button(
                        label="Download docker-compose.yml",
                        data=data["docker_compose"],
                        file_name="docker-compose.yml",
                        mime="text/yaml"
                    )
                
                with tab2:
                    if data.get("dockerfile"):
                        st.write("**Generated Dockerfile:**")
                        st.code(data["dockerfile"], language="dockerfile")
                        st.download_button(
                            label="Download Dockerfile",
                            data=data["dockerfile"],
                            file_name="Dockerfile",
                            mime="text/plain"
                        )
                    else:
                        st.info("Dockerfile generation not enabled. Check 'Generate both Dockerfile & docker-compose' above.")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend server. Make sure it's running on http://127.0.0.1:8000")
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Repository might be too large or server is slow.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")