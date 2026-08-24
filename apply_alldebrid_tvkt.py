#!/usr/bin/env python3
from pathlib import Path
import argparse, base64, json, subprocess, re

UPSTREAM = "https://github.com/ayman708-UX/PlayTorrioTVKT.git"
REPLACEMENTS = json.loads('{"data/AppPreferences.kt": [["private const val KEY_TORBOX_API_KEY = \\"torbox_api_key\\"", "private const val KEY_TORBOX_API_KEY = \\"torbox_api_key\\"\\n    private const val KEY_ALLDEBRID_API_KEY = \\"alldebrid_api_key\\"", "AllDebrid preference key"], ["/** \\"realdebrid\\" or \\"torbox\\" */", "/** \\"realdebrid\\", \\"torbox\\", or \\"alldebrid\\" */", "provider comment"], ["    var torboxApiKey: String\\n        get() = prefs.getString(KEY_TORBOX_API_KEY, \\"\\") ?: \\"\\"\\n        set(value) = prefs.edit().putString(KEY_TORBOX_API_KEY, value).apply()", "    var torboxApiKey: String\\n        get() = prefs.getString(KEY_TORBOX_API_KEY, \\"\\") ?: \\"\\"\\n        set(value) = prefs.edit().putString(KEY_TORBOX_API_KEY, value).apply()\\n\\n    var allDebridApiKey: String\\n        get() = prefs.getString(KEY_ALLDEBRID_API_KEY, \\"\\") ?: \\"\\"\\n        set(value) = prefs.edit().putString(KEY_ALLDEBRID_API_KEY, value).apply()", "AllDebrid preference property"]], "data/debrid/DebridResolver.kt": [["            \\"torbox\\" -> TorBoxClient.resolve(source, isMovie, season, episode)\\n            else -> null", "            \\"torbox\\" -> TorBoxClient.resolve(source, isMovie, season, episode)\\n            \\"alldebrid\\" -> AllDebridClient.resolve(source, isMovie, season, episode)\\n            else -> null", "AllDebrid resolver branch"]], "ui/screens/SettingsScreen.kt": [["                    torboxApiKey = AppPreferences.torboxApiKey,", "                    torboxApiKey = AppPreferences.torboxApiKey,\\n                    allDebridApiKey = AppPreferences.allDebridApiKey,", "remote settings AllDebrid state"], ["            var tbApiKey by remember { mutableStateOf(AppPreferences.torboxApiKey) }", "            var tbApiKey by remember { mutableStateOf(AppPreferences.torboxApiKey) }\\n            var adApiKey by remember { mutableStateOf(AppPreferences.allDebridApiKey) }", "TV AllDebrid local state"], ["listOf(\\"realdebrid\\" to \\"Real-Debrid\\", \\"torbox\\" to \\"TorBox\\")", "listOf(\\"realdebrid\\" to \\"Real-Debrid\\", \\"torbox\\" to \\"TorBox\\", \\"alldebrid\\" to \\"AllDebrid\\")", "TV provider selector"], ["                val (keyValue, keyLabel) = if (debridProvider == \\"realdebrid\\")\\n                    rdApiKey to \\"Real-Debrid API Key\\"\\n                else\\n                    tbApiKey to \\"TorBox API Key\\"", "                val (keyValue, keyLabel) = when (debridProvider) {\\n                    \\"realdebrid\\" -> rdApiKey to \\"Real-Debrid API Key\\"\\n                    \\"torbox\\" -> tbApiKey to \\"TorBox API Key\\"\\n                    \\"alldebrid\\" -> adApiKey to \\"AllDebrid API Key\\"\\n                    else -> \\"\\" to \\"API Key\\"\\n                }", "TV API key label/value"], ["                        if (debridProvider == \\"realdebrid\\") {\\n                            rdApiKey = v\\n                            AppPreferences.realDebridApiKey = v\\n                        } else {\\n                            tbApiKey = v\\n                            AppPreferences.torboxApiKey = v\\n                        }", "                        when (debridProvider) {\\n                            \\"realdebrid\\" -> {\\n                                rdApiKey = v\\n                                AppPreferences.realDebridApiKey = v\\n                            }\\n                            \\"torbox\\" -> {\\n                                tbApiKey = v\\n                                AppPreferences.torboxApiKey = v\\n                            }\\n                            \\"alldebrid\\" -> {\\n                                adApiKey = v\\n                                AppPreferences.allDebridApiKey = v\\n                            }\\n                        }", "TV AllDebrid key writer"], ["                                val debridKeyChanged = (change.proposedRealDebridApiKey != AppPreferences.realDebridApiKey) ||\\n                                    (change.proposedTorboxApiKey != AppPreferences.torboxApiKey)", "                                val debridKeyChanged = (change.proposedRealDebridApiKey != AppPreferences.realDebridApiKey) ||\\n                                    (change.proposedTorboxApiKey != AppPreferences.torboxApiKey) ||\\n                                    (change.proposedAllDebridApiKey != AppPreferences.allDebridApiKey)", "remote key-change detection"], ["                                                    AppPreferences.torboxApiKey = captured.proposedTorboxApiKey", "                                                    AppPreferences.torboxApiKey = captured.proposedTorboxApiKey\\n                                                    AppPreferences.allDebridApiKey = captured.proposedAllDebridApiKey", "remote AllDebrid apply"]], "server/SettingsConfigServer.kt": [["      val torboxApiKey: String = \\"\\",", "      val torboxApiKey: String = \\"\\",\\n      val allDebridApiKey: String = \\"\\",", "remote state field"], ["      val proposedTorboxApiKey: String = \\"\\",", "      val proposedTorboxApiKey: String = \\"\\",\\n      val proposedAllDebridApiKey: String = \\"\\",", "pending-change field"], ["            val torboxApiKey = (parsed[\\"torboxApiKey\\"] as? String) ?: current.torboxApiKey", "            val torboxApiKey = (parsed[\\"torboxApiKey\\"] as? String) ?: current.torboxApiKey\\n            val allDebridApiKey = (parsed[\\"allDebridApiKey\\"] as? String) ?: current.allDebridApiKey", "parse remote AllDebrid key"], ["              proposedTorboxApiKey = torboxApiKey,", "              proposedTorboxApiKey = torboxApiKey,\\n              proposedAllDebridApiKey = allDebridApiKey,", "pending remote AllDebrid key"], ["        <button class=\\"provider-btn\\" id=\\"btnTb\\" onclick=\\"selectProvider(\'torbox\')\\">TorBox</button>", "        <button class=\\"provider-btn\\" id=\\"btnTb\\" onclick=\\"selectProvider(\'torbox\')\\">TorBox</button>\\n        <button class=\\"provider-btn\\" id=\\"btnAd\\" onclick=\\"selectProvider(\'alldebrid\')\\">AllDebrid</button>", "phone AllDebrid provider button"], ["      <div id=\\"tbKeyRow\\" style=\\"display:none\\">\\n        <div class=\\"section-label\\" style=\\"margin-top:1.5rem\\">TorBox API Key</div>\\n        <input class=\\"api-key-input\\" type=\\"password\\" id=\\"tbApiKey\\" placeholder=\\"Paste your TorBox API key…\\" autocomplete=\\"off\\" spellcheck=\\"false\\">\\n      </div>", "      <div id=\\"tbKeyRow\\" style=\\"display:none\\">\\n        <div class=\\"section-label\\" style=\\"margin-top:1.5rem\\">TorBox API Key</div>\\n        <input class=\\"api-key-input\\" type=\\"password\\" id=\\"tbApiKey\\" placeholder=\\"Paste your TorBox API key…\\" autocomplete=\\"off\\" spellcheck=\\"false\\">\\n      </div>\\n      <div id=\\"adKeyRow\\" style=\\"display:none\\">\\n        <div class=\\"section-label\\" style=\\"margin-top:1.5rem\\">AllDebrid API Key</div>\\n        <input class=\\"api-key-input\\" type=\\"password\\" id=\\"adApiKey\\" placeholder=\\"Paste your AllDebrid API key…\\" autocomplete=\\"off\\" spellcheck=\\"false\\">\\n      </div>", "phone AllDebrid key input"], ["  document.getElementById(\'btnTb\').classList.toggle(\'active\', id === \'torbox\');\\n  document.getElementById(\'rdKeyRow\').style.display = id === \'realdebrid\' ? \'\' : \'none\';\\n  document.getElementById(\'tbKeyRow\').style.display = id === \'torbox\' ? \'\' : \'none\';", "  document.getElementById(\'btnTb\').classList.toggle(\'active\', id === \'torbox\');\\n  document.getElementById(\'btnAd\').classList.toggle(\'active\', id === \'alldebrid\');\\n  document.getElementById(\'rdKeyRow\').style.display = id === \'realdebrid\' ? \'\' : \'none\';\\n  document.getElementById(\'tbKeyRow\').style.display = id === \'torbox\' ? \'\' : \'none\';\\n  document.getElementById(\'adKeyRow\').style.display = id === \'alldebrid\' ? \'\' : \'none\';", "phone provider JS"], ["    document.getElementById(\'tbApiKey\').value = state.torboxApiKey || \'\';\\n    document.getElementById(\'rdApiKey\').oninput = function() { dirty = true; updateSaveButton(); };\\n    document.getElementById(\'tbApiKey\').oninput = function() { dirty = true; updateSaveButton(); };", "    document.getElementById(\'tbApiKey\').value = state.torboxApiKey || \'\';\\n    document.getElementById(\'adApiKey\').value = state.allDebridApiKey || \'\';\\n    document.getElementById(\'rdApiKey\').oninput = function() { dirty = true; updateSaveButton(); };\\n    document.getElementById(\'tbApiKey\').oninput = function() { dirty = true; updateSaveButton(); };\\n    document.getElementById(\'adApiKey\').oninput = function() { dirty = true; updateSaveButton(); };", "load remote AllDebrid key"], ["    torboxApiKey: document.getElementById(\'tbApiKey\').value.trim(),", "    torboxApiKey: document.getElementById(\'tbApiKey\').value.trim(),\\n    allDebridApiKey: document.getElementById(\'adApiKey\').value.trim(),", "save remote AllDebrid key"]]}')
CLIENT = base64.b64decode('cGFja2FnZSBjb20ucGxheXRvcnJpby50di5kYXRhLmRlYnJpZAoKaW1wb3J0IGFuZHJvaWQudXRpbC5Mb2cKaW1wb3J0IGNvbS5wbGF5dG9ycmlvLnR2LmRhdGEuQXBwUHJlZmVyZW5jZXMKaW1wb3J0IGtvdGxpbnguY29yb3V0aW5lcy5EaXNwYXRjaGVycwppbXBvcnQga290bGlueC5jb3JvdXRpbmVzLmRlbGF5CmltcG9ydCBrb3RsaW54LmNvcm91dGluZXMud2l0aENvbnRleHQKaW1wb3J0IG9raHR0cDMuRm9ybUJvZHkKaW1wb3J0IG9raHR0cDMuT2tIdHRwQ2xpZW50CmltcG9ydCBva2h0dHAzLlJlcXVlc3QKaW1wb3J0IG9yZy5qc29uLkpTT05BcnJheQppbXBvcnQgb3JnLmpzb24uSlNPTk9iamVjdAppbXBvcnQgamF2YS51dGlsLmNvbmN1cnJlbnQuVGltZVVuaXQKCm9iamVjdCBBbGxEZWJyaWRDbGllbnQgewogICAgcHJpdmF0ZSBjb25zdCB2YWwgVEFHID0gIkFsbERlYnJpZENsaWVudCIKICAgIHByaXZhdGUgY29uc3QgdmFsIEJBU0UgPSAiaHR0cHM6Ly9hcGkuYWxsZGVicmlkLmNvbSIKCiAgICBwcml2YXRlIHZhbCBodHRwID0gT2tIdHRwQ2xpZW50LkJ1aWxkZXIoKQogICAgICAgIC5jb25uZWN0VGltZW91dCgxNSwgVGltZVVuaXQuU0VDT05EUykKICAgICAgICAucmVhZFRpbWVvdXQoMzAsIFRpbWVVbml0LlNFQ09ORFMpCiAgICAgICAgLmJ1aWxkKCkKCiAgICBwcml2YXRlIGRhdGEgY2xhc3MgQWRGaWxlKHZhbCBwYXRoOiBTdHJpbmcsIHZhbCBzaXplOiBMb25nLCB2YWwgbGluazogU3RyaW5nKQoKICAgIHN1c3BlbmQgZnVuIHJlc29sdmUoCiAgICAgICAgbWFnbmV0VXJpOiBTdHJpbmcsCiAgICAgICAgaXNNb3ZpZTogQm9vbGVhbiA9IHRydWUsCiAgICAgICAgc2Vhc29uOiBJbnQ/ID0gbnVsbCwKICAgICAgICBlcGlzb2RlOiBJbnQ/ID0gbnVsbCwKICAgICk6IFN0cmluZz8gPSB3aXRoQ29udGV4dChEaXNwYXRjaGVycy5JTykgewogICAgICAgIHRyeSB7CiAgICAgICAgICAgIHZhbCBhcGlLZXkgPSBBcHBQcmVmZXJlbmNlcy5hbGxEZWJyaWRBcGlLZXkudHJpbSgpCiAgICAgICAgICAgIGlmIChhcGlLZXkuaXNFbXB0eSgpKSB7CiAgICAgICAgICAgICAgICBMb2cudyhUQUcsICJObyBBUEkga2V5IGNvbmZpZ3VyZWQiKQogICAgICAgICAgICAgICAgcmV0dXJuQHdpdGhDb250ZXh0IG51bGwKICAgICAgICAgICAgfQoKICAgICAgICAgICAgdmFsIHVwbG9hZCA9IHBvc3QoCiAgICAgICAgICAgICAgICAiJEJBU0UvdjQvbWFnbmV0L3VwbG9hZCIsCiAgICAgICAgICAgICAgICBhcGlLZXksCiAgICAgICAgICAgICAgICBGb3JtQm9keS5CdWlsZGVyKCkuYWRkKCJtYWduZXRzW10iLCBtYWduZXRVcmkpLmJ1aWxkKCkKICAgICAgICAgICAgKQogICAgICAgICAgICB2YWwgdXBsb2FkRGF0YSA9IGRlY29kZURhdGEodXBsb2FkKSA/OiByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICB2YWwgdXBsb2FkZWQgPSB1cGxvYWREYXRhLm9wdEpTT05BcnJheSgibWFnbmV0cyIpCiAgICAgICAgICAgIGlmICh1cGxvYWRlZCA9PSBudWxsIHx8IHVwbG9hZGVkLmxlbmd0aCgpID09IDApIHJldHVybkB3aXRoQ29udGV4dCBudWxsCgogICAgICAgICAgICB2YWwgbWFnbmV0ID0gdXBsb2FkZWQub3B0SlNPTk9iamVjdCgwKSA/OiByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICBtYWduZXQub3B0SlNPTk9iamVjdCgiZXJyb3IiKT8ubGV0IHsKICAgICAgICAgICAgICAgIExvZy53KFRBRywgIlVwbG9hZCBlcnJvcjogJHtpdC5vcHRTdHJpbmcoImNvZGUiKX0gLSAke2l0Lm9wdFN0cmluZygibWVzc2FnZSIpfSIpCiAgICAgICAgICAgICAgICByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICB9CgogICAgICAgICAgICB2YWwgbWFnbmV0SWQgPSBtYWduZXQub3B0TG9uZygiaWQiLCAtMUwpCiAgICAgICAgICAgIGlmIChtYWduZXRJZCA8PSAwKSByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAoKICAgICAgICAgICAgdmFyIHJlYWR5ID0gbWFnbmV0Lm9wdEJvb2xlYW4oInJlYWR5IiwgZmFsc2UpCiAgICAgICAgICAgIHZhciBhdHRlbXB0cyA9IDAKICAgICAgICAgICAgd2hpbGUgKCFyZWFkeSAmJiBhdHRlbXB0cyA8IDQwKSB7CiAgICAgICAgICAgICAgICB2YWwgc3RhdHVzID0gcG9zdCgKICAgICAgICAgICAgICAgICAgICAiJEJBU0UvdjQuMS9tYWduZXQvc3RhdHVzIiwKICAgICAgICAgICAgICAgICAgICBhcGlLZXksCiAgICAgICAgICAgICAgICAgICAgRm9ybUJvZHkuQnVpbGRlcigpLmFkZCgiaWQiLCBtYWduZXRJZC50b1N0cmluZygpKS5idWlsZCgpCiAgICAgICAgICAgICAgICApCiAgICAgICAgICAgICAgICB2YWwgZGF0YSA9IGRlY29kZURhdGEoc3RhdHVzKSA/OiByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICAgICAgdmFsIHZhbHVlID0gZGF0YS5vcHQoIm1hZ25ldHMiKQogICAgICAgICAgICAgICAgdmFsIG9iaiA9IHdoZW4gKHZhbHVlKSB7CiAgICAgICAgICAgICAgICAgICAgaXMgSlNPTk9iamVjdCAtPiB2YWx1ZQogICAgICAgICAgICAgICAgICAgIGlzIEpTT05BcnJheSAtPiBpZiAodmFsdWUubGVuZ3RoKCkgPiAwKSB2YWx1ZS5vcHRKU09OT2JqZWN0KDApIGVsc2UgbnVsbAogICAgICAgICAgICAgICAgICAgIGVsc2UgLT4gbnVsbAogICAgICAgICAgICAgICAgfQoKICAgICAgICAgICAgICAgIHZhbCBjb2RlID0gb2JqPy5vcHRJbnQoInN0YXR1c0NvZGUiLCAtMSkgPzogLTEKICAgICAgICAgICAgICAgIGlmIChjb2RlID09IDQpIHsKICAgICAgICAgICAgICAgICAgICByZWFkeSA9IHRydWUKICAgICAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgaWYgKGNvZGUgPj0gNSkgewogICAgICAgICAgICAgICAgICAgIExvZy53KFRBRywgIk1hZ25ldCBmYWlsZWQ6ICR7b2JqPy5vcHRTdHJpbmcoInN0YXR1cyIpfSAoJGNvZGUpIikKICAgICAgICAgICAgICAgICAgICByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgYXR0ZW1wdHMrKwogICAgICAgICAgICAgICAgZGVsYXkoMzAwMCkKICAgICAgICAgICAgfQogICAgICAgICAgICBpZiAoIXJlYWR5KSByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAoKICAgICAgICAgICAgdmFsIGZpbGVzUmVzcG9uc2UgPSBwb3N0KAogICAgICAgICAgICAgICAgIiRCQVNFL3Y0L21hZ25ldC9maWxlcyIsCiAgICAgICAgICAgICAgICBhcGlLZXksCiAgICAgICAgICAgICAgICBGb3JtQm9keS5CdWlsZGVyKCkuYWRkKCJpZFtdIiwgbWFnbmV0SWQudG9TdHJpbmcoKSkuYnVpbGQoKQogICAgICAgICAgICApCiAgICAgICAgICAgIHZhbCBmaWxlc0RhdGEgPSBkZWNvZGVEYXRhKGZpbGVzUmVzcG9uc2UpID86IHJldHVybkB3aXRoQ29udGV4dCBudWxsCiAgICAgICAgICAgIHZhbCBtYWduZXRzID0gZmlsZXNEYXRhLm9wdEpTT05BcnJheSgibWFnbmV0cyIpCiAgICAgICAgICAgIGlmIChtYWduZXRzID09IG51bGwgfHwgbWFnbmV0cy5sZW5ndGgoKSA9PSAwKSByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAoKICAgICAgICAgICAgdmFsIG1hZ25ldEZpbGVzID0gbWFnbmV0cy5vcHRKU09OT2JqZWN0KDApID86IHJldHVybkB3aXRoQ29udGV4dCBudWxsCiAgICAgICAgICAgIG1hZ25ldEZpbGVzLm9wdEpTT05PYmplY3QoImVycm9yIik/LmxldCB7CiAgICAgICAgICAgICAgICBMb2cudyhUQUcsICJGaWxlcyBlcnJvcjogJHtpdC5vcHRTdHJpbmcoImNvZGUiKX0gLSAke2l0Lm9wdFN0cmluZygibWVzc2FnZSIpfSIpCiAgICAgICAgICAgICAgICByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAogICAgICAgICAgICB9CgogICAgICAgICAgICB2YWwgZmxhdCA9IG11dGFibGVMaXN0T2Y8QWRGaWxlPigpCiAgICAgICAgICAgIGZsYXR0ZW4obWFnbmV0RmlsZXMub3B0SlNPTkFycmF5KCJmaWxlcyIpLCAiIiwgZmxhdCkKICAgICAgICAgICAgaWYgKGZsYXQuaXNFbXB0eSgpKSByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAoKICAgICAgICAgICAgdmFsIGNhbmRpZGF0ZXMgPSBmbGF0Lm1hcEluZGV4ZWQgeyBpbmRleCwgZiAtPiBUcmlwbGUoaW5kZXgsIGYucGF0aCwgZi5zaXplKSB9CiAgICAgICAgICAgIHZhbCBwaWNrZWRJbmRleCA9IEVwaXNvZGVGaWxlTWF0Y2hlci5waWNrRmlsZSgKICAgICAgICAgICAgICAgIGNhbmRpZGF0ZXMsIGlzTW92aWUsIHNlYXNvbiwgZXBpc29kZQogICAgICAgICAgICApID86IHJldHVybkB3aXRoQ29udGV4dCBudWxsCiAgICAgICAgICAgIHZhbCBwaWNrZWQgPSBmbGF0W3BpY2tlZEluZGV4XQogICAgICAgICAgICBpZiAocGlja2VkLmxpbmsuaXNCbGFuaygpKSByZXR1cm5Ad2l0aENvbnRleHQgbnVsbAoKICAgICAgICAgICAgdmFsIHVubG9ja1Jlc3BvbnNlID0gcG9zdCgKICAgICAgICAgICAgICAgICIkQkFTRS92NC9saW5rL3VubG9jayIsCiAgICAgICAgICAgICAgICBhcGlLZXksCiAgICAgICAgICAgICAgICBGb3JtQm9keS5CdWlsZGVyKCkuYWRkKCJsaW5rIiwgcGlja2VkLmxpbmspLmJ1aWxkKCkKICAgICAgICAgICAgKQogICAgICAgICAgICB2YWwgdW5sb2NrID0gZGVjb2RlRGF0YSh1bmxvY2tSZXNwb25zZSkgPzogcmV0dXJuQHdpdGhDb250ZXh0IG51bGwKICAgICAgICAgICAgdW5sb2NrLm9wdFN0cmluZygibGluayIsICIiKS50YWtlSWYgeyBpdC5pc05vdEJsYW5rKCkgfQogICAgICAgIH0gY2F0Y2ggKGU6IEV4Y2VwdGlvbikgewogICAgICAgICAgICBMb2cuZShUQUcsICJFcnJvciByZXNvbHZpbmcgdmlhIEFsbERlYnJpZCIsIGUpCiAgICAgICAgICAgIG51bGwKICAgICAgICB9CiAgICB9CgogICAgcHJpdmF0ZSBmdW4gcG9zdCh1cmw6IFN0cmluZywgYXBpS2V5OiBTdHJpbmcsIGJvZHk6IEZvcm1Cb2R5KTogU3RyaW5nPyB7CiAgICAgICAgdmFsIHJlcXVlc3QgPSBSZXF1ZXN0LkJ1aWxkZXIoKQogICAgICAgICAgICAudXJsKHVybCkKICAgICAgICAgICAgLmhlYWRlcigiQXV0aG9yaXphdGlvbiIsICJCZWFyZXIgJGFwaUtleSIpCiAgICAgICAgICAgIC5wb3N0KGJvZHkpCiAgICAgICAgICAgIC5idWlsZCgpCiAgICAgICAgcmV0dXJuIGh0dHAubmV3Q2FsbChyZXF1ZXN0KS5leGVjdXRlKCkudXNlIHsgaXQuYm9keT8uc3RyaW5nKCkgfQogICAgfQoKICAgIHByaXZhdGUgZnVuIGRlY29kZURhdGEocmF3OiBTdHJpbmc/KTogSlNPTk9iamVjdD8gewogICAgICAgIGlmIChyYXcuaXNOdWxsT3JCbGFuaygpKSByZXR1cm4gbnVsbAogICAgICAgIHZhbCByb290ID0gcnVuQ2F0Y2hpbmcgeyBKU09OT2JqZWN0KHJhdykgfS5nZXRPck51bGwoKSA/OiByZXR1cm4gbnVsbAogICAgICAgIGlmIChyb290Lm9wdFN0cmluZygic3RhdHVzIikgPT0gImVycm9yIikgewogICAgICAgICAgICB2YWwgZXJyb3IgPSByb290Lm9wdEpTT05PYmplY3QoImVycm9yIikKICAgICAgICAgICAgTG9nLncoVEFHLCAiQVBJIGVycm9yOiAke2Vycm9yPy5vcHRTdHJpbmcoImNvZGUiKX0gLSAke2Vycm9yPy5vcHRTdHJpbmcoIm1lc3NhZ2UiKX0iKQogICAgICAgICAgICByZXR1cm4gbnVsbAogICAgICAgIH0KICAgICAgICByZXR1cm4gcm9vdC5vcHRKU09OT2JqZWN0KCJkYXRhIikKICAgIH0KCiAgICBwcml2YXRlIGZ1biBmbGF0dGVuKG5vZGVzOiBKU09OQXJyYXk/LCBwcmVmaXg6IFN0cmluZywgb3V0OiBNdXRhYmxlTGlzdDxBZEZpbGU+KSB7CiAgICAgICAgaWYgKG5vZGVzID09IG51bGwpIHJldHVybgogICAgICAgIGZvciAoaSBpbiAwIHVudGlsIG5vZGVzLmxlbmd0aCgpKSB7CiAgICAgICAgICAgIHZhbCBub2RlID0gbm9kZXMub3B0SlNPTk9iamVjdChpKSA/OiBjb250aW51ZQogICAgICAgICAgICB2YWwgbmFtZSA9IG5vZGUub3B0U3RyaW5nKCJuIiwgIiIpCiAgICAgICAgICAgIHZhbCBwYXRoID0gaWYgKHByZWZpeC5pc0VtcHR5KCkpIG5hbWUgZWxzZSAiJHByZWZpeC8kbmFtZSIKICAgICAgICAgICAgdmFsIGNoaWxkcmVuID0gbm9kZS5vcHRKU09OQXJyYXkoImUiKQogICAgICAgICAgICBpZiAoY2hpbGRyZW4gIT0gbnVsbCkgewogICAgICAgICAgICAgICAgZmxhdHRlbihjaGlsZHJlbiwgcGF0aCwgb3V0KQogICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgb3V0ICs9IEFkRmlsZSgKICAgICAgICAgICAgICAgICAgICBwYXRoID0gcGF0aCwKICAgICAgICAgICAgICAgICAgICBzaXplID0gbm9kZS5vcHRMb25nKCJzIiwgMEwpLAogICAgICAgICAgICAgICAgICAgIGxpbmsgPSBub2RlLm9wdFN0cmluZygibCIsICIiKQogICAgICAgICAgICAgICAgKQogICAgICAgICAgICB9CiAgICAgICAgfQogICAgfQp9Cg==').decode("utf-8")

