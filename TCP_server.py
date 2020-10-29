import socket
import threading


# no database
product = {"沙魚": {"amount": 1000, "price": 450},
           "軟絲": {"amount": 1000, "price": 850},
           "花蟹": {"amount": 1000, "price": 750},
           "花蟹(小的)": {"amount": 1000, "price": 450},
           "花蟹(再小一點)": {"amount": 1000, "price": 350},
           "大沙母": {"amount": 1000, "price": 850},
           "海瓜子": {"amount": 1000, "price": 180},
           "奶油貝": {"amount": 1000, "price": 250},
           "生蠔": {"amount": 1000, "price": 180},
           "木瓜螺": {"amount": 1000, "price": 350},
           "小花龍": {"amount": 1000, "price": 1250},
           "水姑娘": {"amount": 1000, "price": 1680},
           "象蚌": {"amount": 1000, "price": 650}}

clients = {}
# peters = 20000000
# np(a) = (0.01*op)^(a/10 + 0.5) + op


def clientBuyProduct(userName, pName, amount, balance):
    # 用戶端買東西
    msg = {"statusCode": 0}
    if (pName in product):
        _product = product[pName]
        if(amount > 0 and _product["amount"] >= amount):
            oldPrice = _product["price"]
            cost = amount * oldPrice
            if (cost > balance):
                msg["statusCode"] = -1
                msg["errorMsg"] = "你確定你有足夠的錢嗎？這要花你 %.2f 元喔" % cost
            else:
                newAmount = _product["amount"] - amount
                newPrice = round(oldPrice + (oldPrice * 0.01)
                                 ** (amount / 20), 2)
                _product["price"] = newPrice
                _product["amount"] = newAmount

                # ====
                msg["statusCode"] = 1
                msg["message"] = "你只要相信海，海就會幫助你，你用 %.2f 元買了 %d 隻 %s" % (
                    cost, amount, pName)
                msg["product"] = pName
                msg["amount"] = amount
                msg["cost"] = cost
                # ====

                print("%s 以時價 %.2f 買了 %d 隻 %s" %
                      (userName, oldPrice, amount, pName))
                print("%s 時價變動為 %.2f，剩餘數量為 %d" % (pName, newPrice, newAmount))
                broadcast("[!] %s 漲價了！" % pName)
        else:
            msg["statusCode"] = -1
            msg["errorMessage"] = "庫存不夠欸，你要不要買別的"
            print(amount)
    else:
        msg["statusCode"] = -1
        msg["errorMessage"] = "海龍王沒賣這種海鮮"
    return msg


def clientSellProduct(userName, pName, amount):
    # return a msg including product name and totalPrice

    msg = {"statusCode": 0}
    if (pName in product):
        _product = product[pName]
        if(amount > 0):
            oldPrice = _product["price"]
            newAmount = _product["amount"] + amount

            newPrice = round(oldPrice - (oldPrice * 0.009901)
                             ** (amount / 20), 2)

            _product["price"] = newPrice
            _product["amount"] = newAmount
            msg["statusCode"] = 2
            msg["message"] = "你以總價 %.2f 的價錢將 %d 隻 %s賣給了海龍王，海龍王會感謝你的" % (
                oldPrice * amount, amount, pName)
            msg["product"] = pName
            msg["amount"] = amount
            msg["revenue"] = oldPrice * amount
            print("%s 以時價 %.2f 賣了 %d 隻 %s" %
                  (userName, oldPrice, amount, pName))
            print("%s 時價變動為 %.2f，剩餘數量為 %d" % (pName, newPrice, newAmount))
            broadcast("[!] %s 降價了！" % pName)
        else:
            msg["statusCode"] = -1
            msg["errorMessage"] = "你的貨呢"
    else:
        msg["statusCode"] = -1
        msg["errorMessage"] = "海龍王不收購這種東西"
    return msg


def lookProductList():
    msg = {"statusCode": 3}
    msg["list"] = product
    return msg


def broadcast(msg):
    emsg = {"statusCode": 0, "msg": msg}
    for user_name in clients:
        client = clients.get(user_name)
        client.send(str(emsg).encode("UTF-8"))


def client_thread(client_socket, addr):
    user_name = client_socket.recv(1024).decode("UTF-8")
    while user_name in clients:
        client_socket.send("exist".encode("UTF-8"))
        user_name = client_socket.recv(1024).decode("UTF-8")

    client_socket.send("enter ok".encode("UTF-8"))
    clients[user_name] = client_socket
    address = "%s:%d" % (addr[0], addr[1])
    print("[!] 來自 %s 的 %s 進入市場了" % (address, user_name))

    broadcast("[!] 有新的使用者進入市場了！")

    run = True

    while run:

        try:
            dmsg = client_socket.recv(1024).decode("UTF-8")
            msg = eval(dmsg)

            responseMsg = {}



            if msg["optionCode"] == 1:
                pName = msg["product"]
                amount = int(msg["amount"])
                balance = int(msg["balance"])
                responseMsg = clientBuyProduct(
                    user_name, pName, amount, balance)
                # ...
            elif msg["optionCode"] == 2:
                pName = msg["product"]
                amount = int(msg["amount"])
                responseMsg = clientSellProduct(user_name, pName, amount)
                # ...
            elif msg["optionCode"] == 3:
                responseMsg = lookProductList()
                # ...
            elif msg["optionCode"] == 0:
                responseMsg = {"statusCode": 999}
                
            response = str(responseMsg).encode('UTF-8')
            client_socket.send(response)

            if msg["optionCode"] == 0:
                run = False
                del clients[user_name]
                client_socket.close()
                print("[!] %s 離線了" % user_name)
                broadcast("[!] 有使用者離開市場了！")
        # 'client_socket.close()
        except:
            print("[!] %s 意外斷線了" % user_name)
            del clients[user_name]
            broadcast("[!] 有使用者離開市場了！")
            run = False


host = "169.254.2.203"
port = 8888

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

server.listen(5)
print("海龍王市場開市")

while True:
    client, addr = server.accept()

    client_handle = threading.Thread(
        target=client_thread, args=(client, addr,))
    client_handle.start()