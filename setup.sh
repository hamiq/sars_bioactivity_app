mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"hi70@scarletmail.rutgers.edu\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml