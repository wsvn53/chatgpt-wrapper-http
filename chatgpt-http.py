import asyncio
from chatgpt_wrapper import ChatGPT

import http.server
import json
import urllib.parse
import subprocess

bot = ChatGPT(headless=False)
print("-> ChatGPT started:", bot)

def RestartChatGPT():
        subprocess.run(['pkill', 'firefox'])
        bot = ChatGPT(headless=False) 
        print("-> ChatGPT restarted:", bot) 
        return bot

class ChatGPTHandler(http.server.BaseHTTPRequestHandler):
	def do_POST(self): 
		global bot

		if self.path == '/chatgpt': 
			content_type = self.headers.get('Content-Type') 
			if content_type != 'application/json': 
				self.send_response(400) 
				self.end_headers() 
				return
 
			content_len = int(self.headers.get('Content-Length')) 
			post_body = self.rfile.read(content_len) 
			print("* Post body:", post_body) 
			post_data = json.loads(post_body.decode('utf-8'))
 
 			# get message in post_data 
			message = post_data['message'] 
			print("* Sending message:", message)

			response = ""
			retry_count = 3 
			while True: 
				response = asyncio.run(bot.ask(message)) 
				print("* Response:", response) 

				# if repsonse empty or contains "login session expired" or reach retry_count 
				if response != '' and 'login session expired' not in response:
					break 
				if retry_count == 0: 
					break

				print("* [!] Empty response, restart ChatGPT now. Remain", retry_count) 
				bot = RestartChatGPT()
				print("* Now bot using:", bot)
				retry_count = retry_count - 1

			if response == "": 
				response = "Oops, ChatGPT wrapper is striking..."

			response_payload = {'message': response} 
			response_payload_json = json.dumps(response_payload).encode('utf-8')

			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.send_header('Content-length', len(response_payload_json))
			self.end_headers()
			self.wfile.write(response_payload_json)
		else:
			self.send_response(404) 
			self.end_headers()

# use flask to start a http server to listen on 8080
server_address = ('', 8080)
httpd = http.server.HTTPServer(server_address, ChatGPTHandler)
print('-> Starting server on port 8080...')
httpd.serve_forever()
