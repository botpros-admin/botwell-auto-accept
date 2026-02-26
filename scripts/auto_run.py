"""
Auto-accept terminal Run button + Accept All in Anti Gravity.
UIA Invoke with foreground lock — no focus stealing.
Expands "Step Requires Input" and scrolls to bottom when needed.
"""
import time
import sys
import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

import comtypes
import comtypes.client

CHECK_INTERVAL = 0.5

def setup_uia():
    comtypes.CoInitialize()
    comtypes.client.GetModule("UIAutomationCore.dll")
    from comtypes.gen.UIAutomationClient import IUIAutomation
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}",
        interface=IUIAutomation,
    )
    return uia

def invoke_with_focus_lock(el, InvokePattern):
    """Invoke element without stealing focus."""
    pattern = el.GetCurrentPattern(10000)
    invoke = pattern.QueryInterface(InvokePattern)
    user32.LockSetForegroundWindow(1)
    try:
        invoke.Invoke()
    finally:
        user32.LockSetForegroundWindow(2)

def find_buttons_by_name(uia, root, name):
    """Find buttons matching exact name."""
    cond = uia.CreateAndCondition(
        uia.CreatePropertyCondition(30003, 50000),  # Button
        uia.CreatePropertyCondition(30005, name),    # Name
    )
    return root.FindAll(4, cond)

def find_run_button(uia, root):
    """Find the Run button. Returns element or None."""
    cond_button = uia.CreatePropertyCondition(30003, 50000)
    buttons = root.FindAll(4, cond_button)
    for i in range(buttons.Length):
        el = buttons.GetElement(i)
        try:
            name = el.CurrentName
        except Exception:
            continue
        if name and name.startswith("Run") and "Alt" in name:
            return el
    return None

def find_accept_all(uia, root):
    """Find Accept All. Returns (element, parent) or None."""
    cond = uia.CreatePropertyCondition(30005, "Accept all")
    elements = root.FindAll(4, cond)
    walker = uia.ControlViewWalker
    for i in range(elements.Length):
        el = elements.GetElement(i)
        try:
            parent = walker.GetParentElement(el)
            return (el, parent)
        except Exception:
            return (el, None)
    return None

def find_allow_conversation(uia, root):
    """Find 'Allow This Conversation' button."""
    els = find_buttons_by_name(uia, root, "Allow This Conversation")
    if els.Length > 0:
        return els.GetElement(0)
    return None

def find_retry_button(uia, root):
    """Find 'Retry' button."""
    els = find_buttons_by_name(uia, root, "Retry")
    if els.Length > 0:
        return els.GetElement(0)
    return None

def find_keep_waiting(uia, root):
    """Find 'Keep Waiting' button."""
    els = find_buttons_by_name(uia, root, "Keep Waiting")
    if els.Length > 0:
        return els.GetElement(0)
    return None

def find_steps_requiring_input(uia, root):
    """Find 'Step Requires Input' elements by partial name match."""
    # Search for text elements containing 'Requires Input'
    cond = uia.CreatePropertyCondition(30003, 50020)  # Text type
    texts = root.FindAll(4, cond)
    results = []
    for i in range(texts.Length):
        el = texts.GetElement(i)
        try:
            name = el.CurrentName or ""
        except Exception:
            continue
        if "Requires Input" in name:
            results.append(el)
    return results

def click_expand_button(uia, root, InvokePattern):
    """Click the 'Expand' button if present."""
    els = find_buttons_by_name(uia, root, "Expand")
    for i in range(els.Length):
        el = els.GetElement(i)
        try:
            invoke_with_focus_lock(el, InvokePattern)
            return True
        except Exception:
            pass
    return False

def click_scroll_to_bottom(uia, root, InvokePattern):
    """Click the 'Scroll to bottom' button if present."""
    els = find_buttons_by_name(uia, root, "Scroll to bottom")
    for i in range(els.Length):
        el = els.GetElement(i)
        try:
            invoke_with_focus_lock(el, InvokePattern)
            return True
        except Exception:
            pass
    return False

