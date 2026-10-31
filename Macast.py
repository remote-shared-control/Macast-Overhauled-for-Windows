# Copyright (c) 2021 by xfangfang. All Rights Reserved.
"""Windows portable entry point. Imports follow argument parsing and DPI setup."""

import argparse
import gettext
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys


def configure_logs(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = RotatingFileHandler(Path(directory) / 'application.log',
                                  maxBytes=1024 * 1024, backupCount=2, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    root.addHandler(handler)
    latency = logging.getLogger('MacastLatency')
    latency.propagate = False
    latency.setLevel(logging.INFO)
    timing = RotatingFileHandler(Path(directory) / 'latency.log',
                                 maxBytes=1024 * 1024, backupCount=1, encoding='utf-8')
    timing.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    latency.addHandler(timing)


def main():
    parser = argparse.ArgumentParser(description='Macast-Overhauled for Windows 10/11')
    parser.add_argument('--config-dir', help='Use a separate settings/plugin directory')
    parser.add_argument('--diagnose', metavar='JSON_FILE', help='Check resources and MPV IPC, write a report, then exit')
    parser.add_argument('--smoke-test', metavar='JSON_FILE', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.config_dir:
        os.environ['MACAST_CONFIG_DIR'] = str(Path(args.config_dir).resolve())
    # Set before importing the UI modules (macast/__init__ re-exports the GUI).
    if sys.platform == 'win32':
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except (AttributeError, OSError):
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
    from macast import Setting, SETTING_DIR
    from macast.resources import mpv_path
    Setting.mpv_default_path = mpv_path()
    if args.diagnose:
        from macast.diagnostics import diagnose
        report = diagnose()
        Path(args.diagnose).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return 0 if report['ok'] else 1
    instance = None
    if sys.platform == 'win32':
        from macast.windows import SingleInstance
        instance = SingleInstance(SETTING_DIR)
        if instance.already_running:
            instance.close()
            return 0
    configure_logs(SETTING_DIR)
    gettext.NullTranslations().install()
    try:
        if args.smoke_test:
            from macast.smoke import run_smoke
            report = run_smoke()
            Path(args.smoke_test).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            return 0 if report['ok'] else 1
        from macast.macast import gui
        gui(lang=gettext.gettext)
        return 0
    except Exception:
        logging.getLogger('Macast').exception('Startup failed')
        if args.smoke_test:
            import traceback
            Path(args.smoke_test).write_text(json.dumps({'ok': False, 'error': traceback.format_exc()}, indent=2), encoding='utf-8')
        elif sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                'Macast could not start. See application.log in:\n' + SETTING_DIR,
                'Macast-Overhauled', 0x10)
        return 1
    finally:
        if instance is not None:
            instance.close()


if __name__ == '__main__':
    raise SystemExit(main())
