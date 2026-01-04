"""
Canvas API Client Module.

This module handles the initialization and configuration of the Canvas API client,
managing authentication via environment variables or direct arguments.
"""

import os
from canvasapi import Canvas
from dotenv import load_dotenv

def get_client(api_url=None, api_key=None):
    """
    Initialize and return a Canvas client.
    
    If api_url or api_key are not provided, attempts to load them 
    from environment variables CANVAS_API_URL and CANVAS_API_KEY.
    """
    load_dotenv()

    url = api_url or os.getenv("CANVAS_API_URL")
    key = api_key or os.getenv("CANVAS_API_KEY")

    if not url or not key:
        raise ValueError("Canvas API URL and Key are required. Set them in arguments or environment variables.")

    return Canvas(url, key)
