import ugfx, easydraw, system, badge

ugfx.init()
ugfx.clear(ugfx.BLACK)
ugfx.flush()
ugfx.clear(ugfx.WHITE)
ugfx.flush()

ugfx.orientation(0)
screen_size = (ugfx.width()-15,ugfx.height())
max_onscreen = 10 # 10 lines is max that can fit on screen

font_types = (
  ("Roboto_Regular12", 12, 45),
  ("Roboto_Regular18", 18, 33),
  ("Roboto_Regular22", 22, 20))

ugfx.input_init()

ugfx.input_attach(ugfx.JOY_DOWN, lambda pressed: move_view("down", pressed))
ugfx.input_attach(ugfx.JOY_UP, lambda pressed: move_view("up", pressed))
ugfx.input_attach(ugfx.JOY_LEFT, lambda pressed: move_view("left", pressed))
ugfx.input_attach(ugfx.JOY_RIGHT, lambda pressed: move_view("right", pressed))
ugfx.input_attach(ugfx.BTN_START, lambda pressed: quit(pressed))

def quit(pressed):
  if pressed:
  	system.home()

def get_string_width(string, font_id):
	return ugfx.get_string_width(string, font_types[font_id][0])
  
def parse_input_line(input_line, breaking_mode):
	if input_line.startswith("###"):
		font_id = 0
	elif input_line.startswith("##"):
		font_id = 1
	elif input_line.startswith("#"):
		font_id = 2
	else:
		font_id = 0

	input_line = input_line.lstrip("#")

	if breaking_mode=="experimental":
		smallletters=['ijl !1t():\'.,']
		halfletters=['IJT[]']
		words=input_line.split(" ")
		sentencelen=0
		sentence=""
		output_lines=[]
		output_fonts = [font_id]
		for word in words:
			wordlen=2
			for letter in word:
				if letter in smallletters:
					wordlen+=2
				elif letter in halfletters:
					wordlen+=4
				else:
					wordlen+=6
			if sentencelen+wordlen<screen_size[0]:
				sentencelen+=wordlen
				sentence=sentence+" "+word if len(sentence) else word
			else:
				output_fonts += [font_id]
				output_lines+=[sentence]
				sentencelen=wordlen
				sentence=word
		output_lines+=[sentence]
	elif breaking_mode=="better":
		output_lines = [""]
		output_fonts = [font_id]
		counter = 0
		current_width = 0
		for char in input_line:
			current_char_width = get_string_width(char, font_id)
			if current_width + current_char_width < screen_size[0]:
				output_lines[counter] += char
				current_width += current_char_width
			else:
				output_lines += [char]
				output_fonts += [font_id]

				counter += 1
				current_width = 0
	elif breaking_mode == "worse":
		output_lines = []
		output_fonts = []
		length = font_types[font_id][2]
		while input_line:
			if len(input_line) >= length:
				output_lines += [input_line[:length]]
				output_fonts += [font_id]
				input_line = input_line[length:]
			else:
				output_lines += [input_line]
				output_fonts += [font_id]
				input_line = ""
	else: 
		raise ValueError("this breaking mode does not exist")

	return output_lines, output_fonts

def create_view(start_position, action):
	global view,parsed_lines,parsed_fonts,article_length
	
	ugfx.clear(ugfx.WHITE)
	steps = 0
	if action == "next":
		current_height = 0, font_types[parsed_fonts[start_position]][1]
		while current_height[1] <= screen_size[1] and steps+start_position < article_length:
			ugfx.string(
				5,
				current_height[0],
				parsed_lines[start_position+steps].strip(),
				font_types[parsed_fonts[start_position+steps]][0],
				ugfx.BLACK)
			steps += 1
			current_height = (current_height[1],
							  current_height[1] + font_types[parsed_fonts[start_position+steps]][1])
		view = (start_position, start_position + steps)
	elif action == "prev":
		current_height = 0, font_types[parsed_fonts[start_position]][1]
		while current_height[1] <= screen_size[1] and steps+start_position > 0:
			ugfx.string(
				5,
				screen_size[1] - current_height[1],
				parsed_lines[start_position+steps].strip(),
				font_types[parsed_fonts[start_position+steps]][0],
				ugfx.BLACK)
			steps -= 1
			current_height = (current_height[1],
							  current_height[1] + font_types[parsed_fonts[start_position+steps]][1])
		view = (start_position+steps, start_position)
	else:
		raise ValueError("this action doesn't exist")

	ugfx.flush()
	return view

def move_view(button_direction, pressed):
	global view,article_length,start,max_onscreen,f,eof
	if pressed:
		if button_direction == "down":
			start_position = view[0]+1
			action = "next"
		elif button_direction == "up":
			start_position = view[0]-1
			action = "next"
		elif button_direction == "right":
			start_position = view[1]
			action = "next"
		elif button_direction == "left":
			start_position = view[0]
			action = "prev"
		else:
			raise ValueError("this direction doesn't exist")
		if start_position <= 0:
			start_position = 0
			action = "next"
		elif start_position >= article_length:
			start_position = article_length
			action= "prev"
		if start_position + max_onscreen >= article_length:
			if f:
			  ugfx.fill_circle(291, 5, 10, ugfx.BLACK)
			  ugfx.flush()
			  if not eof:
				if not read_data():
				  eof = True
				  print('EOF')
			else:
			  print('File not yet read!')
		print("scroll: " + str(start_position)+" "+str(article_length))
		view = create_view(start_position, action)

def read(path, render="experimental", begin = 0, lines = 15):
  global view,start,read_lines,breaking_mode,parsed_lines,parsed_fonts,article_length,f,eof,first_run,file
  start = begin
  read_lines = lines
  breaking_mode = render
  parsed_lines = []
  parsed_fonts = []
  article_length = 0
  eof = False
  first_run = True
  file = path

  easydraw.messageCentered("Loading "+path+"\nFrom "+str(start)+" to "+str(start+lines), True, "/media/busy.png")
  try:
	f = open(path,mode = 'r',encoding = 'utf-8')
	easydraw.messageCentered("Rendering", True, "/media/ok.png")
	read_data()
	view = create_view(0, "next")
  except BaseException as e:
	import sys,system
	sys.print_exception(e)
	system.home()
	  
def read_data():
  global start,start_position,read_lines,breaking_mode,parsed_lines,parsed_fonts,article_length,f,first_run,file
  badge.nvs_set_u16('md_reader', file.replace('/', '_')[-15:], start)
  data_read = False
  print("data: "+str(start)+" "+str(read_lines))
  for i, raw_line in enumerate(f):
	if first_run and i < start:
	  pass
	else:
	  data_read = True
	  temp_parsed_lines, temp_parsed_fonts = parse_input_line(raw_line, breaking_mode)
	  parsed_lines += temp_parsed_lines
	  parsed_fonts += temp_parsed_fonts
	  if i > read_lines:
		article_length = len(parsed_lines)
		start += i
		break
  first_run = False
  return data_read