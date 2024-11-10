import socket
import threading
from datetime import datetime

# Lista över alla anslutna klienter och deras användarnamn
clients = []
nicknames = []

# Funktion som hanterar klientens meddelanden
def handle_client(client_socket):
    '''
    Funktin som tar emot meddelande från klienten, kontrollera om klienten har skickat ett kommando eller 
    om meddelande inte har någon kommando skickas det som ett vanlig meddelande. Den har också ett 
    exeption om anslutningen bryts och tar bort klienten. 
    Den sänder ett meddelande till alla andra anslutna om att användaren har lämnat chatten
    '''
    while True:
        try:
            # Tar emot meddelande från klienten
            message = client_socket.recv(1024).decode('utf-8')
            # Tar emot upp till 1024 bytes av data från klienten

            # If sats för att kontrollera om klienten har skickat ett kommando
            if message == '/users':
                # Om /users används skickas det ur en lista på anslutna användare
                client_socket.send(f'Anslutna användaren: {", ".join(nicknames)}'.encode('utf-8'))
            elif message == '/help':
                # Om klienten skickar /help skickas det ut en lista på alla tillgänliga kommando
                help_message = "Tillgängliga kommandon: \n/users - Lista alla anslutna användaren \n/leave - Lämna chatrummet \n/help - Visa denna hjälp"
                client_socket.send(help_message.encode('utf-8'))
            else:
                # Om meddelande inte har någon kommando skickas det som ett vanlig meddelande
                # Hämta index för den aktuella klienten i clients-listan
                index = clients.index(client_socket)
                # Använder index för att hämta klientens användar namn från nicknames-listan
                nickname = nicknames[index]
                
                # Sänder meddelandet tillsammans med användarnamnet med hjälp av broadcast funktionen
                broadcast(f'{nickname}: {message}', client_socket)
        except:
            # Hämtar index för den klienten i clients-listan
            index = clients.index(client_socket)
            # Tar bort klienten socket från clients-listan
            clients.remove(client_socket)
            # Stänger anslutningen
            client_socket.close()

            # Hämtar klientens användarnamn från nicknames-listan
            nickname = nicknames[index]
            # Sänder ett meddelande till alla andra anslutna om att användaren har lämnat chatten
            broadcast(f'{nickname} lämnade chatten!', client_socket)
            # Tar bort användarnamnet från nicknames-listan
            nicknames.remove(nickname)
            # Avslutar while-loopen för att stänga av tråden för denna klient eftersom anslutningen har brutits
            break

# Funktion för att sända meddelande till alla anslutna klienter
def broadcast(message, client_socket):
    '''
    Funktion för att sända meddelande till alla anslutna klienter. 
    Lägger till en tidsstämpel till alla meddelande, sedan lägger till tidsstämpel och själva meddelande till 
    full_message varibeln för att kunna skicka ut tiden en meddelande skickades. 
    Iterera över alla anslutna klienter, kontrollerar att meddelande inte skickas tillbacka till avsändaren.
    Om det uppstår nåt fel stänger klientens socket.
    '''

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f'[{timestamp}] {message}'
    # Iterera över alla anslutna klienter
    for client in clients:
        # Kontrollerar att inte skicka meddelande tillbaka till avsändaren
        if client != client_socket:
            try:
                client.send(full_message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

# Starta TCP-servern
def start_server():
    '''
    Funktion för att startar TCP-servern som hanterar anslutningar från klienter.
    Sätter servern i lyssningsläge, vilket gör att den väntar på inkommande anslutningar från klienter.
    '''

    # Skapar ett nytt socket-objekt för servern AF-INET anger att vi använder IPv4, och SOCK_STREAM anger att vi använder TCP-protokollet
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555)) # Binder serverns socket till IP-adressen 0.0.0.0 och porton 5555
    server.listen()

    # Skriver ut ett meddelande till konsollen när serven är aktiv och redo
    print("Servern är igång och väntar på klienter...")

    # En oändlig loop som accepterar nya anslutningar
    while True:
        client_socket, addr = server.accept()
        print(f"Ny anslutning från {addr}")

        # Tar emot klientens nickname eller användarnamn
        nickname = client_socket.recv(1024).decode('utf-8')
        nicknames.append(nickname) # Lägger till den i nicknames-listan
        clients.append(client_socket) # Lägger till klientens sokcet i clients-listan

        # Skriver ut användarsnamnet och meddelar alla anslutna om en ny användare
        print(f'Användarnamn är {nickname}!')
        broadcast(f'{nickname} har anslutit sig till chatten!', client_socket)
        client_socket.send('Du är nu ansluten till chatten!'.encode('utf-8'))

        # Skickar en välkomstmeddelande efter klienten har anslutit
        client_socket.send("\nVälkommen till chatrummet! Använd /help för kommando. ".encode('utf-8'))

        # Starta en ny tråd för att hantera klienten
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

# Starta servern
if __name__ == "__main__":
    start_server()
