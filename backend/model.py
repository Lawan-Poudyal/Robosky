import cv2
import numpy as np
from random import randint
from sklearn.cluster import DBSCAN
from ultralytics import YOLO
from dotenv import load_dotenv
load_dotenv()
from skidl import *

CONF = 0.35
WEIGHTS = "best.pt"
SAVE = True

def get_component_stack(image_src):
	components = get_components_bboxes(image_src)
	print(components)

	image = cv2.imread(image_src, cv2.IMREAD_GRAYSCALE)
	final_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

	mask = mask_image(image, components)

	blurred = cv2.GaussianBlur(image, (3, 3), 0)
	edges = cv2.Canny(blurred, 100, 200)
	edges = cv2.bitwise_and(edges, edges, mask=mask)
	contours, _ = cv2.findContours(
		edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
	)

	merged_contours = []

	# Process each contour and apply convex hull
	hulls = []
	for contour in contours:
		hull = cv2.convexHull(contour)
		hulls.append(hull)

	clustors = group_nearby_hulls(hulls, eps=200)
	for clustor in clustors:
		for hull in clustor:
			merged_contours.append(hull)

	comp_map = {}
	for i, clustor in enumerate(clustors):
		color = (randint(0, 255), randint(0, 255), randint(0, 255))
		clustor = remove_small_contours(clustor, 100)

		for contour in clustor:
			for comp in components:
				box = components[comp]
				center = get_center(box)
				center = (int(center[0]), int(center[1]))
				distance = cv2.pointPolygonTest(contour, center, True)
				if distance < 0:
					distance *= -1
					if distance < 400:
						if i not in comp_map:
							comp_map.update({ i: [comp]})
						elif comp not in comp_map[i]:
							comp_map[i].append(comp)
	
			cv2.drawContours(final_img, [contour], -1, color, 10)

	print(comp_map)
	comp_stack = []
	filter_ = []
	for wire in comp_map:
		for comp in comp_map[wire]:
			if comp not in filter_:
				filter_.append(comp)
	
	for comp in filter_:
		name = "_".join(comp.split("_")[:-1])
		comp_stack.append([name])
	return comp_stack

def get_components_bboxes(image_src):
	model = YOLO(WEIGHTS)
	results = model.predict(source = image_src, conf = CONF, save=SAVE)
	print(results)

	components = {}
	for result in results:
		try:
			boxes = result.boxes.xyxy
			confidences = result.boxes.conf
			labels = result.boxes.cls
	
			for box, confidence, label in zip(boxes, confidences, labels):
				x1, y1, x2, y2 = map(int, box) 
				label_name = result.names[int(label)]
				components.update({
					f"{label_name}_{randint(0, 255)}": [(x1, y1), (x2, y2)]
				})
	
		except Exception as e:
			print(e)

	return components

def mask_image(image, components):
	width = 10
	mask = np.ones(image.shape[:2], dtype=np.uint8)
	for comp in components:
		box = components[comp]
		# center = get_center(box)
		# cv2.circle(final_img, center, 2, (0, 0, 255), -1)
	
		image[
			box[0][1]:box[1][1],
			box[0][0]:box[1][0]
		] = 255
		mask[
			box[0][1]-width:box[1][1]+width,
			box[0][0]-width:box[1][0]+width
		] = 0
	return mask

def group_nearby_hulls(hulls, eps=50, min_samples=5):
	# Calculate centroids of all hulls
	centroids = calculate_centroids(hulls)

	# Apply DBSCAN clustering
	clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(centroids)

	# Group hulls based on cluster labels
	clusters = {}
	for idx, label in enumerate(clustering.labels_):
		if label not in clusters:
			clusters[label] = []
		clusters[label].append(hulls[idx])

	# Convert to a list of clusters
	return list(clusters.values())

