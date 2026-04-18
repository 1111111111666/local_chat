#python server.py 
import asyncio
import websockets
import json
from datetime import datetime
import socket

# Список всех подключённых клиентов
clients = set()

async def handler(websocket):
    """Обрабатывает одно подключение клиента"""
    clients.add(websocket)
    name = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            # Первое сообщение — пользователь представился
            if data['type'] == 'join':
                name = data['name']
                await broadcast({
                    'type': 'system',
                    'text': f'{name} присоединился к чату',
                    'time': datetime.now().strftime("%H:%M:%S")
                })
                print(f"📥 {name} подключился")
            
            # Обычное текстовое сообщение
            elif data['type'] == 'message':
                print(f"💬 {name}: {data['text']}")
                await broadcast({
                    'type': 'message',
                    'name': name,
                    'text': data['text'],
                    'time': datetime.now().strftime("%H:%M:%S")
                })
    
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ {name or 'Кто-то'} отключился")
    finally:
        clients.remove(websocket)
        if name:
            await broadcast({
                'type': 'system',
                'text': f'{name} покинул чат',
                'time': datetime.now().strftime("%H:%M:%S")
            })

async def broadcast(message):
    """Отправляет сообщение всем клиентам"""
    if clients:
        # ✅ ИСПРАВЛЕНО: создаём задачи из корутин
        tasks = [asyncio.create_task(client.send(json.dumps(message))) for client in clients]
        await asyncio.wait(tasks)

async def main():
    # Запускаем сервер на всех интерфейсах
    async with websockets.serve(handler, "0.0.0.0", 8765):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print("=" * 50)
        print("🔥 ЧАТ-СЕРВЕР ЗАПУЩЕН!")
        print("=" * 50)
        print(f"WebSocket порт: 8765")
        print(f"IP-адрес вашего ноутбука: {local_ip}")
        print("=" * 50)
        print("Что делать дальше:")
        print("1. Запустите HTTP-сервер для раздачи client.html")
        print("   (в другом терминале: python -m http.server 8080)")
        print("2. Сообщите другу:")
        print(f"   - Подключиться к вашему Wi-Fi")
        print(f"   - Открыть http://{local_ip}:8080/client.html")
        print("=" * 50)
        
        await asyncio.Future()  # Бесконечная работа

if __name__ == "__main__":
    asyncio.run(main())