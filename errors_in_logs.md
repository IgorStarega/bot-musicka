wilson@skrzynka-z-bananami:~/docker/bot-musicka$ docker compose logs
bot-musicka  | 2026-04-27 07:36:40 INFO     discord.client logging in using static token
bot-musicka  | 2026-04-27 07:36:40,225:INFO:discord.client: logging in using static token
bot-musicka  | 2026-04-27 07:36:40,716:INFO:MusicBot: ✅ Znaleziono plik ciasteczek: config/cookies.txt
bot-musicka  | 2026-04-27 07:36:40,989:INFO:MusicBot: Zsynchronizowano komendy slash dla Miusnigg#9157
bot-musicka  | 2026-04-27 07:36:42 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: 05a13ba5dfc2e9f9d238c5d47ebff532).
bot-musicka  | 2026-04-27 07:36:42,029:INFO:discord.gateway: Shard ID None has connected to Gateway (Session ID: 05a13ba5dfc2e9f9d238c5d47ebff532).
bot-musicka  | 2026-04-27 07:36:44,033:INFO:MusicBot: Zalogowano jako Miusnigg#9157 (ID: 1488852113411936316)
bot-musicka  | 2026-04-27 07:36:44,034:INFO:MusicBot: ------
bot-musicka  | 2026-04-27 07:37:12 INFO     discord.voice_state Connecting to voice...
bot-musicka  | 2026-04-27 07:37:12,481:INFO:discord.voice_state: Connecting to voice...
bot-musicka  | 2026-04-27 07:37:12 INFO     discord.voice_state Starting voice handshake... (connection attempt 1)
bot-musicka  | 2026-04-27 07:37:12,481:INFO:discord.voice_state: Starting voice handshake... (connection attempt 1)
bot-musicka  | 2026-04-27 07:37:12 INFO     discord.voice_state Voice handshake complete. Endpoint found: c-waw04-7cacab58.discord.media:2096
bot-musicka  | 2026-04-27 07:37:12,868:INFO:discord.voice_state: Voice handshake complete. Endpoint found: c-waw04-7cacab58.discord.media:2096
bot-musicka  | 2026-04-27 07:37:13 INFO     discord.voice_state Voice connection complete.
bot-musicka  | 2026-04-27 07:37:13,143:INFO:discord.voice_state: Voice connection complete.
bot-musicka  | 2026-04-27 07:37:13,582:INFO:MusicBot: ▶️ /play [1486620807957577803]: https://open.spotify.com/track/1VvXLOfkv1zxa3LZ0zBXt2?si=0bf...
bot-musicka  | 2026-04-27 07:37:13,922:INFO:MusicBot: [/play] Calling get_info for: https://open.spotify.com/track/1VvXLOfkv1zxa3LZ0zB
bot-musicka  | 2026-04-27 07:37:13,922:INFO:MusicBot: [get_info START] URL: https://open.spotify.com/track/1VvXLOfkv1zxa3LZ0zBXt2?si=0bf
bot-musicka  | 2026-04-27 07:37:13,922:INFO:MusicBot: [get_info] Using search options: extract_flat=False, player_client=['web_embedded', 'tv_embedded', 'android']
bot-musicka  | 2026-04-27 07:37:13,922:INFO:MusicBot: [get_info] Attempting primary extract_info...
bot-musicka  | ERROR: [DRM] The requested site is known to use DRM protection. It will NOT be supported.
bot-musicka  |        Please DO NOT open an issue, unless you have evidence that the video is not DRM protected
bot-musicka  | 2026-04-27 07:37:14,102:INFO:MusicBot: [get_info PRIMARY SUCCESS] Got data with entries count: 0
bot-musicka  | 2026-04-27 07:37:14,102:WARNING:MusicBot: [get_info] Primary returned None, using empty dict
bot-musicka  | 2026-04-27 07:37:14,103:INFO:MusicBot: [/play] get_info returned type: dict, is dict: True
bot-musicka  | 2026-04-27 07:37:14,103:INFO:MusicBot: [/play] Entries count: 0
bot-musicka  | 2026-04-27 07:37:14,103:WARNING:MusicBot: [/play] No entries found, sending error response
bot-musicka  | 2026-04-27 07:37:14,423:WARNING:MusicBot: Brak: https://open.spotify.com/track/1VvXLOfkv1zxa3LZ0zB
bot-musicka  | 2026-04-27 07:37:32,760:INFO:MusicBot: ▶️ /play [1486620807957577803]: https://www.youtube.com/watch?v=Rryet816_t8...
bot-musicka  | 2026-04-27 07:37:33,033:INFO:MusicBot: [/play] Calling get_info for: https://www.youtube.com/watch?v=Rryet816_t8
bot-musicka  | 2026-04-27 07:37:33,033:INFO:MusicBot: [get_info START] URL: https://www.youtube.com/watch?v=Rryet816_t8
bot-musicka  | 2026-04-27 07:37:33,033:INFO:MusicBot: [get_info] Using search options: extract_flat=False, player_client=['web_embedded', 'tv_embedded', 'android']
bot-musicka  | 2026-04-27 07:37:33,033:INFO:MusicBot: [get_info] Attempting primary extract_info...
bot-musicka  | ERROR: [youtube] Rryet816_t8: Sign in to confirm you’re not a bot. Use --cookies-from-browser or --cookies for the authentication. See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies. Also see  https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies  for tips on effectively exporting YouTube cookies
bot-musicka  | 2026-04-27 07:37:34,157:INFO:MusicBot: [get_info PRIMARY SUCCESS] Got data with entries count: 0
bot-musicka  | 2026-04-27 07:37:34,158:WARNING:MusicBot: [get_info] Primary returned None, using empty dict
bot-musicka  | 2026-04-27 07:37:34,158:INFO:MusicBot: [/play] get_info returned type: dict, is dict: True
bot-musicka  | 2026-04-27 07:37:34,158:INFO:MusicBot: [/play] Entries count: 0
bot-musicka  | 2026-04-27 07:37:34,158:WARNING:MusicBot: [/play] No entries found, sending error response
bot-musicka  | 2026-04-27 07:37:34,598:WARNING:MusicBot: Brak: https://www.youtube.com/watch?v=Rryet816_t8
wilson@skrzynka-z-bananami:~/docker/bot-musicka$ 