def main():
    sys.stdout.reconfigure(line_buffering=True)
    print("Auto-Accept active")

    uia = setup_uia()
    from comtypes.gen.UIAutomationClient import IUIAutomationInvokePattern
    root = uia.GetRootElement()
    run_clicks = 0
    accept_clicks = 0
    allow_clicks = 0
    retry_clicks = 0

    while True:
        try:
            # Step 0a: Click "Allow This Conversation" if present
            allow_el = find_allow_conversation(uia, root)
            if allow_el:
                try:
                    invoke_with_focus_lock(allow_el, IUIAutomationInvokePattern)
                    allow_clicks += 1
                    print(f"[Allow:{allow_clicks}] Clicked Allow This Conversation")
                    time.sleep(0.3)
                except Exception:
                    pass

            # Step 0b: Click "Keep Waiting" if present
            kw_el = find_keep_waiting(uia, root)
            if kw_el:
                try:
                    invoke_with_focus_lock(kw_el, IUIAutomationInvokePattern)
                    print("[KeepWaiting] Clicked Keep Waiting")
                    time.sleep(0.3)
                except Exception:
                    pass

            # Step 0c: Click "Retry" if present
            retry_el = find_retry_button(uia, root)
            if retry_el:
                try:
                    invoke_with_focus_lock(retry_el, IUIAutomationInvokePattern)
                    retry_clicks += 1
                    print(f"[Retry:{retry_clicks}] Clicked Retry")
                    time.sleep(0.3)
                except Exception:
                    pass

            # Step 1: Check for "Step Requires Input" — expand it
            steps = find_steps_requiring_input(uia, root)
            if steps:
                # Click the "Expand" button to reveal the hidden Run button
                if click_expand_button(uia, root, IUIAutomationInvokePattern):
                    print("  Expanded step requiring input")
                    time.sleep(0.3)
                # Also try invoking the step text itself
                for step_el in steps:
                    try:
                        invoke_with_focus_lock(step_el, IUIAutomationInvokePattern)
                        print("  Clicked step-requires-input text")
                        time.sleep(0.3)
                    except Exception:
                        pass

            # Step 2: Look for Run / Accept All
            run_el = find_run_button(uia, root)
            accept_result = find_accept_all(uia, root)

            if not run_el and not accept_result:
                time.sleep(CHECK_INTERVAL)
                continue

            # Step 3: Try to invoke directly
            invoked_run = False
            invoked_accept = False

            if run_el:
                try:
                    invoke_with_focus_lock(run_el, IUIAutomationInvokePattern)
                    invoked_run = True
                    run_clicks += 1
                    print(f"[Run:{run_clicks}] Invoked Run button")
                except Exception:
                    pass

            if accept_result:
                el, parent = accept_result
                target = parent if parent else el
                try:
                    invoke_with_focus_lock(target, IUIAutomationInvokePattern)
                    invoked_accept = True
                    accept_clicks += 1
                    print(f"[Accept:{accept_clicks}] Invoked Accept all")
                except Exception:
                    pass

            # Step 4: If invoke failed, scroll to bottom and retry
            if (run_el and not invoked_run) or (accept_result and not invoked_accept):
                if click_scroll_to_bottom(uia, root, IUIAutomationInvokePattern):
                    print("  Scrolled to bottom, retrying...")
                    time.sleep(0.3)

                    if run_el and not invoked_run:
                        run_el = find_run_button(uia, root)
                        if run_el:
                            try:
                                invoke_with_focus_lock(run_el, IUIAutomationInvokePattern)
                                run_clicks += 1
                                print(f"[Run:{run_clicks}] Invoked Run (after scroll)")
                            except Exception:
                                pass

                    if accept_result and not invoked_accept:
                        accept_result = find_accept_all(uia, root)
                        if accept_result:
                            el, parent = accept_result
                            target = parent if parent else el
                            try:
                                invoke_with_focus_lock(target, IUIAutomationInvokePattern)
                                accept_clicks += 1
                                print(f"[Accept:{accept_clicks}] Invoked Accept all (after scroll)")
                            except Exception:
                                pass

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print(f"Stopped. Run: {run_clicks}, Accept: {accept_clicks}")
            comtypes.CoUninitialize()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
