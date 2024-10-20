import os,re,copy
from bs4 import BeautifulSoup
from urllib.request import urlopen
from rich.console import Console
from time import sleep

console = Console()

# Color code variables for terminal output
YELLOW = "\033[38;2;255;215;0;1;4m"
RED = "\033[38;2;255;0;0;1m"
END = "\033[0m"
def message():
	text="\033[1mThank you for using Cricfetch!\U0001F3CF\n\nWe hope you enjoyed staying up-to-date with the latest cricket news and trends. If you have any feedback or suggestions, we'd love to hear from you! Keep an eye out for future updates and improvements.\n\nSee you soon, and stay on top of the game!\U0001F3AF\033[0m"
	for msg in text:
		print(msg,flush=True,end="")
		sleep(0.01)

def center_text(text):
    """Centers text based on terminal width, excluding any ANSI escape codes."""
    clean_text = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)
    padding = (os.get_terminal_size().columns - len(clean_text)) // 2
    print(' ' * padding + text)

def display_title(text):
    """Displays a centered title with length-check to avoid overflow."""
    terminal_width = os.get_terminal_size().columns
    if len(text) > terminal_width - 3:
        print(f"{YELLOW}{text[:terminal_width - 3]}...{END}\n")
    else:
        center_text(f"{YELLOW}{text}{END}")

def fetch_page(link, message):
    """Fetches and parses a web page with error handling."""
    with console.status(f"[bold yellow]{message}...", spinner="line", spinner_style="bold red"):
        try:
            return BeautifulSoup(urlopen(link), 'lxml')
        except Exception as e:
            print(f"{RED}Error fetching the page: {e}{END}")
            return None

def save_to_file(heading, content):
    """Saves the extracted content to a file."""
    for attempt in range(2):
        file_name = input(f"Enter file name or path\n{RED}Note: Existing files will be overwritten{END}\n")
        try:
            with open(file_name, "w") as file:
                file.write(heading + "\n")
                for element in content.find_all(['p', 'h1']):
                    if element.name == "h1":
                        break
                    elif element.get_text().strip() != "Welcome to ESPN India Edition" and element.get_text().strip() != "Advertisement":
                        file.write(element.get_text() + "\n")
                break
        except (FileNotFoundError, PermissionError, IsADirectoryError, OSError, TypeError) as e:
            print(f"{RED}{str(e).capitalize()}{END}")

def clear_screen():
    """Clears the terminal screen."""
    print("\033[2J\033[H", end='')

def display_precautions():
    """Displays a set of precautionary instructions to the user."""
    terminal_width = os.get_terminal_size().columns
    print(f"\033[38;2;255;215;0;1m{'-' * terminal_width}{END}")
    center_text(f"{RED}PRECAUTIONS{END}")
    print(f"\033[38;2;255;215;0;1m{'-' * terminal_width}{END}")
    print("• Ensure a stable internet connection.\n")
    print("• Provide valid inputs when prompted.\n")
    print(f"\033[1mPlease read the precautions before proceeding.{END}\n")

    user_response = input("Wanna Continue (y/n):").strip().lower()
    if user_response == "y":
        clear_screen()
    elif user_response == "n":
        print(f"\n\033[1mProgram terminated successfully.{END}")
        os._exit(0)
    else:
        print(f"\n\033[1mProgram terminated due to {RED}invalid input.{END}")
        os._exit(0)

def handle_exit_input(user_input):
    """Terminates the program if input is '0'."""
    if user_input == "0":
        print(f"\n\033[1mProgram terminated due to {RED}invalid input.{END}")
        os._exit(0)