def apply_replacements(path, items):
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new, label in items:
        if new in text:
            continue

        if old not in text and label == "remote key-change detection":
            pattern = (
                r'val\s+debridKeyChanged\s*=\s*'
                r'\(change\.proposedRealDebridApiKey\s*!=\s*AppPreferences\.realDebridApiKey\)\s*\|\|\s*'
                r'\(change\.proposedTorboxApiKey\s*!=\s*AppPreferences\.torboxApiKey\)'
            )
            match = re.search(pattern, text, flags=re.MULTILINE)
            if not match:
                raise RuntimeError(f"Could not find patch point in {path}: {label}")
            indent = text[text.rfind("\n", 0, match.start()) + 1:match.start()]
            replacement = (
                "val debridKeyChanged = "
                "(change.proposedRealDebridApiKey != AppPreferences.realDebridApiKey) ||\n"
                + indent + "    (change.proposedTorboxApiKey != AppPreferences.torboxApiKey) ||\n"
                + indent + "    (change.proposedAllDebridApiKey != AppPreferences.allDebridApiKey)"
            )
            text = text[:match.start()] + replacement + text[match.end():]
            changed = True
            continue

        if old not in text:
            raise RuntimeError(f"Could not find patch point in {path}: {label}")
        text = text.replace(old, new, 1)
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print("patched", path)
    else:
        print("already patched", path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--clone", metavar="DIR")
    args = ap.parse_args()

    if args.clone:
        root = Path(args.clone).resolve()
        if root.exists() and any(root.iterdir()):
            raise SystemExit(f"{root} already exists and is not empty")
        subprocess.check_call(["git", "clone", "--depth", "1", UPSTREAM, str(root)])
    else:
        root = Path(args.project or ".").resolve()

    base = root / "app/src/main/java/com/playtorrio/tv"
    if not base.exists():
        raise SystemExit("Not a PlayTorrioTVKT checkout")

    for rel, items in REPLACEMENTS.items():
        path = base / rel
        if not path.exists():
            raise RuntimeError(f"Missing expected source file: {path}")

        # DebridResolver formatting changes frequently upstream; patch it
        # semantically instead of depending on exact whitespace.
        if rel == "data/debrid/DebridResolver.kt":
            resolver_text = path.read_text(encoding="utf-8")
            if '"alldebrid"' not in resolver_text:
                pattern = r'(?m)^(\s*)"torbox"\s*->\s*TorBoxClient\.resolve\(source, isMovie, season, episode\)\s*$'
                match = re.search(pattern, resolver_text)
                if not match:
                    raise RuntimeError(
                        f"Could not locate TorBox resolver branch in {path}"
                    )
                indent = match.group(1)
                insertion = (
                    match.group(0)
                    + "\n"
                    + indent
                    + '"alldebrid"  -> AllDebridClient.resolve(source, isMovie, season, episode)'
                )
                resolver_text = (
                    resolver_text[:match.start()]
                    + insertion
                    + resolver_text[match.end():]
                )
                path.write_text(resolver_text, encoding="utf-8")
                print("patched", path)
            else:
                print("already patched", path)
            continue

        apply_replacements(path, items)

    client_path = base / "data/debrid/AllDebridClient.kt"
    if not client_path.exists() or client_path.read_text(encoding="utf-8") != CLIENT:
        client_path.write_text(CLIENT, encoding="utf-8")
        print("created", client_path)
    else:
        print("already patched", client_path)

    print("AllDebrid patch applied successfully.")

if __name__ == "__main__":
    main()
