import os
import json
import re
import httpx
from datetime import datetime, timezone, timedelta

def extract_image_urls(html_content: str) -> list:
    """从HTML内容中提取图片URL"""
    if not html_content:
        return []
    
    img_urls = []
    
    lightbox_matches = re.findall(r'href="(https://ask\.oceanbase\.com/uploads/default/original/[^"]+\.png)"', html_content)
    img_urls.extend(lightbox_matches)
    
    src_matches = re.findall(r'src="(https://ask\.oceanbase\.com/uploads/default/optimized/[^"]+\.png)"', html_content)
    for url in src_matches:
        if url not in img_urls:
            img_urls.append(url)
    
    return img_urls

def fetch_post_content(topic_id: int) -> dict:
    url = f"https://ask.oceanbase.com/t/{topic_id}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    response = httpx.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    
    data = response.json()
    posts = data.get("post_stream", {}).get("posts", [])
    
    if posts:
        first_post = posts[0]
        raw_content = first_post.get("cooked", "")
        image_urls = extract_image_urls(raw_content)
        
        return {
            "topic_id": topic_id,
            "title": data.get("title"),
            "content": raw_content,
            "author": first_post.get("name"),
            "username": first_post.get("username"),
            "url": f"https://ask.oceanbase.com/t/topic/{topic_id}",
            "image_urls": image_urls
        }
    return {"topic_id": topic_id, "error": "No posts found", "url": f"https://ask.oceanbase.com/t/topic/{topic_id}"}

def fetch_today_posts():
    tz_shanghai = timezone(timedelta(hours=8))
    today = datetime.now(tz_shanghai).strftime("%Y-%m-%d")
    
    url = f"https://ask.oceanbase.com/search?q=%23oceanbase%20after%3A{today}%20order%3Alatest&page=1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    response = httpx.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    
    topics_dict = {}
    topics_data = data.get("topics", [])
    for topic_data in topics_data:
        topic_id = topic_data.get("id")
        topics_dict[topic_id] = {
            "title": topic_data.get("title"),
            "created_at": topic_data.get("created_at")
        }
    
    posts_info = []
    posts_data = data.get("posts", [])
    
    for post in posts_data:
        topic_id = post.get("topic_id")
        topic_info = topics_dict.get(topic_id, {})
        created_at = topic_info.get("created_at")
        
        if created_at and created_at.startswith(today):
            post_info = {
                "id": post.get("id"),
                "created_at": created_at,
                "topic_id": topic_id,
                "topic_title": topic_info.get("title"),
                "url": f"https://ask.oceanbase.com/t/topic/{topic_id}" if topic_id else None
            }
            posts_info.append(post_info)
    
    post_ids_length = len(data.get("grouped_search_result", {}).get("post_ids", []))

    return {
        "posts_count": post_ids_length,
        "today_posts_count": len(posts_info),
        "posts": posts_info
    }

if __name__ == "__main__":
    result = fetch_today_posts()
    print(f"Total posts found: {result['posts_count']}")
    print(f"Today's posts: {result['today_posts_count']}")
    print("\nPosts info:")
    print(json.dumps(result["posts"], indent=2, ensure_ascii=False))
