# Snow Depth Measurement
Automated measurement of snow depth using outdoor cameras

Project Structure:
- the main python script that is executed by the user is snow_depth.py
- the remaining scripts that are used to perform individual functions (e.g.
	equalization) are stored inside the "./includes" directory

Steps:
1) enter the following command into the terminal "python snow_depth.py"
2) this brings up the GUI that is used to set the parameters required for the
		execution of the script
3) inside the GUI the user may generate a template and create settings/HSV profiles

		templates:
		- used to register the input images
		- stored in "./includes/templates"
		- to generate a template proceed to and follow the instructions

		settings profile:
		- store settings used in the script (e.g. crop, minimum blob size, etc.)
		- to create a settings profile proceed to and follow the instructions

		HSV profile:
		- used to filter the input image and detect blobs

		- all settings are stored inside the preferences.cfg file which is found in
			the same directory as snow_depth.py (this file is automatically generated,
			accessed and modified by the script. The user does not need to alter it)

4) press to run the script (the steps of the script are detailed below)

Script process:
1) Filter out night Images (filter_night.py)
	- the snow depth cannot be measured in night images so these are filtered out
	- the provided HSV range(s) are used to determine the number of pixels deemed
		to be part of blobs
	- if the pixel count is greater than the threshold the image is considered day

2) Equalize images (equalize.py)
 	- the template and input images are equalized according to the parameters
		specified in the GUI
	- uses local histogram equalization

3) Register images to template (register.py)
	- images are registered to the template
	- uses ORB feature detection with a brute force matcher
	- fine tuned using ECC alignment algorithm

4) Overlay ROI onto Images (snow_depth.py)
	- the ROI from the template are overlayed onto the registered images
	- outputted for debugging purposes only

5) Determine which stakes are valid (check_stakes.py)
	- each image is checked to determine which stakes in the image are valid
	- conditions for valid stake: at least two blobs found
	- image is filtered using the rois determined from the template
	- each roi is checked for a contour resembling a blob
	- returns dictionary with image name as key
	- each value is an array listing which stakes are valid

6) Determine intersection points (get_intersection.py)
	- each valid stake is fitted with 3 lines that pass through the uppermost
		and lowest blobs
	- spike in pixel intensity (indicating transition to white/snow) is detected
		and used as the point of intersection
	- median intersection point is used
