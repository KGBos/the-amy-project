# Context7 Usage Guide

> [!IMPORTANT]
> **Who is this for?**
> This guide is for AI Agents (like Antigravity) developers working on "The Amy Project".
> It explains how to access library documentation to ensure you are writing accurate, up-to-date code.

## What is Context7?

Context7 is an **MCP Server** that provides real-time documentation and code examples for libraries. It prevents hallucinations by providing the exact API signatures for the specific versions of libraries we use.

## How to use Context7

You have access to two tools via the `context7` MCP server:

1.  `resolve-library-id`: Use this to find the correct library ID for a given package.
2.  `query-docs`: Use this to fetch documentation and examples.

### Workflow

1.  **Identify the Library**: When you are about to write code using a library you aren't 100% unsure about (e.g., `mem0ai`, `google-genai`, `freeplay`), check if you need docs.
2.  **Resolve ID**: Call `resolve-library-id`.
    ```json
    {
      "libraryName": "mem0",
      "query": "How to store memory with user_id in mem0"
    }
    ```
3.  **Get Docs**: The tool will return a `libraryId` (e.g., `/mem0/mem0`). Use this ID to query the docs.
    ```json
    {
      "libraryId": "/mem0/mem0",
      "query": "add memory example python"
    }
    ```
4.  **Implement**: Use the retrieved code snippets to implement your feature correctly.

## Best Practices

*   **Don't Guess**: If you see an error like `AttributeError: ... object has no attribute 'add'`, it means your training data is stale. Use Context7 to find the correct method name.
*   **Version Awareness**: Context7 respects versions. If `requirements.txt` specifies a version, mention it in your query.
*   **Limit Calls**: Don't spam the tool. Get the docs you need in 1-2 queries.
