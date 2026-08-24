#!/usr/bin/env python3
# Patch current PlayTorrioTV/main to add AllDebrid support.
# Target checked against GitHub main on 2026-08-24.

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/ayman708-UX/PlayTorrioTV.git"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        print(f"  [already] {label}")
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"Patch point '{label}' expected exactly once, found {count}. "
            "The upstream file may have changed; use a PlayTorrioTV/main checkout "
            "matching 2026-08-24 or update this patch point."
        )
    print(f"  [patch]   {label}")
    return text.replace(old, new, 1)


def patch_file(path: Path, transforms) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing expected file: {path}")
    original = path.read_text(encoding="utf-8")
    text = original
    for old, new, label in transforms:
        text = replace_once(text, old, new, label)
    if text != original:
        backup = path.with_suffix(path.suffix + ".alldebrid.bak")
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding="utf-8")
        print(f"  [write]   {path}")
    else:
        print(f"  [unchanged] {path}")


def patch_settings_service(root: Path) -> None:
    path = root / "lib/services/settings_service.dart"
    transforms = [
        (
            "  String _debridProvider = 'real-debrid'; // 'real-debrid' or 'torbox'\n",
            "  String _debridProvider = 'real-debrid'; // 'real-debrid', 'torbox', or 'alldebrid'\n",
            "document supported debrid providers",
        ),
        (
            "  String _torboxApiKey = '';\n  String get torboxApiKey => _torboxApiKey;\n",
            "  String _torboxApiKey = '';\n  String get torboxApiKey => _torboxApiKey;\n\n  String _allDebridApiKey = '';\n  String get allDebridApiKey => _allDebridApiKey;\n",
            "add AllDebrid key model/getter",
        ),
        (
            "    _realDebridApiKey = _prefs.getString('rd_api_key') ?? '';\n    _torboxApiKey = _prefs.getString('tb_api_key') ?? '';\n",
            "    _realDebridApiKey = _prefs.getString('rd_api_key') ?? '';\n    _torboxApiKey = _prefs.getString('tb_api_key') ?? '';\n    _allDebridApiKey = _prefs.getString('ad_api_key') ?? '';\n",
            "load AllDebrid key",
        ),
        (
            "  void setTorboxApiKey(String value) {\n    _torboxApiKey = value;\n    _prefs.setString('tb_api_key', value);\n    notifyListeners();\n    _broadcastSettings();\n  }\n",
            "  void setTorboxApiKey(String value) {\n    _torboxApiKey = value;\n    _prefs.setString('tb_api_key', value);\n    notifyListeners();\n    _broadcastSettings();\n  }\n\n  void setAllDebridApiKey(String value) {\n    _allDebridApiKey = value.trim();\n    _prefs.setString('ad_api_key', _allDebridApiKey);\n    notifyListeners();\n    _broadcastSettings();\n  }\n",
            "add AllDebrid key setter",
        ),
        (
            "        'rd_api_key': _realDebridApiKey,\n        'tb_api_key': _torboxApiKey,\n",
            "        'rd_api_key': _realDebridApiKey,\n        'tb_api_key': _torboxApiKey,\n        'ad_api_key': _allDebridApiKey,\n",
            "include AllDebrid key in settings/profile JSON",
        ),
        (
            "    _realDebridApiKey = '';\n    _torboxApiKey = '';\n    _cacheSizeMB = 512;\n",
            "    _realDebridApiKey = '';\n    _torboxApiKey = '';\n    _allDebridApiKey = '';\n    _cacheSizeMB = 512;\n",
            "reset AllDebrid in profile defaults",
        ),
        (
            "    _prefs.setString('rd_api_key', '');\n    _prefs.setString('tb_api_key', '');\n    _prefs.setInt('cache_size_mb', 512);\n",
            "    _prefs.setString('rd_api_key', '');\n    _prefs.setString('tb_api_key', '');\n    _prefs.setString('ad_api_key', '');\n    _prefs.setInt('cache_size_mb', 512);\n",
            "clear persisted AllDebrid key for new profile",
        ),
        (
            "    if (json.containsKey('tb_api_key')) {\n      _torboxApiKey = json['tb_api_key'] as String;\n      _prefs.setString('tb_api_key', _torboxApiKey);\n    }\n",
            "    if (json.containsKey('tb_api_key')) {\n      _torboxApiKey = json['tb_api_key'] as String;\n      _prefs.setString('tb_api_key', _torboxApiKey);\n    }\n    if (json.containsKey('ad_api_key')) {\n      _allDebridApiKey = (json['ad_api_key'] as String).trim();\n      _prefs.setString('ad_api_key', _allDebridApiKey);\n    }\n",
            "import/apply AllDebrid key",
        ),
        (
            "        <option value=\"real-debrid\">Real-Debrid</option>\n        <option value=\"torbox\">TorBox</option>\n",
            "        <option value=\"real-debrid\">Real-Debrid</option>\n        <option value=\"torbox\">TorBox</option>\n        <option value=\"alldebrid\">AllDebrid</option>\n",
            "add AllDebrid to remote provider selector",
        ),
        (
            "    <div class=\"card hidden\" id=\"tbKeyCard\">\n      <div class=\"setting-info\">\n        <h3>TorBox API Key</h3>\n        <p>Get it from torbox.app/settings</p>\n      </div>\n      <input type=\"text\" class=\"text-input\" id=\"tbApiKey\" placeholder=\"Paste your API key here\" autocomplete=\"off\">\n    </div>\n",
            "    <div class=\"card hidden\" id=\"tbKeyCard\">\n      <div class=\"setting-info\">\n        <h3>TorBox API Key</h3>\n        <p>Get it from torbox.app/settings</p>\n      </div>\n      <input type=\"text\" class=\"text-input\" id=\"tbApiKey\" placeholder=\"Paste your API key here\" autocomplete=\"off\">\n    </div>\n    <div class=\"card hidden\" id=\"adKeyCard\">\n      <div class=\"setting-info\">\n        <h3>AllDebrid API Key</h3>\n        <p>Paste a personal API key from your AllDebrid account</p>\n      </div>\n      <input type=\"text\" class=\"text-input\" id=\"adApiKey\" placeholder=\"Paste your API key here\" autocomplete=\"off\">\n    </div>\n",
            "add AllDebrid token field to remote settings",
        ),
        (
            "      document.getElementById('rdKeyCard').classList.toggle('hidden', provider !== 'real-debrid');\n      document.getElementById('tbKeyCard').classList.toggle('hidden', provider !== 'torbox');\n",
            "      document.getElementById('rdKeyCard').classList.toggle('hidden', provider !== 'real-debrid');\n      document.getElementById('tbKeyCard').classList.toggle('hidden', provider !== 'torbox');\n      document.getElementById('adKeyCard').classList.toggle('hidden', provider !== 'alldebrid');\n",
            "toggle AllDebrid token UI",
        ),
        (
            "          document.getElementById('rdApiKey').value = msg.data.rd_api_key || '';\n          document.getElementById('tbApiKey').value = msg.data.tb_api_key || '';\n",
            "          document.getElementById('rdApiKey').value = msg.data.rd_api_key || '';\n          document.getElementById('tbApiKey').value = msg.data.tb_api_key || '';\n          document.getElementById('adApiKey').value = msg.data.ad_api_key || '';\n",
            "hydrate AllDebrid token in remote UI",
        ),
        (
            "    let rdTimer, tbTimer;\n",
            "    let rdTimer, tbTimer, adTimer;\n",
            "add AllDebrid input debounce timer",
        ),
        (
            "    document.getElementById('tbApiKey').addEventListener('input', (e) => {\n      clearTimeout(tbTimer);\n      tbTimer = setTimeout(() => sendUpdate({ tb_api_key: e.target.value }), 500);\n    });\n",
            "    document.getElementById('tbApiKey').addEventListener('input', (e) => {\n      clearTimeout(tbTimer);\n      tbTimer = setTimeout(() => sendUpdate({ tb_api_key: e.target.value }), 500);\n    });\n    document.getElementById('adApiKey').addEventListener('input', (e) => {\n      clearTimeout(adTimer);\n      adTimer = setTimeout(() => sendUpdate({ ad_api_key: e.target.value }), 500);\n    });\n",
            "save AllDebrid token from remote UI",
        ),
        (
            "        rd_api_key: document.getElementById('rdApiKey').value,\n        tb_api_key: document.getElementById('tbApiKey').value,\n",
            "        rd_api_key: document.getElementById('rdApiKey').value,\n        tb_api_key: document.getElementById('tbApiKey').value,\n        ad_api_key: document.getElementById('adApiKey').value,\n",
            "include AllDebrid in remote settings export",
        ),
    ]
    patch_file(path, transforms)


