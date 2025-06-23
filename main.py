from datetime import datetime
import time
from colorama import Fore
import requests
import random
from fake_useragent import UserAgent
import asyncio
import json
import gzip
import brotli
import zlib
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class penguclash:
    BASE_URL = "https://api.pudgy-clash.elympics.ai/"
    HEADERS = {
        "accept": "*/*",
        "accept-encoding": "br",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "cache-control": "no-cache",
        "elympics-sdk-version": "0.15.4",
        "origin": "https://pengu-clash.elympics.host",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://pengu-clash.elympics.host/",
        "sec-ch-ua": '"Microsoft Edge WebView2";v="137", "Microsoft Edge";v="137", "Not/A)Brand";v="24", "Chromium";v="137"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    }

    def __init__(self):
        self.config = self.load_config()
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.session = self.sessions()
        self._original_requests = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        self.proxy_session = None

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Ｐｅｎｇｕ Ｃｌａｓｈ Ｂｏｔ", Fore.CYAN)
        self.log("🚀 Created by 𝔹𝕚𝕃𝔸𝕃 𝕊𝕋𝕌𝔻𝕀𝕆", Fore.CYAN)
        self.log("📢 Channel: https://t.me/BilalStudio3\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )

    def sessions(self):
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 520]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def decode_response(self, response):
        """
        Mendekode response dari server secara umum.

        Parameter:
            response: objek requests.Response

        Mengembalikan:
            - Jika Content-Type mengandung 'application/json', maka mengembalikan objek Python (dict atau list) hasil parsing JSON.
            - Jika bukan JSON, maka mengembalikan string hasil decode.
        """
        # Ambil header
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        content_type = response.headers.get("Content-Type", "").lower()

        # Tentukan charset dari Content-Type, default ke utf-8
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()

        # Ambil data mentah
        data = response.content

        # Dekompresi jika perlu
        try:
            if content_encoding == "gzip":
                data = gzip.decompress(data)
            elif content_encoding in ["br", "brotli"]:
                data = brotli.decompress(data)
            elif content_encoding in ["deflate", "zlib"]:
                data = zlib.decompress(data)
        except Exception:
            # Jika dekompresi gagal, lanjutkan dengan data asli
            pass

        # Coba decode menggunakan charset yang didapat
        try:
            text = data.decode(charset)
        except Exception:
            # Fallback: deteksi encoding dengan chardet
            detection = chardet.detect(data)
            detected_encoding = detection.get("encoding", "utf-8")
            text = data.decode(detected_encoding, errors="replace")

        # Jika konten berupa JSON, kembalikan hasil parsing JSON
        if "application/json" in content_type:
            try:
                return json.loads(text)
            except Exception:
                # Jika parsing JSON gagal, kembalikan string hasil decode
                return text
        else:
            return text

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def _get_random_user_agent(self) -> str:
        """Generate a simple random User-Agent string."""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0)"
            " Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Edg/137.0.0.0 Safari/537.36",
        ]
        return random.choice(agents)

    def login(self, index: int) -> None:
        self.log("🔐 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        self.log(f"📋 Using token: {token[:10]}... (truncated for security)", Fore.CYAN)

        # Step 1: Authenticate via Elympics API
        auth_url = "https://api.elympics.cc/v2/Auth/user/Telegram-Auth-v2"
        payload = json.dumps(
            {
                "initDataRaw": token,
                "typedData": '{"id":"6e4cf20b-7599-40ce-8db1-ffe00d6e71cc","version":"1071","name":"Pengu Clash"}',
                "invitationCode": "",
                "gameId": "6e4cf20b-7599-40ce-8db1-ffe00d6e71cc",
            }
        )
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://pengu-clash.elympics.host",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://pengu-clash.elympics.host/",
            "sec-ch-ua": '"Microsoft Edge WebView2";v="137", "Microsoft Edge";v="137", "Not/A)Brand";v="24", "Chromium";v="137"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": self._get_random_user_agent(),
        }

        try:
            self.log("📡 Sending Elympics auth request...", Fore.CYAN)
            resp = requests.post(auth_url, headers=headers, data=payload)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {resp.text}", Fore.RED)
            except Exception:
                pass
            return
        except ValueError:
            self.log("❌ Failed to parse JSON response", Fore.RED)
            return

        # Simpan auth tokens
        self.token = data.get("jwtToken", "")
        self.userid = data.get("userId", "")

        if not (self.token and self.userid):
            self.log("❌ Login response missing expected fields", Fore.RED)
            return

        self.log("✅ Login successful!", Fore.GREEN)
        self.log(f"    • jwtToken: {self.token[:10]}... (truncated)", Fore.CYAN)
        self.log(f"    • userId: {self.userid}", Fore.CYAN)

        # Step 2: Fetch player data
        player_url = f"{self.BASE_URL}player"
        player_headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}
        try:
            self.log("📡 Fetching player data...", Fore.CYAN)
            player_resp = requests.get(player_url, headers=player_headers)
            player_resp.raise_for_status()
            player_data = player_resp.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch player data: {e}", Fore.RED)
            try:
                self.log(f"📄 Response content: {player_resp.text}", Fore.RED)
            except Exception:
                pass
            return
        except ValueError:
            self.log("❌ Failed to parse player JSON", Fore.RED)
            return

        # Tampilkan data penting dari player
        self.log("👾 Player Info:", Fore.GREEN)
        self.log(f"    • ID: {player_data.get('id', 'N/A')}", Fore.CYAN)
        team = player_data.get("team", {})
        self.log(f"    • Team ID: {team.get('id', 'N/A')}", Fore.CYAN)
        chars = team.get("characters", [])
        for idx, char in enumerate(chars, start=1):
            self.log(
                f"      - Character {idx}: {char.get('name', 'N/A')} ({char.get('type', 'N/A')})",
                Fore.CYAN,
            )
        items = player_data.get("items", [])
        self.log(f"    • Total Items: {len(items)}", Fore.CYAN)
        # Bisa diperluas sesuai kebutuhan

    def spin(self) -> None:
        """Check spin availability and perform spin if possible"""
        spin_status_url = f"{self.BASE_URL}player/spin"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        # Cek ketersediaan spin
        try:
            self.log("🔄 Checking spin availability...", Fore.CYAN)
            status_resp = requests.get(spin_status_url, headers=headers)
            status_resp.raise_for_status()
            status = status_resp.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Spin status check failed: {e}", Fore.RED)
            return
        except ValueError:
            self.log("❌ Failed to parse spin status JSON", Fore.RED)
            return

        if not status.get("spinnable", False):
            avail_at = status.get("availableAt", "N/A")
            self.log(f"🕒 Next spin available at: {avail_at}", Fore.YELLOW)
            return

        # Lakukan spin
        try:
            self.log("🎰 Performing spin...", Fore.CYAN)
            spin_resp = requests.post(spin_status_url, headers=headers)
            spin_resp.raise_for_status()
            result = spin_resp.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Spin request failed: {e}", Fore.RED)
            return
        except ValueError:
            self.log("❌ Failed to parse spin result JSON", Fore.RED)
            return

        resource = result.get("resource", {})
        amount = resource.get("amount", 0)
        formatted = resource.get("formattedAmount", "0")
        self.log(
            f"✅ Spin successful! Won {formatted} ({amount}) {resource.get('type','')}",
            Fore.GREEN,
        )
        if result.get("extraSpin", False):
            self.log("✨ You earned an extra spin!", Fore.GREEN)

    def chest(self) -> None:
        """Fetch, claim free chest if available, and open all owned chests."""
        free_chest_url = f"{self.BASE_URL}player/chests/free"
        chests_url = f"{self.BASE_URL}player/chests"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        # 1) Check & claim free chest if available
        try:
            self.log("🎁 Checking free chest...", Fore.CYAN)
            free_resp = requests.get(free_chest_url, headers=headers)
            free_resp.raise_for_status()
            free_data = free_resp.json()
            if free_data.get("claimable", False):
                self.log("🔓 Free chest is claimable — claiming now...", Fore.CYAN)
                claim_resp = requests.post(free_chest_url, headers=headers)
                if claim_resp.status_code == 200:
                    self.log("✅ Free chest claimed successfully!", Fore.GREEN)
                else:
                    self.log(
                        f"❌ Free chest claim failed (status {claim_resp.status_code})",
                        Fore.RED,
                    )
            else:
                avail = free_data.get("availableAt", "unknown time")
                self.log(
                    f"⏳ Free chest not yet claimable. Next at {avail}", Fore.YELLOW
                )
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Free chest check/claim error: {e}", Fore.RED)
        except ValueError:
            self.log("❌ Failed to parse free chest JSON", Fore.RED)

        # 2) Fetch owned chests
        try:
            self.log("📦 Fetching owned chests...", Fore.CYAN)
            resp = requests.get(chests_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch chests: {e}", Fore.RED)
            return
        except ValueError:
            self.log("❌ Failed to parse chests JSON", Fore.RED)
            return

        owned = data.get("ownedChests", [])
        for chest in owned:
            rarity = chest.get("rarity")
            amount = chest.get("amount", 0)
            self.log(f"    • Chest {rarity}: {amount}", Fore.CYAN)

        # 3) Open each owned chest with amount > 0
        opened_any = False
        for chest in owned:
            rarity = chest.get("rarity")
            amount = chest.get("amount", 0)
            for _ in range(amount):
                opened_any = True
                try:
                    self.log(f"🔓 Opening {rarity} chest...", Fore.CYAN)
                    open_resp = requests.post(
                        f"{chests_url}player/chests/open",
                        headers=headers,
                        data=json.dumps({"rarity": rarity}),
                    )
                    open_resp.raise_for_status()
                    result = open_resp.json()
                    res = result.get("resource", {})
                    item = result.get("item", {})
                    self.log(
                        f"✅ Opened {rarity}: +{res.get('formattedAmount','0')} {res.get('type','')}",
                        Fore.GREEN,
                    )
                    self.log(
                        f"    • Item: {item.get('name','N/A')} ({item.get('rarity','N/A')})",
                        Fore.GREEN,
                    )
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Failed to open {rarity} chest: {e}", Fore.RED)
                    break
                except ValueError:
                    self.log("❌ Failed to parse open chest JSON", Fore.RED)
                    break

        # 4) Summary / refresh
        if not opened_any:
            self.log("📭 No owned chests to open.", Fore.YELLOW)
        else:
            try:
                self.log("🔄 Refreshing chests...", Fore.CYAN)
                resp = requests.get(chests_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self.log("📦 Updated chests:", Fore.GREEN)
                for chest in data.get("ownedChests", []):
                    self.log(
                        f"    • Chest {chest.get('rarity')}: {chest.get('amount')}",
                        Fore.CYAN,
                    )
            except Exception:
                pass

    def quest(self) -> None:
        """Fetch quests, start those available, and claim completed ones in two phases."""
        url = f"{self.BASE_URL}quests"
        headers = {**self.HEADERS, "authorization": f"Bearer {self.token}"}

        def get_sections():
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json().get("sections", [])
            except Exception as e:
                self.log(f"❌ Error fetching quests: {e}", Fore.RED)
                return []

        def identify(sections):
            to_start, to_claim = [], []
            for sec in sections:
                for q in sec.get("quests", []):
                    qid = q.get("id")
                    state = q.get("state", {})
                    prog = state.get("progress", {})
                    completed = state.get("completed", {}).get("total", 0) or state.get(
                        "claimed", {}
                    ).get("total", 0)
                    current = prog.get("current", 0)
                    total = prog.get("total", 0)

                    if total > 0 and current == 0 and completed == 0:
                        to_start.append(qid)
                    if completed > 0 or (total > 0 and current >= total):
                        to_claim.append(qid)
            return to_start, to_claim

        # Phase 1: Start quests
        self.log("📜 Phase 1: Starting quests...", Fore.CYAN)
        sections = get_sections()
        startable, _ = identify(sections)
        for qid in startable:
            try:
                self.log(f"▶️ Starting {qid}...", Fore.CYAN)
                start_resp = requests.post(f"{url}/{qid}/progress", headers=headers)
                start_resp.raise_for_status()
                self.log(f"✅ Started {qid}", Fore.GREEN)
            except Exception as e:
                self.log(f"❌ Start {qid} failed: {e}", Fore.RED)

        # Phase 2: Claim quests (including newly started)
        self.log("📜 Phase 2: Claiming quests...", Fore.CYAN)
        sections = get_sections()
        _, claimable = identify(sections)
        for qid in claimable:
            try:
                self.log(f"🏆 Claiming {qid}...", Fore.CYAN)
                claim_resp = requests.post(f"{url}/{qid}/claim", headers=headers)
                claim_resp.raise_for_status()
                self.log(f"✅ Claimed {qid}", Fore.GREEN)
            except Exception as e:
                self.log(f"❌ Claim {qid} failed: {e}", Fore.RED)

        # Final refresh display
        self.log("🔄 Final quest statuses:", Fore.CYAN)
        sections = get_sections()
        for sec in sections:
            self.log(
                f"-- {sec.get('title')} (expires {sec.get('expiration')})", Fore.CYAN
            )
            for q in sec.get("quests", []):
                prog = q.get("state", {}).get("progress", {})
                completed = q.get("state", {}).get("completed", {}).get(
                    "total", 0
                ) or q.get("state", {}).get("claimed", {}).get("total", 0)
                self.log(
                    f"   • {q.get('title')} [{prog.get('current',0)}/{prog.get('total',0)}], Completed: {completed}",
                    Fore.CYAN,
                )

    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

    def override_requests(self):
        import random

        """Override requests functions globally when proxy is enabled."""
        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete
        else:
            self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
            # Restore original functions if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]


async def process_account(account, original_index, account_label, blu, config):

    ua = UserAgent()
    blu.HEADERS["user-agent"] = ua.random

    # Menampilkan informasi akun
    display_account = account[:10] + "..." if len(account) > 10 else account
    blu.log(f"👤 Processing {account_label}: {display_account}", Fore.YELLOW)

    # Override proxy jika diaktifkan
    if config.get("proxy", False):
        blu.override_requests()
    else:
        blu.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

    # Login (fungsi blocking, dijalankan di thread terpisah) dengan menggunakan index asli (integer)
    await asyncio.to_thread(blu.login, original_index)

    blu.log("🛠️ Starting task execution...", Fore.CYAN)
    tasks_config = {
        "spin": "Auto spin",
        "chest": "Auto open chest",
        "quest": "Auto solve quest",
    }

    for task_key, task_name in tasks_config.items():
        task_status = config.get(task_key, False)
        color = Fore.YELLOW if task_status else Fore.RED
        blu.log(
            f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
            color,
        )
        if task_status:
            blu.log(f"🔄 Executing {task_name}...", Fore.CYAN)
            await asyncio.to_thread(getattr(blu, task_key))

    delay_switch = config.get("delay_account_switch", 10)
    blu.log(
        f"➡️ Finished processing {account_label}. Waiting {Fore.WHITE}{delay_switch}{Fore.CYAN} seconds before next account.",
        Fore.CYAN,
    )
    await asyncio.sleep(delay_switch)


async def worker(worker_id, blu, config, queue):
    """
    Setiap worker akan mengambil satu akun dari antrian dan memprosesnya secara berurutan.
    Worker tidak akan mengambil akun baru sebelum akun sebelumnya selesai diproses.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, blu, config)
        queue.task_done()
    blu.log(f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN)


async def main():
    blu = penguclash()
    config = blu.load_config()
    all_accounts = blu.query_list
    num_threads = config.get("thread", 1)  # Jumlah worker sesuai konfigurasi

    if config.get("proxy", False):
        proxies = blu.load_proxies()

    blu.log(
        "🎉 [LIVEXORDS] === Welcome to Pengu clash Automation === [LIVEXORDS]",
        Fore.YELLOW,
    )
    blu.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)

    while True:
        # Buat queue baru dan masukkan semua akun (dengan index asli)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))

        # Buat task worker sesuai dengan jumlah thread yang diinginkan
        workers = [
            asyncio.create_task(worker(i + 1, blu, config, queue))
            for i in range(num_threads)
        ]

        # Tunggu hingga semua akun di queue telah diproses
        await queue.join()

        # Opsional: batalkan task worker (agar tidak terjadi tumpang tindih)
        for w in workers:
            w.cancel()

        blu.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        blu.log(
            f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.",
            Fore.CYAN,
        )
        await asyncio.sleep(delay_loop)


if __name__ == "__main__":
    asyncio.run(main())
