import asyncio
import sys
from datetime import datetime, timedelta
from mnemonic import Mnemonic
from bip32utils import BIP32Key, BIP32_HARDEN
import aiohttp
from colorama import Fore, Back, Style, init

init(autoreset=True)

class EthConsoleUI:
    def __init__(self):
        self.scanned = 0
        self.found = 0
        self.total_balance = 0.0
        self.log_buffer = []
        self.max_log_lines = 25
        self.init_screen()

    def init_screen(self):
        print("\033[2J\033[H") # CLEAR SCREEN
        self.draw_header()
        print("\n" + "-" * 80 + "\n")
        self.prepare_log_area()

    def draw_header(self):
        header = f"{Back.BLACK}{Fore.CYAN} | ETH Scanner | {Fore.YELLOW}Scanned: {self.scanned} |"
        header += f"{Fore.CYAN}Found: {self.found} | {Fore.MAGENTA}Balance: {self.total_balance:.8f} LTC |"
        print(f'\033[1;1H{header}{Style.RESET_ALL}')

    def prepare_log_area(self):
        print('\n' + '-' * 80)
        for _ in range(self.max_log_lines + 2):
            print()
        sys.stdout.write(f'\033[4;0H')
        sys.stdout.flush()

    def update_header(self):
        self.draw_header()
        sys.stdout.write(f'\033[2;0H{'_'*80}')
        sys.stdout.flush()

    def add_log(self, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'{color}{timestamp} | {message}{Style.RESET_ALL}'
        
        # Add to buffer and maintain max length
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer.pop(0)

        # Redraw all logs
            self.redraw_logs()

    def redraw_logs(self):
        sys.stdout.write(f"\033[4;0H")
        for entry in self.log_buffer[-self.max_log_lines:]:
            sys.stdout.write(entry + '\n')
        sys.stdout.flush()

class EthScanner:
    def __init__(self):
        self.ui = EthConsoleUI()
        self.is_scanning = False
        self.start_time = datetime.datetime.now()
    async def mnemonic_to_address(self, mnemonic):
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(mnemonic)
        root_key = BIP32Key.fromEntropy(seed)
        # ETH BIP44 path: m/44'/60'/0'/0'/0
        child_key = root_key.ChildKey(44 + BIP32_HARDEN)
        child_key = child_key.ChildKey(2 + BIP32_HARDEN)
        child_key = child_key.ChildKey(0 + BIP32_HARDEN)
        child_key = child_key.ChildKey(0)
        child_key = child_key.ChildKey(0)
        return child_key.Address()
    
    async def get_balance(self, session, address):
        url = f'https://api.etherscan.io/api?module=account&action=balance&address={address}'
        try:
            async with session.get(url) as response:
                data = await response.json()
                return int(data['result']) / 10**18 # Convert wei to ETH
        except:
            return 0 
        
    async def get_transactions(self,session, address):
        url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={self.api_key}'
        try:
            async with session.get(url) as response:
                data = await response.json()
                return data['results']
        except:
            return []
        
    def check_inactive(self, transactions):
        if not transactions:
            return False
        last_tx = max(int(tx['timeStamp']) for tx in transactions if tx.get('timeStamp'))
        last_active = datetime.fromtimestamp(last_tx)
        return (datetime.now() - last_active).days >= 365
    
    def save_result(self, mnemonic, address, balance):
        with open('eth_active.txt', 'a') as f:
            f.write(f'{datetime.now().isoformat()}|{mnemonic}|{address}|{balance:.6f}\n')

    async def start(self):
        self.is_scanning = True
        async with aiohttp.ClientSession() as session:
            while self.is_scanning:
                try:
                    mnemo = Mnemonic("english")
                    mnemonic = mnemo.generate(128)
                    address = await self.generate_address(mnemonic)

                    self.ui.scanned += 1
                    self.ui.update_header()
                    self.ui.add_log(f'Checking: {address}', Fore.WHITE)
                    self.ui.add_log(f'Mnemonic: {mnemonic}', Fore.LIGHTBLACK_EX)

                    balance = await self.get_balance(session, address)
                    if balance <= 0:
                        self.ui.add_log('0.0 ETH', Fore.RED)
                        await asyncio.sleep(1.2)
                        continue

                    self.ui.found += 1
                    self.ui.total_balance += balance
                    self.save_result(mnemonic, address, balance)
                    self.ui.add_log(f"FOUND: {balance:.6f} ETH", Fore.GREEN)
                    await asyncio.sleep(5)

                except Exception as e:
                    self.ui.add_log(f'Error: {str(e)}', Fore.RED)
                    await asyncio.sleep(2)

if __name__ == '__main__':
    scanner = EthScanner()
    try:
        asyncio.run(scanner.start())
    except KeyboardInterrupt:
        scanner.is_scanning = False
        print("\n\033[33mScanning stopped\033[0m")