def patch_settings_screen(root: Path) -> None:
    path = root / "lib/screens/settings_screen.dart"
    transforms = [
        (
            "                      options: const {'real-debrid': 'Real-Debrid', 'torbox': 'TorBox'},\n",
            "                      options: const {\n                        'real-debrid': 'Real-Debrid',\n                        'torbox': 'TorBox',\n                        'alldebrid': 'AllDebrid',\n                      },\n",
            "add AllDebrid to TV provider selector",
        ),
        (
            "                      title: _settings.debridProvider == 'real-debrid' ? 'Real-Debrid API Key' : 'TorBox API Key',\n                      subtitle: _settings.debridProvider == 'real-debrid'\n                          ? (_settings.realDebridApiKey.isEmpty ? 'Not set — configure via phone' : 'Configured')\n                          : (_settings.torboxApiKey.isEmpty ? 'Not set — configure via phone' : 'Configured'),\n",
            "                      title: _settings.debridProvider == 'real-debrid'\n                          ? 'Real-Debrid API Key'\n                          : _settings.debridProvider == 'torbox'\n                              ? 'TorBox API Key'\n                              : 'AllDebrid API Key',\n                      subtitle: _settings.debridProvider == 'real-debrid'\n                          ? (_settings.realDebridApiKey.isEmpty ? 'Not set — configure via phone' : 'Configured')\n                          : _settings.debridProvider == 'torbox'\n                              ? (_settings.torboxApiKey.isEmpty ? 'Not set — configure via phone' : 'Configured')\n                              : (_settings.allDebridApiKey.isEmpty ? 'Not set — configure via phone' : 'Configured'),\n",
            "show AllDebrid key status on TV settings",
        ),
    ]
    patch_file(path, transforms)


