import socket
import threading

# Funktion för att ta emot meddelanden från servern
def receive_messages(client_socket):
    '''
    Funktion som kontinuerligt tar emot meddelande från servern och printar ut de. Om ett undantag inträffar
    printar den ut ett meddelande om att anslutningen bröts och stänger klientens socket och avbryter loopen
    '''
    while True:
        try:
            # Tar emot meddelanden från servern
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Anslutningen till servern bröts.")
            client_socket.close()
            break

# Funktion för att skicka meddelanden till servern
def send_messages(client_socket):
    '''
    Funktion som körs oändlig för att låta användaren skicka flera meddelande under samma anslutning.
    Den använder sig utav en IF-sats för att kontrollera om användaren vill lämna chatten genom att skriva /leave,
    annars skickar den ut meddelande som ett vanlig meddelande.
    '''
    while True:
        message = input('')
        # If sats för att kunna lämna chatrummet om användaren vill
        if message.lower() == '/leave':
            print("Du har lämnat chatrummet.")
            client_socket.close()
            break
        else:
            client_socket.send(message.encode('utf-8'))

# Starta klienten och anslut till servern
def start_client():
    '''
    Funktionen skapar en ny TCP-socket och ansluts till servern IP-adress och port.
    Användarens nickname skickas till servern för identifering.
    Två trådar startas, en för att skicka meddelande och den andra för att ta emot meddelande.
    Och om något går fel skickas det ett fel meddelande till användaren.
    '''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 5555))

        # Ange ett användarnamn
        nickname = input("Ange ditt användarnamn: ")
        client.send(nickname.encode('utf-8'))

        # Starta tråd för att ta emot meddelanden
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        # Starta tråd för att skicka meddelanden
        send_thread = threading.Thread(target=send_messages, args=(client,))
        send_thread.start()
        send_thread.join()
    
    except Exception as e:
        print("Kunde inte ansluta till servern:", e)
        client.close()

def menu():
    '''
    Meny som använder sig utav en loop för att låta användaren bestämma vad hen vill göra.
    Använder sig utav en IF-sats för att kontrollera vad användaren vill göra.
    '''
    while True:
        print("\nVälj ett av alternativ:")
        print("1. Ansut till chatrummet")
        print("2. Avsluta programmet")
        choice = input("Ditt val: ")

        if choice == '1':
            start_client()
        elif choice == '2':
            print("Programmet avslutas")
            break
        else:
            print("Ogiltigt val, prova igen")

# Starta klienten
if __name__ == "__main__":
    menu()

