import http.server
import socketserver
import webbrowser

def start_server(server_port):
    # 创建一个简单的HTTP请求处理程序，该处理程序会提供当前目录下的文件
    handler = http.server.SimpleHTTPRequestHandler

    # 创建一个TCPServer并绑定到指定端口
    with socketserver.TCPServer(("", server_port), handler) as httpd:
        print(f"Serving at port {server_port}")

        # 开启服务器，直到用户按下Ctrl+C停止
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass



    print("Server stopped.")


if __name__ == '__main__':
    # 使用webbrowser在默认浏览器中打开修改后的HTML文件
    webbrowser.open("http://192.168.70.59:15665/html/graphForJava.html")
    # 使用端口号15665，你也可以选择其他端口号
    port = 15665
    start_server(port)
