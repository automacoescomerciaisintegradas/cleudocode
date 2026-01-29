import sys
import os
import json
import asyncio
import argparse
from playwright.async_api import async_playwright

SESSION_DIR = os.path.join(os.getcwd(), ".agent-browser-sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

def get_session_path(session_name):
    return os.path.join(SESSION_DIR, f"{session_name}.json")

def get_refs_path(session_name):
    return os.path.join(SESSION_DIR, f"{session_name}_refs.json")

async def load_state(session_name):
    path = get_session_path(session_name)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {"cookies": [], "origins": [], "url": "about:blank"}

async def save_state(session_name, context, page):
    state = await context.storage_state()
    state["url"] = page.url
    path = get_session_path(session_name)
    with open(path, 'w') as f:
        json.dump(state, f)

async def load_refs(session_name):
    path = get_refs_path(session_name)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_refs(session_name, refs):
    path = get_refs_path(session_name)
    with open(path, 'w') as f:
        json.dump(refs, f)

async def run_command(args, cmd_args):
    session_name = args.session
    command = args.cmd
    
    async with async_playwright() as p:
        # Configuration
        headless = not args.headed
        browser = await p.chromium.launch(headless=headless)
        
        state_data = await load_state(session_name)
        storage_state = {k: v for k, v in state_data.items() if k != "url"}
        
        context = await browser.new_context(storage_state=storage_state if state_data.get("cookies") else None)
        page = await context.new_page()
        
        # Restore URL if not 'open' command
        if command != "open" and state_data.get("url") and state_data["url"] != "about:blank":
            try:
                await page.goto(state_data["url"], wait_until="domcontentloaded")
            except:
                pass
        
        if not page:
            page = await context.new_page()

        try:
            # Navigation
            if command == "open":
                url = cmd_args[0]
                if not url.startswith("http"):
                    url = "https://" + url
                await page.goto(url)
                print(f"Opened {url}")
            
            elif command == "back":
                await page.go_back()
                print("Went back")
            
            elif command == "forward":
                await page.go_forward()
                print("Went forward")
            
            elif command == "reload":
                await page.reload()
                print("Reloaded")

            elif command == "snapshot":
                interactive_only = "-i" in cmd_args or "--interactive" in cmd_args
                elements = await page.evaluate("""
                    () => {
                        const interactives = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"], [role="checkbox"], [role="radio"]'));
                        return interactives.map((el, i) => {
                            const rect = el.getBoundingClientRect();
                            if (rect.width === 0 || rect.height === 0 || window.getComputedStyle(el).display === 'none') return null;
                            
                            let text = el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '';
                            text = text.trim().substring(0, 50);
                            
                            let selector = el.tagName.toLowerCase();
                            if (el.id) selector += `#${CSS.escape(el.id)}`;
                            else if (el.name) selector += `[name="${CSS.escape(el.name)}"]`;
                            
                            return {
                                tag: el.tagName,
                                text: text,
                                role: el.getAttribute('role') || el.tagName.toLowerCase(),
                                selector: selector.substring(0, 200)
                            };
                        }).filter(x => x !== null);
                    }
                """)
                
                refs = {}
                for i, el in enumerate(elements):
                    ref = f"e{i+1}"
                    refs[ref] = el['selector']
                    if not args.json:
                        # Clean text for console encoding
                        safe_text = el['text'].encode('ascii', 'ignore').decode('ascii')
                        tag = el['tag'].upper()
                        print(f"{tag} \"{safe_text}\" [ref={ref}]")
                
                if args.json:
                    print(json.dumps({"elements": elements, "refs": refs}))
                
                save_refs(session_name, refs)
                
            # Find / Semantic Locators
            elif command == "find":
                # agent-browser find role button click --name "Submit"
                type = cmd_args[0]
                value = cmd_args[1]
                action = cmd_args[2]
                
                locator = None
                if type == "role":
                    locator = page.get_by_role(value, name=cmd_args[4] if "--name" in cmd_args else None)
                elif type == "text":
                    locator = page.get_by_text(value)
                elif type == "label":
                    locator = page.get_by_label(value)
                elif type == "placeholder":
                    locator = page.get_by_placeholder(value)
                elif type == "alt":
                    locator = page.get_by_alt_text(value)
                elif type == "title":
                    locator = page.get_by_title(value)
                elif type == "testid":
                    locator = page.get_by_test_id(value)
                elif type == "first":
                    locator = page.locator(value).first
                elif type == "last":
                    locator = page.locator(value).last
                elif type == "nth":
                    locator = page.locator(cmd_args[2]).nth(int(value))
                    action = cmd_args[3] if len(cmd_args) > 3 else "text"

                if locator:
                    if action == "click":
                        await locator.click()
                        print(f"Found and clicked {value}")
                    elif action == "fill":
                        text = cmd_args[3]
                        await locator.fill(text)
                        print(f"Found and filled {value} with {text}")
                    elif action == "text":
                        print(await locator.inner_text())
                else:
                    print(f"Locator {type} {value} failed.")

            # Browser Settings
            elif command == "set":
                sub = cmd_args[0]
                if sub == "viewport":
                    w, h = int(cmd_args[1]), int(cmd_args[2])
                    await page.set_viewport_size({"width": w, "height": h})
                    print(f"Viewport set to {w}x{h}")
                elif sub == "device":
                    # Device emulation is usually done at context creation, 
                    # but we can try to resize for now.
                    print("Device emulation currently requires a new session.")
                elif sub == "geo":
                    lat, lng = float(cmd_args[1]), float(cmd_args[2])
                    await context.set_geolocation({"latitude": lat, "longitude": lng})
                    print(f"Geo set to {lat}, {lng}")
                elif sub == "offline":
                    is_off = cmd_args[1] == "on"
                    await context.set_offline(is_off)
                    print(f"Offline mode: {is_off}")
                elif sub == "media":
                    await page.emulate_media(color_scheme=cmd_args[1])
                    print(f"Media set to {cmd_args[1]}")

            # Get Info Improvements
            elif command == "get":
                sub = cmd_args[0]
                if sub == "html":
                    ref_id = cmd_args[1].replace("@", "")
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    print(await page.inner_html(selector))
                elif sub == "value":
                    ref_id = cmd_args[1].replace("@", "")
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    print(await page.input_value(selector))
                elif sub == "attr":
                    ref_id = cmd_args[1].replace("@", "")
                    attr = cmd_args[2]
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    print(await page.get_attribute(selector, attr))
                elif sub == "count":
                    selector = cmd_args[1]
                    print(await page.locator(selector).count())
                elif sub == "box":
                    ref_id = cmd_args[1].replace("@", "")
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    box = await page.locator(selector).bounding_box()
                    print(json.dumps(box))
                elif sub == "text":
                    ref_id = cmd_args[1].replace("@", "")
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    print(await page.inner_text(selector))
                elif sub == "url":
                    print(page.url)
                elif sub == "title":
                    print(await page.title())

            # Check State
            elif command == "is":
                sub = cmd_args[0]
                ref_id = cmd_args[1].replace("@", "")
                refs = await load_refs(session_name)
                selector = refs.get(ref_id)
                if sub == "visible":
                    print(await page.is_visible(selector))
                elif sub == "enabled":
                    print(await page.is_enabled(selector))
                elif sub == "checked":
                    print(await page.is_checked(selector))

            # Tabs & Windows
            elif command == "tab":
                if not cmd_args:
                    # List tabs
                    pages = context.pages
                    for i, p in enumerate(pages):
                        print(f"Tab {i}: {p.url}")
                elif cmd_args[0] == "new":
                    new_page = await context.new_page()
                    if len(cmd_args) > 1:
                        await new_page.goto(cmd_args[1])
                    print(f"New tab opened: {new_page.url}")
                elif cmd_args[0].isdigit():
                    idx = int(cmd_args[0])
                    if idx < len(context.pages):
                        page = context.pages[idx]
                        print(f"Switched to tab {idx}")
                    else:
                        print("Tab index out of range")
                elif cmd_args[0] == "close":
                    await page.close()
                    print("Tab closed")

            elif command == "window" and cmd_args[0] == "new":
                # In Playwright, a new window is often a new context, 
                # but we'll just open a new page in current context for now.
                new_page = await context.new_page()
                print("New window/page opened")

            # Frames
            elif command == "frame":
                if cmd_args[0] == "main":
                    print("Back to main frame")
                    # In our model, we restart every time, so 'page' is always main.
                else:
                    selector = cmd_args[0]
                    frame = page.frame_locator(selector)
                    print(f"Switched context to frame {selector}")
                    # Note: Our simple script doesn't easily persist frame context across processes.

            # Dialogs
            elif command == "dialog":
                sub = cmd_args[0]
                if sub == "accept":
                    # Playwright handles dialogs automatically or via events.
                    # We'd need to set up the listener BEFORE the action.
                    print("Dialog listener setup required.")
                elif sub == "dismiss":
                    print("Dialog listener setup required.")

            elif command == "click":
                ref_id = cmd_args[0].replace("@", "")
                refs = await load_refs(session_name)
                selector = refs.get(ref_id)
                if selector:
                    await page.click(selector)
                    print(f"Clicked {ref_id}")
                else:
                    print(f"Ref {ref_id} not found.")
                    
            elif command == "fill":
                ref_id = cmd_args[0].replace("@", "")
                text = cmd_args[1]
                refs = await load_refs(session_name)
                selector = refs.get(ref_id)
                if selector:
                    await page.fill(selector, text)
                    print(f"Filled {ref_id} with {text}")
                else:
                    print(f"Ref {ref_id} not found.")

            elif command == "type":
                ref_id = cmd_args[0].replace("@", "")
                text = cmd_args[1]
                refs = await load_refs(session_name)
                selector = refs.get(ref_id)
                if selector:
                    await page.type(selector, text)
                    print(f"Typed {text} into {ref_id}")

            elif command == "wait":
                if cmd_args and cmd_args[0].startswith("@"):
                    ref_id = cmd_args[0].replace("@", "")
                    refs = await load_refs(session_name)
                    selector = refs.get(ref_id)
                    if selector:
                        await page.wait_for_selector(selector)
                        print(f"Waited for {ref_id}")
                elif cmd_args and cmd_args[0].isdigit():
                    await page.wait_for_timeout(int(cmd_args[0]))
                    print(f"Waited {cmd_args[0]}ms")
                else:
                    await page.wait_for_load_state("networkidle")
                    print("Waited for network idle")

            elif command == "screenshot":
                path = cmd_args[0] if cmd_args else "screenshot.png"
                full_page = "--full" in cmd_args
                await page.screenshot(path=path, full_page=full_page)
                print(f"Saved screenshot to {path}")

            elif command == "close":
                state_path = get_session_path(session_name)
                if os.path.exists(state_path):
                    os.remove(state_path)
                if os.path.exists(get_refs_path(session_name)):
                    os.remove(get_refs_path(session_name))
                print("Session closed.")
                await browser.close()
                return

            await save_state(session_name, context, page)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="agent-browser IA CLI")
    parser.add_argument("name", help="Must be 'IA'")
    parser.add_argument("cmd", help="Command to run")
    parser.add_argument("--session", default="default", help="Session name")
    parser.add_argument("--headed", action="store_true", help="Run headed")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args, cmd_args = parser.parse_known_args()
    
    if args.name != "IA":
        print("Usage: agent-browser IA <command> [args]")
        sys.exit(1)
        
    asyncio.run(run_command(args, cmd_args))
