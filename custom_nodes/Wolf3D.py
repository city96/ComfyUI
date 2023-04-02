from io import BytesIO
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch
import json
import os
import requests

class Wolf3D:
	def __init__(self):
		self.output_dir = os.path.join(r"D:\Software\AI\ComfyUI-dev", "temp")
		self.type = "temp"

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"sprite": ("IMAGE", ),
				"sprite_mask": ("MASK", ),
				"wall": ("IMAGE", ),
				"door": ("IMAGE", ),
				"stone": ("IMAGE", ),
				"wood": ("IMAGE", ),
			},
			"optional": {
				"text": ("STRING", {"default" : "asd", "hascanvas": True}),
			}
		}

	RETURN_TYPES = ()
	OUTPUT_NODE = True
	FUNCTION = "Wolf3D"
	CATEGORY = "3D"
	
	def Wolf3D(self, sprite, sprite_mask, wall, door, stone, wood, text="asd"):
		filename_prefix="Texture"
		def map_filename(filename):
			prefix_len = len(os.path.basename(filename_prefix))
			prefix = filename[:prefix_len + 1]
			try:
				digits = int(filename[prefix_len + 1:].split('_')[0])
			except:
				digits = 0
			return (digits, prefix)

		def np_to_img(image):
			i = 255. * image.cpu().numpy()
			img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
			return img
		
		def get_texture(wall,door,stone,wood):
			texture = Image.new("RGB",(128,256))
			wall = np_to_img(wall)
			wall = wall.resize((64,64), Image.NEAREST)
			texture.paste(wall, (0, 0))
			texture.paste(wall, (64, 0))

			door = np_to_img(door)
			door = door.resize((64,64), Image.NEAREST)
			texture.paste(door, (0, 64))
			texture.paste(door, (64, 64))

			stone = np_to_img(stone)
			stone = stone.resize((64,64), Image.NEAREST)
			texture.paste(stone, (0, 128))
			texture.paste(stone, (64, 128))

			wood = np_to_img(wood)
			wood = wood.resize((64,64), Image.NEAREST)
			texture.paste(wood, (0, 192))
			texture.paste(wood, (64, 192))
			return texture

		def get_sprite(img,mask):
			img = np_to_img(img)
			img = img.resize((64,64), Image.NEAREST)
			mask = np_to_img(mask).convert('L')
			mask = ImageOps.invert(mask)
			mask = mask.resize((64,64), Image.NEAREST)
			blank = Image.new("RGBA",(64,64),(255,0,0,0))
			
			asd = Image.composite(img, blank, mask)
			# asd.show()
			return asd

		subfolder = os.path.dirname(os.path.normpath(filename_prefix))
		filename = os.path.basename(os.path.normpath(filename_prefix))

		full_output_folder = os.path.join(self.output_dir, subfolder)

		if os.path.commonpath((self.output_dir, os.path.abspath(full_output_folder))) != self.output_dir:
			print("Saving image outside the output folder is not allowed.")
			return {}

		try:
			counter = max(filter(lambda a: a[1][:-1] == filename and a[1][-1] == "_", map(map_filename, os.listdir(full_output_folder))))[0] + 1
		except ValueError:
			counter = 1
		except FileNotFoundError:
			os.makedirs(full_output_folder, exist_ok=True)
			counter = 1

		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)

		results = list()
		images = [get_sprite(sprite[0],sprite_mask).resize((64,64), Image.NEAREST),get_texture(wall[0],door[0],stone[0],wood[0])]
		for image in images:
			file = f"{filename}_{counter:05}_.png"
			image.save(os.path.join(full_output_folder, file), compress_level=4)
			results.append({
				"filename": file,
				"subfolder": subfolder,
				"type": self.type
			});
			counter += 1
		return { "ui": { "textures": results } }

NODE_CLASS_MAPPINGS = {
	"Wolf3D": Wolf3D,
}

NODE_DISPLAY_NAME_MAPPINGS = {
	"Wolf3D": "Wolf3D",
}
