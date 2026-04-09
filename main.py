import database as db
import os

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_RED = "\033[31m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_CYAN = "\033[36m"

current_user = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print(f"{C_BLUE}{'='*60}{C_RESET}")
    print(f"{C_BOLD}{title.center(60)}{C_RESET}")
    print(f"{C_BLUE}{'='*60}{C_RESET}")
    if current_user:
        role_color = C_RED if current_user[1] == 'admin' else C_GREEN
        print(f"Zalogowany: {C_BOLD}{role_color}{current_user[1].upper()}{C_RESET}")
    else:
        print(f"Zalogowany: {C_BOLD}Gość{C_RESET}")
    print("-" * 60)

def main_menu():
    print_header("FOOTBALL MATCH CENTER")
    if not current_user:
        print(f"{C_CYAN}1.{C_RESET} Logowanie")
        print(f"{C_CYAN}2.{C_RESET} Rejestracja nowego konta") # NOWA OPCJA
    else:
        print(f"{C_CYAN}1.{C_RESET} Wyloguj")
        
    print(f"{C_CYAN}3.{C_RESET} Przeglądaj mecze (wg Sezonu)")
    print(f"{C_CYAN}4.{C_RESET} Tabela Ligowa ")
    print(f"{C_CYAN}5.{C_RESET} Szukaj drużyny ")
    
    if current_user and current_user[1] == 'admin':
        print(f"{C_RED}6. [ADMIN] Dodaj wynik meczu{C_RESET}")
        
    print(f"{C_CYAN}0.{C_RESET} Wyjście")
    return input("\n👉 Wybierz opcję: ")
def register_screen():
    print_header("REJESTRACJA")
    while True:
        username = input("Podaj login (min. 3 znaki): ").strip()
        if len(username) < 3:
            print(f"{C_RED}Login jest za krótki! Spróbuj ponownie.{C_RESET}")
            continue
        if " " in username:
            print(f"{C_RED}Login nie może zawierać spacji!{C_RESET}")
            continue
        break
    while True:
        password = input("Podaj hasło (min. 4 znaki): ").strip()
        if len(password) < 4:
            print(f"{C_RED}Hasło jest za krótkie!{C_RESET}")
            continue
            
        confirm = input("Powtórz hasło: ").strip()
        if password != confirm:
            print(f"{C_RED}Hasła nie są identyczne! Spróbuj ponownie.{C_RESET}")
            continue
        break
    success, message = db.register_user(username, password)
    if success:
        print(f"\n{C_GREEN}✅ {message}{C_RESET}")
        print("Możesz się teraz zalogować.")
    else:
        print(f"\n{C_RED}❌ {message}{C_RESET}")
    
    input("\n[Enter] aby wrócić")
def login():
    global current_user
    print_header("LOGOWANIE")
    user = input("Login: ")
    password = input("Hasło: ")
    result = db.login(user, password)
    if result:
        current_user = result
        print(f"\n{C_GREEN} Zalogowano pomyślnie!{C_RESET}")
    else:
        print(f"\n{C_RED} Błąd logowania.{C_RESET}")
    input("\n[Enter] aby kontynuować")

def view_match_details():
    match_id = input("\n⚽ Podaj ID meczu, aby zobaczyć strzelców (lub Enter by pominąć): ")
    if not match_id: return

    details = db.get_match_details(match_id)
    if not details:
        print(f"{C_RED}Nie znaleziono meczu.{C_RESET}")
        input("Enter")
        return

    info = details['info']
    events = details['events'] 

    print(f"\n{C_BOLD}--- SZCZEGÓŁY MECZU ---{C_RESET}")
    print(f"{C_YELLOW}{info[4]}{C_RESET}")
    score_display = f"{C_BOLD}{info[0]} {info[2]} - {info[3]} {info[1]}{C_RESET}"
    print(f"\n{score_display.center(50)}")
    print("-" * 50)

    if not events:
        print("Brak zarejestrowanych zdarzeń.")
    else:
        print(f"{'Min':<5} | {'Zawodnik':<20} | {'Drużyna'}")
        print("-" * 40)
        for e in events:
            icon = "⚽" if e[3] == 'goal' else "🟨"
            print(f"{e[1]:<5} | {icon} {e[0]:<17} | {e[2]}")
    
    input("\n[Enter] aby wrócić...")

def show_matches_screen():
    print_header("LISTA MECZÓW")
    season_id = input("Podaj ID sezonu (np. 9 dla 2024/25): ") or "9"
    matches = db.get_matches_by_season(season_id)
    
    if not matches:
        print("Brak meczów dla tego sezonu.")
        input("Enter...")
        return

    print(f"\n{'ID':<4} | {'Data':<12} | {'Gospodarz':<18} | {'Wynik':^7} | {'Gość':<18}")
    print("-" * 70)
    
    for m in matches:
        res = f"{m[5]}:{m[6]}" if m[5] is not None else "-:-"
        if m[5] is not None:
            color = C_GREEN if m[5] > m[6] else (C_RED if m[5] < m[6] else C_YELLOW)
            res_str = f"{color}{res:^7}{C_RESET}"
        else:
            res_str = f"{res:^7}"

        print(f"{m[0]:<4} | {m[4]:<12} | {m[1]:<18} | {res_str} | {m[2]:<18}")
    view_match_details()

def show_standings():
    print_header("TABELA LIGOWA")
    season_id = input("Podaj ID sezonu (np. 9): ") or "9"
    table = db.get_season_standings(season_id)
    
    print(f"\n{'Msc':<4} | {'Drużyna':<20} | {'M':<3} | {'Pkt':<4} | {'W':<3} | {'R':<3} | {'P':<3} | {'Bramki'}")
    print("-" * 75)
    
    for i, (team, stats) in enumerate(table, 1):
        color = C_YELLOW if i == 1 else (C_GREEN if i <= 4 else C_RESET)
        goals = f"{stats['gz']}-{stats['gs']}"
        print(f"{color}{i:<4}{C_RESET} | {team:<20} | {stats['m']:<3} | {C_BOLD}{stats['pts']:<4}{C_RESET} | {stats['w']:<3} | {stats['d']:<3} | {stats['l']:<3} | {goals}")
    
    input("\n[Enter] aby wrócić")

def search_team():
    print_header("WYSZUKIWARKA")
    query = input("Wpisz nazwę drużyny (np. Real): ")
    results = db.search_matches_by_team(query)
    
    print(f"\nZnaleziono {len(results)} ostatnich meczów:")
    for m in results:
        print(f"[{m[5]}] {m[1]} {m[3]}:{m[4]} {m[2]} (ID: {m[0]})")
    
    view_match_details()

def admin_panel():
    while True:
        print_header("PANEL ADMINA")
        print(f"{C_CYAN}1.{C_RESET} Edytuj wynik meczu (Update)")
        print(f"{C_CYAN}2.{C_RESET} Dodaj nową drużynę (Create)")
        print(f"{C_CYAN}3.{C_RESET} Dodaj nowego piłkarza (Create)")
        print(f"{C_RED}4. Usuń mecz (Delete){C_RESET}")
        print(f"{C_RED}5. Usuń piłkarza (Delete){C_RESET}")
        print(f"{C_CYAN}0.{C_RESET} Powrót do menu głównego")
        
        opcja = input("\n Wybierz opcję: ")
        
        if opcja == '0':
            return 
        elif opcja == '1':
            print("\n--- EDYCJA MECZU ---")
            match_id = input("Podaj ID meczu: ")
            try:
                details = db.get_match_details(match_id)
                if not details:
                    print(f"{C_RED}Nie znaleziono meczu o takim ID.{C_RESET}")
                    input("Enter...")
                    continue
                
                info = details['info']
                print(f"Edytujesz: {C_BOLD}{info[1]} vs {info[2]}{C_RESET} (Data: {info[4]})")
                
                h_score = int(input(f"Gole {info[1]} (Gospodarze): "))
                a_score = int(input(f"Gole {info[2]} (Goście): "))
                
                scorers_list = []
                print("\n--- Dodawanie strzelców ---")
                while True:
                    dec = input("Dodać strzelca? (t/n): ")
                    if dec.lower() != 't': break
                    try:
                        p_id = int(input("ID Piłkarza: "))
                        minute = int(input("Minuta: "))
                        scorers_list.append((p_id, minute))
                    except ValueError:
                        print("Błędne dane (muszą być liczby).")

                db.add_match_results(match_id, h_score, a_score, scorers_list)
                
            except ValueError:
                print(f"{C_RED}Błąd: Wprowadzono niepoprawne liczby.{C_RESET}")
        elif opcja == '2':
            print("\n--- NOWA DRUŻYNA ---")
            name = input("Nazwa drużyny: ")
            city = input("Miasto: ")
            stadium = input("Stadion: ")
            
            if name and city:
                success, msg = db.add_team(name, city, stadium)
                color = C_GREEN if success else C_RED
                print(f"\n{color}{msg}{C_RESET}")
            else:
                print(f"{C_RED}Nazwa i miasto są wymagane!{C_RESET}")

        elif opcja == '3':
            print("\n--- NOWY PIŁKARZ ---")
            try:
                team_id = int(input("ID Drużyny: "))
                first_name = input("Imię: ")
                last_name = input("Nazwisko: ")
                position = input("Pozycja (np. Napastnik): ")
                
                if first_name and last_name:
                    success, msg = db.add_player(team_id, first_name, last_name, position)
                    color = C_GREEN if success else C_RED
                    print(f"\n{color}{msg}{C_RESET}")
                else:
                    print(f"{C_RED}Imię i nazwisko są wymagane!{C_RESET}")
            except ValueError:
                print(f"{C_RED}ID Drużyny musi być liczbą.{C_RESET}")

        elif opcja == '4':
            print(f"\n{C_RED}--- USUWANIE MECZU ---{C_RESET}")
            match_id = input("Podaj ID meczu do usunięcia: ")
            confirm = input(f"Czy na pewno usunąć mecz {match_id}? Operacji nie da się cofnąć! (tak/nie): ")
            
            if confirm.lower() == 'tak':
                success, msg = db.delete_match(match_id)
                color = C_GREEN if success else C_RED
                print(f"\n{color}{msg}{C_RESET}")
            else:
                print("Anulowano.")
        elif opcja == '5':
            print(f"\n{C_RED}--- USUWANIE PIŁKARZA ---{C_RESET}")
            player_id = input("Podaj ID piłkarza: ")
            confirm = input("Czy na pewno usunąć? (tak/nie): ")
            
            if confirm.lower() == 'tak':
                success, msg = db.delete_player(player_id)
                color = C_GREEN if success else C_RED
                print(f"\n{color}{msg}{C_RESET}")
            else:
                print("Anulowano.")

        else:
            print("Nieprawidłowa opcja.")
        
        input("\n[Enter] aby kontynuować...")
if __name__ == '__main__':
    while True:
        choice = main_menu()
        if choice == '1': login()
        elif choice == '2': 
            if not current_user:
                register_screen()
            else:
                pass
        elif choice == '3': show_matches_screen()
        elif choice == '4': show_standings()
        elif choice == '5': search_team()
        elif choice == '6' and current_user and current_user[1] == 'admin': admin_panel()
        elif choice == '0':
            print(f"\n{C_CYAN}Do widzenia! 👋{C_RESET}")
            break
        else:
            if current_user and choice == '1':
                 pass
            else:
                 print("Nieprawidłowa opcja.")
