# Frontend — Member A

## Files

- main.py: launches Streamlit using the same interpreter or runs the app in an existing Streamlit context; normal Ctrl+C shutdown is handled.
- frontend/app.py: layout, sidebar, session state, event consumption and downloads.
- frontend/components.py: friendly tool labels, examples and historical trace renderer.
- frontend/styles.css: styling extracted from the uploaded UI.
- .streamlit/config.toml: light theme, loopback binding and disabled usage statistics.

The supported destinations come from tools._catalog.supported_cities(), rather than a second hard-coded list. No Tokyo/Bali claim remains. Exactly ten dropdown options exist: all tools plus the nine individual tools.

Use the normal Streamlit widgets to change layout. Avoid wrapping separate widget calls in raw HTML div tags: independent Markdown blocks do not form a reliable shared widget container.

## User flow

Choose All tools for a complete plan, or choose one tool for a focused request. Type the required details; the placeholder suggests an example. Selection alone does not execute a tool. Missing details may lead to a question. Each request retains its selected label in visible history.

Expand the tool trace to see actual inputs and outputs. JSON downloads appear only for saved files that pass validation. Sidebar file preview is not a fresh agent conversation; ask Load itinerary to place a saved plan into model history.

## Tests and manual checks

AppTest covers chat events, selection, correct destination labels and New conversation. Before submission check the app in your actual browser: text contrast, dropdown readability, long answers, narrow window layout, downloads and Ctrl+C shutdown. Automated widget checks are not a full visual inspection across browsers.
