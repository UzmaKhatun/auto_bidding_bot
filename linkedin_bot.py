from playwright.sync_api import sync_playwright
import time
import random
import os


def human_delay(min=2, max=5):
    time.sleep(random.uniform(min, max))


def get_browser(p):
    session_path = os.path.abspath("./session")
    return p.chromium.launch_persistent_context(
        user_data_dir=session_path,
        headless=False,
        slow_mo=100,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled"
        ]
    )


# ─────────────────────────────────────────
# FUNCTION 1 — Search LinkedIn Posts
# ─────────────────────────────────────────
def search_posts():
    results = []
    browser = None

    try:
        with sync_playwright() as p:
            browser = get_browser(p)
            page = browser.new_page()

            print("Opening LinkedIn search...")
            page.goto(
                "https://www.linkedin.com/search/results/content/?keywords=looking%20for%20developer&sortBy=date",
                wait_until="domcontentloaded",
                timeout=30000
            )

            human_delay(4, 6)
            page.screenshot(path="search_debug.png")

            # Scroll to load posts
            page.evaluate("window.scrollBy(0, 800)")
            human_delay(2, 3)

            # Wait for posts
            page.wait_for_selector(
                ".update-components-text",
                timeout=15000
            )

            posts = page.query_selector_all(
                ".update-components-text"
            )
            print(f"Total posts found: {len(posts)}")

            for post in posts[:1]:   # only return 1 post per run
                try:
                    # Get post text
                    content = post.query_selector(
                        "span.break-words"
                    )

                    # Get parent with URN
                    post_urn = post.evaluate("""
                        el => {
                            let parent = el.closest('[data-urn]');
                            return parent ? 
                            parent.getAttribute('data-urn') : '';
                        }
                    """)

                    if content and post_urn:
                        post_text = content.inner_text().strip()
                        post_id = post_urn.split(
                            "activity:"
                        )[-1] if "activity:" in post_urn else post_urn
                        # post_url = f"https://www.linkedin.com/feed/update/{post_urn}"
                        if "urn:li:activity:" in post_urn:
                            post_url = f"https://www.linkedin.com/feed/update/{post_urn}"
                        else:
                            post_url = f"https://www.linkedin.com/feed/update/urn:li:activity:{post_urn}"

                        if len(post_text) > 20:
                            results.append({
                                "post_id": post_id,
                                "post_url": post_url,
                                "post_content": post_text
                            })
                            print(f"✅ Found: {post_text[:60]}...")

                except Exception as e:
                    print(f"Post error: {e}")
                    continue

    except Exception as e:
        print(f"Search error: {str(e)}")

    finally:
        if browser:
            try:
                browser.close()
            except:
                pass
        # Always wait after closing
        time.sleep(5)

    return {"posts": results}


# ─────────────────────────────────────────
# FUNCTION 2 — Post Comment
# ─────────────────────────────────────────
def post_comment(post_url, comment):
    browser = None

    try:
        time.sleep(5)

        with sync_playwright() as p:
            browser = get_browser(p)
            page = browser.new_page()

            print(f"Opening post: {post_url}")
            page.goto(
                post_url,
                wait_until="domcontentloaded",
                timeout=30000
            )
            human_delay(4, 6)

            page.screenshot(path="post_debug.png")

            # Scroll to comments section
            page.evaluate("window.scrollBy(0, 400)")
            human_delay(2, 3)

            # Click comment trigger if needed
            try:
                comment_trigger = page.wait_for_selector(
                    "button.comment-button",
                    timeout=5000
                )
                if comment_trigger:
                    comment_trigger.click()
                    human_delay(2, 3)
                    print("✅ Clicked comment trigger")
            except:
                print("Comment box already visible")

            # Find TipTap editor
            try:
                page.wait_for_selector(
                    "div.tiptap.ProseMirror",
                    timeout=10000,
                    state="visible"
                )
                editor = page.query_selector(
                    "div.tiptap.ProseMirror"
                )
                print("✅ Found TipTap editor")
            except:
                editor = page.query_selector(
                    "div[role='textbox']"
                )
                print("✅ Found textbox fallback")

            if editor:
                # Click to focus
                editor.click()
                human_delay(1, 2)

                # Clear any existing text
                page.keyboard.press("Control+a")
                page.keyboard.press("Delete")
                human_delay(0.5, 1)

                # Inject text via execCommand
                # so LinkedIn registers it as real input
                safe_comment = comment.replace(
                    '`', "'"
                ).replace('\\', '')

                page.evaluate(f"""
                    () => {{
                        const editor = document.querySelector(
                            'div.tiptap.ProseMirror'
                        );
                        if (editor) {{
                            editor.focus();
                            document.execCommand(
                                'insertText',
                                false,
                                `{safe_comment}`
                            );
                        }}
                    }}
                """)

                human_delay(2, 3)
                page.screenshot(path="before_submit.png")
                print("Before submit saved")

                # Find and click correct submit button
                # Button index 1 is always the submit button
                # 0 = toolbar Comment
                # 1 = submit Comment (correct one)
                # 2 = be first to comment
                try:
                    all_comment_btns = page.locator(
                        "button", has_text="Comment"
                    ).all()

                    print(f"Total buttons: {len(all_comment_btns)}")

                    submit_btn = all_comment_btns[1]
                    submit_btn.scroll_into_view_if_needed()
                    human_delay(1, 2)
                    submit_btn.click()
                    print("✅ Clicked submit button")

                    human_delay(4, 6)
                    page.screenshot(path="after_comment.png")
                    print("After submit saved")

                    # Verify comment was posted
                    editor_content = page.evaluate("""
                        () => {
                            const editor = document.querySelector(
                                'div.tiptap.ProseMirror'
                            );
                            return editor ? 
                            editor.innerText.trim() : '';
                        }
                    """)

                    if editor_content == '':
                        print("✅ Comment posted successfully!")
                        page.close()
                        browser.close()
                        return {
                            "status": "success",
                            "post_url": post_url
                        }
                    else:
                        print("❌ Comment box still has text")
                        page.close()
                        browser.close()
                        return {
                            "status": "failed",
                            "reason": "comment not submitted"
                        }

                except Exception as e:
                    print(f"Submit error: {str(e)}")
                    page.close()
                    browser.close()
                    return {
                        "status": "error",
                        "reason": str(e)
                    }

            else:
                print("❌ Editor not found")
                page.close()
                browser.close()
                return {
                    "status": "failed",
                    "reason": "editor not found"
                }

    except Exception as e:
        print(f"Comment error: {str(e)}")
        return {
            "status": "error",
            "reason": str(e)
        }

    finally:
        if browser:
            try:
                browser.close()
            except:
                pass
        time.sleep(10)