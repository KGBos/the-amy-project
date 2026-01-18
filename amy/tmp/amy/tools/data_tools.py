from google.adk.tools import FunctionTool

@FunctionTool
def read_personal_data(query: str) -> str:
    """
    Reads personal data from the user's data store based on a query.

    Args:
        query: The question or query to find relevant data for.
               e.g., "What is Mom's phone number?", "Find my notes on the Q2 project."

    Returns:
        A string containing the requested data, or 'Data not found.'
    """
    # TODO: Implement the connection to your personal database or file system.
    # This could be a vector database, a SQL database, or just text files.
    print(f"--- TOOL: Reading data for query: {query} ---")
    raise NotImplementedError("Connect this tool to your personal data store.")

@FunctionTool
def write_personal_data(data: str, category: str) -> str:
    """
    Writes new personal data to the user's data store.

    Args:
        data: The information to save.
        category: The category to store the data under (e.g., 'contact', 'note', 'reminder').

    Returns:
        A string confirming the data was saved, e.g., 'Successfully saved data.'
    """
    # TODO: Implement the connection to your personal database or file system.
    print(f"--- TOOL: Writing data to category '{category}': {data} ---")
    raise NotImplementedError("Connect this tool to your personal data store.")