def main():
    src = fetch_page("https://www.espn.in/cricket/", "Extracting today's headlines")
    if src is None:
        print(f"{RED}Issue occurred while extracting news. Please check your connection or try again later.{END}")
        os._exit(0)

    original_src = copy.deepcopy(src)

    while True:
        print(f"{RED}{'-' * os.get_terminal_size().columns}{END}")
        center_text(f"{YELLOW}HEADLINES{END}")
        print(f"{RED}{'-' * os.get_terminal_size().columns}{END}")

        # Display available headlines
        headline_links = []
        for index, a in enumerate(src.find_all("a", attrs={'data-mptype': 'headline'})):
            if a['href'] not in headline_links:
                headline_links.append(a['href'])
                print(f"{index + 1}) {a.get_text()}\n")

        user_option = input("\nChoose from the options:\n1) Explore news (headlines)\n2) Search News\n").strip()

        if user_option == "1":
            news_index = input("\nEnter news number:").strip()
            handle_exit_input(news_index)
            try:
                print("\n")
                src = fetch_page(f"https://www.espn.in{headline_links[abs(int(news_index)) - 1]}", "Extracting news")
                if src is None:
                    print(f"{RED}Try again later.{END}")
                    os._exit(0)
            except Exception:
                print(f"\n\033[1mProgram terminated due to {RED}invalid news number.{END}")
                break
            else:
                heading = src.find("h1").extract().get_text()
                display_title(heading)
                for element in src.find_all(['p', 'h1']):
                    if element.name == "h1":
                        break
                    elif element.get_text().strip() != "Welcome to ESPN India Edition":
                        print(element.get_text() + "\n")

                approve = input("Would you like to save it to a file (y/n):").strip().lower()
                if approve == "y":
                    save_to_file(heading.capitalize(), original_src)

            explore_more = input("\nExplore more (y/n):").strip().lower()
            if explore_more == 'n':
                print(f"\n\033[1mProgram terminated successfully.{END}")
                clear_screen()
                message()
                break
            elif explore_more == 'y':
                src = original_src
                clear_screen()
            else:
                print(f"\n\033[1mProgram terminated due to {RED}invalid input.{END}")
                break

        elif user_option == "2":
            search_topic = input("\nEnter news topic:").strip()
            print("\n")
            topic = search_topic.replace(' ', '+')
            if re.fullmatch(r'[A-Za-z0-9+]+', topic):
                src = fetch_page(f"https://sports.ndtv.com/search/news/?q={topic}", "Extracting news")
                if src is None:
                    print(f"{RED}Kindly check your internet connection or try again later.{END}")
                    os._exit(0)
                original_src = copy.deepcopy(src)

                news_links = src.find_all("a", class_="SrcLst_ttl")[:5]
                if not news_links:
                    print("\nNo results found.")
                    break

                while True:
                    clear_screen()
                    print(f"{RED}{'-' * os.get_terminal_size().columns}{END}")
                    center_text(f"{YELLOW}NEWS{END}")
                    print(f"{RED}{'-' * os.get_terminal_size().columns}{END}")

                    # Display available news (limit to 5)
                    for count, news_link in enumerate(news_links, start=1):
                        print(f"{count}){news_link.get_text()}\n")

                    news_choice = input("\nEnter news number:").strip()
                    handle_exit_input(news_choice)
                    try:
                        selected_news = news_links[abs(int(news_choice)) - 1]['href']
                        print("\n")
                        src = fetch_page(selected_news, "Extracting news")
                        if src is None:
                            print(f"{RED}Check your internet connection or try again later.{END}")
                            os._exit(0)
                    except Exception:
                        print(f"\n\033[1mProgram terminated due to {RED}invalid news number.{END}")
                        break
                    else:
                        display_title(src.find("h1").get_text())
                        for paragraph in src.find_all("p"):
                            if paragraph.get_text().strip() != "Advertisement":
                                print(paragraph.get_text() + "\n")

                        approve = input("Want to save it to a file (y/n):").strip().lower()
                        if approve == "y":
                            save_to_file(src.find("h1").get_text().capitalize(), original_src)

                    explore_more = input("\nExplore more (y/n):").strip().lower()
                    if explore_more == 'n':
                        print(f"\n\033[1mProgram terminated successfully.{END}")
                        clear_screen()
                        message()
                        break
                    elif explore_more == 'y':
                        src = original_src
                        clear_screen()
                    else:
                        print(f"\n\033[1mProgram terminated due to {RED}invalid input.{END}")
                        break
                break
            else:
                print(f"\n\033Program terminated due to invalid topic input.{END}")
                break

        else:
            print(f"\n\033[1mProgram terminated due to {RED}invalid input.{END}")
            break

if __name__ == "__main__":
    display_precautions()
    main()
