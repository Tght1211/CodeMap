import psutil


def shut_down(server_port):
    # 关掉对应端口的服务
    def find_and_stop_server(port):
        for process in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in process.connections():
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        print(f"Stopping server with PID {process.info['pid']}")
                        psutil.Process(process.info['pid']).terminate()
                        return True
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                pass
        return False

    if find_and_stop_server(server_port):
        print("Server stopped.")
    else:
        print("Server not found.")


if __name__ == '__main__':
    # 指定之前启动服务器时的端口
    server_port = 15665
    shut_down(server_port)
