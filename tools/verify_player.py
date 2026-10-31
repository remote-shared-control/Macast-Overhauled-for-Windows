"""Render a silent local test pattern using D3D11, capture ModernZ and test ASS planes.

This optional developer check briefly opens the player's video window. It does
not contact media services or require a phone. Outputs remain under build/.
"""

import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUTPUT = ROOT / 'build/player-check'
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ['MACAST_CONFIG_DIR'] = str(OUTPUT / 'config')

import cherrypy
from macast.protocol import Protocol
from macast_renderer.mpv import MPVRenderer
from macast_renderer.ipc import WindowsQueryClient


def until(condition, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.03)
    raise TimeoutError('Player state did not become ready')


def main():
    # Test the player binary shipped in the portable bundle.
    player = ROOT / 'dist/Macast-Overhauled-Windows/_internal/bin/mpv.exe'
    protocol = Protocol()
    get_protocol = lambda: protocol
    cherrypy.engine.subscribe('get_protocol', get_protocol)
    renderer = MPVRenderer(path=str(player))
    client = None
    report = {'ok': False}
    try:
        renderer.start()
        until(lambda: renderer.ipc_once_connected)
        client = WindowsQueryClient(renderer.mpv_sock)
        client.command(['set_property', 'autofit', '960x540'])
        renderer.set_media_url_options('av://lavfi:testsrc=size=960x540:rate=25', options={'pause': 'yes'})
        until(lambda: renderer._file_loaded)
        subtitles = OUTPUT / 'normal.srt'
        subtitles.write_text('1\n00:00:00,000 --> 00:00:20,000\nNormal subtitles / 普通字幕\n', encoding='utf-8')
        danmaku = OUTPUT / 'danmaku.ass'
        danmaku.write_text('[Script Info]\nScriptType: v4.00+\nPlayResX: 960\nPlayResY: 540\n'
            '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
            'Style: Default,sans-serif,26,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,8,20,20,30,1\n'
            '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
            'Dialogue: 0,0:00:00.00,0:00:20.00,Default,,0,0,0,,Danmaku / 独立弹幕\n', encoding='utf-8')
        renderer.set_media_sub_file({'url': str(subtitles), 'title': 'Normal subtitles'})
        renderer.set_media_danmaku_file({'url': str(danmaku), 'title': 'Danmaku'})
        until(lambda: bool(client.command(['get_property', 'user-data/macast/danmaku/available'])))
        renderer.set_media_title('Macast-Overhauled for Windows')
        client.command(['script-message-to', 'modernz', 'osc-visibility', 'always', 'true'])
        renderer.set_media_sub_show(False)
        time.sleep(0.1)
        report['danmaku_independent'] = client.command(['get_property', 'secondary-sub-visibility']) is True
        renderer.set_media_sub_show(True)
        renderer.set_media_danmaku_show(False)
        time.sleep(0.1)
        report['subtitles_independent'] = client.command(['get_property', 'sub-visibility']) is True
        renderer.set_media_danmaku_show(True)
        time.sleep(0.4)
        report['final_danmaku_enabled'] = client.command(['get_property', 'user-data/macast/danmaku/enabled'])
        report['final_secondary_visible'] = client.command(['get_property', 'secondary-sub-visibility'])
        report['secondary_sid'] = client.command(['get_property', 'secondary-sid'])
        report['secondary_text'] = client.command(['get_property', 'secondary-sub-text'])
        report['secondary_position'] = client.command(['get_property', 'secondary-sub-pos'])
        report['subtitles_above_controls'] = client.command(['get_property', 'sub-pos']) < 100
        report['video_output'] = client.command(['get_property', 'current-vo'])
        report['video_params'] = client.command(['get_property', 'video-out-params'])
        report['gpu_api'] = client.command(['get_property', 'gpu-api'])
        client.command(['screenshot-to-file', str(OUTPUT / 'modernz-windows.png'), 'window'])
        report['ok'] = bool(report['video_output'] == 'gpu' and report['subtitles_above_controls'] and report['danmaku_independent']
                            and report['subtitles_independent'] and report['final_danmaku_enabled']
                            and report['final_secondary_visible'] and report['secondary_position'] == 100
                            and (OUTPUT / 'modernz-windows.png').is_file())
    finally:
        if client:
            client.close()
        renderer.stop()
        cherrypy.engine.unsubscribe('get_protocol', get_protocol)
        (OUTPUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if not report['ok']:
        raise RuntimeError(report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