ALLDEBRID_IMPL = r'''  // ── AllDebrid ──────────────────────────────────────────────────
  // Current AllDebrid API flow:
  //   upload magnet -> poll v4.1 status -> get v4 file tree -> unlock file link.
  static Future<String> _resolveAllDebrid(
    String magnetUri,
    String apiKey, {
    EpisodeTarget? episode,
    int? fileIdx,
  }) async {
    final key = apiKey.trim();
    if (key.isEmpty) throw DebridException('AllDebrid API key not set');

    final headers = {'Authorization': 'Bearer $key'};

    // 1. Upload magnet.
    final uploadRes = await http.post(
      Uri.parse('$_adBase/v4/magnet/upload'),
      headers: headers,
      body: {'magnets[]': magnetUri},
    );
    final uploadData = _adDecode(uploadRes, 'magnet/upload');
    final uploadedMagnets = (uploadData['magnets'] as List?) ?? const [];
    if (uploadedMagnets.isEmpty || uploadedMagnets.first is! Map) {
      throw DebridException('AllDebrid: empty magnet upload response');
    }
    final uploaded = (uploadedMagnets.first as Map).cast<String, dynamic>();
    _adThrowEmbeddedError(uploaded, 'magnet/upload');
    final magnetId = uploaded['id'];
    if (magnetId == null) {
      throw DebridException('AllDebrid: magnet upload returned no id');
    }

    // 2. Wait until the magnet is ready.  AllDebrid statusCode 4 = Ready;
    // codes >= 5 are terminal errors.
    bool ready = uploaded['ready'] == true;
    for (int i = 0; !ready && i < 40; i++) {
      final statusRes = await http.post(
        Uri.parse('$_adBase/v4.1/magnet/status'),
        headers: headers,
        body: {'id': magnetId.toString()},
      );
      final statusData = _adDecode(statusRes, 'magnet/status');
      final magnets = statusData['magnets'];
      Map<String, dynamic>? magnet;
      if (magnets is List && magnets.isNotEmpty && magnets.first is Map) {
        magnet = (magnets.first as Map).cast<String, dynamic>();
      } else if (magnets is Map) {
        magnet = magnets.cast<String, dynamic>();
      }
      if (magnet == null) {
        throw DebridException('AllDebrid: magnet/status returned no magnet');
      }

      final statusCode = (magnet['statusCode'] as num?)?.toInt() ?? -1;
      if (statusCode == 4) {
        ready = true;
        break;
      }
      if (statusCode >= 5) {
        throw DebridException(
          'AllDebrid magnet failed: ${magnet['status'] ?? 'unknown'} (code $statusCode)',
        );
      }
      await Future.delayed(const Duration(seconds: 3));
    }
    if (!ready) {
      throw DebridException('AllDebrid: torrent not ready after waiting');
    }

    // 3. Get the recursive file tree and flatten it while preserving order.
    final filesRes = await http.post(
      Uri.parse('$_adBase/v4/magnet/files'),
      headers: headers,
      body: {'id[]': magnetId.toString()},
    );
    final filesData = _adDecode(filesRes, 'magnet/files');
    final fileMagnets = (filesData['magnets'] as List?) ?? const [];
    if (fileMagnets.isEmpty || fileMagnets.first is! Map) {
      throw DebridException('AllDebrid: empty magnet/files response');
    }
    final fileMagnet = (fileMagnets.first as Map).cast<String, dynamic>();
    _adThrowEmbeddedError(fileMagnet, 'magnet/files');

    final flatFiles = <Map<String, dynamic>>[];
    _flattenAdFiles((fileMagnet['files'] as List?) ?? const [], '', flatFiles);
    if (flatFiles.isEmpty) {
      throw DebridException('AllDebrid: no files in magnet');
    }

    final videoFiles = flatFiles
        .where((f) => _isVideoFile((f['path'] ?? '') as String))
        .toList();
    if (videoFiles.isEmpty) {
      throw DebridException('AllDebrid: no video files in magnet');
    }

    // 4. Pick the intended file.
    Map<String, dynamic>? picked;

    // TV episode match gets priority because torrent file indexes from some
    // Stremio addons can be missing or inconsistent across providers.
    if (episode != null) {
      for (final file in videoFiles) {
        final path = (file['path'] ?? '') as String;
        if (_isEpisodeMatch(path, episode.season, episode.episode)) {
          picked = file;
          break;
        }
      }
    }

    // Stremio fileIdx is normally a zero-based torrent file index.  The
    // flattened AllDebrid tree preserves file traversal order, so try that
    // exact index first.  Then try video-only indexing for addons that expose
    // an index after filtering non-video files.
    if (picked == null && fileIdx != null && fileIdx >= 0) {
      if (fileIdx < flatFiles.length &&
          _isVideoFile((flatFiles[fileIdx]['path'] ?? '') as String)) {
        picked = flatFiles[fileIdx];
      } else if (fileIdx < videoFiles.length) {
        picked = videoFiles[fileIdx];
      }
    }

    // Movie / final fallback: largest video file.
    if (picked == null) {
      int bestSize = -1;
      for (final file in videoFiles) {
        final size = (file['size'] as num?)?.toInt() ?? 0;
        if (size > bestSize) {
          bestSize = size;
          picked = file;
        }
      }
    }

    if (picked == null) {
      throw DebridException('AllDebrid: could not select a video file');
    }
    final unlockLink = (picked['link'] ?? '') as String;
    if (unlockLink.isEmpty) {
      throw DebridException('AllDebrid: selected file has no unlock link');
    }

    // 5. Turn AllDebrid's per-file link into the direct stream URL.
    final unlockRes = await http.post(
      Uri.parse('$_adBase/v4/link/unlock'),
      headers: headers,
      body: {'link': unlockLink},
    );
    final unlockData = _adDecode(unlockRes, 'link/unlock');
    final directUrl = unlockData['link'] as String?;
    if (directUrl == null || directUrl.isEmpty) {
      if (unlockData['delayed'] != null) {
        throw DebridException('AllDebrid returned a delayed link (not supported)');
      }
      throw DebridException('AllDebrid: link/unlock returned no link');
    }
    return directUrl;
  }

  static Map<String, dynamic> _adDecode(http.Response res, String endpoint) {
    Map<String, dynamic> body;
    try {
      final decoded = jsonDecode(res.body);
      if (decoded is! Map) {
        throw const FormatException('response is not an object');
      }
      body = decoded.cast<String, dynamic>();
    } catch (e) {
      throw DebridException(
        'AllDebrid $endpoint returned invalid JSON (${res.statusCode}): $e',
      );
    }

    if (body['status'] == 'error') {
      final error = body['error'];
      if (error is Map) {
        throw DebridException(
          'AllDebrid $endpoint: ${error['code'] ?? 'error'} - ${error['message'] ?? res.body}',
        );
      }
      throw DebridException('AllDebrid $endpoint: ${res.body}');
    }
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw DebridException(
        'AllDebrid $endpoint failed: ${res.statusCode} ${res.body}',
      );
    }

    final data = body['data'];
    if (data is! Map) {
      throw DebridException('AllDebrid $endpoint returned no data object');
    }
    return data.cast<String, dynamic>();
  }

  static void _adThrowEmbeddedError(Map<String, dynamic> object, String endpoint) {
    final error = object['error'];
    if (error is Map) {
      throw DebridException(
        'AllDebrid $endpoint: ${error['code'] ?? 'error'} - ${error['message'] ?? 'request failed'}',
      );
    }
  }

  static void _flattenAdFiles(
    List<dynamic> nodes,
    String prefix,
    List<Map<String, dynamic>> out,
  ) {
    for (final node in nodes) {
      if (node is! Map) continue;
      final name = (node['n'] as String?) ?? '';
      final path = prefix.isEmpty ? name : '$prefix/$name';
      final children = node['e'];
      if (children is List) {
        _flattenAdFiles(children, path, out);
      } else {
        out.add({
          'path': path,
          'size': (node['s'] as num?)?.toInt() ?? 0,
          'link': (node['l'] as String?) ?? '',
        });
      }
    }
  }

'''


