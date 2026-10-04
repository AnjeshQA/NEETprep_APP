"""Brings the Android emulator window to the front (un-minimizes it first). Never raises."""
import logging
import shutil
import subprocess

log = logging.getLogger(__name__)

_WINDOW_TITLE = "Android Emulator"


def bring_emulator_to_front() -> bool:
    """Returns True if a window was found and activated. Failures are logged, not raised."""
    try:
        from Xlib import X, display, protocol
    except ImportError:
        return _wmctrl_fallback()
    try:
        d = display.Display()
        root = d.screen().root
        net_list = d.intern_atom('_NET_CLIENT_LIST')
        net_name = d.intern_atom('_NET_WM_NAME')
        prop = root.get_full_property(net_list, X.AnyPropertyType)
        for wid in (prop.value if prop else []):
            win = d.create_resource_object('window', wid)
            name = win.get_full_property(net_name, X.AnyPropertyType)
            title = name.value.decode(errors='ignore') if name else ''
            if _WINDOW_TITLE not in title or ':' not in title:  # skip the small toolbar window
                continue
            win.map()  # un-minimize
            event = protocol.event.ClientMessage(
                window=win, client_type=d.intern_atom('_NET_ACTIVE_WINDOW'),
                data=(32, [2, X.CurrentTime, 0, 0, 0]))  # source=2 (pager) so the WM allows focus
            root.send_event(event, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
            d.flush()
            log.info(f"Emulator window brought to front: '{title}'")
            return True
        log.warning("Emulator window not found on screen (is the emulator running with a visible window?)")
    except Exception as e:
        log.warning(f"Could not bring emulator to front: {e}")
    return False


def _wmctrl_fallback() -> bool:
    if shutil.which("wmctrl"):
        return subprocess.run(["wmctrl", "-a", _WINDOW_TITLE]).returncode == 0
    log.warning("Could not bring emulator to front: install python-xlib (pip install python-xlib) or wmctrl")
    return False
