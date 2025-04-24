from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from test import ica_scraper, run_deepseek
from typing import List, Dict, Any, Optional
import time
import db

app = FastAPI(title="ICA Scraper API", description="API for scraping and categorizing ICA products")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory cache to store results
results_cache = {
    "last_update": 0,
    "data": None,
    "is_loading": False
}

# Cache expiration time in seconds (1 hour)
CACHE_EXPIRATION = 3600

async def update_cache():
    """Update the cache with fresh data"""
    try:
        results_cache["is_loading"] = True
        articles = await ica_scraper()
        
        if articles:
            categorized_items = []
            # Process articles in chunks
            chunk_size = 5  # Adjust this based on the LLM's context window
            
            for i in range(0, len(articles), chunk_size):
                chunk = articles[i : i + chunk_size]
                response = run_deepseek(None, chunk)
                
                if response:
                    categorized_items.extend(response)
            
            if categorized_items:
                # Store in database
                db.clear_database()  # Clear old data
                db.add_data(categorized_items)  # Add new data
                
                # Update cache
                results_cache["data"] = categorized_items
                results_cache["last_update"] = time.time()
            else:
                results_cache["data"] = []
        else:
            results_cache["data"] = []
    except Exception as e:
        print(f"Error updating cache: {e}")
        results_cache["data"] = []
    finally:
        results_cache["is_loading"] = False

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "ICA Scraper API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "API information"},
            {"path": "/products", "method": "GET", "description": "Get categorized products"},
            {"path": "/refresh", "method": "POST", "description": "Force refresh the product data"}
        ]
    }

@app.get("/products")
async def get_products():
    """Get the categorized products from cache or database"""
    current_time = time.time()
    
    # Check if cache is expired or empty
    if (current_time - results_cache["last_update"] > CACHE_EXPIRATION or 
        results_cache["data"] is None):
        # If not already loading, start a background task to update the cache
        if not results_cache["is_loading"]:
            asyncio.create_task(update_cache())
        
        # Try to get data from database while waiting for cache update
        try:
            db_products = db.get_all_products()
            if db_products:
                return {
                    "data": db_products,
                    "last_updated": results_cache["last_update"],
                    "is_loading": results_cache["is_loading"],
                    "source": "database"
                }
        except Exception as e:
            print(f"Error retrieving from database: {e}")
    
    # Return cached data (might be None or old if refresh is in progress)
    return {
        "data": results_cache["data"],
        "last_updated": results_cache["last_update"],
        "is_loading": results_cache["is_loading"],
        "source": "cache"
    }

@app.post("/refresh")
async def refresh_products(background_tasks: BackgroundTasks):
    """Force a refresh of the product data"""
    if not results_cache["is_loading"]:
        background_tasks.add_task(update_cache())
        return {"message": "Refresh started", "status": "success"}
    else:
        return {"message": "Refresh already in progress", "status": "busy"}

# Initialize the database on startup
@app.on_event("startup")
async def startup_event():
    db.setup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 