def patch_debrid_service(root: Path) -> None:
    path = root / "lib/services/debrid_service.dart"
    transforms = [
        (
            "  static const _rdBase = 'https://api.real-debrid.com/rest/1.0';\n  static const _tbBase = 'https://api.torbox.app/v1/api';\n",
            "  static const _rdBase = 'https://api.real-debrid.com/rest/1.0';\n  static const _tbBase = 'https://api.torbox.app/v1/api';\n  static const _adBase = 'https://api.alldebrid.com';\n",
            "add AllDebrid API base",
        ),
        (
            "    if (settings.debridProvider == 'torbox') {\n      return _resolveTorbox(magnetUri, settings.torboxApiKey, episode: episode, fileIdx: fileIdx);\n    } else {\n      return _resolveRealDebrid(magnetUri, settings.realDebridApiKey, episode: episode, fileIdx: fileIdx);\n    }\n",
            "    if (settings.debridProvider == 'torbox') {\n      return _resolveTorbox(magnetUri, settings.torboxApiKey, episode: episode, fileIdx: fileIdx);\n    } else if (settings.debridProvider == 'alldebrid') {\n      return _resolveAllDebrid(magnetUri, settings.allDebridApiKey, episode: episode, fileIdx: fileIdx);\n    } else {\n      return _resolveRealDebrid(magnetUri, settings.realDebridApiKey, episode: episode, fileIdx: fileIdx);\n    }\n",
            "dispatch AllDebrid provider",
        ),
        (
            "  // ── TorBox ───────────────────────────────────────────────────\n",
            ALLDEBRID_IMPL + "  // ── TorBox ───────────────────────────────────────────────────\n",
            "add AllDebrid resolver/API flow",
        ),
    ]
    patch_file(path, transforms)


