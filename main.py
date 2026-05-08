from fastapi import FastAPI
from pydantic import BaseModel
from linkedin_bot import search_posts, post_comment

app = FastAPI()

# Endpoint 1 — n8n calls this to find posts
@app.get("/search-posts")
def search_posts_route():
    results = search_posts()
    return results

class PostRequest(BaseModel):
    post_url: str
    comment: str

@app.post("/post-comment")
def post_comment_route(data: PostRequest):
    # Clean the URL - remove spaces and extra characters
    clean_url = data.post_url.strip().replace(" ", "")
    clean_comment = data.comment.strip()
    
    result = post_comment(clean_url, clean_comment)
    return result
