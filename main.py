import requests
import json
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from datetime import datetime
import time
import random
import threading
import subprocess
import sys
import csv
from plyer import notification

class KeywordScraper:
    def __init__(self):
        self.check_dependencies()
        self.keyword = None
        self.related_keywords = []
        self.settings = {
            "scraping_level": 1,  # 1: Basic, 2: Moderate, 3: Extensive
            "min_keyword_length": 3,
            "notification_alert": False,
            "api_source": "google",  # Options: 'google', 'bing'
            "result_path": "results"  # Default path for saving files
        }
        self.load_settings()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json"
        }
        self.console = Console(record=True)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.console.print("[bold green]Welcome to Keyword Scraper![/bold green] \n[bold yellow]Join our Telegram channels for more information and support:[/bold yellow] \n[cyan]https://t.me/pasjonatyk[/cyan] | [red]https://t.me/cwelplus[/red]\n")

    def check_dependencies(self):
        required_packages = ["requests", "rich", "plyer"]
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.console.print(f"[bold red]Package '{package}' is not installed. Installing now...[/bold red]")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                self.settings.update(json.load(file))

    def save_settings(self):
        with open("settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_related_keywords(self):
        try:
            self.console.print("[bold yellow]Fetching related keywords...[/bold yellow]")
            time.sleep(random.uniform(0.5, 1.5))
            if self.settings["api_source"] == "google":
                response = requests.get(f"http://suggestqueries.google.com/complete/search?client=firefox&q={self.keyword}", headers=self.headers)
            elif self.settings["api_source"] == "bing":
                response = requests.get(f"https://api.bing.com/osjson.aspx?query={self.keyword}", headers=self.headers)
            else:
                raise ValueError("Unsupported API source. Please choose 'google' or 'bing'.")
            response.raise_for_status()
            suggestions = json.loads(response.text)
            if len(suggestions) > 1 and isinstance(suggestions[1], list):
                self.related_keywords = suggestions[1]
                self.console.print("[bold green]Related keywords successfully fetched![/bold green]")
                if self.settings["notification_alert"]:
                    notification.notify(
                        title="Void Scraper",
                        message="Scraping completed successfully!",
                        app_name="Void Scraper",  # Zmieniono na "Void Scraper"
                        timeout=5
                    )
            else:
                raise ValueError("Unexpected response format.")
        except requests.exceptions.RequestException as req_err:
            self.console.print(f"[bold red]Network error occurred while fetching keywords:[/bold red] {req_err}")
        except ValueError as val_err:
            self.console.print(f"[bold red]An error occurred:[/bold red] {val_err}")
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred while fetching keywords:[/bold red] {e}")

    def filter_keywords_options(self):
        min_length = self.settings["min_keyword_length"]
        if self.settings.get("remove_spaces", None) is None:
            remove_spaces = Prompt.ask("Remove spaces from keywords? (yes/no)", choices=["yes", "no"]) == "yes"
            self.settings["remove_spaces"] = remove_spaces
        else:
            remove_spaces = self.settings["remove_spaces"]

        if self.settings.get("sort_keywords", None) is None:
            sort_keywords = Prompt.ask("Sort keywords by length? (yes/no)", choices=["yes", "no"]) == "yes"
            self.settings["sort_keywords"] = sort_keywords
        else:
            sort_keywords = self.settings["sort_keywords"]

        self.related_keywords = [kw.replace(" ", "") if remove_spaces else kw for kw in self.related_keywords if len(kw) >= min_length]
        if sort_keywords:
            self.related_keywords.sort(key=len)

        self.console.print(f"[bold green]Keywords filtered with minimum length of {min_length} characters." + (" Spaces removed." if remove_spaces else "") + (" Sorted by length." if sort_keywords else "") + "[/bold green]")

    def export_keywords(self, file_path=None, file_format='txt'):
        try:
            if not self.related_keywords:
                raise ValueError("No keywords available to export.")
            
            # Default path logic
            if file_path is None:
                if not os.path.exists(self.settings["result_path"]):
                    os.makedirs(self.settings["result_path"])
                file_path = f"{self.settings['result_path']}/keywords_{self.timestamp}.{file_format}"

            if file_format == 'txt':
                with open(file_path, 'w') as file:
                    for keyword in self.related_keywords:
                        file.write(f"{keyword}\n")
            elif file_format == 'csv':
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Keywords"])
                    for keyword in self.related_keywords:
                        writer.writerow([keyword])
            elif file_format == 'json':
                with open(file_path, 'w') as file:
                    json.dump(self.related_keywords, file, indent=4)
            else:
                raise ValueError("Unsupported file format. Please choose 'txt', 'csv', or 'json'.")
            
            self.console.print(f"[bold green]Keywords successfully exported to {file_path}[/bold green]")
        except ValueError as val_err:
            self.console.print(f"[bold red]An error occurred:[/bold red] {val_err}")
        except Exception as e:
            self.console.print(f"[bold red]An unexpected error occurred while exporting:[/bold red] {e}")

    def display_keywords(self):
        if self.related_keywords:
            table = Table(title="Related Keywords", style="green")
            table.add_column("Index", justify="center", style="cyan", no_wrap=True)
            table.add_column("Keyword", justify="left", style="magenta")

            for idx, related in enumerate(self.related_keywords, start=1):
                table.add_row(str(idx), related)
                if idx % 40 == 0:
                    time.sleep(1.5)

            self.console.print(table)
        else:
            self.console.print("[bold red]No related keywords found.[/bold red]")

    def async_fetch_keywords(self):
        thread = threading.Thread(target=self.get_related_keywords)
        thread.start()
        thread.join()

    def menu(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="menu", ratio=3),
            Layout(name="footer", size=6)
        )
        layout["header"].update(Panel("[bold blue]Keyword Scraper Tool Main Menu[/bold blue]\n[bold yellow]Join us on Telegram![/bold yellow]\n[cyan]https://t.me/pasjonatyk[/cyan] | [red]https://t.me/cwelplus[/red]", style="bold blue", border_style="blue"))
        layout["footer"].update(Panel("[bold cyan]Press the corresponding number to navigate through options.[/bold cyan]\n[bold yellow]Join our community for more tips and discussions![/bold yellow]\n[cyan]https://t.me/pasjonatyk[/cyan] | [red]https://t.me/cwelplus[/red]", border_style="cyan"))

        while True:
            self.clear_console()
            layout["menu"].update(
                Panel(
                    Align.left(
                        "\n[bold cyan]1.[/bold cyan] Enter a new keyword to scrape"
                        "\n[bold cyan]2.[/bold cyan] Display related keywords"
                        "\n[bold cyan]3.[/bold cyan] Export keywords to a file"
                        "\n[bold cyan]4.[/bold cyan] Filter keywords"
                        "\n[bold cyan]5.[/bold cyan] Settings"
                        "\n[bold cyan]6.[/bold cyan] Exit"
                    ),
                    title="[bold green]Options[/bold green]",
                    border_style="green"
                )
            )
            self.console.print(layout)
            choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", choices=["1", "2", "3", "4", "5", "6"])

            if choice == "1":
                self.keyword = Prompt.ask("Enter the keyword")
                self.async_fetch_keywords()
            elif choice == "2":
                self.display_keywords()
                input("\nPress Enter to return to the menu...")
            elif choice == "3":
                if self.related_keywords:
                    file_format = Prompt.ask("Choose file format (txt, csv, json)", choices=["txt", "csv", "json"])
                    self.export_keywords(file_format=file_format)
                else:
                    self.console.print("[bold red]No keywords to export. Please fetch keywords first.[/bold red]")
                input("\nPress Enter to return to the menu...")
            elif choice == "4":
                self.filter_keywords_options()
                input("\nPress Enter to return to the menu...")
            elif choice == "5":
                self.settings_menu()
                input("\nPress Enter to return to the menu...")
            elif choice == "6":
                self.console.print("[bold yellow]Goodbye![/bold yellow]\n[bold yellow]Join our Telegram channels for more updates![/bold yellow]\n[cyan]https://t.me/pasjonatyk[/cyan] | [red]https://t.me/cwelplus[/red]")
                break

    def settings_menu(self):
        while True:
            self.clear_console()
            self.console.print("[bold blue]Settings Menu[/bold blue]")
            self.console.print(f"[bold cyan]1.[/bold cyan] Scraping Level: [bold green]{self.settings['scraping_level']}[/bold green] (1: Basic, 2: Moderate, 3: Extensive)")
            self.console.print(f"[bold cyan]2.[/bold cyan] Minimum Keyword Length: [bold green]{self.settings['min_keyword_length']}[/bold green]")
            self.console.print(f"[bold cyan]3.[/bold cyan] Notification Alert: [bold green]{'Enabled' if self.settings['notification_alert'] else 'Disabled'}[/bold green]")
            self.console.print(f"[bold cyan]4.[/bold cyan] API Source: [bold green]{self.settings['api_source']}[/bold green] (google, bing)")
            self.console.print(f"[bold cyan]5.[/bold cyan] Result Path: [bold green]{self.settings['result_path']}[/bold green] (default: /results)")
            self.console.print("[bold cyan]6.[/bold cyan] Back to Main Menu")

            choice = Prompt.ask("[bold yellow]Choose a setting to modify[/bold yellow]", choices=["1", "2", "3", "4", "5", "6"])

            if choice == "1":
                level = Prompt.ask("Enter scraping level (1: Basic, 2: Moderate, 3: Extensive)", choices=["1", "2", "3"])
                self.settings["scraping_level"] = int(level)
                self.console.print(f"[bold green]Scraping level set to {self.settings['scraping_level']}[/bold green]")
                self.save_settings()
            elif choice == "2":
                min_length = int(Prompt.ask("Enter minimum keyword length", default=str(self.settings["min_keyword_length"])))
                self.settings["min_keyword_length"] = min_length
                self.console.print(f"[bold green]Minimum keyword length set to {self.settings['min_keyword_length']}[/bold green]")
                self.save_settings()
            elif choice == "3":
                notification_choice = Prompt.ask("Enable notification alert? (yes/no)", choices=["yes", "no"])
                self.settings["notification_alert"] = True if notification_choice == "yes" else False
                self.console.print(f"[bold green]Notification alert {'enabled' if self.settings['notification_alert'] else 'disabled'}[/bold green]")
                self.save_settings()
            elif choice == "4":
                api_source = Prompt.ask("Choose API source (google, bing)", choices=["google", "bing"])
                self.settings["api_source"] = api_source
                self.console.print(f"[bold green]API source set to {self.settings['api_source']}[/bold green]")
                self.save_settings()
            elif choice == "5":
                result_path = Prompt.ask("Enter the result path", default=self.settings["result_path"])
                self.settings["result_path"] = result_path
                self.console.print(f"[bold green]Result path set to {self.settings['result_path']}[/bold green]")
                self.save_settings()
            elif choice == "6":
                break

    def run(self):
        self.menu()

if __name__ == "__main__":
    scraper = KeywordScraper()
    scraper.run()
    scraper.console.print("\n[bold yellow]Don't forget to join our Telegram channels for the latest updates and more tools![/bold yellow]\n[cyan]https://t.me/pasjonatyk[/cyan] | [red]https://t.me/cwelplus[/red]")

def create_requirements_file():
    with open("requirements.txt", "w") as f:
        f.write("requests\nrich\nplyer\n")