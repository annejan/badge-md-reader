import easywifi,urequests,easydraw
easywifi.enable()

def get(url, path):
	easydraw.messageCentered("Downloading "+path+"\nFrom "+url, True, "/media/busy.png")
	req = urequests.get(url)
	f=open(path,"w")
	f.write(req.raw.read())
	f.close()
	easydraw.messageCentered("Downloaded "+path, True, "/media/ok.png")