def calculate_centroids(hulls):
	centroids = []
	for hull in hulls:
		moments = cv2.moments(hull)
		if moments['m00'] != 0:
			cx = int(moments['m10'] / moments['m00'])
			cy = int(moments['m01'] / moments['m00'])
			centroids.append([cx, cy])
		else:
			centroids.append([0, 0])	# For degenerate cases
	return np.array(centroids)

def remove_small_contours(contours, min_area):
		return [contour for contour in contours if cv2.contourArea(contour) > min_area]

def get_center(box):
	return (np.int32((box[0][0] + box[1][0]) / 2), np.int32((box[0][1] + box[1][1]) / 2))


def create_circuit_topology(comp_stack):
	print(comp_stack)
	"""
	Create a flexible circuit topology with support for variable-length lists in each layer
	"""
	# Create input & output voltages and ground reference
	vin, vout, gnd = Net('VI'), Net('VO'), Net('GND')

	# More flexible component stack with variable-length layers

	# Mapping of components
	footprint_map = {
		#"and": "Logic_Integrated_Circuits:74HC08",
		#"antenna": "RF_Module:RF_Antenna",
		"capacitor-polarized": "Capacitor_SMD:C_1825_4564Metric_Pad1.57x6.80mm_HandSolder",
		"capacitor-unpolarized": "Capacitor_SMD:C_1825_4564Metric_Pad1.57x6.80mm_HandSolder",
		#"crossover": "NetCrossover:Cross_Small",
		# "diac": "Diode:Diac",
		"diode": "Diode_THT:D_T-1_P10.16mm_Horizontal",
		# "diode-light_emitting": "LED_THT:LED_D5.0mm_P2.54mm",
		#"fuse": "Fuse:Fuse_Holder5x20mm_P5.08mm",
		"gnd": "Symbol:GND",
		#"inductor": "Inductor_THT:L_Axial_D6.5mm_P10.16mm",
		#"integrated_circuit": "Package_DIP:DIP-14_W7.62mm",
		#"integrated_cricuit-ne555": "Package_DIP:DIP-8_W7.62mm",
		#"lamp": "Lamp_THT:Bulb_D3.8mm_P1.27mm",
		#"microphone": "Audio_Module:Microphone_Cylindrical_D9.7mm_P2.54mm",
		#"motor": "Motor_Module:DC_Motor",
		# "nand": "Logic_Integrated_Circuits:74HC00",
		# "nor": "Logic_Integrated_Circuits:74HC02",
		# "not": "Logic_Integrated_Circuits:74HC04",
		#"operational_amplifier": "Amplifier_OpAmp:DIP-8_W7.62mm",
		#"optocoupler": "Optocoupler:DIP-4_W7.62mm",
		# "or": "Logic_Integrated_Circuits:74HC32",
		# "probe-current": "Measurement_Module:Current_Probe",
		# "relay": "Relay_THT:Relay_SPDT_Legacy",
		"resistor": "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P15.24mm_Horizontal",
		# "resistor-adjustable": "Resistor_Variable:RV_Potentiometer_20x4mm",
		# "resistor-photo": "Resistor_Special:LDR",
		# "schmitt_trigger": "Logic_Integrated_Circuits:74HC14",
		# "socket": "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
		# "speaker": "Audio_Module:Speaker_Round_D15mm_P2.54mm",
		# "switch": "Switch_THT:SW_Push_SPST",
		# "terminal": "Connector:Terminal_Block_P5.08mm_2x02",
		# "text": "Symbol:Text",
		# "thyristor": "Thyristor_THT:SCR_TO-220",
		# "transformer": "Transformer_THT:Transformer_EI30",
		# "transistor": "Transistor_THT:TO-92_BCE",
		# "transistor-photo": "Photo_Transistor:TIL78",
		# "triac": "Triac_THT:TRIAC_TO-220",
		# "varistor": "Varistor_THT:V_Disc_10mm",
		# "voltage-dc": "Power_Module:DC_Supply",
		# "voltage-dc_ac": "Power_Module:AC_DC_Supply",
		# "voltage-dc_regulator": "Voltage_Regulator:Linear_Regulator_TO-220",
		# "vss": "Symbol:VSS",
		# "xor": "Logic_Integrated_Circuits:74HC86",
	}

	name_map = {
		# "and": "AND",
		# "antenna": "ANT",
		"capacitor-polarized": "C",
		"capacitor-unpolarized": "C",
		# "crossover": "CROSS",
		# "diac": "DIAC",
		"diode": "D",
		# "diode-light_emitting": "LED",
		# "fuse": "FUSE",
		"gnd": "GND",
		# "inductor": "L",
		# "integrated_circuit": "IC",
		# "integrated_cricuit-ne555": "NE555",
		# "lamp": "LAMP",
		# "microphone": "MIC",
		# "motor": "MOT",
		# "nand": "NAND",
		# "nor": "NOR",
		# "not": "NOT",
		# "operational_amplifier": "OPAMP",
		# "optocoupler": "OPTO",
		# "or": "OR",
		# "probe-current": "CURR_PROBE",
		# "relay": "RELAY",
		"resistor": "R",
		# "resistor-adjustable": "R_ADJ",
		# "resistor-photo": "R_PHOTO",
		# "schmitt_trigger": "SCHMITT",
		# "socket": "SOCKET",
		# "speaker": "SPKR",
		# "switch": "SW",
		# "terminal": "TERM",
		# "text": "TXT",
		# "thyristor": "THY",
		# "transformer": "XFMR",
		# "transistor": "Q",
		# "transistor-photo": "Q_PHOTO",
		# "triac": "TRIAC",
		# "varistor": "VAR",
		# "voltage-dc": "V_DC",
		# "voltage-dc_ac": "V_DC_AC",
		# "voltage-dc_regulator": "V_REG",
		# "vss": "VSS",
		# "xor": "XOR",
	}

	# Store actual parts to manage connections
	# previous_layer_parts = []
	try:
		new_comp_stack = []
		for comps in comp_stack:
			for comp in comps:
				if comp in name_map:
					new_comp_stack.append([comp])

		print(new_comp_stack)
		prev = None
		for i, comps in enumerate(new_comp_stack):
			for comp in comps:
				part = Part("Device", name_map[comp], 
							footprint=footprint_map[comp])
				
				if i == 0:
					part[1] += vin
				elif i == len(new_comp_stack) - 1:
					part[1] += prev[2]
					part[2] += gnd
				else:
					part[1] += prev[2]
				prev = part
		 

		# Generate netlist
		generate_netlist(tool=KICAD8)
				
		"""
		# Iterate through each layer in the stack
		for layer_index, layer in enumerate(comp_stack):
			current_layer_parts = []
			print(layer_index)

			# Iterate through each component in the current layer
			for comp_index, comp_type in enumerate(layer):
				# Create part with specific footprint
				print(comp_type)
				if comp_type not in name_map:
					continue
				part = Part("Device", name_map[comp_type], 
							footprint=footprint_map[comp_type])
				
				# Connection logic
				if layer_index == 0:
					# First layer: connect first pin to input voltage
					part[1] += vin
				
				if layer_index == len(comp_stack) - 1:
					# Last layer: connect last pin to output voltage
					part[2] += vout
				
				# Inter-layer connections
				if previous_layer_parts:
					# Connect current part to a part from the previous layer
					# Use modulo to handle cases with different layer lengths
					prev_part_index = comp_index % len(previous_layer_parts)
					part[1] += previous_layer_parts[prev_part_index]
				
				# Store current part for next iteration
				current_layer_parts.append(part)
				
				# Debug output
				print(f"Layer {layer_index}, Component {comp_index}: "
					  f"Created {part.name} part, footprint: {part.footprint}")

			# Update previous layer for next iteration
			previous_layer_parts = current_layer_parts
			"""

	

	except Exception as e:
		print(f"Circuit generation failed: {e}")

if __name__ == "__main__":
	comp_stack = [["capacitor-unpolarized"], ["resistor"]]
	create_circuit_topology(comp_stack)