def validate_patched(root: Path) -> None:
    checks = {
        root / "lib/services/settings_service.dart": [
            "String _allDebridApiKey = '';",
            "_prefs.getString('ad_api_key')",
            "void setAllDebridApiKey(String value)",
            "'ad_api_key': _allDebridApiKey",
            '<option value="alldebrid">AllDebrid</option>',
            'id="adApiKey"',
            "provider !== 'alldebrid'",
            "ad_api_key: document.getElementById('adApiKey').value",
        ],
        root / "lib/screens/settings_screen.dart": [
            "'alldebrid': 'AllDebrid'",
            "'AllDebrid API Key'",
            "_settings.allDebridApiKey.isEmpty",
        ],
        root / "lib/services/debrid_service.dart": [
            "static const _adBase = 'https://api.alldebrid.com';",
            "settings.debridProvider == 'alldebrid'",
            "$_adBase/v4/magnet/upload",
            "$_adBase/v4.1/magnet/status",
            "$_adBase/v4/magnet/files",
            "$_adBase/v4/link/unlock",
            "_flattenAdFiles",
        ],
    }
    missing = []
    for path, needles in checks.items():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                missing.append(f"{path}: {needle}")
    if missing:
        raise RuntimeError("Validation failed:\n  " + "\n  ".join(missing))
    print("\nValidation: PASS — all AllDebrid integration markers are present.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add AllDebrid support to PlayTorrioTV (Google/Android TV)."
    )
    parser.add_argument(
        "repo",
        nargs="?",
        help="Path to an existing PlayTorrioTV checkout",
    )
    parser.add_argument(
        "--clone",
        metavar="DEST",
        help="Clone current PlayTorrioTV/main into DEST, then patch it",
    )
    args = parser.parse_args()

    if bool(args.repo) == bool(args.clone):
        parser.error("provide exactly one of: REPO_PATH or --clone DEST")

    if args.clone:
        root = Path(args.clone).expanduser().resolve()
        if root.exists() and any(root.iterdir()):
            raise RuntimeError(f"Clone destination is not empty: {root}")
        root.parent.mkdir(parents=True, exist_ok=True)
        print(f"Cloning {REPO_URL} -> {root}")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "main", REPO_URL, str(root)],
            check=True,
        )
    else:
        root = Path(args.repo).expanduser().resolve()

    if not (root / "pubspec.yaml").is_file():
        raise RuntimeError(f"Not a PlayTorrioTV project root: {root}")

    print(f"Patching: {root}")
    patch_settings_service(root)
    patch_settings_screen(root)
    patch_debrid_service(root)
    validate_patched(root)

    print("\nDone.")
    print("Build with:")
    print(f"  cd {root}")
    print("  flutter pub get")
    print("  flutter build apk --release --split-per-abi")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
